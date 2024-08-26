import time
import pstats
import cProfile
import objgraph
import tracemalloc
import memory_profiler

class zenprofiler:
    def __init__(self):
        self.profiler = None
        self.memory_profile = None
        self.tracemalloc_snapshot = None
        self.start_time = None
    
    def start_profiling(self):
        """Start profiling with cProfile."""
        self.profiler = cProfile.Profile()
        self.profiler.enable()
    
    def stop_profiling(self):
        """Stop profiling and print results."""
        if self.profiler:
            self.profiler.disable()
            stats = pstats.Stats(self.profiler)
            stats.sort_stats(pstats.SortKey.TIME)
            stats.print_stats()
    
    def start_memory_profiling(self):
        """Start memory profiling."""
        self.memory_profile = memory_profiler.memory_usage(-1, interval=1, timeout=1)
    
    def stop_memory_profiling(self):
        """Stop memory profiling and print results."""
        if self.memory_profile:
            print("Memory usage (MB):", self.memory_profile[-1])
    
    def start_tracemalloc(self):
        """Start tracing memory allocations."""
        tracemalloc.start()
    
    def stop_tracemalloc(self):
        """Stop tracing and print memory allocation statistics."""
        if tracemalloc.is_tracing():
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')
            print("Top memory allocations:")
            for stat in top_stats[:10]:
                print(stat)
    
    def set_trace(self):
        """Set a breakpoint using ipdb."""
        import ipdb; ipdb.set_trace()
    
    def track_object_references(self, obj):
        """Visualize object references using objgraph."""
        objgraph.show_refs([obj], filename='object_references.png')
    
    def profile_function(self, func, *args, **kwargs):
        """Profile a specific function."""
        self.start_profiling()
        result = func(*args, **kwargs)
        self.stop_profiling()
        return result
    
    def profile_method(self, method, *args, **kwargs):
        """Profile a specific method."""
        self.start_profiling()
        result = method(*args, **kwargs)
        self.stop_profiling()
        return result
    
    def measure_execution_time(self, func, *args, **kwargs):
        """Measure the execution time of a function."""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Execution time: {end_time - start_time:.4f} seconds")
        return result

