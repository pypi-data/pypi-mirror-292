# bugster/decorators.py

import pytest


def login(func):
    return pytest.mark.login(func)
