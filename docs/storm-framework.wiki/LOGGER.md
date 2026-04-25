# Internal Logger Documentation

**Logger** is a component that functions to record events or activities in a system/application. It is usually used for system monitoring and debugging.

## Why does Storm have a logger?

The logger in Storm is custom, and we optimized the code to achieve speed and stability against massive I/O, and memory safety.

We made it using the Rust programming language because Rust is a low-level language that guarantees speed equivalent to the C programming language but with very good memory safety.

## Logger Features

Storm Logger has 2 different logic mechanisms in handling a system log.

1. `smf.printf`: It is a standard log function that will output to the terminal quickly.
2. `smf.printd`: This is the log for debugging, we made it not throw the log to the terminal but save the log to a local database **SQLite** in `lib/sqlite/logging/`.

## Further explanation

`smf.printf`: This is designed to capture Logs very efficiently compared to using Python's built-in `print` which is a bit of a bottleneck and has a bit of a delay although the comparison is slightly different.

`smf.printd`: This log base is the same but only it captures logs with more detailed and complete data for efficient debugging and monitoring of Storm system behavior.

### Debug Level

We use the debug level as usual, namely:

**DEBUG, INFO, WARN, ERROR, CRITICAL:** For filters to make it easier to find fatal logs.

## Logger Usage

1. Use direct import into Python.

```python
import smf
```

2. Then use the function:

```python
smf.printf("example", err, file=sys.stderr, flush=True)
smf.printf("example", a, b, c)

smf.printd("example", err, level="ERROR")
smf.printd("example", a, b, c, level="DEBUG")
```

## Export Log

Because for log `smf.printd` By default, logs are always saved in SQLite, so we need to export the log with the following command:

```bash
smf> export log <value>
```

content `<value>` with the appropriate log level, it will export the log according to the log level to a txt file and save it in $HOME.
