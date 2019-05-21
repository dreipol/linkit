from django.core.exceptions import ValidationError
from django.forms import forms

from linkit.link import Link
from linkit.widgets import LinkWidget


class LinkFormField(forms.Field):
    widget = LinkWidget

    def __init__(self, config: dict, name: str, *args, **kwargs):
        self.config = config
        self.field_name = name
        widget_instance = self.widget(config=self.config)
        super().__init__(widget=widget_instance, *args, **kwargs)

    def to_python(self, value: Link):
        """
        Gets called from the widgets value_from_data_dict method. We could hook in here to transform the data.
        """
        return value

    def clean(self, value: Link) -> Link:
        """
        Validate given Link object. Currently we're only checking for required or not.
        """
        if value.data('value') in self.empty_values and self.required:
            raise ValidationError(self.error_messages['required'])

        return value
