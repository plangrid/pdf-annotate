# -*- coding: utf-8 -*-
import pytest

from tests.annotations import setUpModule


@pytest.fixture(scope='module', autouse=True)
def pytest_setup():
    setUpModule()
