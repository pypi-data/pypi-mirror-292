# Copyright © 2024 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.policy import string_propagation
from contrast.agent.policy import registry
from contrast.agent.policy.applicator import register_import_hooks
from contrast.agent.policy.rewriter import apply_rewrite_policy
from contrast.agent.settings import Settings
from contrast.assess_extensions import cs_str
from contrast.patches import (
    cs_str as cs_str_patches,
    register_assess_patches,
    register_common_patches,
    register_library_patches,
)
from contrast.utils.namespace import Namespace
from contrast.utils.patch_utils import repatch_imported_modules
from contrast_rewriter import register as register_rewriter

from contrast_vendor import structlog as logging

logger = logging.getLogger("contrast")

HAS_FUNCHOOK = cs_str.has_funchook()
ALWAYS_PURE_PYTHON_METHODS = ["format", "__repr__", "__getitem__"]


class module(Namespace):
    hook = None
    assess_patches_enabled: bool = False


hook_module_map = {
    str: cs_str.create_unicode_hook_module() if HAS_FUNCHOOK else None,
    bytes: cs_str.create_bytes_hook_module() if HAS_FUNCHOOK else None,
    bytearray: cs_str.create_bytearray_hook_module() if HAS_FUNCHOOK else None,
}


def apply_extension_hook(funchook, strtype, hook_module, method_name):
    """
    Apply extension hook for a particular string method

    Returns False if the hook failed to apply and True otherwise
    """
    hook_name = f"apply_{method_name}_hook"
    hook_method = getattr(hook_module, hook_name)

    try:
        hook_method(funchook)
    except RuntimeError as e:
        logger.debug(
            "Failed to apply C extension hook for %s.%s. Will retry in pure python. %s",
            strtype.__name__,
            method_name,
            e,
        )
        return False

    return True


def enable_method_hooks(funchook, hook_module_map, use_extension_hooks=True):
    """
    Enable string propagation hooks for individual string type methods

    This method uses policy to determine all of the string methods that need to be
    patched. For each string type, it first attempts to apply the patch using C
    extension hooks (if not explicitly disallowed by `use_extension_hooks`). If that
    fails for any reason, it will then fall back to applying a pure Python patch.
    """
    use_extension_hooks = use_extension_hooks and HAS_FUNCHOOK

    for strtype, hook_module in hook_module_map.items():
        for node in registry.get_string_method_nodes():
            method_name = node.method_name

            if method_name.lower() in ["cast", "concat"]:
                # these are applied directly in the C extension only
                continue

            real_method_name = (
                "format_map" if method_name == "formatmap" else method_name
            )

            if not hasattr(strtype, real_method_name):
                continue

            if method_name not in ALWAYS_PURE_PYTHON_METHODS and use_extension_hooks:
                if apply_extension_hook(funchook, strtype, hook_module, method_name):
                    logger.debug(
                        "Applied C extension hook for %s.%s",
                        strtype.__name__,
                        method_name,
                    )
                    continue

            cs_str_patches.patch_strtype_method(strtype, real_method_name)
            logger.debug(
                "Applied pure Python patch for %s.%s", strtype.__name__, method_name
            )


def enable_assess_patches(use_extension_hooks=True):
    """
    Enables extension hooks and other string patches.

    Has no effect if these patches are already enabled.
    """
    if module.assess_patches_enabled:
        return

    logger.debug("has funchook: %s", HAS_FUNCHOOK)

    # NOTE: This function *must* be called before the extension is initialized
    # string_propagation.build_string_propagator_functions()
    string_propagation.build_string_propagator_functions()

    try:
        module.hook = cs_str.initialize()

        cs_str.enable_required_hooks(module.hook)
    except RuntimeError:
        logger.error(
            "Local python builds on OSX may lead to 'Failed to unprotect memory'"
        )
        logger.error(
            "If this applies to you, try running `contrast-fix-interpreter-permissions`"
        )
        raise

    use_extension_hooks = (
        use_extension_hooks
        and not Settings().config.get("agent.python.assess.use_pure_python_hooks")
        and HAS_FUNCHOOK
    )

    cs_str_patches.enable_str_properties()
    enable_method_hooks(
        module.hook, hook_module_map, use_extension_hooks=use_extension_hooks
    )

    try:
        cs_str.install(module.hook)
    except RuntimeError:
        logger.error(
            "Local python builds on OSX may lead to 'Failed to unprotect memory'"
        )
        logger.error(
            "If this applies to you, try running `contrast-fix-interpreter-permissions`"
        )
        raise

    module.assess_patches_enabled = True


def disable_assess_patches():
    """
    Disables extension hooks and other string patches.

    Has no effect if these patches are not already enabled.

    This does not disable "pure python" strtype patches applied with set_attr_on_type.
    """
    if not module.assess_patches_enabled:
        return

    cs_str.disable(module.hook)

    module.assess_patches_enabled = False


def _enable_protect_patches():
    register_common_patches()

    logger.debug("adding protect policy")
    register_import_hooks(protect_mode=True)

    # This has no effect if the patches are not enabled
    disable_assess_patches()


def _enable_assess_patches(settings: Settings):
    enable_assess_patches()

    # Policy-based rewrites need to be applied prior to any policy patches.
    # Policy patches can be layered on top of rewritten functions. So that
    # means we need to make sure that the "original" function called by the
    # policy patch is the *rewritten* one.
    # Pathlib rewrites must not be applied here. They are only stable when applied by
    # the runner. The exact reason for this is unknown, but it's related to repatching.
    # If this causes noticeable issues, use the runner. This will eventually be
    # mandatory anyway, and policy-based rewrites will be removed from here entirely.
    apply_rewrite_policy(rewrite_pathlib=False)

    logger.debug("enabled assess string patches")
    register_common_patches()
    register_assess_patches()

    logger.debug("adding assess policy")
    register_import_hooks()

    # This is included as a fallback so that we continue to support the case
    # where the runner is not used. If the rewriter has already been enabled by
    # the runner, this has no effect (other than to log a message).
    # Eventually once the runner is fully supported we might feel comfortable
    # removing this code.
    if settings.is_rewriter_enabled:
        register_rewriter(override_config=True)


def enable_patches():
    settings = Settings()

    if settings.is_analyze_libs_enabled():
        register_library_patches()

    if settings.is_protect_enabled():
        _enable_protect_patches()

    from contrast.agent import agent_state

    if agent_state.module.assess_enabled:
        _enable_assess_patches(settings)

    logger.debug("revisiting imported modules to apply patches")
    repatch_imported_modules()
