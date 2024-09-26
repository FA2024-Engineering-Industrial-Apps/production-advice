import time
from BruteForcing_Parallel_func import call_list_parallel
from BruteForcing_Serial_func import call_list
from BruteForcing_Hybrid_func import call_list_hybrid

#if __name__ == "__main__":
pcb_list =  list(range(1, 6))


start_time_parallel = time.time()
result_parallel = call_list_hybrid(pcb_list)
end_time_parallel = time.time()
execution_time_parallel = end_time_parallel - start_time_parallel

print(" Function Result:")
print(result_parallel)
print(f" Execution Time: {execution_time_parallel} seconds")


