from typing import Type, Optional

from cms.forms.fields import PageSelectFormField
from cms.models import Page
from django.forms import CharField, ModelChoiceField
from django.utils.translation import ugettext_lazy as _
from filer.fields.file import AdminFileFormField
from filer.models import File

from linkit.link import Link
from linkit.models import FakeLink


class LinkType(object):
    """ Base class for all possible link types. """
    identifier = None
    type_label = None

    def __init__(self, link: Link):
        self.link = link

    @classmethod
    def post_attribute(cls) -> str:
        return cls.identifier

    @property
    def value(self):
        """
        Check if the current Link object has a type matching our identifier. Opposing to the real_value method,
        this method just returns the value we saved in the json. E.g a model id or a string.
        """
        if self.link.data('type') == self.identifier:
            return self.link.data('value')

        return None

    def real_value(self):
        """ Returns the actual value selected. E.g. a Page or a FilerFile instance. """
        raise NotImplementedError

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

    def render(self):
        raise NotImplementedError


class ModelLinkType(LinkType):
    model = None

    def real_value(self):
        return self.model.objects.filter(pk=self.link.data('value')).first()

    @property
    def href(self):
        real_value = self.real_value()
        if real_value:
            return real_value.get_absolute_url()

        return False

    @property
    def label(self):
        real_value = self.real_value()
        if real_value:
            return str(real_value)

        return False

    def queryset(self):
        return self.model.objects.all()

    def render(self):
        field = ModelChoiceField(queryset=self.queryset())
        return field.widget.render(self.id, self.value, attrs=self.attrs)


class PageType(LinkType):
    identifier = 'page'
    type_label = _('CMS Seite')

    def real_value(self) -> Optional[Page]:
        return Page.objects.filter(pk=self.link.data('value')).first()

    @property
    def href(self):
        real_value = self.real_value()
        if real_value:
            return real_value.get_absolute_url()

        return False

    @property
    def label(self):
        real_value = self.real_value()
        if real_value:
            return real_value.get_title()

        return False

    @classmethod
    def post_attribute(cls) -> str:
        """ Overwrite the default since the PageSelectFormField Widget returns it like that. ¯\_(ツ)_/¯ """
        return '{}_1'.format(cls.identifier)

    def render(self):
        field = PageSelectFormField(queryset=Page.objects.drafts(), to_field_name=self.id)
        return field.widget.render(self.id, self.value, attrs=self.attrs)


class FileType(LinkType):
    identifier = 'file'
    type_label = _('Datei')

    @property
    def href(self):
        real_value = self.real_value()
        if real_value:
            return real_value.url

        return False

    @property
    def label(self):
        real_value = self.real_value()
        if real_value:
            return real_value.label

        return False

    def real_value(self) -> Optional[File]:
        return File.objects.filter(pk=self.link.data('value')).first()

    def render(self):
        rel = FakeLink._meta.get_field('fake_file').remote_field
        field = AdminFileFormField(rel=rel, queryset=None, to_field_name=self.id)
        return field.widget.render(name=self.id, value=self.value, attrs=self.attrs)


class InputType(LinkType):
    """ Hint: This is the field for an external link. """
    identifier = 'input'
    type_label = _('externer Link')

    @property
    def href(self):
        return self.real_value() or None

    @property
    def label(self):
        return self.real_value() or None

    def real_value(self) -> Optional[str]:
        return self.link.data('value')

    def render(self):
        field = CharField()
        return field.widget.render(self.id, self.value, attrs=self.attrs)


class LinkTypeManager(object):
    def __init__(self):
        self._types = {}

    def get(self, identifier: str):
        if identifier not in self._types:
            raise ValueError(
                'Invalid type "{}". Make sure to register it in the LinkTypeManager before using.'.format(identifier))

        return self._types[identifier]

    def instance(self, identifier: str, link: Link):
        return self.get(identifier)(link)

    def register(self, link_type: Type[LinkType]):
        self._types[link_type.identifier] = link_type

    def type_choices(self, limit_to: list) -> list:
        """ Transform possible registered types to a usable format for the ChoicesField. """
        result = {}
        for identifier, type in self._types.items():
            if identifier not in limit_to:
                continue
            result[identifier] = type.type_label

        return list(result.items())

    def post_parameters(self, field_name: str) -> dict:
        """ Helper for the widget to tell it wat post attributes are relevant. """
        parameters = {}
        for identifier, type in self._types.items():
            parameters[identifier] = '{}_link_{}'.format(field_name, type.post_attribute())

        return parameters


type_manager = LinkTypeManager()
type_manager.register(PageType)
type_manager.register(FileType)
type_manager.register(InputType)
