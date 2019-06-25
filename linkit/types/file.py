from typing import Optional

from django.utils.translation import ugettext_lazy as _
from filer.fields.file import AdminFileFormField
from filer.models import File

from linkit.models import FakeLink
from linkit.types.contracts import LinkType, TypeForm


class LinkItFilerField(AdminFileFormField):
    """
    Custom Filer field type we can use in our own forms. We need a fake relationship for this field to work
    properly. Unfortunately I never really understood the reasons for it :(
    """

    def __init__(self, *args, **kwargs):
        kwargs['rel'] = FakeLink._meta.get_field('fake_file').remote_field
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        """
        Overwrite the default logic and don't do any testing or similar and just return the id. Otherwise we
        couldn't just pass in None as a queryset which again would result in a multitude of problems.
        """
        return value


class FileTypeForm(TypeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].link_type = self.link_type

    file = LinkItFilerField(queryset=None, to_field_name=None)


class FileType(LinkType):
    identifier = 'file'
    type_label = _('File')
    form_class = FileTypeForm

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
        return File.objects.filter(pk=self.link.data('value').get('file')).first()
