"""Project plugins."""

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _

from .forms import ShowValueForm
from .models import ShowValue


@plugin_pool.register_plugin
class ShowValuePlugin(CMSPluginBase):
    """Show value plugin."""

    model = ShowValue
    form = ShowValueForm
    name = _("Show JSON value")
    module = "jq"
    render_template = "djangocms_jq/plugin.html"
    change_form_template = "admin/djangocms_jq/change_form.html"
    text_enabled = True
