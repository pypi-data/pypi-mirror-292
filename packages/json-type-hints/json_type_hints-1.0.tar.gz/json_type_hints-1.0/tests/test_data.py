from dataclasses import dataclass


@dataclass
class MyClass1:
    prop1: int
    prop2: tuple[str, bytes]


@dataclass
class MyClass2:
    prop1: list[MyClass1]
    prop2: str


CLS_NAME_1 = "MyClass1"
CLS_NAME_2 = "MyClass2"
TYPE_DICT_CLS1 = {CLS_NAME_1: MyClass1}
TYPE_DICT_CLS2 = {CLS_NAME_2: MyClass2}
TYPE_DICT_FULL = {CLS_NAME_1: MyClass1, CLS_NAME_2: MyClass2}
CLASS_1_OBJ_1 = MyClass1(prop1=1, prop2=("bytes1", b"\x01"))
CLASS_1_OBJ_2 = MyClass1(prop1=2, prop2=("bytes2", b"\x01\x00"))
CLASS_2_OBJ_1 = MyClass2(prop1=[CLASS_1_OBJ_1, CLASS_1_OBJ_2], prop2="cls2")
INPUT_DICT = {"key1": 1, "key2": CLASS_2_OBJ_1}
DUMPS_STR = (
    '{"key1":1,"key2":{"__type__":"MyClass2","__data__":{"prop1":[{"__type__":"MyClass1",'
    '"__data__":{"prop1":1,"prop2":{"__type__":"tuple","__data__":["bytes1",'
    '{"__type__":"bytes","__data__":"AQ=="}]}}},{"__type__":"MyClass1",'
    '"__data__":{"prop1":2,"prop2":{"__type__":"tuple","__data__":["bytes2",'
    '{"__type__":"bytes","__data__":"AQA="}]}}}],"prop2":"cls2"}}}'
)
LOADS_DEFAULT_ONLY = {
    "key1": 1,
    "key2": {
        "__type__": CLS_NAME_2,
        "__data__": {
            "prop1": [
                {"__type__": CLS_NAME_1, "__data__": {"prop1": 1, "prop2": ("bytes1", b"\x01")}},
                {
                    "__type__": CLS_NAME_1,
                    "__data__": {"prop1": 2, "prop2": ("bytes2", b"\x01\x00")},
                },
            ],
            "prop2": "cls2",
        },
    },
}
LOADS_CLS_1_ONLY = {
    "key1": 1,
    "key2": {
        "__type__": CLS_NAME_2,
        "__data__": {
            "prop1": [CLASS_1_OBJ_1, CLASS_1_OBJ_2],
            "prop2": "cls2",
        },
    },
}
