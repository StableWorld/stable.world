# flake8: noqa
import unittest
import pytest
from stable_world.interact.yaml_insert import yaml_add_lines_to_machine_pre

inputs = [('''
section:
- hi
''',
'''machine:
  pre:
    - a
    - b

section:
- hi
'''), ('''
machine:
     environment:
      - hi=1
''', '''
machine:
     pre:
       - a
       - b
     environment:
      - hi=1
'''
), ('''
machine:
     environment:
      - hi=1
     pre:
      - this
''', '''
machine:
     environment:
      - hi=1
     pre:
      - a
      - b
      - this
'''
)]


@pytest.mark.parametrize("test_input,expected", inputs)
def test_yaml_add_lines(test_input, expected):
        result = yaml_add_lines_to_machine_pre(test_input, ['a', 'b'])
        assert expected == result
