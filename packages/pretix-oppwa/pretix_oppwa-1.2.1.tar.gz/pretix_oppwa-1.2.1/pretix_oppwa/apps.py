from django.utils.translation import gettext_lazy

from pretix_oppwa import __compatibility__, __version__

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")


class PluginApp(PluginConfig):
    default = True
    name = "pretix_oppwa"
    verbose_name = "OPPWA payments"

    class PretixPluginMeta:
        name = gettext_lazy("OPPWA payments")
        author = "pretix Team"
        description = gettext_lazy(
            "Easily connect to any payment provider using OPPWA-based technology."
        )
        visible = True
        version = __version__
        compatibility = "pretix>=2024.4.0"
        category = "PAYMENT"
        compatibility = __compatibility__

    def ready(self):
        from . import signals  # NOQA
