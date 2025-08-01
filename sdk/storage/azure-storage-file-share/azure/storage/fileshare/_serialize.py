# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, Dict, Optional, Tuple, Union, TYPE_CHECKING

from azure.core import MatchConditions

from ._parser import _datetime_to_str, _get_file_permission
from ._generated.models import (
    SourceModifiedAccessConditions,
    LeaseAccessConditions,
    SourceLeaseAccessConditions,
    DestinationLeaseAccessConditions,
    CopyFileSmbInfo
)

if TYPE_CHECKING:
    from ._lease import ShareLeaseClient
    from .aio._lease_async import ShareLeaseClient as ShareLeaseClientAsync


_SUPPORTED_API_VERSIONS = [
    '2019-02-02',
    '2019-07-07',
    '2019-10-10',
    '2019-12-12',
    '2020-02-10',
    '2020-04-08',
    '2020-06-12',
    '2020-08-04',
    '2020-10-02',
    '2020-12-06',
    '2021-02-12',
    '2021-04-10',
    '2021-06-08',
    '2021-08-06',
    '2021-12-02',
    '2022-11-02',
    '2023-01-03',
    '2023-05-03',
    '2023-08-03',
    '2023-11-03',
    '2024-05-04',
    '2024-08-04',
    '2024-11-04',
    '2025-01-05',
    '2025-05-05',
    '2025-07-05',
    '2025-11-05',
]


def _get_match_headers(
    kwargs: Dict[str, Any],
    match_param: str,
    etag_param: str
) -> Tuple[Optional[str], Optional[str]]:
    if_match = None
    if_none_match = None
    match_condition = kwargs.pop(match_param, None)
    if match_condition == MatchConditions.IfNotModified:
        if_match = kwargs.pop(etag_param, None)
        if not if_match:
            raise ValueError(f"'{match_param}' specified without '{etag_param}'.")
    elif match_condition == MatchConditions.IfPresent:
        if_match = '*'
    elif match_condition == MatchConditions.IfModified:
        if_none_match = kwargs.pop(etag_param, None)
        if not if_none_match:
            raise ValueError(f"'{match_param}' specified without '{etag_param}'.")
    elif match_condition == MatchConditions.IfMissing:
        if_none_match = '*'
    elif match_condition is None:
        if etag_param in kwargs:
            raise ValueError(f"'{etag_param}' specified without '{match_param}'.")
    else:
        raise TypeError(f"Invalid match condition: {match_condition}")
    return if_match, if_none_match


def get_source_conditions(kwargs: Dict[str, Any]) -> SourceModifiedAccessConditions:
    if_match, if_none_match = _get_match_headers(kwargs, 'source_match_condition', 'source_etag')
    return SourceModifiedAccessConditions(
        source_if_modified_since=kwargs.pop('source_if_modified_since', None),
        source_if_unmodified_since=kwargs.pop('source_if_unmodified_since', None),
        source_if_match=if_match or kwargs.pop('source_if_match', None),
        source_if_none_match=if_none_match or kwargs.pop('source_if_none_match', None)
    )


def get_access_conditions(
    lease: Optional[Union["ShareLeaseClient", "ShareLeaseClientAsync", str]]
) -> Optional[LeaseAccessConditions]:
    if lease is None:
        return None
    if hasattr(lease, "id"):
        lease_id = lease.id
    else:
        lease_id = lease
    return LeaseAccessConditions(lease_id=lease_id)


def get_source_access_conditions(
    lease: Optional[Union["ShareLeaseClient", "ShareLeaseClientAsync", str]]
) -> Optional[SourceLeaseAccessConditions]:
    if lease is None:
        return None
    if hasattr(lease, "id"):
        lease_id = lease.id
    else:
        lease_id = lease
    return SourceLeaseAccessConditions(source_lease_id=lease_id)


def get_dest_access_conditions(
    lease: Optional[Union["ShareLeaseClient", "ShareLeaseClientAsync", str]]
) -> Optional[DestinationLeaseAccessConditions]:
    if lease is None:
        return None
    if hasattr(lease, "id"):
        lease_id = lease.id
    else:
        lease_id = lease
    return DestinationLeaseAccessConditions(destination_lease_id=lease_id)


def get_smb_properties(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    ignore_read_only = kwargs.pop('ignore_read_only', None)
    set_archive_attribute = kwargs.pop('set_archive_attribute', None)
    file_permission = kwargs.pop('file_permission', None)
    file_permission_key = kwargs.pop('permission_key', None)
    file_attributes = kwargs.pop('file_attributes', None)
    file_creation_time = kwargs.pop('file_creation_time', None)
    file_last_write_time = kwargs.pop('file_last_write_time', None)
    file_change_time = kwargs.pop('file_change_time', None)

    file_permission_copy_mode = None
    file_permission = _get_file_permission(file_permission, file_permission_key, None)

    if file_permission:
        if file_permission.lower() == "source":
            file_permission = None
            file_permission_copy_mode = "source"
        else:
            file_permission_copy_mode = "override"
    elif file_permission_key:
        if file_permission_key.lower() == "source":
            file_permission_key = None
            file_permission_copy_mode = "source"
        else:
            file_permission_copy_mode = "override"
    return {
        'file_permission': file_permission,
        'file_permission_key': file_permission_key,
        'copy_file_smb_info': CopyFileSmbInfo(
            file_permission_copy_mode=file_permission_copy_mode,
            ignore_read_only=ignore_read_only,
            file_attributes=file_attributes,
            file_creation_time=_datetime_to_str(file_creation_time),
            file_last_write_time=_datetime_to_str(file_last_write_time),
            file_change_time=_datetime_to_str(file_change_time),
            set_archive_attribute=set_archive_attribute
        )

    }


def get_rename_smb_properties(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    file_permission = kwargs.pop('file_permission', None)
    file_permission_key = kwargs.pop('permission_key', None)
    file_attributes = kwargs.pop('file_attributes', None)
    file_creation_time = kwargs.pop('file_creation_time', None)
    file_last_write_time = kwargs.pop('file_last_write_time', None)
    file_change_time = kwargs.pop('file_change_time', None)

    file_permission = _get_file_permission(file_permission, file_permission_key, None)

    return {
        'file_permission': file_permission,
        'file_permission_key': file_permission_key,
        'copy_file_smb_info': CopyFileSmbInfo(
            file_attributes=file_attributes,
            file_creation_time=_datetime_to_str(file_creation_time),
            file_last_write_time=_datetime_to_str(file_last_write_time),
            file_change_time=_datetime_to_str(file_change_time)
        )}


def get_api_version(kwargs: Dict[str, Any]) -> str:
    api_version = kwargs.get('api_version', None)
    if api_version and api_version not in _SUPPORTED_API_VERSIONS:
        versions = '\n'.join(_SUPPORTED_API_VERSIONS)
        raise ValueError(f"Unsupported API version '{api_version}'. Please select from:\n{versions}")
    return api_version or _SUPPORTED_API_VERSIONS[-1]
