#! env python

# https://docs.google.com/document/d/1CvAClvFfyA5R-PhYUmn5OOQtYMH4h6I0nSsKchNAySU/preview

import sys
import re
import json

with open(sys.argv[1], "r") as f:
    lines = f.readlines()

f = open("events.out", "w")

objs = []

for line in lines:
    mo = re.match("(\d+) \[(.*)\] (\d+)", line) # start of a command
    if mo:
        pid = mo.group(1)
        cmd = mo.group(2)
        ts = mo.group(3)

        mo = re.match(".*nvcc_wrapper.*/(.*?\.cpp)", cmd)
        if mo:
            name = mo.group(1)
            cat = "cpp"
        else:
            name = ""
            cat = "cmd"

        obj = {
            "name": name,
            "cat": cat,
            "ph": "B",
            "ts": ts,
            "pid": 0,
            "tid": pid,
            "args": {"cmd": cmd},
        }
        objs += [obj]

    mo = re.match("(\d+) (\d+)", line) # end of a command
    if mo:
        pid = mo.group(1)
        ts = mo.group(2)

        obj = {
            "name": "",
            "cat": "",
            "ph": "E",
            "ts": ts,
            "pid": 0,
            "tid": pid,
            "args": {},
        }
        objs += [obj]

# remove all without ends
i = 0
while i < len(objs):
    if objs[i]["ph"] == 'B':
        found_end = False
        for j in range(i+1, len(objs)):
            if objs[i]["tid"] == objs[j]["tid"] and objs[j]["ph"] == 'E':
                found_end = True
                break
        if not found_end:
            print("didn't find end to ", i, objs[i])
            objs = objs[:i] + objs[i+1:]
            i -= 1
    i += 1

# remove all length < 2
i = 0
while i < len(objs):
    if objs[i]["ph"] == 'B':
        for j in range(i+1, len(objs)):
            if objs[i]["tid"] == objs[j]["tid"] and objs[j]["ph"] == 'E':
                if int(objs[j]["ts"]) - int(objs[i]["ts"]) < 2:
                    print(i, j, "length <2")
                    objs = objs[:j] + objs[j+1:]
                    objs = objs[:i] + objs[i+1:]
                    i -= 1
                    break
    i += 1


# sort by timestamp in viewer
objs = sorted(objs, key=lambda o: o["ts"])


meta_objs = []
tsi = 0
for o in objs:
    if o["ph"] == 'B':
        meta_objs += [
            {
                "name": "thread_sort_index",
                "ph": "M",
                "pid": o["pid"],
                "tid": o["tid"],
                "args": {"sort_index": tsi},
            }
        ]
        tsi += 1

objs = objs + meta_objs

f.write(json.dumps(objs))