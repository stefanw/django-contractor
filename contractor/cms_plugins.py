from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import ContractWorkPlugin


@plugin_pool.register_plugin
class ContractWorkCMSPlugin(CMSPluginBase):
    """
    Plugin for including a selection of entries
    """
    module = 'Contract'
    name = 'Render contract work'
    model = ContractWorkPlugin
    render_template = 'contractor/render.html'
    text_enabled = True

    def render(self, context, instance, placeholder):
        """
        Update the context with plugin's data
        """
        context = super().render(context, instance, placeholder)
        context['instance'] = instance
        context['html'] = instance.get_html()
        context['path'] = instance.contract.get_file_url()
        return context
