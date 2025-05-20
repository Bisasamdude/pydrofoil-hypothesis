from _pydrofoil import sailtypes
from hypothesis import given, strategies as st
import _pydrofoil


@st.composite
def gen_bitvektor(draw, typ):
    value = draw(st.integers(0, 2 ** typ.width - 1))
    return _pydrofoil.bitvector(typ.width, value)


@st.composite
def gen_Enum(draw, typ):
    return draw(st.sampled_from(typ.elements))


@st.composite
def gen_Tuple(draw, strategies):
    l = [draw(strategy) for strategy in strategies]
    return tuple(l)


@st.composite
def gen_Union(draw, classes, strategies, machine):
    assert len(classes) == len(strategies)
    index = draw(st.integers(0, len(classes) - 1))
    cls_name = classes[index]
    strategy = strategies[index]
    value = draw(strategy)
    cls = getattr(machine.types, cls_name)
    if isinstance(value, tuple):
        return cls(*value)
    else:
        return cls(value)


@st.composite
def gen_Struct(draw, name, strategies, machine):
    l = [draw(strategy) for strategy in strategies]
    return getattr(machine.types, name)(*l)


def hypothesis_from_pydrofoil_type(typ, machine):
    # takes a pydrofoil type and returns a hypothesis strategy
    if isinstance(typ, sailtypes.SmallFixedBitVector):
        return gen_bitvektor(typ)
    elif isinstance(typ, sailtypes.Bool):
        return st.booleans()
    elif isinstance(typ, sailtypes.MachineInt):
        return st.integers(-2 * 63, 2 * 63 - 1)
    elif isinstance(typ, sailtypes.Enum):
        return gen_Enum(typ)
    elif isinstance(typ, sailtypes.Tuple):
        strategies = [
            hypothesis_from_pydrofoil_type(elementtyp, machine) for elementtyp in typ
        ]
        return gen_Tuple(strategies)
    elif isinstance(typ, sailtypes.Struct):
        strategies = [
            (hypothesis_from_pydrofoil_type(elementtyp, machine))
            for (typs, elementtyp) in typ.fields
        ]
        name = typ.name
        return gen_Struct(name, strategies, machine)
    elif isinstance(typ, sailtypes.Union):
        classes = [cls for (cls, constructor_typ) in typ.constructors]
        strategies = [
            hypothesis_from_pydrofoil_type(constructor_typ, machine)
            for (cls, constructor_typ) in typ.constructors
        ]
        return gen_Union(classes, strategies, machine)
    elif typ.__class__.__name__ == "types.Unit":
        return st.just(())
    else:
        assert False, "not implemented yet"
