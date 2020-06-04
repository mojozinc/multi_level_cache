MultiLevelCache
N-levels of LRU cache, capacity and strategy can defined by using config.yml<br><br>
How to run this:
```bash
python3 client.py
```
tested to run on python 3.7.7. No external packages required

Output should look something like
```bash
sjangra in ~/p/p/multi_level_cache >> python3 client.py
read:  f=None, time taken: 0.61
write: m=g, time taken: 0.61
write: f=c, time taken: 0.61
write: c=f, time taken: 0.6
write: l=i, time taken: 0.61
write: h=a, time taken: 0.61
write: a=c, time taken: 0.6
write: a=k, time taken: 0.62
write: c=i, time taken: 0.61
read:  g=None, time taken: 0.61
read:  h=a, time taken: 0.1
read:  m=g, time taken: 0.6
write: e=d, time taken: 0.61
write: g=k, time taken: 0.6
read:  k=None, time taken: 0.6
write: d=j, time taken: 0.61
write: d=n, time taken: 0.61
read:  m=g, time taken: 0.31
write: l=d, time taken: 0.61
write: a=e, time taken: 0.61
```
N random events are generated to stimulate the cache