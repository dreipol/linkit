import json
from typing import Optional


class Link(object):
    def __init__(self, config: dict, data: dict = None, name: str = None):
        data = data or {}

        self.name = name
        self._config = config
        self._data = {
            'type': data.get('type', None),
            'value': data.get('value', None),
            'label': data.get('label', None),
            'model': data.get('model', None),
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
    def value(self):
        """ Resolve the current type from the type_manager and get the real value of the link. """
        from linkit.types import type_manager
        return type_manager.instance(self.data('type'), self).real_value()

    @property
    def href(self):
        from linkit.types import type_manager
        return type_manager.instance(self.data('type'), self).href

    @property
    def target(self):
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
        from linkit.types import type_manager

        if self.config('allow_label') and self.data('label'):
            return self.data('label')

        return type_manager.instance(self.data('type'), self).label

    def to_json(self) -> str:
        return json.dumps(self.data())

    def config_to_json(self) -> str:
        """ Only used for debugging in the template. """
        return json.dumps(self.config())
