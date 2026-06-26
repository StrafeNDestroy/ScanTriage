from collections import defaultdict
from pathlib import Path 

data_set = [] 









field_stats = defaultdict(lambda:{"present": 0, "none": 0, "types":set()})
for record in data_set:
    for field in ["product", "version"]:
        value = record.get(field)
        if value is None: 
            field_stats[field]["none"] += 1
        else:
            field_stats[field]["present"] += 1
            field_stats[field]["types"].add(type(value).__name__)
for field, stats in field_stats.items():
    print(field,stats)
