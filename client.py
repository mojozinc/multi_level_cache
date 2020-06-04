import yaml
from n_cache import NCache
from pprint import pprint
import random
from time import time


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def main():
    config = []
    with open("config.yml") as fp:
        config = yaml.safe_load(fp)
    cache = NCache(config)
    data = "a b c d e f g h i j k l m n".split()
    for _ in range(20):
        k, v = random.choice(data), random.choice(data)
        if random.randint(0, 10) < 7:
            st = time()
            cache.write(k, v)
            print(
                bcolors.OKBLUE
                + "write: {}={}, time taken: {:.2}".format(k, v, time() - st)
                + bcolors.ENDC
            )
        else:
            st = time()
            v = cache.read(k)
            color = bcolors.OKGREEN if v else bcolors.FAIL
            print(
                color
                + "read:  {}={}, time taken: {:.2}".format(k, v, time() - st)
                + bcolors.ENDC
            )


if __name__ == "__main__":
    main()
