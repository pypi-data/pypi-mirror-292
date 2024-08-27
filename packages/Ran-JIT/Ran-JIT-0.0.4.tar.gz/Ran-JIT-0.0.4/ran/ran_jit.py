## DO NOT TOUCH WITHOUT A GUIDE

import numba
import inspect
import os
import psutil

def apply_jit_to_all_functions(module_globals):
    """
    Apply JIT compilation to user-defined functions selectively, only if they benefit from JIT.
    """
    for name, obj in module_globals.items():
        if inspect.isfunction(obj) and name != 'apply_jit_to_all_functions':
        
            if name == 'optimize_system_resources':
                print(f"RAN LIB : Skipping JIT for {name} as it handles system resources.")
                continue
            
            try:
                
                source_code = inspect.getsource(obj)
                num_loops = source_code.count('for ') + source_code.count('while ')

                
                if num_loops > 0 or 'np.' in source_code:
                    print(f"RAN LIB : JIT applied to {name}.")
                    module_globals[name] = numba.njit(obj, nopython=True, cache=True)
                else:
                    print(f"RAN LIB : Skipping JIT for {name} due to low complexity.")
            except Exception as e:
                print(f"RAN LIB : Skipping JIT for {name}: {e}")

## DO NOT TOUCH

def optimize_system_resources():
    """
    Adjusts system resources to give the process more priority, 
    potentially improving performance for CPU-bound tasks.
    """
    p = psutil.Process(os.getpid())

    try:
       
        p.nice(psutil.HIGH_PRIORITY_CLASS)
        print("Process priority set to high.")
    except AttributeError:
        # This might fail on non-Windows systems; try a lower level adjustment
        p.nice(-10)  # Unix systems: -20 is highest priority, 19 is lowest
        print("RAN LIB : Process priority increased (Unix).")

    # Optionally, you could lock memory to prevent swapping, but this is risky:
    # try:
    #     p.memory_full_info()  # To allocate memory first
    #     os.mlockall(os.MCL_CURRENT | os.MCL_FUTURE)
    #     print("RAN LIB : Memory locked to prevent swapping.")
    # except (AttributeError, PermissionError):
    #     print("RAN LIB : Memory locking not possible or failed.")


if __name__ != "__main__":
    apply_jit_to_all_functions(globals())
    optimize_system_resources()
