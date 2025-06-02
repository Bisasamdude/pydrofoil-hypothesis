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
    if rs != 0:  # TODO: change to 'if rs:' after bitvector.__bool__ is fixed
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

