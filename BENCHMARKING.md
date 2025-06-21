# BENCHMARKING

## Reading eve.json files

This is probably the most consuming part. Using the regular Python JSON library versus [orjson](https://github.com/ijl/orjson):

```python
import timeit
timeit.timeit(setup="from suricatalog.filter import TimestampFilter;from suricatalog.log import EveLogHandler; files=['/home/josevnz/Downloads/eve_large.json']; filter=TimestampFilter()", stmt="[x for x in EveLogHandler().get_events(eve_files=files, data_filter=filter)]", number=1000)
```


| Library | Number of executions | Results           |
|---------|----------------------|-------------------|
| json    | 1000                 | 83.44790102099978 |
| orjson  | 1000                 | 82.53240521799944 |

For a small file eve.json the speed-up _was very small_, but for larger files may matter. Also, memory usage is supposed to be better with orjson. 