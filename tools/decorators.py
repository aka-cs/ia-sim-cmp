def only_once(f):
    value = None
    once = False
    
    def wrapper():
        nonlocal value, once
        if not once:
            value = f()
            once = True
        return value
    
    return wrapper
