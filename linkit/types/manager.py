from json import JSONEncoder
from typing import Type

from django.db import models

from linkit.types.contracts import LinkType


class LinkTypeSerializer(JSONEncoder):
    """
    Our default serializer which makes sure our 'model' LinkType with its ModelChoiceField gets correctly
    Json-Serialized. You can use your own by overwriting the public serializer property on the
    LinkTypeManager.
    """

    def default(self, obj):
        if isinstance(obj, models.Model):
            return obj.pk
        return JSONEncoder.default(self, obj)


class LinkTypeManager(object):
    def __init__(self):
        self._types = {}
        self.serializer = LinkTypeSerializer

    def get(self, identifier: str):
        if identifier not in self._types:
            raise ValueError(
                'Invalid type "{}". Make sure to register it in the LinkTypeManager before using.'.format(identifier))

        return self._types[identifier]

    def instance(self, identifier: str, link):
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


type_manager = LinkTypeManager()
