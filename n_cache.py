"""Multi level cache"""
import warnings
from collections import OrderedDict
from pprint import pprint
from time import sleep

import yaml

from custom_exceptions import StrategyNotSupported

MAX_LEVELS = 4
READ_TIME_PER_LEVEL = [0.1, 0.2, 0.3, 0.4]
WRITE_TIME_PER_LEVEL = [0.1, 0.2, 0.3, 0.4]


class LruCache:
    """least recently used, cache"""
    def __init__(self, capacity=0):
        self.capacity = capacity
        self.cache = OrderedDict()

    def read(self, key):
        """read value of key, return none if cache miss"""
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)  # make key hot
        return self.cache[key]

    def write(self, key, value):
        """store value for key,
        just increases priority, if key already present
        optionally might return the evicted item if capacity is exceeded
        """
        self.cache[key] = value
        popped = None
        if len(self.cache) > self.capacity:
            popped = self.cache.popitem(last=False)
        return popped


class NCache:
    """Multi level cache"""
    strategy_to_class = dict(lru=LruCache)

    def __init__(self, config):
        self.cache_config_list = config
        if len(self.cache_config_list) > MAX_LEVELS:
            warnings.warn(
                "Max cache levels exceeded\nwill only initiate {} levels".format(
                    MAX_LEVELS
                )
            )
        self.cache_stack = []
        for cache_config in self.cache_config_list[:MAX_LEVELS]:
            strategy = cache_config["STRATEGY"]
            capacity = cache_config["CAPACITY"]
            if strategy not in self.strategy_to_class:
                raise StrategyNotSupported()
            cache_class = self.strategy_to_class[strategy]
            self.cache_stack.append(cache_class(capacity=capacity))
        self.levels = len(self.cache_stack)

    def _read_level_(self, level, key):
        value = self.cache_stack[level].read(key)
        sleep(READ_TIME_PER_LEVEL[level])
        return value

    def _write_level_(self, level, key, value):
        popped = self.cache_stack[level].write(key, value)
        sleep(WRITE_TIME_PER_LEVEL[level])
        return popped

    def read(self, key, debug=False):
        """Tries to read key from all levels,
        if found, updates all the lower cold caches
        """
        for level in range(self.levels):
            value = self._read_level_(level, key)
            if value is not None:
                # cache hit
                # update all cold cache levels
                for cold_level in range(level):
                    self._write_level_(cold_level, key, value)
                return value
        # cache miss
        return None

    def write(self, key, value):
        """writes a key value pair to all cache levels
        returns a dict of popped items, if any None if no items were popped
        """
        popped = {}
        for level in range(self.levels):
            _popped_ = self._write_level_(level, key, value)
            if _popped_:
                popped[level] = _popped_
        return popped or None

if __name__ == "__main__":
    with open("config.yml") as fp:
        config = yaml.safe_load(fp)
    cache = NCache(config)