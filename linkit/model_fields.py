import json
from typing import Optional, Union

from django.db import models

from linkit.link import Link


class LinkField(models.Field):
    """
    Basically just a CharField which holds our values. The json holds the following properties:
    type: str       Matches type from config
    value: dict     Value of the LinkType (could be a model_id, a string or multiple key/values
    label: str      Link label if allow_label from the config is True
    target: str     None or _blank
    no_follow: bool True or False
    """

    def __init__(self, types: list = None, allow_target: bool = False, allow_label: bool = True,
                 allow_no_follow: bool = False, *args, **kwargs):
        kwargs['max_length'] = 2000
        self.config = {
            'types': types or ['page'],
            'allow_target': allow_target,
            'allow_label': allow_label,
            'allow_no_follow': allow_no_follow,
        }

        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        from linkit.form_fields import LinkFormField
        defaults = {'form_class': LinkFormField, 'config': self.config, 'name': self.name}
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def _parse_link(self, value: Optional[str]) -> Link:
        """ Map given json string to Link object. """
        data = {}

        if value:
            data = json.loads(value)

        return Link(config=self.config, data=data, name=self.name)

    def get_prep_value(self, link: Optional[Link]) -> Optional[str]:
        """ Opposite of to_python to ensure our Link object can be stored in the DB. """
        if link:
            return link.to_json()

        return None

    def from_db_value(self, value: Optional[str], expression, connection, context = None) -> Optional[Link]:
        """ Convert data stored in db to Link object. """
        return self._parse_link(value)

    def to_python(self, value: Optional[Union[Link, str]]) -> Optional[Link]:
        """ Similar as from_db_value but used in deserialization or during the clean() in forms. """
        if isinstance(value, Link):
            return value

        return self._parse_link(value)

    def get_internal_type(self):
        return 'CharField'

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()

        # Enforced default in __init__, no need to return it
        del kwargs['max_length']

        # We need to include the current config and the fieldname to be able to reconstruct the field
        kwargs['types'] = self.config['types']
        kwargs['allow_target'] = self.config['allow_target']
        kwargs['allow_label'] = self.config['allow_label']
        kwargs['allow_no_follow'] = self.config['allow_no_follow']

        kwargs['name'] = self.name

        return name, path, args, kwargs
