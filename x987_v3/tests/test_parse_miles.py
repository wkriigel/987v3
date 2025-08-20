import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from x987.utils.text import parse_miles

@pytest.mark.parametrize(
    'src,expected',
    [
        ('52,123 miles', 52123),
        ('52k miles', 52000),
        ('1.5k mi', 1500),
        ('no miles here', None),
    ],
)
def test_parse_miles(src, expected):
    assert parse_miles(src) == expected
