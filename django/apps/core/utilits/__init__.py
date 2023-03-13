import time
from django.db.models import When, Value, Case, CharField

def timeit(f):
    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        print('func:%r args:[%r, %r] took: %2.4f sec' % (f.__name__, args, kw, te - ts))
        return result
    return timed


def display_value(choices, field):
    options = [
        When(**{field: k, 'then': Value(v)})
        for k, v in choices
    ]
    return Case(
        *options, output_field=CharField()
    )
