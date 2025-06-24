import pytest
from pydrofoilhypothesis import pydrofoilhypothesis
import _pydrofoil

from hypothesis import given

m = _pydrofoil.RISCV64()
itype_args = dict(m.types.ast.sail_type.constructors)["ITYPE"]
itype_args_strategy = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(itype_args, m)

register_value_typ = dict(m.register_info())["x1"]
register_value_strategy = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(
    register_value_typ, m
)
cur_privilege_typ = dict(m.register_info())["cur_privilege"]
cur_privilege_strategy = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(
    cur_privilege_typ, m
)


@given(itype_args_strategy, cur_privilege_strategy, register_value_strategy)
def test_itype_stays_in_supervisor_mode(args, cur_privilege_value, register_value):
    immediate, rs, rd, iop = args
    instruction = m.types.ITYPE(*args)
    if rs:  
        m.lowlevel.wX(rs.unsigned(), register_value)
    m.write_register("cur_privilege", cur_privilege_value)
    oldvalues = [m.lowlevel.rX(i) for i in range(32)]
    res = m.lowlevel.execute(instruction)
    assert res == 'RETIRE_SUCCESS'
    assert m.read_register("cur_privilege") == cur_privilege_value  # unchanged
    newvalues = [m.lowlevel.rX(i) for i in range(32)]
    for index, (oldval, newval) in enumerate(zip(oldvalues, newvalues)):
        if oldval != newval:
            assert index == rd.unsigned()
            
                       
@given(itype_args_strategy, cur_privilege_strategy, register_value_strategy, pydrofoilhypothesis.random_register_values(m, [], [name for (name, typ) in m.register_info() if 'x' in name]))
def test_itype_stays_in_supervisor_mode_random_Registers(args, cur_privilege_value, register_value, register_values):
    immediate, rs, rd, iop = args
    instruction = m.types.ITYPE(*args)
    register_values = {name: typ for name, typ in register_values.items() if ('tlb' not in name) and ('cur_privilege' not in name) and ('x' not in name)}
    for name, value in register_values.items():
        m.write_register(name, value)
    if rs:  
        m.lowlevel.wX(rs.unsigned(), register_value)
    m.write_register("cur_privilege", cur_privilege_value)
    oldvalues = [m.lowlevel.rX(i) for i in range(32)]
    res = m.lowlevel.execute(instruction)
    assert res == 'RETIRE_SUCCESS'
    assert m.read_register("cur_privilege") == cur_privilege_value  # unchanged
    newvalues = [m.lowlevel.rX(i) for i in range(32)]
    for index, (oldval, newval) in enumerate(zip(oldvalues, newvalues)):
        if oldval != newval:
            assert index == rd.unsigned()
    for name, value in register_values.items():
        assert m.read_register(name) == value

