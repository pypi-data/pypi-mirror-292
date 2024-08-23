import podite
from podite import BYTES_CATALOG, JSON_CATALOG, pod
from podite._utils import get_concrete_type, get_calling_module, _GetitemToCall


def _open_orders_array(name, type_):
    module = get_calling_module()

    max_length = 1024

    @pod(dataclass_fn=None)
    class _ArrayPod:
        length_relative_offset = -6148

        @classmethod
        def _is_static(cls) -> bool:
            return BYTES_CATALOG.is_static(get_concrete_type(module, type_))

        @classmethod
        def _calc_size(cls, obj, **kwargs):
            ty = get_concrete_type(module, type_)
            body_size = sum(
                (BYTES_CATALOG.calc_size(ty, elem, **kwargs) for elem in obj)
            )
            return body_size

        @classmethod
        def _calc_max_size(cls):
            return (
                BYTES_CATALOG.calc_max_size(get_concrete_type(module, type_)) * max_length
            )

        @classmethod
        def _from_bytes_partial(cls, buffer, **kwargs):
            pos = buffer.tell()
            buffer.seek(length_relative_offset - max_length, 1)
            max_open_orders = BYTES_CATALOG.unpack_partial(podite.U16, buffer)
            buffer.seek(pos)

            result = []
            for _ in range(max_open_orders):
                value = BYTES_CATALOG.unpack_partial(
                    get_concrete_type(module, type_), buffer, **kwargs
                )
                result.append(value)

            return result

        @classmethod
        def _to_bytes_partial(cls, buffer, obj, **kwargs):
            if len(obj) > max_length:
                raise RuntimeError("actual_length > max_length")
            for elem in obj:
                BYTES_CATALOG.pack_partial(
                    get_concrete_type(module, type_), buffer, elem
                )

        @classmethod
        def _to_dict(cls, obj):
            return [JSON_CATALOG.pack(get_concrete_type(module, type_), e) for e in obj]

        @classmethod
        def _from_dict(cls, raw):
            return [
                JSON_CATALOG.unpack(get_concrete_type(module, type_), e) for e in raw
            ]

    _ArrayPod.__name__ = f"{name}[{type_}, {_ArrayPod.length_relative_offset}]"
    _ArrayPod.__qualname__ = _ArrayPod.__name__

    return _ArrayPod


OpenOrdersArray = _GetitemToCall("FixedLenArray", _open_orders_array)
