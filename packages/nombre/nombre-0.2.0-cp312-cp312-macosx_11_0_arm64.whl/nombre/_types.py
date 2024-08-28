from __future__ import annotations

from typing import Any, Literal, Mapping, TypedDict, Union
import tooltime


class FilenameFormat(TypedDict):
    template: str
    partitions: Mapping[str, PartitionFormat]


class FilenameMetadata(TypedDict):
    variables: Mapping[str, str]
    partitions: Mapping[str, tuple[Any, Any]]


class PartitionFormat(TypedDict):
    datatype: Literal[
        'integer',
        'timestamp',
        'category',
    ]
    format: Literal[
        'decimal',
        'hex',
        'timestamp',
        'time',
        'date',
        'month',
        'year',
        'name',
    ]
    n_chars: int | None
    template: str


class PartitionRangeSet(TypedDict):
    start: int | tooltime.Timestamp
    end: int | tooltime.Timestamp
    sizes: list[int] | list[tooltime.Timelength] | None
    count: int | None
    leftovers: Literal[
        'separate',  # put leftover values into their own partition
        'omit',  # omit leftovers from partitions
        'prepend',  # put leftovers into first partition
        'append',  # include leftover values in last partition
        'distribute',  # distribute leftovers over the first n partitions
        'error',  # raise errors if there are any leftovers
    ]

PartitionRangeList = list[tuple[Any, Any]]

PartitionCategoryList = list[str]

PartitionCollection = Union[PartitionRangeList, PartitionRangeList, PartitionCategoryList]

