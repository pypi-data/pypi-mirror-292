# json-type-hints
**json-type-hints** is a simple extension of the standard json library intended to help facilitate transferring python objects as json encoded strings. Data types that don't have corresponding json types are preserved by encoding them as dictionaries with `__type__` and `__data__` fields. It encodes and decodes `bytes` and `tuple` by default (replacing the default json library encoding of `tuple` as `list`) and allows adding additional types.

provides `dumps` and `loads` methods