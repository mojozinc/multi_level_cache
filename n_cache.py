"""Multi level cache"""
from collections import OrderedDict
from exceptions import StrategyNotSupported
import warnings
import yaml

MAX_LEVELS = 4
READ_TIME_PER_LEVEL = [1, 2, 3, 4]
WRITE_TIME_PER_LEVEL = [1, 2, 3, 4]


class lrucache:
    def __init__(self, capacity=0):
        self.capacity = capacity
        self.cache = OrderedDict()

    def read(self, key):
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)  # make key hot
        return self.cache[key]

    def write(self, key, value):
        self.cache[key] = value
        popped = None
        if len(self.cache) > self.capacity:
            popped = self.cache.popitem()
        return popped


class NCache:
    strategy_to_class = dict(lru=lrucache)

    def __init__(self, configfile):
        self.cache_config_list = yaml.safe_load(configfile)
        if len(self.cache_config_list) > MAX_LEVELS:
            warnings.warn(
                "Max cache levels exceeded\nwill only initiate {} levels".format(MAX_LEVELS)
            )
        self.cache_stack = []
        for cache_config in self.cache_config_list[:MAX_LEVELS]:
            startegy = cache_config["STRATEGY"]
            capacity = cache_config["CAPACITY"]
            if strategy not in self.strategy_to_class:
                raise StrategyNotSupported()
            cache_class = self.strategy_to_class(strategy)
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

    def read(self, key):
        for level in range(self.levels):
            value = self._read_level_(level, key)
            if value != None:
                # cache hit
                # update all cold cache levels
                for cold_level in range(level):
                    self._write_level_(cold_level, key, value)
                return value
        # cache miss
        return None

    def write(self, key, value):
        popped = []
        for level in range(self.levels):
            _popped_ = self._write_level_(level, key, value)
            popped.append(_popped_)
        return popped
