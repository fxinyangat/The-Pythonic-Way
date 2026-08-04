
import functools
import time

def retry(retries=3, delay=1):
    """Decorator to retry a function that raises an error"""
    def decorator(func):
        functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"Retry {i+1} for {func.__name__} after error: {e}")
                    time.sleep(delay)
            print(f"All {retries} raised failed.")
            raise last_exception
        return wrapper
    return decorator
            
class APIClient:
    def __init__(self):
        self.attempts = 0
        
    @retry(retries=3, delay=2)
    def fetch_data(self):
        self.attempts = 0
        
        if self.attempts < 3:
            raise ConnectionError("Server Timeout")
        
        return {"status":"success", "data":[1,2,3]}
   
   
   
    