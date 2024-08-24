from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from enum import Enum
from types import UnionType
from typing import Any, get_args, get_origin, get_type_hints


def dictionaryFactory(data):
    new_list = []
    for datum in data:
        if not datum[1]:
            continue
        data_type = type(datum[1])
        if data_type == datetime:
            new_list.append((datum[0], datum[1].isoformat()))
        elif data_type == list and issubclass(type(datum[1][0]), Enum):
            sub_list = []
            for item in datum[1]:
                sub_list.append(item.value.lower())
            new_list.append((datum[0], sub_list))
        elif issubclass(data_type, Enum):
            new_list.append((datum[0], datum[1].value))
        else:
            new_list.append(datum)

    return dict(new_list)


def deserialize(field_type, field_value):
    if isinstance(field_type, UnionType):
        args = get_args(field_type)
        result = None
        for arg in args:
            try:
                return deserialize(arg, field_value)
            except:
                pass

        return result

    if get_origin(field_type) is list:
        items = []
        arg = get_args(field_type)[0]
        for item in field_value:
            items.append(deserialize(arg, item))
        return items

    if get_origin(field_type) is dict:
        items = {}
        args = get_args(field_type)
        for k, v in field_value.items():
            items.update({deserialize(args[0], k): deserialize(args[1], v)})
        return items

    if issubclass(field_type, Serializeable):
        return field_type.fromJson(field_value)

    if field_type is Any:
        return field_value

    return field_type(field_value)


class Serializeable:
    def toDictionary(self):
        return asdict(self, dict_factory=dictionaryFactory)

    def toJson(self):
        return json.dumps(self.toDictionary())

    @classmethod
    def fromJson(cls, content: dict[str, Any]):
        test = {}
        for field, field_type in get_type_hints(cls).items():
            if field in content:
                test.update({field: deserialize(field_type, content[field])})

        return cls(**test)
