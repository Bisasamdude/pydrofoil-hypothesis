from _pydrofoil import sailtypes
from hypothesis import given, strategies as st
import _pydrofoil


@st.composite
def gen_bitvektorwidth1(draw, typ):
    value = draw(st.integers(0, 2**typ.width - 1))
    return _pydrofoil.bitvector(typ.width, value)


def hypothesis_from_pydrofoil_type(typ):
    # takes a pydrofoil type and returns a hypothesis strategy
    if isinstance(typ, sailtypes.SmallFixedBitVector):
        return gen_bitvektorwidth1(typ)
    elif isinstance(typ, sailtypes.Bool):
        return st.booleans()
    else:
        assert False, "not implemented yet"