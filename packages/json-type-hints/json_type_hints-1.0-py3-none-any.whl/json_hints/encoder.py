import base64
import json


class ExtendedJSONEncoder(json.JSONEncoder):
    """
    A subclass of ``JSONEncoder`` intended to only be used in ``dumps``. Overrides the ``encode``
    method to change the handling of ``tuple`` and ``bytes``.
    """

    def __init__(
        self,
        *,
        skipkeys=False,
        ensure_ascii=True,
        check_circular=True,
        allow_nan=True,
        sort_keys=False,
        indent=None,
        separators=None,
        default=None,
        encode_types=None,
    ):
        super().__init__(
            skipkeys=skipkeys,
            ensure_ascii=ensure_ascii,
            check_circular=check_circular,
            allow_nan=allow_nan,
            sort_keys=sort_keys,
            indent=indent,
            separators=separators,
            default=default,
        )
        self.encode_types = encode_types

    def encode(self, o):
        def add_type_hints(item):
            if isinstance(item, tuple):
                return {"__type__": "tuple", "__data__": [add_type_hints(e) for e in item]}
            if isinstance(item, list):
                return [add_type_hints(e) for e in item]
            if isinstance(item, dict):
                return {key: add_type_hints(value) for key, value in item.items()}
            if isinstance(item, bytes):
                return {"__type__": "bytes", "__data__": base64.b64encode(item).decode()}
            if self.encode_types:
                backup = item
                item = self.encode_types(item)
                if item != backup:
                    if not (isinstance(item, dict) and "__type__" in item and "__data__" in item):
                        raise TypeError(
                            "encode_types must return a dict with '__type__' and '__data__' keys"
                        )
                    item["__data__"] = add_type_hints(item["__data__"])
            return item

        return super().encode(add_type_hints(o))
