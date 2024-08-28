from __future__ import annotations

import typing


if typing.TYPE_CHECKING:
    from typing import Any, Mapping, Sequence
    from .types import FilenameFormat, PartitionCollection, FilenameMetadata  # type: ignore


def create_filenames(
    variables: Mapping[str, PartitionCollection | str | Any],
    format: FilenameFormat,
) -> list[str]:
    from . import _nombre_rust

    # parse each variable as 1) partition, 2) multi values, or 3) single value
    single_values = {}
    multi_values = {}
    partition_sets: dict[str, Any] = {}
    for name, value in variables.items():
        if isinstance(value, dict):
            if 'leftovers' not in value:
                value = value.copy()
                value['leftovers'] = 'separate'
            partition_sets[name] = value
        elif isinstance(value, list):
            if name in format['partitions'].keys():
                partition_sets[name] = value
            else:
                multi_values[name] = [str(subvalue) for subvalue in value]
        elif isinstance(value, str):
            single_values[name] = value
        else:
            single_values[name] = str(value)

    # fill in missing values of format spec
    format = _fill_in_format(format)

    filenames: list[str] = _nombre_rust.create_filenames(
        format=format,
        single_values=single_values,
        multi_values=multi_values,
        partition_sets=partition_sets,
    )

    return filenames


def parse_filename(filename: str, format: FilenameFormat) -> FilenameMetadata:
    from . import _nombre_rust

    format = _fill_in_format(format)
    return _nombre_rust.parse_filename(filename, format)


def parse_filenames(
    filenames: Sequence[str], format: FilenameFormat
) -> list[FilenameMetadata]:
    from . import _nombre_rust

    format = _fill_in_format(format)
    parsed: list[FilenameMetadata] = _nombre_rust.parse_filenames(
        filenames, format
    )
    return parsed


def _fill_in_format(format: FilenameFormat) -> FilenameFormat:
    partition_formats = format.get('partitions')
    if partition_formats is None:
        format['partition_formats'] = {}
    elif set(partition_formats.keys()) != {
        'template',
        'partitions',
    }:
        new_partition_formats = {}
        for name, partition_format in partition_formats.items():
            if set(partition_format.keys()) != {
                'datatype',
                'format',
                'n_chars',
                'template_type',
                'template',
                'categories',
            }:
                partition_format = partition_format.copy()

                # detect bound_type if needed
                if (
                    'datatype' not in partition_format
                    or 'format' not in partition_format
                ):
                    # TODO: detect bound type
                    if name in partition_formats:
                        bound_type = 'integer'
                    else:
                        raise Exception(
                            'no partitions specified for ' + str(name)
                        )
                else:
                    bound_type = None

                # fill in datatype
                if 'datatype' not in partition_format:
                    if bound_type == 'timestamp':
                        partition_format['datatype'] = 'timestamp'
                    else:
                        partition_format['datatype'] = 'integer'

                # fill in format
                if 'format' not in partition_format:
                    if bound_type == 'date':
                        partition_format['format'] = 'date'
                    elif bound_type == 'timestamp':
                        partition_format['format'] = 'datetime'
                    else:
                        partition_format['format'] = 'decimal'

                # fill in template
                if 'template' not in partition_format:
                    if partition_format['datatype'] == 'category':
                        partition_format['template'] = '{name}'
                    else:
                        partition_format['template'] = '{start}_to_{end}'


            new_partition_formats[name] = partition_format

        format = {
            'template': format['template'],
            'partitions': new_partition_formats,
        }

    return format

