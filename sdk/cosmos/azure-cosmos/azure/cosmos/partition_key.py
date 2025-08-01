# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Create partition keys in the Azure Cosmos DB SQL API service.
"""
from io import BytesIO
import binascii
import struct
from typing import Any, Dict, IO, List, Sequence, Type, Union, cast, overload
from typing_extensions import Literal

from ._cosmos_integers import _UInt32, _UInt64, _UInt128
from ._cosmos_murmurhash3 import murmurhash3_128 as _murmurhash3_128, murmurhash3_32 as _murmurhash3_32
from ._routing.routing_range import Range as _Range


_MaximumExclusiveEffectivePartitionKey = 0xFF
_MinimumInclusiveEffectivePartitionKey = 0x00
_MaxStringChars = 100
_MaxStringBytesToAppend = 100
_MaxPartitionKeyBinarySize = \
    (1  # type marker
     + 9  # hash value
     + 1  # type marker
     + _MaxStringBytesToAppend
     + 1  # trailing zero
     ) * 3


class _PartitionKeyComponentType:
    Undefined = 0x0
    Null = 0x1
    PFalse = 0x2
    PTrue = 0x3
    MinNumber = 0x4
    Number = 0x5
    MaxNumber = 0x6
    MinString = 0x7
    String = 0x8
    MaxString = 0x9
    Int64 = 0xA
    Int32 = 0xB
    Int16 = 0xC
    Int8 = 0xD
    Uint64 = 0xE
    Uint32 = 0xF
    Uint16 = 0x10
    Uint8 = 0x11
    Binary = 0x12
    Guid = 0x13
    Float = 0x14
    Infinity = 0xFF

class _PartitionKeyKind:
    HASH: str = "Hash"
    MULTI_HASH: str = "MultiHash"

class _PartitionKeyVersion:
    V1: int = 1
    V2: int = 2

class NonePartitionKeyValue:
    """Represents None value for partitionKey when it's missing in a container.
    """


class _Empty:
    """Represents empty value for partitionKey when it's missing in an item belonging
    to a migrated container.
    """


class _Undefined:
    """Represents undefined value for partitionKey when it's missing in an item belonging
    to a multi-partition container.
    """


class _Infinity:
    """Represents infinity value for partitionKey."""

_SingularPartitionKeyType = Union[None, bool, float, int, str, Type[NonePartitionKeyValue], _Empty, _Undefined]
_SequentialPartitionKeyType = Sequence[_SingularPartitionKeyType]
_PartitionKeyType = Union[_SingularPartitionKeyType, _SequentialPartitionKeyType]

class PartitionKey(dict):
    """Key used to partition a container into logical partitions.

    See https://learn.microsoft.com/azure/cosmos-db/partitioning-overview#choose-partitionkey
    for information on how to choose partition keys.

    This constructor supports multiple overloads:

    1. **Single Partition Key**:

       **Parameters**:
        - `path` (str): The path of the partition key.
        - `kind` (Literal["Hash"], optional): The kind of partition key. Defaults to "Hash".
        - `version` (int, optional): The version of the partition key. Defaults to 2.

       **Example**:
         >>> pk = PartitionKey(path="/id")

    2. **Hierarchical Partition Key**:

       **Parameters**:
        - `path` (List[str]): A list of paths representing the partition key, supports up to three hierarchical levels.
        - `kind` (Literal["MultiHash"], optional): The kind of partition key. Defaults to "MultiHash".
        - `version` (int, optional): The version of the partition key. Defaults to 2.

       **Example**:
         >>> pk = PartitionKey(path=["/id", "/category"], kind="MultiHash")

    :ivar str path: The path(s) of the partition key.
    :ivar str kind: The kind of partition key ("Hash" or "MultiHash") (default: "Hash").
    :ivar int version: The version of the partition key (default: 2).
    """

    @overload
    def __init__(self, path: List[str], *, kind: Literal["MultiHash"] = "MultiHash",
                 version: int = _PartitionKeyVersion.V2
    ) -> None:
        ...

    @overload
    def __init__(self, path: str, *, kind: Literal["Hash"] = "Hash",
                 version:int = _PartitionKeyVersion.V2
    ) -> None:
        ...

    def __init__(self, *args, **kwargs):
        path = args[0] if args else kwargs['path']
        kind = args[1] if len(args) > 1 else kwargs.get('kind', _PartitionKeyKind.HASH if isinstance(path, str)
        else _PartitionKeyKind.MULTI_HASH)
        version = args[2] if len(args) > 2 else kwargs.get('version', _PartitionKeyVersion.V2)
        super().__init__(paths=[path] if isinstance(path, str) else path, kind=kind, version=version)

    def __repr__(self) -> str:
        return "<PartitionKey [{}]>".format(self.path)[:1024]

    @property
    def kind(self) -> Literal["MultiHash", "Hash"]:
        return self["kind"]

    @kind.setter
    def kind(self, value: Literal["MultiHash", "Hash"]) -> None:
        self["kind"] = value

    @property
    def path(self) -> str:
        if self.kind == _PartitionKeyKind.MULTI_HASH:
            return ''.join(self["paths"])
        return self["paths"][0]

    @path.setter
    def path(self, value: Union[str, List[str]]) -> None:
        if isinstance(value, str):
            self["paths"] = [value]
        else:
            self["paths"] = value

    @property
    def version(self) -> int:
        return self["version"]

    @version.setter
    def version(self, value: int) -> None:
        self["version"] = value

    def _get_epk_range_for_prefix_partition_key(
        self,
        pk_value: _SequentialPartitionKeyType
    ) -> _Range:
        if self.kind != _PartitionKeyKind.MULTI_HASH:
            raise ValueError(
                "Effective Partition Key Range for Prefix Partition Keys is only supported for Hierarchical Partition Keys.")  # pylint: disable=line-too-long
        len_pk_value = len(pk_value)
        len_paths = len(self["paths"])
        if len_pk_value >= len_paths:
            raise ValueError(
                f"{len_pk_value} partition key components provided. Expected less than {len_paths} " +
                "components (number of container partition key definition components)."
            )
        # Prefix Partitions always have exclusive max
        min_epk = self._get_effective_partition_key_string(pk_value)
        if min_epk == _MinimumInclusiveEffectivePartitionKey:
            min_epk = ""
            return _Range(min_epk, min_epk, True, False)

        if min_epk == _MaximumExclusiveEffectivePartitionKey:
            return _Range("FF", "FF", True, False)

        max_epk = str(min_epk) + "FF"
        return _Range(min_epk, max_epk, True, False)

    def _get_epk_range_for_partition_key(
            self,
            pk_value: _PartitionKeyType
    ) -> _Range:
        if self._is_prefix_partition_key(pk_value):
            return self._get_epk_range_for_prefix_partition_key(
                cast(_SequentialPartitionKeyType, pk_value))

        # else return point range
        if isinstance(pk_value, (list, tuple)) or (isinstance(pk_value, Sequence) and not isinstance(pk_value, str)):
            effective_partition_key_string = self._get_effective_partition_key_string(pk_value)
        else:
            effective_partition_key_string =\
                self._get_effective_partition_key_string([pk_value])
        return _Range(effective_partition_key_string, effective_partition_key_string, True, True)

    @staticmethod
    def _truncate_for_v1_hashing(
            value: _SingularPartitionKeyType
    ) -> _SingularPartitionKeyType:
        if isinstance(value, str):
            return value[:100]
        return value

    @staticmethod
    def _get_effective_partition_key_for_hash_partitioning(
            pk_value: Union[str, _SequentialPartitionKeyType]
    ) -> str:
        truncated_components = []
        # In Python, Strings are sequences, so we make sure we instead hash the entire string instead of each character
        if isinstance(pk_value, str):
            truncated_components.append(PartitionKey._truncate_for_v1_hashing(pk_value))
        else:
            truncated_components = [PartitionKey._truncate_for_v1_hashing(v) for v in pk_value]
        with BytesIO() as ms:
            for component in truncated_components:
                if isinstance(component, int) and not isinstance(component, bool):
                    component = float(int(_UInt32(component)))
                PartitionKey._write_for_hashing(component, ms)

            ms_bytes: bytes = ms.getvalue()
            # We use Our own MurmurHash3 implementation to match the behavior of other SDKs
            # We put into a Cosmos Integer of Unsigned 32-bit Integer, to match the behavior of other SDKs
            hash_as_int: _UInt32 = _murmurhash3_32(bytearray(ms_bytes), 0)
            hash_value = float(int(hash_as_int))

        partition_key_components = [hash_value] + truncated_components
        return _to_hex_encoded_binary_string_v1(partition_key_components)

    @staticmethod
    def _get_hashed_partition_key_string(
            pk_value: _SequentialPartitionKeyType,
            kind: str,
            version: int = _PartitionKeyVersion.V2,
    ) -> Union[int, str]:
        if not pk_value:
            return _MinimumInclusiveEffectivePartitionKey

        if kind == _PartitionKeyKind.HASH:
            if version == _PartitionKeyVersion.V1:
                return PartitionKey._get_effective_partition_key_for_hash_partitioning(pk_value)
            if version == _PartitionKeyVersion.V2:
                return PartitionKey._get_effective_partition_key_for_hash_partitioning_v2(pk_value)
        elif kind == _PartitionKeyKind.MULTI_HASH:
            return PartitionKey._get_effective_partition_key_for_multi_hash_partitioning_v2(pk_value)
        return _to_hex_encoded_binary_string(pk_value)

    def _get_effective_partition_key_string(
        self,
        pk_value: _SequentialPartitionKeyType
    ) -> Union[int, str]:
        if isinstance(self, _Infinity):
            return _MaximumExclusiveEffectivePartitionKey

        return PartitionKey._get_hashed_partition_key_string(pk_value=pk_value, kind=self.kind, version=self.version)

    @staticmethod
    def _write_for_hashing(
            value: _SingularPartitionKeyType,
            writer: IO[bytes]
    ) -> None:
        PartitionKey._write_for_hashing_core(value, bytes([0]), writer)

    @staticmethod
    def _write_for_hashing_v2(
        value: _SingularPartitionKeyType,
        writer: IO[bytes]
    ) -> None:
        PartitionKey._write_for_hashing_core(value, bytes([0xFF]), writer)

    @staticmethod
    def _write_for_hashing_core(
        value: _SingularPartitionKeyType,
        string_suffix: bytes,
        writer: IO[bytes]
    ) -> None:
        if value is True:
            writer.write(bytes([_PartitionKeyComponentType.PTrue]))
        elif value is False:
            writer.write(bytes([_PartitionKeyComponentType.PFalse]))
        elif value is None or value == {} or value == NonePartitionKeyValue:
            writer.write(bytes([_PartitionKeyComponentType.Null]))
        elif isinstance(value, int):
            writer.write(bytes([_PartitionKeyComponentType.Number]))
            # Cast to Float to ensure correct packing
            writer.write(struct.pack('<d', float(value)))
        elif isinstance(value, float):
            writer.write(bytes([_PartitionKeyComponentType.Number]))
            writer.write(struct.pack('<d', value))
        elif isinstance(value, str):
            writer.write(bytes([_PartitionKeyComponentType.String]))
            writer.write(value.encode('utf-8'))
            writer.write(string_suffix)
        elif isinstance(value, _Undefined):
            writer.write(bytes([_PartitionKeyComponentType.Undefined]))

    @staticmethod
    def _get_effective_partition_key_for_hash_partitioning_v2(
        pk_value: _SequentialPartitionKeyType
    ) -> str:
        with BytesIO() as ms:
            for component in pk_value:
                PartitionKey._write_for_hashing_v2(component, ms)

            ms_bytes = ms.getvalue()
            hash128 = _murmurhash3_128(bytearray(ms_bytes), _UInt128(0, 0))
            hash_bytes = _UInt128.to_byte_array(hash128)
            hash_bytes.reverse()

            # Reset 2 most significant bits, as max exclusive value is 'FF'.
            # Plus one more just in case.
            hash_bytes[0] &= 0x3F

        return ''.join('{:02X}'.format(x) for x in hash_bytes)

    @staticmethod
    def _get_effective_partition_key_for_multi_hash_partitioning_v2(
        pk_value: _SequentialPartitionKeyType
    ) -> str:
        sb = []
        for value in pk_value:
            ms = BytesIO()
            binary_writer = ms  # In Python, you can write bytes directly to a BytesIO object

            # Assuming paths[i] is the correct object to call write_for_hashing_v2 on
            PartitionKey._write_for_hashing_v2(value, binary_writer)

            ms_bytes = ms.getvalue()
            hash128 = _murmurhash3_128(bytearray(ms_bytes), _UInt128(0, 0))
            hash_v_bytes = hash128.to_byte_array()
            hash_v = list(reversed(hash_v_bytes))

            # Reset 2 most significant bits, as max exclusive value is 'FF'.
            # Plus one more just in case.
            hash_v[0] &= 0x3F
            sb.append(_to_hex(bytearray(hash_v), 0, len(hash_v)))

        return ''.join(sb).upper()

    def _is_prefix_partition_key(
            self,
            partition_key: _PartitionKeyType) -> bool:  # pylint: disable=line-too-long
        if self.kind != _PartitionKeyKind.MULTI_HASH:
            return False
        ret = ((isinstance(partition_key, Sequence) and
                not isinstance(partition_key, str)) and len(self['paths']) != len(partition_key))
        return ret


def _return_undefined_or_empty_partition_key(is_system_key: bool) -> Union[_Empty, _Undefined]:
    if is_system_key:
        return _Empty()
    return _Undefined()


def _to_hex(bytes_object: bytearray, start: int, length: int) -> str:
    return binascii.hexlify(bytes_object[start:start + length]).decode()


def _to_hex_encoded_binary_string(components: Sequence[object]) -> str:
    buffer_bytes = bytearray(_MaxPartitionKeyBinarySize)
    ms = BytesIO(buffer_bytes)

    for component in components:
        if isinstance(component, (bool, int, float, str, _Infinity, _Undefined)):
            component = cast(_SingularPartitionKeyType, component)
            _write_for_binary_encoding(component, ms)
        else:
            raise TypeError(f"Unexpected type for PK component: {type(component)}")

    return _to_hex(buffer_bytes[:ms.tell()], 0, ms.tell())

def _to_hex_encoded_binary_string_v1(components: Sequence[object]) -> str:
    ms = BytesIO()
    for component in components:
        if isinstance(component, (bool, int, float, str, _Infinity, _Undefined)):
            component = cast(_SingularPartitionKeyType, component)
            _write_for_binary_encoding_v1(component, ms)
        else:
            raise TypeError(f"Unexpected type for PK component: {type(component)}")

    return _to_hex(bytearray(ms.getvalue()), 0, ms.tell())

def _write_for_binary_encoding_v1(
    value: _SingularPartitionKeyType,
    binary_writer: IO[bytes]
) -> None:
    if isinstance(value, bool):
        binary_writer.write(bytes([(_PartitionKeyComponentType.PTrue if value else _PartitionKeyComponentType.PFalse)]))

    elif isinstance(value, _Infinity):
        binary_writer.write(bytes([_PartitionKeyComponentType.Infinity]))

    elif isinstance(value, (int, float)):  # Assuming number value is int or float
        binary_writer.write(bytes([_PartitionKeyComponentType.Number]))
        # For V1 Hashing we need to encode the value as a UInt64 From a Float regardless if it was an int or float
        if isinstance(value, float):
            payload = _UInt64(_UInt64.encode_double_as_uint64(value))
        else:
            payload = _UInt64(_UInt64.encode_double_as_uint64(float(value)))

        # Encode first chunk with 8-bits of payload
        binary_writer.write(bytes([int((payload >> (64 - 8)))]))
        payload <<= 8

        # Encode remaining chunks with 7 bits of payload followed by single "1" bit each.
        byte_to_write = 0
        first_iteration = True
        while payload != 0:
            if not first_iteration:
                binary_writer.write(bytes([byte_to_write]))
            else:
                first_iteration = False

            byte_to_write = int((payload >> (64 - 8)) | int(0x01))
            payload <<= 7

        # Except for last chunk that ends with "0" bit.
        binary_writer.write(bytes([(byte_to_write & 0xFE)]))

    elif isinstance(value, str):
        binary_writer.write(bytes([_PartitionKeyComponentType.String]))
        utf8_value = value.encode('utf-8')
        short_string = len(utf8_value) <= _MaxStringBytesToAppend

        for index in range(short_string and len(utf8_value) or _MaxStringBytesToAppend + 1):
            char_byte = utf8_value[index]
            char_byte += 1
            binary_writer.write(bytes([char_byte]))

        if short_string:
            binary_writer.write(bytes([0x00]))

    elif isinstance(value, _Undefined):
        binary_writer.write(bytes([_PartitionKeyComponentType.Undefined]))

def _write_for_binary_encoding(
    value: _SingularPartitionKeyType,
    binary_writer: IO[bytes]
) -> None:
    if isinstance(value, bool):
        binary_writer.write(bytes([(_PartitionKeyComponentType.PTrue if value else _PartitionKeyComponentType.PFalse)]))

    elif isinstance(value, _Infinity):
        binary_writer.write(bytes([_PartitionKeyComponentType.Infinity]))

    elif isinstance(value, (int, float)):  # Assuming number value is int or float
        binary_writer.write(bytes([_PartitionKeyComponentType.Number]))
        payload = _UInt64.encode_double_as_uint64(value)  # Function to be defined elsewhere

        # Encode first chunk with 8-bits of payload
        binary_writer.write(bytes([(payload >> (64 - 8))]))
        payload <<= 8

        # Encode remaining chunks with 7 bits of payload followed by single "1" bit each.
        byte_to_write = 0
        first_iteration = True
        while payload != 0:
            if not first_iteration:
                binary_writer.write(bytes([byte_to_write]))
            else:
                first_iteration = False

            byte_to_write = (payload >> (64 - 8)) | 0x01
            payload <<= 7

        # Except for last chunk that ends with "0" bit.
        binary_writer.write(bytes([(byte_to_write & 0xFE)]))

    elif isinstance(value, str):
        binary_writer.write(bytes([_PartitionKeyComponentType.String]))
        utf8_value = value.encode('utf-8')
        short_string = len(utf8_value) <= _MaxStringBytesToAppend

        for index in range(short_string and len(utf8_value) or _MaxStringBytesToAppend + 1):
            char_byte = utf8_value[index]
            if char_byte < 0xFF:
                char_byte += 1
            binary_writer.write(bytes([char_byte]))

        if short_string:
            binary_writer.write(bytes([0x00]))

    elif isinstance(value, _Undefined):
        binary_writer.write(bytes([_PartitionKeyComponentType.Undefined]))

def _get_partition_key_from_partition_key_definition(
    partition_key_definition: Union[Dict[str, Any], "PartitionKey"]
) -> "PartitionKey":
    """Internal method to create a PartitionKey instance from a dictionary or PartitionKey object.

    :param partition_key_definition: A dictionary or PartitionKey object containing the partition key definition.
    :type partition_key_definition: Union[Dict[str, Any], PartitionKey]
    :return: A PartitionKey instance created from the provided definition.
    :rtype: PartitionKey
    """
    path = partition_key_definition.get("paths", "")
    kind = partition_key_definition.get("kind", "Hash")
    version: int = partition_key_definition.get("version", 1)  # Default to version 1 if not provided
    return PartitionKey(path=path, kind=kind, version=version)

def _build_partition_key_from_properties(container_properties: Dict[str, Any]) -> PartitionKey:
    partition_key_definition = container_properties["partitionKey"]
    return _get_partition_key_from_partition_key_definition(partition_key_definition)
