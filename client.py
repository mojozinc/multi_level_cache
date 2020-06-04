import yaml
from n_cache import NCache
from pprint import pprint
import random
from time import time



def main():
    config = []
    with open("config.yml") as fp:
        config = yaml.safe_load(fp)
    cache = NCache(config)
    keys = "a b c d e a c d f g e".split()
    for k, v in zip(keys, keys):
        st = time()
        cache.write(k, v)
        print("time to write key {}={}: {}".format(k,v, time()-st))
    for k in random.choices(keys, k=3):
        st = time()
        val = cache.read(k)
        print("{}={}, time taken: {}".format(k, val, time()-st))

if __name__ == "__main__":
    main()
