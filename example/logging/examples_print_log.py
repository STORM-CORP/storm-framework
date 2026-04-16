import sys

# Importing the newly compiled Rust module
import smf


class CustomObject:
    def __str__(self):
        return "<CustomObject String Representation>"


def main():
    print("=== 1. Sequential Execution (core_print) ===")
    # Parameter args < 100, will be routed to core_print in Rust.
    # Conversion using zero-cost abstraction (Bound) directly to stdout.
    smf.printf("Status:", 200, "OK")

    # Custom separators and terminators
    smf.printf("A", "B", "C", sep=" | ", end="\n---\n")

    print("\n=== 2. Parallel Execution (parallel_print) ===")
    # Parameter args > 100, will automatically trigger Rayon thread-pool.
    # Memory pointers are extracted into usize, distributed to worker threads,
    # then reconstructed to bypass the GIL bottleneck.
    large_payload = [f"Data_{i}" for i in range(105)]
    # Using the * (unpacking) operator to send a giant tuple to a Rust FFI
    smf.printf(*large_payload, sep=", ")

    print("\n\n=== 3. Data Type Resolution (converters.rs) ===")
    # Testing how FFI Rust handles Python type conversion to Rust String.
    # - Bytes will be captured by `obj.downcast::<PyBytes>()` and escaped.
    # - None will be caught by `obj.is_none()`.
    # - Custom objects will call the `__str__` slot via `obj.str()`.
    raw_bytes = b"Hello\nWorld\x00"
    smf.printf("Data Bytes:", raw_bytes)
    smf.printf("Data None:", None)
    smf.printf("Custom Class:", CustomObject())

    print("\n=== 4. Routing Destinasi I/O (writer.rs) ===")
    # Testing `OutputDestination` polymorphism in Rust.

    # A. Write to Standard Error (stderr)
    smf.printf("This is a critical error message!", file=sys.stderr, flush=True)

    # B. Writing to a physical File (Duck Typing validation in Rust)
    # Rust will validate the existence of the `write` method using `hasattr("write")`.
    # Execution of write() is done via `call_method1("write")` without GIL context overhead.
    with open("storm_log.txt", "w") as f:
        smf.printf("Log Entry: System initialization successful.", file=f)
        smf.printf("Log Entry: Memory is stable.", file=f, flush=True)
        print("-> [Log successfully written to storm_log.txt]")

    print("\n=== 5. Mode Debug (printd) ===")
    # Calling printd which will print stderr via Rust `eprintln!` first
    # before delegating execution back to `printf`.
    smf.printd("Variable A", "Variabel B", "Variabel C")


if __name__ == "__main__":
    main()

# These two logging mechanisms have different meanings and different ways of capturing logs.
# make sure to use these 2 mechanisms according to the logs you want to capture.
# If you use msf.printf() to save to file.txt, then msf.printd()
# will still output to the terminal.
"""
smf.printf -> This is the stdout log
smf.printd -> This is the stderr log
"""
# Use the first one for production as the second one is better for debugging.
# because the first one can catch errors better during production as in the example below:
"""
import smf
import sys

try:
    # Simulating I/O errors
    open("files.txt", "r")
    
except Exception as e:
    # Redirects specific output to the STDERR stream.
    # The flush=True parameter ensures that Rust's I/O buffers are immediately flushed (OS-level flush),
    # so that the error log is written immediately before the application has the potential to crash.
    smf.printf("ERROR =>", e, file=sys.stderr, flush=True)
"""
# Why is this the best? Because Storm uses Rust for more efficient logging logic than C/C++.
# and here are some other better recommendations:
"""
smf.printf("ERROR =>", error)
smf.printf(f"ERROR => {error}")
"""
# You know that the first implementation will use rust native logging speed
# and will send 2 objects directly to the logging logic for massive speed and incredible efficiency.
#
# Use the second implementation method if the resulting logs are small.
