from typing import Optional

from cms.forms.fields import PageSelectFormField
from cms.models import Page
from django.utils.translation import ugettext_lazy as _

from linkit.types.contracts import LinkType, TypeForm


class PageTypeForm(TypeForm):
    def __init__(self, *args, **kwargs):
        """ Set the queryset and label dynamically based on the properties defined on the link type. """
        super().__init__(*args, **kwargs)
        self.fields['page'].to_field_name = self.link_type.id

    page = PageSelectFormField(queryset=Page.objects.drafts(), to_field_name=None)


class PageType(LinkType):
    identifier = 'page'
    type_label = _('CMS Page')
    form_class = PageTypeForm

    def real_value(self) -> Optional[Page]:
        if isinstance(self.link.data('value').get('page'), int):
            return Page.objects.filter(pk=self.link.data('value').get('page')).first()
        else:
            return Page.objects.filter(pk=self.link.data('value').get('page').pk).first()

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

