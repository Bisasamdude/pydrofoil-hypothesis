from _pydrofoil import sailtypes
from hypothesis import given, strategies as st
import _pydrofoil


def _gen_huge_bitvector_default( width):
    # TODO: remove again if pydrofoil bug is fixed
    remaining_width = width
    result = None
    while remaining_width >= 64:
        bv = _pydrofoil.bitvector(64, 0)
        if result is None:
            result = bv
        else:
            result = result @ bv
        remaining_width -= 64
    if remaining_width:
        assert 0 <= remaining_width <= 63
        result = result @ _pydrofoil.bitvector(remaining_width, 0)
    assert len(result) == width
    assert result is not None
    return result
    

def gen_Union_default(classes, values, machine):
    assert len(classes) == len(values)
    index = 0
    cls_name = classes[index]
    value = values[index]
    cls = getattr(machine.types, cls_name)
    if isinstance(value, tuple):
        if len(value) > 0:
            return cls(*value)
        else:
            try:
                return cls(())
            except TypeError:
                return cls() # TODO: this is ridiculous
    elif hasattr(value, 'sail_type') and isinstance(value.sail_type, _pydrofoil.sailtypes.Struct):
        values = [getattr(value, name) for name, _ in value.sail_type.fields]
        return cls(*values)
    else:
        return cls(value)


@st.composite
def gen_FVec(draw, typ, machine):
    if not draw(st.booleans()):
        return [draw(hypothesis_from_pydrofoil_type(typ.of, machine))] * typ.length
    res = []
    for i in range(typ.length):
        res.append(draw(hypothesis_from_pydrofoil_type(typ.of, machine)))
    return res

def hypothesis_from_pydrofoil_type(typ, machine):
    # takes a pydrofoil type and returns a hypothesis strategy
    return BasePydrofoilStrategies(machine).hypothesis_from_pydrofoil_type(typ)

