from collections import namedtuple
from urllib.parse import urlparse, parse_qs, urlunparse
import uuid

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from .utils import is_full_url


CONTRACTOR_DIR = getattr(settings, 'CONTRACTOR_DIR', 'contractor')
CONTRACTOR_URL = getattr(settings, 'CONTRACTOR_URL', settings.MEDIA_URL)

Resource = namedtuple('Resource', ['url', 'attributes', 'filename', 'path'])


def get_url_path(slug, version, filename):
    return '/'.join([CONTRACTOR_DIR, slug, str(version), filename])


class Contract(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL
    )
    token = models.UUIDField(default=uuid.uuid4)
    webhook_active = models.BooleanField(default=False)

    version = models.IntegerField(default=0)
    source_url = models.URLField()

    files = models.TextField(blank=True)

    webhook_log = models.TextField(blank=True)

    class Meta:
        verbose_name = 'contract'
        verbose_name_plural = 'contracts'

    def __str__(self):
        return self.name

    def get_absolute_url(self, filename=''):
        return CONTRACTOR_URL + get_url_path(
            self.slug,
            self.version,
            filename
        )

    def get_webhook_url(self):
        return reverse('contractor:webhook', kwargs={'token': self.token})

    def get_source_files(self):
        for line in self.get_lines():
            if is_full_url(line):
                continue
            else:
                filename = urlparse(line).path
                yield (filename, self.source_url + filename)

    def get_file_path(self, filename=''):
        return get_url_path(self.slug, self.version, filename)

    def get_file_url(self, filename=''):
        if is_full_url(filename):
            return filename

        path = get_url_path(self.slug, self.version, filename)
        return CONTRACTOR_URL + path

    def get_lines(self):
        for line in self.files.splitlines():
            line = line.strip()
            if not line:
                continue
            yield line

    def get_resources(self, filter_files=None):
        for line in self.get_lines():
            if filter_files is not None and not line.startswith(filter_files):
                continue
            url = self.get_file_url(line)
            path = None
            filename = urlparse(line).path
            if not is_full_url(line):
                path = self.get_file_path(filename)
            parsed = urlparse(url)
            url = urlunparse(parsed._replace(query=''))  # remove query
            query = parse_qs(parsed.query, keep_blank_values=True)
            attributes = {key: query[key][0] or True for key in query}

            yield Resource(url, attributes, filename, path)


try:
    from .cms_models import ContractWorkPlugin  # noqa
except ImportError:
    # Ignore errors if Django CMS is not installed
    pass
