from typing import Optional

from django.forms import Form


class LinkType(object):
    """ Base class for all possible link types. """
    identifier = None
    type_label = None
    form_class = None

    def __init__(self, link):
        self.link = link

    def form(self, link_name: str = None, data: dict = None, initial: bool = False, required: bool = True) -> Form:
        """
        Works also for LinkType types. So use this method directly if you only have type and use
        instance_form method if you have an actual instance.
        """
        data = data or self.link.data('value', {})
        link_name = link_name or self.link.name

        kwargs = {'prefix': f'{link_name}_link_{self.identifier}', 'link_type': self, 'required': required}

        if initial:
            kwargs['initial'] = data
        else:
            kwargs['data'] = data

        return self.form_class(**kwargs)

    @property
    def value(self):
        """
        Check if the current Link object has a type matching our identifier. Opposing to the real_value method,
        this method just returns the value we saved in the json. E.g a model id or a string.
        """
        if self.link.data('type') == self.identifier:
            return self.link.data('value')

        return None

    @property
    def href(self) -> Optional[str]:
        """ Returns the href of the real_value. """
        raise NotImplementedError

    @property
    def label(self) -> Optional[str]:
        """ Returns the label of the real_value. """
        raise NotImplementedError

    @property
    def id(self) -> str:
        return '{}_link_{}'.format(self.link.name, self.identifier)

    @property
    def attrs(self) -> dict:
        return {'id': 'id_{}'.format(self.id)}

    def real_value(self):
        """ Returns the actual value selected. E.g. a Page or a FilerFile instance. """
        raise NotImplementedError

    def render(self):
        # We ignore the required parameter since in this case we're just rendering the form and
        # won't do any validation.
        return self.form(initial=True).as_p()


class TypeForm(Form):
    """ Base class for all link type forms. """

    def __init__(self, *args, **kwargs):
        self.link_type = kwargs.pop('link_type')

        # Since we're nesting the printed markup of a form in a parent formfield (LinkFormField), we somehow
        # need to pass the required state of that field down to our actual form.
        self.parent_required = kwargs.pop('required')
        super().__init__(*args, **kwargs)

        for index, field in self.fields.items():
            field.required = self.parent_required
