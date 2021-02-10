import base64
import hashlib
import logging
from urllib.parse import urlunparse, urlparse, urlencode

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

import lxml.html
import requests


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


def is_full_url(line):
    return line.startswith(('https://', 'http://'))


def download_and_save_file(url, path):
    response = requests.get(url)
    # FIXME: returned path is not stored, assumed to be the same
    default_storage.save(path, ContentFile(response.content))


def get_integrity_for_resource(resource):
    if resource.path is None:
        response = requests.get(resource.url)
        raw_bytes = response.content
    else:
        resource_file = default_storage.open(resource.path)
        raw_bytes = resource_file.read()
    raw_digest = hashlib.sha384(raw_bytes).digest()
    b64_digest = base64.b64encode(raw_digest).decode('ascii')
    return 'sha384-{}'.format(b64_digest)


def resource_to_filename(resource):
    parsed = urlparse(resource.url)
    query_params = {
        k: v if isinstance(v, str) else ''
        for k, v in resource.attributes.items()
    }
    query = urlencode(query_params, doseq=True)
    if resource.path:
        return '{}?{}'.format(resource.filename, query)
    return urlunparse(parsed._replace(query=query))
