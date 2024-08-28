from typing import Any

from ovld import ovld


@ovld
def test(x: type[object]):
    return "yes"


print(test(Any))
