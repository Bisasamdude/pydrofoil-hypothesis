from _pydrofoil import sailtypes
from hypothesis import given, strategies as st
import _pydrofoil


@st.composite
def gen_bitvektorwidth1(draw,typ):
    return _pydrofoil.bitvector(draw(st.integers(typ.width,1)),draw(st.integers(0, 2**typ.width)))#-1 weg da sonst 0#1 beim ersten auch noch ändern
    
def hypothesis_from_pydrofoil_type(typ):
    # takes a pydrofoil type and returns a hypothesis strategy
    if isinstance(typ, sailtypes.SmallFixedBitVector):
        return gen_bitvektorwidth1(typ)
    else:
        assert False, "not implemented yet"