import time
import tracemalloc


def test_performance(func, *args):

    tracemalloc.start()  # Start tracing memory allocations
    start_time = time.time()  # Start time measurement

    result = func(*args)  # Execute the function

    elapsed_time = time.time() - start_time  # Calculate elapsed time
    current, peak = tracemalloc.get_traced_memory()  # Get memory usage
    tracemalloc.stop()  # Stop tracing memory allocations

    print(f"Function Name: {func.__name__}\n")
    print(f"Execution Time: {elapsed_time *1000:.2f} ms")
    print(f"Initial Memory: {current/1024:.2f} MB")
    print(f"Final Memory: {peak/1024:.2f} MB")
    print(f"Memory Usage: {(peak-current)/1024:.2f} MB \n\n")
  

    return elapsed_time, current, peak, peak-current

