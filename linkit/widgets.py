from typing import Optional

from cms.utils.urlutils import static_with_version
from django.forms import Widget, CharField, BooleanField, ChoiceField
from django.forms.renderers import DjangoTemplates

from linkit.link import Link
from linkit.types.manager import type_manager


class LinkWidget(Widget):
    template_name = 'django/forms/widgets/link.html'

    def __init__(self, config: dict, attrs=None):
        self.config = config
        super().__init__(attrs)

    def value_from_datadict(self, data, files, name) -> Link:
        """
        Get the selected type and initialise a Link object with all the data that got submitted in the POST.
        For now we'll just assign all the submitted data to the links value property and basically just
        use it as a DTO. In the LinkFormField's clean method this data will be validated and cleaned.
        """
        link_type = type_manager.get(data.get(f'{name}_link_type', None))
        link_data = {
            'type': link_type.identifier,
            'target': '_blank' if data.get('{}_link_target'.format(name), None) else None,
            'label': data.get('{}_link_label'.format(name), None),
            'no_follow': True if data.get('{}_link_no_follow'.format(name), None) else False,
            'value': data
        }

        return Link(config=self.config, data=link_data, name=name)

    @staticmethod
    def type_fields(link: Link) -> dict:
        """ Generate all fields for the different link types that are allowed in this link instance. """
        types = {}
        for link_type in link.config('types'):
            instance = type_manager.instance(link_type, link)
            try:
                markup = instance.render()
            except Exception:
                # Reset link value if target is no longer available
                instance.link._data['value'] = {}
                markup = instance.render()
            types[link_type] = {
                'markup': markup,
                'instance': instance,
            }

        return types

    @staticmethod
    def other_fields(link: Link, field_name: str) -> dict:
        """ All fields (except the type fields) that need to get rendered in the template. """
        label = CharField()
        target = BooleanField()
        no_follow = BooleanField()
        link_type = ChoiceField(choices=type_manager.type_choices(link.config('types')))

        fields = {
            'label': label.widget.render(
                '{}_link_label'.format(field_name),
                link.data('label'),
                attrs={'id': 'id_{}_link_label'.format(field_name)}
            ),
            'target': target.widget.render(
                '{}_link_target'.format(field_name),
                link.data('target') is not None,
                attrs={'id': 'id_{}_link_target'.format(field_name)}
            ),
            'link_type': link_type.widget.render(
                '{}_link_type'.format(field_name),
                link.data('type'),
                attrs={'id': 'id_{}_link_type'.format(field_name)}
            ),
            'no_follow': no_follow.widget.render(
                '{}_link_no_follow'.format(field_name),
                link.data('no_follow'),
                attrs={'id': 'id_{}_link_no_follow'.format(field_name)}
            )
        }

        return fields

    def get_context(self, name: str, value: Link, attrs: dict):
        context = {
            'widget': {
                'name': name,
                'link': value,
                'type_fields': self.type_fields(value),
                'other_fields': self.other_fields(value, name),
                'allow_target': value.config('allow_target'),
                'allow_label': value.config('allow_label'),
                'allowed_types': value.config('types'),
                'allow_no_follow': value.config('allow_no_follow'),
            }
        }
        return context

    def render(self, name: str, value: Optional[Link], attrs: dict = None, renderer: DjangoTemplates = None):
        # On initial init value can be None
        if not value:
            value = Link(config=self.config, name=name)

        context = self.get_context(name, value, attrs)
        return self._render(self.template_name, context, renderer)

    class Media(object):
        """
        Media class copy pasted from the AdminFileWidget, otherwise it wont get rendered. On option would be to
        use a MultiWidget and render the different fields like that but I had a lot of troubles with this
        approach. Maybe there's a better way then just copy pasting it? Reflection?
        """
        css = {
            'all': [
                'filer/css/admin_filer.cms.icons.css',
                'filer/css/admin_filer.css',
                'filer/css/admin_filer.fa.icons.css',
                'filer/css/admin_folderpermissions.css'
            ]
        }
        js = (
            static_with_version('cms/js/dist/bundle.forms.pageselectwidget.min.js'),
            'filer/js/libs/dropzone.min.js',
            'filer/js/addons/dropzone.init.js',
            'filer/js/addons/popup_handling.js',
            'filer/js/addons/widget.js',
        )
