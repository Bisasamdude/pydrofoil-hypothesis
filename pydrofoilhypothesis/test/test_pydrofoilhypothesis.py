import pytest
import _pydrofoil
from pydrofoilhypothesis import pydrofoilhypothesis
m = _pydrofoil.RISCV64()

def test_smoke_test_bitvector():
    # bitvector width 1
    typ = m.lowlevel.bit_str.sail_type.arguments[0]
    strategy = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(typ)
    val = strategy.example()
    assert isinstance(val, _pydrofoil.bitvector)
    assert val == 1 or val == 0
    assert len(val) == 1

    typ2 = m.lowlevel.encdec_backwards.sail_type.arguments[0]
    strategy = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(typ2)
    val = strategy.example()
    assert isinstance(val, _pydrofoil.bitvector)
    assert 0 <= val.unsigned() <= 2 ** 32 - 1
    assert len(val) == 32

def test_generate_bool():
    typ = m.lowlevel.bool_bit_backwards.sail_type.result
    strategy = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(typ)
    val = strategy.example()
    assert val is True or val is False