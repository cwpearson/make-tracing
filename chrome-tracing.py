#! env python

# https://docs.google.com/document/d/1CvAClvFfyA5R-PhYUmn5OOQtYMH4h6I0nSsKchNAySU/preview

import sys
import re
import json
import math

class Span:
    def __init__(self, start, pid, cmd):
        self.start = start #us
        self.pid = pid
        self.cmd = cmd
        self.stop = None

    def is_open(self):
        return self.stop is None

    def get_name(self):
        mo = re.match(".*nvcc_wrapper.*/(.*?\.cpp)", self.cmd)
        if mo:
            return mo.group(1)
        else:
            return ""

    def get_cat(self):
        mo = re.match(".*nvcc_wrapper.*/(.*?\.cpp)", self.cmd)
        if mo:
            return "cpp"
        else:
            return "cmd"


    def b_event(self):
        return {
            "name": self.get_name(),
            "cat": self.get_cat(),
            "ph": "B",
            "ts": self.start,
            "pid": 0,
            "tid": self.pid,
            "args": {"cmd": self.cmd},
        }

    def e_event(self):
        return {
            "name": self.get_name(),
            "cat": self.get_cat(),
            "ph": "E",
            "ts": self.stop,
            "pid": 0,
            "tid": self.pid,
            "args": {},
        }

    def sort_event(self, sort_index):
        return {
            "name": "thread_sort_index",
            "ph": "M",
            "pid": 0,
            "tid": self.pid,
            "args": {"sort_index": sort_index},
        }


with open(sys.argv[1], "r") as f:
    lines = f.readlines()



open_spans = set()
closed_spans = []

for line in lines:
    mo = re.match("B (\d+) (\d+\.\d+) \[(.*)\]", line) # start of a command
    if mo:
        pid = int(mo.group(1))
        ts = float(mo.group(2)) * 1000000 # microseconds
        cmd = mo.group(3)

        open_spans.add(Span(ts, pid, cmd))
        print(len(open_spans), "open spans")

    mo = re.match("E (\d+) (\d+\.\d+)", line) # end of a command
    if mo:
        pid = int(mo.group(1))
        ts = float(mo.group(2)) * 1000000 # microseconds

        for span in open_spans:
            if span.pid == pid:
                open_spans.remove(span)
                span.stop = ts
                closed_spans += [span]
                break
        print(len(open_spans), "open spans")
        print(len(closed_spans), "closed spans")

spans = sorted(closed_spans, key=lambda s: s.start)

# remove small
i = 0
while i < len(spans):
    elapsed = spans[i].stop - spans[i].start
    if elapsed < 1000000:
        spans = spans[:i] + spans[i+1:]
        i -= 1
    i += 1

print(len(spans), "long spans")

obj = {
    "traceEvents": [],
    "displayTimeUnit": "ms",
}

for i, span in enumerate(spans):
    obj["traceEvents"] += [span.b_event()]
    obj["traceEvents"] += [span.e_event()]
    obj["traceEvents"] += [span.sort_event(i)]

with open(sys.argv[2], "w") as f:
    f.write(json.dumps(obj))

# print build parallelism vs time
start_ts = min(span.start for span in spans)
stop_ts = max(span.stop for span in spans)
parallelism_x = []
parallelism_y = []
i = start_ts
while i < stop_ts:
    count = 0
    for span in spans:
        if i >= span.start and i < span.stop and "cpp" == span.get_cat():
            count += 1

    parallelism_x += [int((i - start_ts) / 1000000)]
    parallelism_y += [count]

    i += 1000000

# print csv
for xy in zip(parallelism_x, parallelism_y):
    print str(xy[0]) + "," + str(xy[1])

# histogram compile times
min_elapsed = min(span.stop - span.start for span in spans if span.get_cat() == "cpp")
max_elapsed = max(span.stop - span.start for span in spans if span.get_cat() == "cpp")
nBins = 20
bins = [0 for x in range(nBins)]
for span in spans:
    if span.get_cat() == "cpp":
        elapsed = span.stop - span.start
        iBin = (elapsed - min_elapsed) / (max_elapsed - min_elapsed) * nBins
        print elapsed, min_elapsed, max_elapsed, max_elapsed - min_elapsed, iBin
        iBin = int(iBin)
        iBin = min(iBin, nBins-1)
        bins[iBin] += 1

print bins
