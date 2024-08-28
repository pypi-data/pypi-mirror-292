#todo extract to a small project

"""
    A fluent decorator is a decorator that has arguments, but provides defaults for all of them (or, to be precise,
    could be called without providing any, so it allows for keyword arguments).

    Thanks to this decorator-for-decorators it can be called with or without parenthesis. In the latter case it will
    be equivalent to calling it without any arguments.

    For example:

        @fluent_decorator
        def foo(name="XYZ"):
            def decorator(f):
                # this is where you'd put functools.wraps(f)
                def wrapper(*args, **kwargs):
                    print(name, args, kwargs)
                    return f(*args, **kwargs)
                return wrapper
            return decorator

        @foo
        def x(a, b):
            return a+b

        @foo()
        def y(a, b):
            return a+b

        @foo("ABC")
        def z(a, b):
            return a+b

        print(x(1, 2))
        print(y(2, 3))
        print(z(3, 4))

    will print out:

        XYZ (1, 2) {}
        3
        XYZ (2, 3) {}
        5
        ABC (3, 4) {}
        7

Use @fluent_decorator for decorators implemented as free-floating functions and @fluent_method_decorator for those
implemented as methods.

    """


def _fluent_decorator(d, for_method):

    from functools import wraps
    self_present = 1 if for_method else 0
    if d.__code__.co_argcount > self_present:
        assert d.__defaults__ is not None, \
            "If the subject decorator has any non-keyword arguments, then they must have default values"
    if d.__defaults__ is not None:
        assert len(d.__defaults__) + self_present == d.__code__.co_argcount, \
            "If the subject decorator has any non-keyword arguments, then they all must have default values"

    @wraps(d)
    def wrapped_decorator(*args, **kwargs):
        if len(args) == 1 + self_present and not kwargs and callable(args[self_present]):
            return d(*(args[:self_present]))(*(args[self_present:]), **kwargs)
        return d(*args, **kwargs)

    return wrapped_decorator

def fluent_decorator(d):
    return _fluent_decorator(d, False)

def fluent_method_decorator(d):
    return _fluent_decorator(d, True)