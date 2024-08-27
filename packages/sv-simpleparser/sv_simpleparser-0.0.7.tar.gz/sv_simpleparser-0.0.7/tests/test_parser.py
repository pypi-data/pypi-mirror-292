import pytest
import pathlib
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
from sv_simpleparser import parse_sv


def test_adder():

    mod_name_ref = 'adder'
    port_name_lst_ref = ['A', 'B', 'X']
    param_name_lst_ref = ['DATA_WIDTH', 'TEST']
    port_width_lst_ref = ['[DATA_WIDTH-1:0]', '[DATA_WIDTH-1:0]', '[DATA_WIDTH:0]',]
    file_path = pathlib.Path(project_root)/ 'tests' / 'svfiles_examples' / 'adder.sv'

    mod_lst = parse_sv(file_path)

    mod = mod_lst[0]

    mod_name = mod.name
    port_name_lst = [port.name for port in mod.port_lst]
    port_width_lst = [port.width for port in mod.port_lst]
    param_name_lst = [param.name for param in mod.param_lst]

    assert mod_name == mod_name_ref
    assert port_name_lst == port_name_lst_ref
    assert port_width_lst == port_width_lst_ref
    assert param_name_lst == param_name_lst_ref


def test_bcd_adder():

    mod_name_ref = 'bcd_adder'
    port_name_lst_ref = ['a', 'b', 'cin', 'sum', 'cout']
    port_width_lst_ref = ['[3:0]', '[3:0]', None, '[3:0]', None]
    file_path = pathlib.Path(project_root)/ 'tests' / 'svfiles_examples' / 'bcd_adder.sv'

    mod_lst = parse_sv(file_path)

    mod = mod_lst[0]
    mod_name = mod.name
    port_name_lst = [port.name for port in mod.port_lst]
    port_width_lst = [port.width for port in mod.port_lst]

    assert mod_name == mod_name_ref
    assert port_name_lst == port_name_lst_ref
    assert port_width_lst == port_width_lst_ref
