import pytest
from pydrofoilhypothesis import pydrofoilhypothesis
import _pydrofoil

from hypothesis import given, strategies as st

m = _pydrofoil.RISCV64()


class PydrofoilStrategies(pydrofoilhypothesis.BasePydrofoilStrategies):
    def gen_bitvector(self, draw, typ):
        return _pydrofoil.bitvector(typ.width, 0)

    def union_ast(self, draw, typ):
        return self.machine.types.ILLEGAL(16)


pst = PydrofoilStrategies(m)

typ = m.lowlevel.bit_str.sail_type.arguments[0]
bitvector_width_1_strategy = pst.hypothesis_from_pydrofoil_type(typ)


@given(bitvector_width_1_strategy)
def test_bitvector_width_1(val):
    # bitvector width 1
    assert isinstance(val, _pydrofoil.bitvector)
    assert val == 0
    assert len(val) == 1

uniontyp = m.lowlevel.encdec_backwards.sail_type.result
assert uniontyp.name == 'ast'

@given(pst.hypothesis_from_pydrofoil_type(uniontyp))
def test_customize_ast(ast):
    assert isinstance(ast, m.types.ILLEGAL)

uniontyp2 = m.types.PTW_Result.sail_type

@given(pst.hypothesis_from_pydrofoil_type(uniontyp2))
def test_other_union_not_changed(ptw_result):
    assert isinstance(ptw_result, m.types.PTW_Result)

