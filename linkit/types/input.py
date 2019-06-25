from typing import Optional

from django.forms import CharField
from django.utils.translation import ugettext_lazy as _

from linkit.types.contracts import LinkType, TypeForm


class InputTypeForm(TypeForm):
    input = CharField(label=_('Website'), help_text=_('prefix with https, mailto or tel'), max_length=2048)


class InputType(LinkType):
    """ Hint: This is the field for an external link. """
    identifier = 'input'
    type_label = _('externer Link')
    form_class = InputTypeForm

    @property
    def href(self):
        return self.real_value() or None

    @property
    def label(self):
        return self.real_value() or None

    def real_value(self) -> Optional[str]:
        return self.link.data('value').get('input')

