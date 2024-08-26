import time
import tracemalloc


def test(func, *args):

    tracemalloc.start()  
    start_time = time.time()  

    result = func(*args)

    elapsed_time = time.time() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Function Name: {func.__name__}\n")
    print(f"Execution Time: {elapsed_time *1000:.2f} ms")
    print(f"Initial Memory: {current/1024:.2f} KB")
    print(f"Final Memory: {peak/1024:.2f} KB")
    print(f"Total Memory Usage: {(peak-current)/1024:.2f} KB \n\n")
  

    return elapsed_time, current, peak, peak-current

