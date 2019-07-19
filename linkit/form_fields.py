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
        Validate given Link object. We do this by get a form instance of the link type and grab the
        first error (if one) and raise it.
        """
        form = value.link_type.form(required=self.required)
        if not form.is_valid():
            for key, error in form.errors.as_data().items():
                raise error[0]
        else:
            value._data['value'] = form.cleaned_data

        return value
