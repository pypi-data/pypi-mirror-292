from dataclasses import dataclass
from datetime import datetime

import pytest

from ..Converters.ClassToOMFTypeConverter import omf_type, omf_type_property
from ..Models import OMFContainer, OMFData, OMFExtrapolationMode, Serializeable


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


@dataclass
class MyClass2:
    timestamp: datetime
    value: float


@pytest.mark.parametrize(
    "model,expected",
    [
        (
            OMFContainer(
                'test',
                'test',
                Tags=['1', '2'],
                Metadata={'1': 'hello', '2': 'hi'},
                Extrapolation=OMFExtrapolationMode.All,
            ),
            {
                'Id': 'test',
                'TypeId': 'test',
                'Tags': ['1', '2'],
                'Metadata': {'1': 'hello', '2': 'hi'},
                'Extrapolation': 'All',
            },
        ),
        (
            OMFData[MyClass1]([MyClass1(datetime(2000, 1, 1), 5)]),
            {'Values': [{'timestamp': '2000-01-01T00:00:00', 'value': 5}]},
        ),
        (
            OMFData[MyClass2]([MyClass2(datetime(2000, 1, 1), 5)]),
            {'Values': [{'timestamp': '2000-01-01T00:00:00', 'value': 5}]},
        ),
    ],
)
def test_canSerializeModel(model: Serializeable, expected: dict):
    assert model.toDictionary() == expected
