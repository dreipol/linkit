import json
from typing import Optional

from linkit.types.manager import type_manager


class Link(object):
    def __init__(self, config: dict, data: dict = None, name: str = None):
        data = data or {}

        self.name = name
        self._config = config
        self._data = {
            'type': data.get('type', None),
            'value': data.get('value', None),
            'label': data.get('label', None),
            'target': data.get('target', None),
            'no_follow': data.get('no_follow', None),
        }

    def data(self, attribute: Optional[str] = None, default=None):
        if not attribute:
            return self._data

        return self._data.get(attribute, default)

    def config(self, attribute: Optional[str] = None, default=None):
        if not attribute:
            return self._config

        return self._config.get(attribute, default)

    @property
    def link_type(self):
        """ Resolve the current type from the type_manager. Returns a LinkType. """
        return type_manager.instance(self.data('type'), self)

    @property
    def value(self):
        return self.link_type.real_value()

    @property
    def href(self):
        return self.link_type.href

    @property
    def target(self):
        link_type = self.link_type
        if hasattr(link_type, 'target'):
            return link_type.target

        if self.config('allow_target'):
            return self.data('target') or '_self'

        if self.data('type') in ['input', 'file']:
            return '_blank'

        return '_self'

    @property
    def external(self) -> bool:
        if self.target == '_self':
            return False

        return True

    @property
    def label(self) -> Optional[str]:

        if self.config('allow_label') and self.data('label'):
            return self.data('label')

        return type_manager.instance(self.data('type'), self).label

    def to_json(self) -> str:
        return json.dumps(self.data(), cls=type_manager.serializer)

    def config_to_json(self) -> str:
        """ Only used for debugging in the template. """
        return json.dumps(self.config())

    @property
    def set(self) -> bool:
        """
        Check if we have a value. If we have and its a dict, check if any of the properties
        actually contain anything. We explicitly don't use __bool__ since it's not the
        right use case for this scenario.
        """
        value = self.data('value', None)
        if not value:
            return False

        has_data = False
        if isinstance(value, dict):
            for key, v in value.items():
                if v:
                    has_data = True
                    break

        return has_data
