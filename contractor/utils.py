import logging

from django.core.files.storage import default_storage

from lxml import etree
import lxml.html

logger = logging.getLogger(__name__)


def extract_html(contract, xpath):
    filename, xpath = xpath.split('#', 1)
    path = contract.get_file_path(filename)
    try:
        content = default_storage.open(path).read()
        root = lxml.html.fromstring(content.decode('utf-8'))
    except Exception as e:
        logger.exception(e)
        return ''
    try:
        selection = root.xpath(xpath)
        return '\n'.join(
            etree.tostring(s, pretty_print=True).decode('utf-8')
            for s in selection
        )
    except Exception as e:
        logger.exception(e)
    return ''
