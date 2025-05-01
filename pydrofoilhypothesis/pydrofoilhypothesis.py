from _pydrofoil import sailtypes
from hypothesis import given, strategies as st
import _pydrofoil


@st.composite
def gen_bitvektorwidth1(draw):
    a=_pydrofoil.bitvector(1,draw(st.integers(0,1)))
    print(a)
    return a

def hypothesis_from_pydrofoil_type(typ):
    # takes a pydrofoil type and returns a hypothesis strategy
    if isinstance(typ, sailtypes.SmallFixedBitVector):
        return gen_bitvektorwidth1()
    else:
        assert False, "not implemented yet"