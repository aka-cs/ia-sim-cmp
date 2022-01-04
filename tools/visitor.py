_methods = {}


def _name(obj: type):
    return f"{obj.__module__}.{obj.__qualname__}"


def _declaring_class(obj: type):
    name = _name(obj)
    return name[:name.rfind('.')]


def _visitor_impl(self, arg, **kwargs):
    method = _methods[(_name(type(self)), type(arg))]
    return method(self, arg, **kwargs)


def visitor(arg_type):
    def decorator(fn):
        declaring_class = _declaring_class(fn)
        _methods[(declaring_class, arg_type)] = fn
        return _visitor_impl
    return decorator
