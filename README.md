# make-tracing
Tracing GNU make in chrome://tracing

**this is designed to analyze the Kokkos and Kokkos Kernels projects, and may not work directly for other programs**

copy `trace-make.sh` into your build directory


```
chmod +x trace-make.sh
make SHELL=./trace-make.sh ...
```
This will run your build as normal, except the `trace-make.sh` script will record the start and end timestamp of each command make wants to invoke.
It will produce a `make.trace` file.
You can then convert this to the `chrome://tracing` format with
```
python3 chrome-tracing.py make.trace make.chrometracing
```

Open a chromium browser, navitage to `chrome://tracing` and "Load" the `make.chrometracing` file.
The spans are organized by starting timestamp.
You can click on a span to see the actual command make invokes.

## FAQs

* None of the spans in `chrome://tracing` have a name

`chrome-tracing.py` detects file names by looking for `nvcc_wrapper ... -c /.../filename.cpp` in the command `make` invokes.
If your compiler is different or you compile non-c++ files, the events may not be annotated.
However, you can still click on a span to see what command was invoked.

* Does it work with python 2?

Never tried it.

* I want to use a different name than `make.trace` for the raw timestamp data.

Edit `trace-make.sh`.

* I want to group spans by X or sort spans by Y or filter spans by Z

Not implemented.