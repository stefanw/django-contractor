from django.db import models

from cms.models.pluginmodel import CMSPlugin


class ContractWorkPlugin(CMSPlugin):
    """
    CMS Plugin for displaying latest investigations
    """

    contract = models.ForeignKey(
        'Contract', on_delete=models.CASCADE
    )

    javascript = models.TextField(blank=True)
    styles = models.TextField(blank=True)

    version = models.IntegerField(default=0)
    xpath = models.CharField(max_length=255, blank=True)
    html = models.TextField(blank=True)

    def __str__(self):
        return self.contract.name

    def get_html(self):
        if self.contract.version == self.version:
            return self.html

        if not self.xpath:
            return ''

        from .utils import extract_html

        self.html = extract_html(self.contract, self.xpath)
        self.version = self.contract.version
        self.save()

        return self.html

    def get_js(self):
        return self.contract.get_file_urls(self.javascript)

    def get_css(self):
        return self.contract.get_file_urls(self.styles)
