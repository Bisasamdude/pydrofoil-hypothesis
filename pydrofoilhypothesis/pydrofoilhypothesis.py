from _pydrofoil import sailtypes
from hypothesis import given, strategies as st
import _pydrofoil


@st.composite
def gen_bitvektor(draw, typ):
    value = draw(st.integers(0, 2**typ.width - 1))
    return _pydrofoil.bitvector(typ.width, value)

@st.composite
def gen_Enum(draw, typ):
    value = draw(st.integers(0, 2**typ.width - 1))
    return _pydrofoil.Enum

def hypothesis_from_pydrofoil_type(typ):
    # takes a pydrofoil type and returns a hypothesis strategy
    if isinstance(typ, sailtypes.SmallFixedBitVector):
        return gen_bitvektor(typ)
    elif isinstance(typ, sailtypes.Bool):
        return st.booleans()
    elif isinstance(typ, sailtypes.MachineInt):
        return st.integers(-2**31,2**31)
    elif isinstance(typ, sailtypes.Enum):
        return gen_Enum(typ)
    elif isinstance(typ, sailtypes.Unit):
        return ()
    else:
        assert False, "not implemented yet"