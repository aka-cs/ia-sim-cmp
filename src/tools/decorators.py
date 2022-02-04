def only_once(f):
    value = None
    once = False
    
    def wrapper(*args, **kwargs):
        nonlocal value, once
        if not once:
            value = f(*args, **kwargs)
            once = True
        return value
    
    return wrapper
