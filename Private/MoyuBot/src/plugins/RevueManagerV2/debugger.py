from functools import wraps
import traceback


def debugger(func):
    @wraps(func)
    async def exception_wrapper(*args, **kwargs):
        func_info = str(func.__qualname__)

        result = {
            'func_info': func_info
        }

        try:
            response = await func(*args, **kwargs)
            result['response'] = response
            result['error'] = None
        except Exception as e:
            result['response'] = None
            result['error'] = traceback.format_exc()
        finally:
            return result

    return exception_wrapper
