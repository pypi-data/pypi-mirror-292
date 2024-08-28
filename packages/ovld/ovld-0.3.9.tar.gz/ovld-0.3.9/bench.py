import timeit

from multimethod import multimethod
from multipledispatch import dispatch

from ovld import ovld, recurse

# OVLD


@ovld
def smap(x: list, y: list):
    """One."""
    return [smap(a, b) for a, b in zip(x, y)]


@ovld
def smap(x: tuple, y: tuple):
    return tuple(smap(a, b) for a, b in zip(x, y))


@ovld
def smap(x: dict, y: dict):
    return {k: smap(v, y[k]) for k, v in x.items()}


@ovld
def smap(x: object, y: object):
    return x + y


# OVLD B


@ovld
def smap_b(self, x: list, y: list):
    """Two."""
    return [self(a, b) for a, b in zip(x, y)]


@ovld
def smap_b(self, x: tuple, y: tuple):
    return tuple(self(a, b) for a, b in zip(x, y))


@ovld
def smap_b(self, x: dict, y: dict):
    return {k: self(v, y[k]) for k, v in x.items()}


@ovld
def smap_b(self, x: object, y: object):
    return x + y


# OVLD C


@ovld
def smap_c(x: list, y: list):
    """Two."""
    return [recurse(a, b) for a, b in zip(x, y)]


@ovld
def smap_c(x: tuple, y: tuple):
    return tuple(recurse(a, b) for a, b in zip(x, y))


@ovld
def smap_c(x: dict, y: dict):
    return {k: recurse(v, y[k]) for k, v in x.items()}


@ovld
def smap_c(x: object, y: object):
    return x + y


# multimethods


@multimethod
def smap_mm(x: list, y: list):
    """Three."""
    return [smap_mm(a, b) for a, b in zip(x, y)]


@multimethod
def smap_mm(x: tuple, y: tuple):
    return tuple(smap_mm(a, b) for a, b in zip(x, y))


@multimethod
def smap_mm(x: dict, y: dict):
    return {k: smap_mm(v, y[k]) for k, v in x.items()}


@multimethod
def smap_mm(x: object, y: object):
    return x + y


# multipledispatch


@dispatch(list, list)
def smap_md(x, y):
    """Four."""
    return [smap_md(a, b) for a, b in zip(x, y)]


@dispatch(tuple, tuple)
def smap_md(x, y):
    return tuple(smap_md(a, b) for a, b in zip(x, y))


@dispatch(dict, dict)
def smap_md(x, y):
    return {k: smap_md(v, y[k]) for k, v in x.items()}


@dispatch(object, object)
def smap_md(x, y):
    return x + y


# isinstance


def smap_ii(x, y):
    """Five."""
    if isinstance(x, dict) and isinstance(y, dict):
        return {k: smap_ii(v, y[k]) for k, v in x.items()}
    elif isinstance(x, tuple) and isinstance(y, tuple):
        return tuple(smap_ii(a, b) for a, b in zip(x, y))
    elif isinstance(x, list) and isinstance(y, list):
        return [smap_ii(a, b) for a, b in zip(x, y)]
    else:
        return x + y


# multipledispatch


A = {"xs": list(range(50)), "ys": ("o", (6, 7))}
B = {"xs": list(range(10, 60)), "ys": ("x", (7, 6))}

results = {
    "smap": smap(A, B),
    "smap_mm": smap_mm(A, B),
    "smap_md": smap_md(A, B),
    "smap_ii": smap_ii(A, B),
    "smap_b": smap_b(A, B),
    "smap_c": smap_c(A, B),
}

expected = results["smap"]

for k, v in results.items():
    assert v == expected, f"{k} failed"


# breakpoint()

print("smap_ov\t", timeit.timeit(lambda: smap(A, B), number=10000))
print("smap_mm\t", timeit.timeit(lambda: smap_mm(A, B), number=10000))
print("smap_md\t", timeit.timeit(lambda: smap_md(A, B), number=10000))
print("smap_ii\t", timeit.timeit(lambda: smap_ii(A, B), number=10000))
print("smap_b\t", timeit.timeit(lambda: smap_b(A, B), number=10000))
print("smap_c\t", timeit.timeit(lambda: smap_c(A, B), number=10000))
