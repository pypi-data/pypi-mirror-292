from functools import singledispatch

from tdm.abstract.datamodel import AbstractValue
from tdm.datamodel.values import DateTimeValue, DoubleValue, GeoPointValue, IntValue, StringValue, TimestampValue


@singledispatch
def get_filters(value: AbstractValue, **kwargs) -> dict:
    raise NotImplementedError


@get_filters.register
def _string_filter(value: StringValue, exact: bool = False) -> dict:
    return {"stringFilter": {"str": value.value.replace('"', '?'), "exact": exact}}  # see TKL-987


def _int_timestamp_filter(value: IntValue | TimestampValue, **kwargs) -> dict:
    return {"intFilter": {"start": value.value, "end": value.value}}


@get_filters.register
def _int_filter(value: IntValue, **kwargs) -> dict:
    return _int_timestamp_filter(value)


@get_filters.register
def _timestamp_filter(value: TimestampValue, **kwargs) -> dict:
    return _int_timestamp_filter(value)


@get_filters.register
def _double_filter(value: DoubleValue, **kwargs) -> dict:
    return {"doubleFilter": {"start": value.value, "end": value.value}}


@get_filters.register
def _date_time_filter(value: DateTimeValue, **kwargs) -> dict:
    date_filter = {"date": value.date.__dict__}
    if value.time:
        date_filter["time"] = value.time.__dict__

    return {"dateTimeFilter": {"start": date_filter, "end": date_filter}}


@get_filters.register
def _geo_filter(value: GeoPointValue, **kwargs) -> dict:
    geo_filter = {"radius": 0.0001}
    if value.point:
        geo_filter["point"] = value.point.__dict__
    if value.name:
        geo_filter["name"] = value.name

    return {"geoFilter": geo_filter}
