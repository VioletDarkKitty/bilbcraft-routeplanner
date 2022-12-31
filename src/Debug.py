def debug_print(data, label=None, with_time=False):
    from inspect import stack
    import time

    if label is not None:
        label = " (" + str(label) + "): "
    else:
        label = ""

    if with_time:
        time = str(time.time_ns())
    else:
        time = ""
    stack = stack()[1]
    print("%s:%d %s%s%s\"%s\"" % (stack.filename, stack.lineno, stack.function, time, label, data))
