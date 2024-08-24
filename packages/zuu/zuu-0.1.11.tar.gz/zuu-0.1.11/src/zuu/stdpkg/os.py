import os

import functools

def preserve_cwd(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        original_cwd = os.getcwd()
        try:
            return func(*args, **kwargs)
        finally:
            os.chdir(original_cwd)
    return wrapper
