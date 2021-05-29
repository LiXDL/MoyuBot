from functools import wraps


def debugger(func):
    @wraps(func)
    async def exception_wrapper(*args, **kwargs):
        func_info = str(func.__qualname__).split('.')

        result = {
            'class': func_info[0],
            'function': func_info[1]
        }

        try:
            response = await func(*args, **kwargs)
            result['response'] = response
            result['error'] = None
        except Exception as e:
            result['response'] = None
            result['error'] = e
        finally:
            return result

    return exception_wrapper
