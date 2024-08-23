"""One of the test files showing the use of the --order-group-scope option.
See https://pytest-order.readthedocs.io/en/stable/configuration.html#order-group-scope
"""

import pytest


def test1():
    pass


@pytest.mark.order(before="test1")
def test2():
    pass
