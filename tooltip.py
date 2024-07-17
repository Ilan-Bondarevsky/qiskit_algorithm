
import sys
import os
current_dir = os.getcwd()
sys.path.append(current_dir)

import inspect

def copy_docs_and_signature_from(source_func):
    def decorator(target_func):
        target_func.__doc__ = source_func.__doc__
        target_func.__signature__ = inspect.signature(source_func)
        return target_func
    return decorator
