import pytest
from n_cache import LruCache, NCache
from functools import partial
from pprint import pprint


def __get_side_effect__(cache, triggers, event):
    op, data = event.split(":")
    if op == "w":
        key, value = data.split("=")
        popped = cache.write(key, value)
        if popped:
            return triggers["evicted"](popped)
        else:
            return triggers["write"](event)
    elif op == "r":
        key = data
        value = cache.read(key)
        if value is None:
            return triggers["miss"](key)
        else:
            return triggers["hit"]((key, value))


@pytest.mark.parametrize(
    "size,events,expected_side_effects",
    [
        (
            2,
            ["w:fruit=apple", "w:veggie=okra", "w:organ=heart", "w:wood=sandal"],
            [
                "w:fruit=apple",
                "w:veggie=okra",
                "evicted:fruit=apple",
                "evicted:veggie=okra",
            ],
        ),
        (
            2,
            ["w:fruit=apple", "w:veggie=okra", "r:fruit", "w:wood=sandal"],
            [
                "w:fruit=apple",
                "w:veggie=okra",
                "hit:fruit=apple",
                "evicted:veggie=okra",
            ],
        ),
        (
            2,
            [
                "w:fruit=apple",
                "w:veggie=okra",
                "w:fruit=orange",
                "r:fruit",
                "w:wood=sandal",
                "r:veggie",
            ],
            [
                "w:fruit=apple",
                "w:veggie=okra",
                "w:fruit=orange",
                "hit:fruit=orange",
                "evicted:veggie=okra",
                "miss:veggie",
            ],
        ),
    ],
)
def test_single_level_cache(size, events, expected_side_effects):
    cache = LruCache(size)
    side_effects = []
    triggers = {
        "evicted": lambda popped: "{}:{}={}".format("evicted", popped[0], popped[1]),
        "write": lambda event: event,
        "hit": lambda key_val: "{}:{}={}".format("hit", key_val[0], key_val[1]),
        "miss": lambda key: "{}:{}".format("miss", key),
    }
    get_side_effect = partial(__get_side_effect__, cache, triggers)
    side_effects = list(map(get_side_effect, events))
    assert side_effects == expected_side_effects


@pytest.mark.parametrize(
    "sizes,events,expected_side_effects",
    [
        (
            [2, 3, 10],
            ["w:fruit=apple", "w:veggie=okra", "w:organ=heart", "w:wood=sandal"],
            [
                "w:fruit=apple",
                "w:veggie=okra",
                ("evicted", {0: ("fruit", "apple")}),
                ("evicted", {0: ("veggie", "okra"), 1: ("fruit", "apple")}),
            ],
        ),
        (
            [2, 3, 10],
            ["w:fruit=apple", "w:veggie=okra", "r:fruit", "w:wood=sandal"],
            [
                "w:fruit=apple",
                "w:veggie=okra",
                "hit:fruit=apple",
                ("evicted", {0: ("veggie", "okra")}),
            ],
        ),
        (
            [2, 3, 10],
            [
                "w:fruit=apple",
                "w:veggie=okra",
                "w:fruit=orange",
                "r:fruit",
                "w:wood=sandal",
                "r:veggie",
            ],
            [
                "w:fruit=apple",
                "w:veggie=okra",
                "w:fruit=orange",
                "hit:fruit=orange",
                ("evicted", {0: ("veggie", "okra")}),
                "hit:veggie=okra",
            ],
        ),
    ],
)
def test_multi_level_cache(sizes, events, expected_side_effects):
    config = [{"CAPACITY": size, "STRATEGY": "lru"} for size in sizes]
    cache = NCache(config)
    triggers = {
        "evicted": lambda popped: ("evicted", popped),
        "write": lambda event: event,
        "hit": lambda key_val: "{}:{}={}".format("hit", key_val[0], key_val[1]),
        "miss": lambda key: "{}:{}".format("miss", key),
    }
    get_side_effect = partial(__get_side_effect__, cache, triggers)
    side_effects = list(map(get_side_effect, events))
    assert side_effects == expected_side_effects
