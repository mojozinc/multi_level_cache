import pytest
from n_cache import LruCache, NCache


@pytest.mark.parametrize(
    "size,events,expected_side_effects",
    [
        (
            2,
            ["w:fruit=apple", "w:veggie=okra", "w:organ=heart", "w:wood=sandal"],
            ["w:fruit=apple", "w:veggie=okra", "evicted:fruit=apple", "evicted:veggie=okra"],
        ),
        (
            2,
            ["w:fruit=apple", "w:veggie=okra", "r:fruit", "w:wood=sandal"],
            ["w:fruit=apple", "w:veggie=okra", "hit:fruit=apple", "evicted:veggie=okra"]
        ),
        (
            2,
            ["w:fruit=apple", "w:veggie=okra", "w:fruit=orange", "r:fruit", "w:wood=sandal", "r:veggie"],
            ["w:fruit=apple", "w:veggie=okra", "w:fruit=orange", "hit:fruit=orange", "evicted:veggie=okra", "miss:veggie"]
        ),
    ],
)
def test_single_level_cache(size, events, expected_side_effects):
    cache = LruCache(size)
    side_effects = []
    for event in events:
        op, data = event.split(":")
        if op == "w":
            key, value = data.split("=")
            popped = cache.write(key, value)
            if popped:
                side_effects.append("{}:{}={}".format("evicted", popped[0], popped[1]))
            else:
                side_effects.append(event)
        elif op == "r":
            key = data
            value = cache.read(key)
            if value is None:
                side_effects.append("{}:{}".format("miss", key))
            else:
                side_effects.append("{}:{}={}".format("hit", key, value))
    assert side_effects == expected_side_effects
