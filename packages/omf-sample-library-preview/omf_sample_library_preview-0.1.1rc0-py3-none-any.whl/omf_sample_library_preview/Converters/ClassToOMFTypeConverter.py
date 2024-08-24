from dataclasses import dataclass
from datetime import datetime
from types import FunctionType, NoneType, UnionType
from typing import Any, get_args, get_origin, get_type_hints

from ..Models import (OMFClassification, OMFExtrapolationMode, OMFFormatCode,
                      OMFInterpolationMode, OMFType, OMFTypeCode,
                      OMFTypeProperty, OMFTypeType)


def getOMFTypeFromPythonType(type_hint: type) -> OMFTypeProperty:
    if type_hint is NoneType:
        raise ValueError('Invalid OMF Type: NoneType is not allowed')

    if isinstance(type_hint, UnionType):
        args = get_args(type_hint)
        if len(args) > 2:
            raise ValueError(
                'Invalid OMF Type: Too many types associated with property'
            )
        if args[0] is NoneType and args[1] is NoneType:
            raise ValueError(
                'Invalid OMF Type: Both types for a Union Type cannot be None'
            )
        if args[0] is not NoneType and args[1] is not NoneType:
            raise ValueError(
                'Invalid OMF Type: At least one type for a Union Type must be None'
            )
        if args[0] is not NoneType:
            nullable_type = args[0]
        else:
            nullable_type = args[1]
        result = getOMFTypeFromPythonType(nullable_type)
        result.Type = [result.Type, OMFTypeCode.Null]
        return result
    if type_hint is int:
        return OMFTypeProperty(OMFTypeCode.Integer)
    elif type_hint is float:
        return OMFTypeProperty(OMFTypeCode.Number)
    if type_hint is datetime:
        return OMFTypeProperty(OMFTypeCode.String, OMFFormatCode.DateTime)
    if type_hint is bool:
        return OMFTypeProperty(OMFTypeCode.Boolean)
    if get_origin(type_hint) is list:
        arg = get_args(type_hint)[0]
        return OMFTypeProperty(OMFTypeCode.Array, Items=getOMFTypeFromPythonType(arg))
    if get_origin(type_hint) is dict:
        args = get_args(type_hint)
        if args[0] is not str:
            raise ValueError(
                'Invalid OMF Type: Dictionaries must have key of type string'
            )
        return OMFTypeProperty(
            OMFTypeCode.Object,
            OMFFormatCode.Dictionary,
            AdditionalProperties=getOMFTypeFromPythonType(args[1]),
        )

    return OMFTypeProperty(OMFTypeCode.String)


def getOMFTypePropertyPythonProperty(prop: property) -> OMFTypeProperty:
    type_hint = get_type_hints(prop.fget).get('return', None)
    type_property = getOMFTypeFromPythonType(type_hint)

    if hasattr(prop.fget, '__omf_type_property'):
        user_type_property = getattr(prop.fget, '__omf_type_property')

        # We don't want to use the generated type property if RefType was included
        if user_type_property.RefTypeId:
            return user_type_property

        # Replace undefined user props with generated type properties
        if not user_type_property.Format:
            user_type_property.Format = type_property.Format
        if not user_type_property.Type:
            user_type_property.Type = type_property.Type
        if not user_type_property.Items:
            user_type_property.Items = type_property.Items
        if not user_type_property.AdditionalProperties:
            user_type_property.AdditionalProperties = type_property.AdditionalProperties
        return user_type_property
    return type_property


def convert(omf_class: type) -> OMFType:
    """
    Converts a python class into an OMFType.
    Properties flagged by the @property decorator get automatically added to the OMF Type as OMF Type Properties.
    To customize the returned OMFType, use the @omf_type and @omf_type_property decorators.
    :param omf_class: The python class to be converted into an OMFType
    :returns: OMFType object
    """
    if hasattr(omf_class, '__omf_type'):
        omf_type = getattr(omf_class, '__omf_type')
    else:
        omf_type = OMFType(omf_class.__name__, OMFClassification.Dynamic)

    properties = [
        (k, getOMFTypePropertyPythonProperty(v))
        for k, v in omf_class.__dict__.items()
        if isinstance(v, property)
    ]
    omf_properties = {}
    for id, prop in properties:
        omf_properties.update({id: prop})
    omf_type.Properties = omf_properties
    return omf_type


def omf_type(
    Id=None,
    Classification: OMFClassification = OMFClassification.Dynamic,
    Type: OMFTypeType = OMFTypeType.Object,
    Version: str = None,
    Name: str = None,
    Description: str = None,
    Tags: list[str] = None,
    Metadata: dict[str, Any] = None,
    Enum: dict[str, Any] = None,
    Extrapolation: OMFExtrapolationMode = None,
):
    def wrap(cls):
        id = Id
        if not id:
            id = cls.__name__
        omf_type_attribute = OMFType(
            id,
            Classification,
            Type,
            Version,
            Name,
            Description,
            Tags,
            Metadata,
            Enum,
            Extrapolation,
        )
        setattr(cls, '__omf_type', omf_type_attribute)

        # set annotations to be used by the dataclass constructor
        properties = [
            (k, get_type_hints(v.fget).get('return', None))
            for k, v in cls.__dict__.items()
            if isinstance(v, property)
        ]
        cls.__annotations__ = dict(properties)

        return dataclass(cls)

    return wrap


def omf_type_property(
    Type: OMFTypeCode | list[OMFTypeCode] = None,
    Format: OMFFormatCode = None,
    Items: 'OMFTypeProperty' = None,
    RefTypeId: str = None,
    IsIndex: bool = None,
    IsQuality: bool = None,
    Name: str = None,
    Description: str = None,
    Uom: str = None,
    Minimum: float | int = None,
    Maximum: float | int = None,
    Interpolation: OMFInterpolationMode = None,
):
    def wrap(func):
        if isinstance(func, property):
            raise ValueError(
                "Property type is not a valid input. This decorator automatically creates a property."
            )
        if not isinstance(func, FunctionType):
            raise ValueError("Non-function type is not a valid input.")
        omf_type_property_attribute = OMFTypeProperty(
            Type,
            Format,
            Items,
            RefTypeId,
            IsIndex,
            IsQuality,
            Name,
            Description,
            Uom,
            Minimum,
            Maximum,
            Interpolation,
        )
        setattr(func, '__omf_type_property', omf_type_property_attribute)

        return property(func)

    return wrap