class BasePydrofoilStrategies:
    def __init__(self, machine):
        self.machine = machine

    def hypothesis_from_pydrofoil_type(self, typ):
        machine = self.machine
        if isinstance(typ, sailtypes.SmallFixedBitVector):
            return self._gen_bitvector(typ)
        elif isinstance(typ, sailtypes.BigFixedBitVector):
            return self._gen_bigbitvector(typ)
        elif '.FVec' in str(typ):
            return self._gen_FVec(typ, machine)
        elif isinstance(typ, sailtypes.Bool):
            return self._gen_bool()
        elif isinstance(typ, sailtypes.MachineInt):
            return self._gen_MachineInt()
        elif isinstance(typ, sailtypes.Int):
            return self._gen_Int()
        elif isinstance(typ, sailtypes.String):
            return self._gen_String()
        elif isinstance(typ, sailtypes.Enum):
            return self._gen_Enum(typ)
        elif isinstance(typ, sailtypes.Tuple):
            strategies = [
                hypothesis_from_pydrofoil_type(elementtyp, machine) for elementtyp in typ
            ]
            return self._gen_Tuple(strategies)
        elif isinstance(typ, sailtypes.Struct):
            meth = getattr(self, f'struct_{typ.name}', None)
            if meth is not None:
                return self._gen_specific_Struct(meth, typ)
            if len(typ.fields) == 1:
                return hypothesis_from_pydrofoil_type(typ.fields[0][1], machine)
            strategies = [
                (hypothesis_from_pydrofoil_type(elementtyp, machine))
                for (typs, elementtyp) in typ.fields
            ]
            name = typ.name
            return self._gen_Struct(name, strategies, machine)
        elif isinstance(typ, sailtypes.Union):
            meth = getattr(self, f'union_{typ.name}', None)
            if meth is not None:
                return self._gen_specific_Union(meth, typ)
            classes = [cls for (cls, constructor_typ) in typ.constructors]
            strategies = [
                hypothesis_from_pydrofoil_type(constructor_typ, machine)
                for (cls, constructor_typ) in typ.constructors
            ]
            return self._gen_Union(classes, strategies, machine)
        elif ".Vec" in str(typ):  # TODO: fix when pydrofoil is fixed
            strategy = hypothesis_from_pydrofoil_type(typ.of, machine)
            return self._gen_Vec(strategy)
        elif typ.__class__.__name__ == "sailtypes.Unit": # TODO: fix when pydrofoil is fixed
            return self._gen_Unit()
        elif isinstance(typ, sailtypes.GenericBitVector):
            return self._gen_genericbitvector(typ)
        else:
            assert False, "not implemented yet"

    # _____________________________________________________
    # composite methods with strange interface

    @st.composite
    def _gen_bitvector(draw, self, typ):
        return self.gen_bitvector(draw, typ)
    
    @st.composite
    def _gen_bigbitvector(draw, self, typ):
        return self.gen_bigbitvector(draw, typ.width)
    
    @st.composite
    def _gen_FVec(draw, self, typ, machine):
        return self.gen_FVec(draw, typ, machine)
    
    @st.composite
    def _gen_bool(draw, self):
        return self.gen_bool(draw)

    @st.composite
    def _gen_MachineInt(draw, self):
        return self.gen_MachineInt(draw)
    
    @st.composite
    def _gen_Int(draw, self):
        return self.gen_Int(draw)
    
    @st.composite
    def _gen_String(draw, self):
        return self.gen_String(draw)
    
    @st.composite
    def _gen_Enum(draw, self, typ):
        return self.gen_Enum(draw, typ)
    
    @st.composite
    def _gen_Tuple(draw, self, strategies):
        return self.gen_Tuple(draw, strategies)
    
    @st.composite
    def _gen_Struct(draw, self, classes, strategies, machine):
        return self.gen_Struct(draw, classes, strategies, machine)
    
    @st.composite
    def _gen_specific_Struct(draw, self, meth, typ):
        return meth(draw, typ)
    
    @st.composite
    def _gen_Union(draw, self, classes, strategies, machine):
        return self.gen_Union(draw, classes, strategies, machine)
    
    @st.composite
    def _gen_specific_Union(draw, self, meth, typ):
        return meth(draw, typ)
    
    @st.composite
    def _gen_Vec(draw, self, strategy):
            return self.gen_Vec(draw, strategy)
        
    @st.composite
    def _gen_Unit(draw, self):
        return self.gen_Unit(draw)
    
    @st.composite
    def _gen_genericbitvector(draw, self, typ):
        return self.gen_genericbitvector(draw)

    # _____________________________________________________
    # default implementations


    def gen_bitvector(self, draw, typ):
        value = draw(st.integers(0, 2 ** typ.width - 1))
        return _pydrofoil.bitvector(typ.width, value)

    def gen_bigbitvector(self, draw, width):
        # TODO: simplify when pydrofoil limitation is fixed
        remaining_width = width
        result = None
        while remaining_width >= 64:
            value = draw(st.integers(0, 2 ** 64 - 1))
            bv = _pydrofoil.bitvector(64, value)
            if result is None:
                result = bv
            else:
                result = result @ bv
            remaining_width -= 64
        if remaining_width:
            assert 0 <= remaining_width <= 63
            value = draw(st.integers(0, 2 ** remaining_width - 1))
            result = result @ _pydrofoil.bitvector(remaining_width, value)
        assert len(result) == width
        assert result is not None
        return result
    
    def gen_FVec(self, draw, typ, machine):
        if not draw(st.booleans()):
            return [draw(hypothesis_from_pydrofoil_type(typ.of, machine))] * typ.length
        res = []
        for i in range(typ.length):
            res.append(draw(hypothesis_from_pydrofoil_type(typ.of, machine)))
        return res
    
    def gen_bool(self, draw):
        return draw(st.booleans())
    
    def gen_MachineInt(self, draw):
        return draw(st.integers(-2 * 63, 2 * 63 - 1))
    
    def gen_Int(self, draw):
        return draw(st.integers(-2 * 63, 2 * 63 - 1))
    
    def gen_String(self, draw):
        return draw(st.text(alphabet=st.characters(min_codepoint=0, max_codepoint=127)))
    
    def gen_Enum(self, draw, typ):
        return draw(st.sampled_from(typ.elements))
    
    def gen_Tuple(self, draw, strategies):
        l = [draw(strategy) for strategy in strategies]
        return tuple(l)
    
    def gen_Struct(self, draw, name, strategies, machine):
        l = [draw(strategy) for strategy in strategies]
        return getattr(machine.types, name)(*l)
    
    def gen_Union(self, draw, classes, strategies, machine):
        assert len(classes) == len(strategies)
        index = draw(st.integers(0, len(classes) - 1))
        cls_name = classes[index]
        strategy = strategies[index]
        value = draw(strategy)
        cls = getattr(machine.types, cls_name)
        if isinstance(value, tuple):
            if len(value) > 0:
                return cls(*value)
            else:
                try:
                    return cls(())
                except TypeError:
                    return cls() # TODO: this is ridiculous
        elif hasattr(value, 'sail_type') and isinstance(value.sail_type, _pydrofoil.sailtypes.Struct):
            values = [getattr(value, name) for name, _ in value.sail_type.fields]
            return cls(*values)
        else:
            return cls(value)
        
    def gen_Vec(self, draw, strategy):
        return draw(st.lists(strategy))
    
    def gen_Unit(self, draw):
        return draw(st.just(()))
    
    def gen_genericbitvector(self, draw):
        width = draw(st.integers(0))
        if width <= 64:
            value = draw(st.integers(0, 2 ** width - 1))
            return _pydrofoil.bitvector(width, value)
        else:
            return self.gen_bigbitvector(draw, width)

