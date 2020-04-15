import uuid

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

CONTRACTOR_DIR = getattr(settings, 'CONTRACTOR_DIR', 'contractor')


def get_url_path(slug, version, filename):
    return '/'.join([CONTRACTOR_DIR, slug, str(version), filename])


def is_full_url(line):
    return line.startswith(('https://', 'http://'))


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
        return settings.MEDIA_URL + get_url_path(
            self.slug,
            self.version,
            filename
        )

    def get_webhook_url(self):
        return reverse('contractor:webhook', kwargs={'token': self.token})

    def get_source_files(self):
        for line in self.files.splitlines():
            line = line.strip()
            if not line:
                continue
            if is_full_url(line):
                continue
            else:
                yield (line, self.source_url + line)

    def get_file_path(self, filename=''):
        return get_url_path(self.slug, self.version, filename)

    def get_file_url(self, filename=''):
        if is_full_url(filename):
            return filename

        path = get_url_path(self.slug, self.version, filename)
        return settings.MEDIA_URL + path

    def get_file_urls(self, files=None):
        if not files:
            files = self.files
        for line in files.splitlines():
            line = line.strip()
            if not line:
                continue
            yield self.get_file_url(line)


try:
    from .cms_models import ContractWorkPlugin  # noqa
except ImportError:
    # Ignore errors if Django CMS is not installed
    pass
