"""Admin form."""

from typing import Optional

import jq  # type: ignore[import-not-found]
import requests
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from .fetcher import load_source
from .models import ShowValue


class ShowValueForm(ModelForm):
    """Show value form."""

    class Meta:
        model = ShowValue
        exclude: list[str] = []

    def clean_wrapper(self) -> Optional[str]:
        """Clean field wrapper."""
        value = self.cleaned_data.get("wrapper")
        if value is not None:
            expression = value.count("{}")
            if expression != 1:
                raise ValidationError(_("There must be one {} expression in the string."))
        return value

    def clean(self) -> None:
        """Clean form."""
        cleaned_data = super().clean()
        if self.is_valid():
            if "source" in self.changed_data:
                try:
                    data = load_source(cleaned_data["source"])
                except requests.RequestException as error:
                    self.add_error("source", error)
                else:
                    try:
                        jq.compile(cleaned_data["query"]).input(data).first()
                    except ValueError as error:
                        self.add_error("query", error)
