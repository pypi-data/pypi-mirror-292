"""Project models."""
import decimal
import html
from enum import Enum
from typing import Any

from cms.models.pluginmodel import CMSPlugin
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.formats import number_format
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .fetcher import get_value


class FetchType(Enum):
    """Fetch type."""

    first = 'first'
    all = 'all'
    text = 'text'


FETCHER_CHOICE = (
    (FetchType.first.value, FetchType.first.value),
    (FetchType.all.value, FetchType.all.value),
    (FetchType.text.value, FetchType.text.value),
)


class ShowValue(CMSPlugin):
    """Show value from JSON source."""

    source = models.URLField(
        help_text=_("The URL of the source JSON data. Downloaded data is cached for the time set in settings."))
    query = models.CharField(max_length=255, help_text=_("Query to JSON value."))
    fetcher = models.CharField(max_length=5, choices=FETCHER_CHOICE, default=FetchType.first.value,
                               help_text=_("Functions to get the query result."))
    wrapper = models.CharField(max_length=255, null=True, blank=True,
                               help_text=_('Wrap the value into the string. E.g. "&lt;table&gt;{}&lt;/table&gt;"'))
    mark_safe = models.BooleanField(default=False,
                                    help_text=_("Allow the use of HTML. Caution! Use only with a trusted source."))
    localize = models.BooleanField(default=False, help_text=_("Localize the value. Applies to numbers only."))
    show_when_missing = models.CharField(max_length=255, null=True, blank=True,
                                         help_text=_('Show when value is not available.'))
    attributes = models.JSONField(
        null=True, blank=True, encoder=DjangoJSONEncoder,
        help_text='Tag attributes as JSON data. E.g. {"class": "my-value current", "id": 42}')

    def __str__(self) -> str:
        return f"{self.query} {self.source}"

    @property
    def value(self) -> Any:
        """Get value."""
        value = get_value(self.source, self.query, self.fetcher)
        if value is None:
            return value
        if isinstance(value, list):
            value = "\n".join(map(str, value))
        if self.localize and isinstance(value, (decimal.Decimal, float, int)):
            value = number_format(value, use_l10n=True, force_grouping=True)
        if self.wrapper is not None:
            value = self.wrapper.format(value)
        if self.mark_safe:
            value = mark_safe(value)
        return value

    @property
    def html_attributes(self) -> str:
        """Get HTML attributes."""
        attrs = {} if self.attributes is None else self.attributes.copy()
        if self.value is None:
            attrs["class"] = attrs.get("class", "") + " value-not-available"
        return mark_safe(
            " ".join([f'{html.escape(str(name))}="{html.escape(str(value))}"' for name, value in attrs.items()])
        )