# _________________________________________________________


def default_value(typ, machine):
    if isinstance(typ, sailtypes.SmallFixedBitVector):
        return _pydrofoil.bitvector(typ.width, 0)
    elif isinstance(typ, sailtypes.BigFixedBitVector):
        return _gen_huge_bitvector_default(typ.width)
    elif '.FVec' in str(typ):
        return [default_value(typ.of, machine)] * typ.length
    elif isinstance(typ, sailtypes.Bool):
        return False
    elif isinstance(typ, sailtypes.MachineInt):
        return 0
    elif isinstance(typ, sailtypes.Int):
        return 0
    elif isinstance(typ, sailtypes.String):
        return ""
    elif isinstance(typ, sailtypes.Enum):
        return typ.elements[0]
    elif isinstance(typ, sailtypes.Tuple):
        values = [
            default_value(elementtyp, machine) for elementtyp in typ
        ]
        return tuple(values)
    elif isinstance(typ, sailtypes.Struct):
        if len(typ.fields) == 1:
            return default_value(typ.fields[0][1], machine)
        values = [
            default_value(elementtyp, machine)
            for (typs, elementtyp) in typ.fields
        ]
        return getattr(machine.types, typ.name)(*values)
    elif isinstance(typ, sailtypes.Union):
        classes = [cls for (cls, constructor_typ) in typ.constructors]
        values = [
            default_value(constructor_typ, machine)
            for (cls, constructor_typ) in typ.constructors
        ]
        return gen_Union_default(classes, values, machine)
    elif ".Vec" in str(typ):  # TODO: fix when pydrofoil is fixed
        value = default_value(typ.of, machine)
        return [value]
    elif typ.__class__.__name__ == "sailtypes.Unit": # TODO: fix when pydrofoil is fixed
        return ()
    elif isinstance(typ, sailtypes.GenericBitVector):
        return _pydrofoil.bitvector(1, 0)
    else:
        assert False, "not implemented yet"


@st.composite
def random_register_values(draw, machine, include_registers, always_default_registers):
    register_info = machine.register_info()
    register_names_random = [(name, typ) for (name, typ) in register_info if (name in include_registers) and (name not in always_default_registers)]
    register_no_default = [(name, typ) for (name, typ) in register_info if (name not in always_default_registers) and (name not in include_registers)]
    register_names_random = register_names_random + list(draw(st.sets(st.sampled_from(register_no_default))))
    
    register_names_default = [(name, typ) for (name, typ) in register_info if name not in register_names_random]
    registers_include = {name : draw(hypothesis_from_pydrofoil_type(typ, machine)) for (name, typ) in register_names_random}
    registers_default = {name : default_value(typ, machine) for (name, typ) in register_names_default}
    return registers_include | registers_default
    