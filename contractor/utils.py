import logging

from django.core.files.storage import default_storage

import lxml.html

logger = logging.getLogger(__name__)


def extract_html(contract, xpath):
    if '#' not in xpath:
        filename = 'index.html'
    else:
        filename, xpath = xpath.split('#', 1)

    path = contract.get_file_path(filename)
    try:
        content = default_storage.open(path).read()
        root = lxml.html.fromstring(content.decode('utf-8'))
    except Exception as e:
        logger.exception(e)
        return ''

    # Convert relative img paths to full media URLs
    selections = root.xpath(xpath)
    for selection in selections:
        for img in selection.xpath('//img'):
            src = img.attrib['src']
            if not src.startswith(('http://', 'https://', '/')):
                img.attrib['src'] = contract.get_file_url(src)

    try:
        return '\n'.join(
            lxml.html.tostring(s, pretty_print=True).decode('utf-8')
            for s in selections
        )
    except Exception as e:
        logger.exception(e)
    return ''

compute_subresource_integrity()