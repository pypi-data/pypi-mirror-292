from datetime import datetime
from types import NoneType

import pytest

from ..Converters.ClassToOMFTypeConverter import (convert,
                                                  getOMFTypeFromPythonType,
                                                  omf_type, omf_type_property)
from ..Models import (OMFClassification, OMFFormatCode, OMFType, OMFTypeCode,
                      OMFTypeProperty, OMFTypeType)


@pytest.mark.parametrize(
    "type_hint,expected",
    [
        (bool, OMFTypeProperty(OMFTypeCode.Boolean)),
        (int, OMFTypeProperty(OMFTypeCode.Integer)),
        (float, OMFTypeProperty(OMFTypeCode.Number)),
        (datetime, OMFTypeProperty(OMFTypeCode.String, OMFFormatCode.DateTime)),
        (float | None, OMFTypeProperty([OMFTypeCode.Number, OMFTypeCode.Null])),
        (None | float, OMFTypeProperty([OMFTypeCode.Number, OMFTypeCode.Null])),
        (
            list[int],
            OMFTypeProperty(
                OMFTypeCode.Array, None, OMFTypeProperty(OMFTypeCode.Integer)
            ),
        ),
        (
            dict[str, str],
            OMFTypeProperty(
                OMFTypeCode.Object,
                OMFFormatCode.Dictionary,
                AdditionalProperties=OMFTypeProperty(OMFTypeCode.String),
            ),
        ),
        (
            list[list[int]],
            OMFTypeProperty(
                OMFTypeCode.Array,
                None,
                OMFTypeProperty(
                    OMFTypeCode.Array, None, OMFTypeProperty(OMFTypeCode.Integer)
                ),
            ),
        ),
        (
            dict[str, dict[str, str]],
            OMFTypeProperty(
                OMFTypeCode.Object,
                OMFFormatCode.Dictionary,
                AdditionalProperties=OMFTypeProperty(
                    OMFTypeCode.Object,
                    OMFFormatCode.Dictionary,
                    AdditionalProperties=OMFTypeProperty(OMFTypeCode.String),
                ),
            ),
        ),
    ],
)
def test_validGetOMFTypeFromPythonType(type_hint: type, expected: OMFTypeProperty):
    assert getOMFTypeFromPythonType(type_hint) == expected


@pytest.mark.parametrize(
    "type_hint", [NoneType, float | int, float | int | str, dict[int, str]]
)
def test_invalidGetOMFTypeFromPythonType(type_hint: type):
    with pytest.raises(ValueError):
        getOMFTypeFromPythonType(type_hint)


@omf_type()
class MyClass1:
    def __init__(self, timestamp: datetime, value: float):
        self.__timestamp = timestamp
        self.__value = value

    @omf_type_property(IsIndex=True)
    def timestamp(self) -> datetime:
        return self.__timestamp

    @omf_type_property()
    def value(self) -> float:
        return self.__value


@pytest.mark.parametrize(
    "omf_class,expected",
    [
        (
            MyClass1,
            OMFType(
                'MyClass1',
                OMFClassification.Dynamic,
                OMFTypeType.Object,
                Properties={
                    'timestamp': OMFTypeProperty(
                        OMFTypeCode.String, OMFFormatCode.DateTime, IsIndex=True
                    ),
                    'value': OMFTypeProperty(OMFTypeCode.Number),
                },
            ),
        )
    ],
)
def test_convert(omf_class: type, expected: OMFType):
    assert convert(omf_class) == expected
