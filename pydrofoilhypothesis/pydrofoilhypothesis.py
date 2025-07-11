from _pydrofoil import sailtypes
from hypothesis import given, strategies as st
from hypothesis.strategies import DrawFn
import _pydrofoil


def hypothesis_from_pydrofoil_type(typ, machine: _pydrofoil.RISCV64):
    """Returns a Hypothesis strategy to generate a random instance of the given pydrofoil type.

    Args:
        typ: A pydrofoil type (e.g. Struct, Union, BitVector).
        machine: Instance of _pydrofoil.RISCV64()

    Returns:
        A Hypothesis strategy generating instances of the specified type.
    """
    return BasePydrofoilStrategies(machine).hypothesis_from_pydrofoil_type(typ)


class BasePydrofoilStrategies:
    def __init__(self, machine: _pydrofoil.RISCV64):
        """Initialize the strategy generator with a pydrofoil machine instance."""
        self.machine = machine

    def hypothesis_from_pydrofoil_type(self, typ: _pydrofoil.sailtypes.SailType):
        """Returns a Hypothesis strategy to generate a random instance of the given pydrofoil type.

        Args:
            typ: A pydrofoil type (e.g. Struct, Union, BitVector).
            machine: Instance of _pydrofoil.RISCV64()

        Returns:
            A Hypothesis strategy generating instances of the specified type.
        """
        machine = self.machine
        if isinstance(typ, sailtypes.SmallFixedBitVector):
            return self._gen_bitvector(typ)
        elif isinstance(typ, sailtypes.BigFixedBitVector):
            return self._gen_bigbitvector(typ)
        elif ".FVec" in str(typ):  # TODO: fix when pydrofoil is fixed
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
                hypothesis_from_pydrofoil_type(elementtyp, machine)
                for elementtyp in typ
            ]
            return self._gen_Tuple(strategies)
        elif isinstance(typ, sailtypes.Struct):
            meth = getattr(self, f"struct_{typ.name}", None)
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
            meth = getattr(self, f"union_{typ.name}", None)
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
        elif (
            typ.__class__.__name__ == "sailtypes.Unit"
        ):  # TODO: fix when pydrofoil is fixed
            return self._gen_Unit()
        elif isinstance(typ, sailtypes.GenericBitVector):
            return self._gen_genericbitvector()
        else:
            assert False, "not implemented yet"

    # _____________________________________________________
    # composite methods with strange interface

    @st.composite
    def _gen_bitvector(
        draw: DrawFn, self, typ: sailtypes.SmallFixedBitVector
    ) -> _pydrofoil.bitvector:
        return self.gen_bitvector(draw, typ)

    @st.composite
    def _gen_bigbitvector(
        draw: DrawFn, self, typ: sailtypes.BigFixedBitVector
    ) -> _pydrofoil.bitvector:
        return self.gen_bigbitvector(draw, typ)

    @st.composite
    def _gen_FVec(
        draw: DrawFn, self, typ, machine: _pydrofoil.RISCV64
    ):  # TODO Add FVec Annotaion
        return self.gen_FVec(draw, typ, machine)

    @st.composite
    def _gen_bool(draw: DrawFn, self) -> bool:
        return self.gen_bool(draw)

    @st.composite
    def _gen_MachineInt(draw: DrawFn, self) -> int:
        return self.gen_MachineInt(draw)

    @st.composite
    def _gen_Int(draw: DrawFn, self) -> int:
        return self.gen_Int(draw)

    @st.composite
    def _gen_String(draw: DrawFn, self) -> str:
        return self.gen_String(draw)

    @st.composite
    def _gen_Enum(draw: DrawFn, self, typ: sailtypes.Enum) -> list:
        return self.gen_Enum(draw, typ)

    @st.composite
    def _gen_Tuple(draw: DrawFn, self, strategies: list) -> tuple:
        return self.gen_Tuple(draw, strategies)

    @st.composite
    def _gen_Struct(
        draw: DrawFn, self, classes: list, strategies: list, machine: _pydrofoil.RISCV64
    ):
        return self.gen_Struct(draw, classes, strategies, machine)

    @st.composite
    def _gen_specific_Struct(draw: DrawFn, self, meth: callable, typ: sailtypes.Struct):
        return meth(draw, typ)

    @st.composite
    def _gen_Union(
        draw: DrawFn, self, classes: list, strategies: list, machine: _pydrofoil.RISCV64
    ):
        return self.gen_Union(draw, classes, strategies, machine)

    @st.composite
    def _gen_specific_Union(draw: DrawFn, self, meth: callable, typ: sailtypes.Struct):
        return meth(draw, typ)

    @st.composite
    def _gen_Vec(draw: DrawFn, self, strategy) -> _pydrofoil.bitvector:
        return self.gen_Vec(draw, strategy)

    @st.composite
    def _gen_Unit(draw: DrawFn, self) -> tuple:
        return self.gen_Unit(draw)

    @st.composite
    def _gen_genericbitvector(draw: DrawFn, self) -> _pydrofoil.bitvector:
        return self.gen_genericbitvector(draw)

    # _____________________________________________________
    # default implementations

    def gen_bitvector(
        self, draw: DrawFn, typ: sailtypes.SmallFixedBitVector
    ) -> _pydrofoil.bitvector:
        """Generates a _pydrofoil.bitvector of the specified width up to 63 with a random value"""
        value = draw(st.integers(0, 2 ** typ.width - 1))
        return _pydrofoil.bitvector(typ.width, value)

    def gen_bigbitvector(
        self, draw: DrawFn, typ: sailtypes.BigFixedBitVector
    ) -> _pydrofoil.bitvector:
        return self.gen_bigbitvector(draw, typ.width)

    def gen_FVec(
        self, draw: DrawFn, typ, machine: _pydrofoil.RISCV64
    ) -> list:  # TODO Anno FVec
        """Generates a list (FVec) containing length random elements of the vector's element type."""
        res = []
        for i in range(typ.length):
            res.append(draw(hypothesis_from_pydrofoil_type(typ.of, machine)))
        return res

    def gen_bool(self, draw: DrawFn) -> bool:
        """Generates a random boolean value."""
        return draw(st.booleans())

    def gen_MachineInt(self, draw: DrawFn) -> int:
        """Generates a signed int with in 2*63"""
        return draw(st.integers(-2 * 63, 2 * 63 - 1))

    def gen_Int(self, draw: DrawFn) -> int:
        """Generates a int"""
        return draw(st.integers(-2 * 63, 2 * 63 - 1))  # TODO ?????

    def gen_String(self, draw: DrawFn) -> str:
        """Generates a random ASCII string."""
        return draw(st.text(alphabet=st.characters(min_codepoint=0, max_codepoint=127)))

    def gen_Enum(self, draw: DrawFn, typ) -> list:
        """Randomly selects one of the elements defined in the enum."""
        return draw(st.sampled_from(typ.elements))

    def gen_Tuple(self, draw: DrawFn, strategies) -> tuple:
        """Generates a Tuple with random values for each Strategy"""
        l = [draw(strategy) for strategy in strategies]
        return tuple(l)

    def gen_Struct(
        self, draw: DrawFn, name: str, strategies: list, machine: _pydrofoil.RISCV64
    ) -> sailtypes.Struct:
        """Generates a Struct by applying random values to the fields of the structure."""
        l = [draw(strategy) for strategy in strategies]
        return getattr(machine.types, name)(*l)

    def gen_Union(
        self, draw: DrawFn, classes: list, strategies: list, machine: _pydrofoil.RISCV64
    ) -> sailtypes.Union:
        """Generates a Union by selecting one of its constructors and generating an instance."""
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
                    return cls()  # TODO: this is ridiculous
        elif hasattr(value, "sail_type") and isinstance(
            value.sail_type, _pydrofoil.sailtypes.Struct
        ):
            values = [getattr(value, name) for name, _ in value.sail_type.fields]
            return cls(*values)
        else:
            return cls(value)

    def gen_Vec(self, draw: DrawFn, strategy) -> list:
        """Generates a list of elements using the given strategy (used for variable-length vectors)."""
        return draw(st.lists(strategy))

    def gen_Unit(self, draw: DrawFn) -> tuple:
        """Returns the unit value (an empty tuple)."""
        return draw(st.just(()))

    def gen_genericbitvector(self, draw: DrawFn) -> _pydrofoil.bitvector:
        """Generates a _pydrofoil.bitvector width a random width and value"""
        width = draw(st.integers(0))
        if width <= 64:
            value = draw(st.integers(0, 2 ** width - 1))
            return _pydrofoil.bitvector(width, value)
        else:
            return self._help_gen_bigbitvector(draw, width)
        
    # _________________________________________________________
        
    def _help_gen_bigbitvector(self, draw: DrawFn, width: int) -> _pydrofoil.bitvector:
        """Generates a _pydrofoil.bitvector of width by composing multiple 64-bit segments"""
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


# _________________________________________________________


def default_value(typ, machine):
    """Returns a default (zero-like or empty) value for the given pydrofoil type."""
    if isinstance(typ, sailtypes.SmallFixedBitVector):
        return _pydrofoil.bitvector(typ.width, 0)
    elif isinstance(typ, sailtypes.BigFixedBitVector):
        return _gen_huge_bitvector_default(typ.width)
    elif ".FVec" in str(typ):
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
        values = [default_value(elementtyp, machine) for elementtyp in typ]
        return tuple(values)
    elif isinstance(typ, sailtypes.Struct):
        if len(typ.fields) == 1:
            return default_value(typ.fields[0][1], machine)
        values = [
            default_value(elementtyp, machine) for (typs, elementtyp) in typ.fields
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
    elif (
        typ.__class__.__name__ == "sailtypes.Unit"
    ):  # TODO: fix when pydrofoil is fixed
        return ()
    elif isinstance(typ, sailtypes.GenericBitVector):
        return _pydrofoil.bitvector(1, 0)
    else:
        assert False, "not implemented yet"


def _gen_huge_bitvector_default(width: int) -> _pydrofoil.bitvector:
    """Generates a _pydrofoil.bitvector of a given width filled with 0s. Used for large widths exceeding 64-bit."""
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


def gen_Union_default(classes, values, machine: _pydrofoil.RISCV64) -> sailtypes.Union:
    """Creates a default instance of a Union using the first constructor and its corresponding default value."""
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
                return cls()  # TODO: this is ridiculous
    elif hasattr(value, "sail_type") and isinstance(
        value.sail_type, _pydrofoil.sailtypes.Struct
    ):
        values = [getattr(value, name) for name, _ in value.sail_type.fields]
        return cls(*values)
    else:
        return cls(value)


@st.composite
def random_register_values(
    draw: DrawFn,
    machine: _pydrofoil.RISCV64,
    include_registers: list,
    always_default_registers: list,
) -> dict:
    """Generates a dictionary of register names to values.

    Args:
        draw (DrawFn): Hypothesis draw function.
        machine: The target pydrofoil machine definition.
        include_registers (list[str]): List of register names which will be assigned random values.
        always_default_registers (list[str]): List of register names which will be set to default values.

    Returns:
        dict: Mapping from register names to values.
    """
    register_info = machine.register_info()
    register_names_random = [
        (name, typ)
        for (name, typ) in register_info
        if (name in include_registers) and (name not in always_default_registers)
    ]
    register_no_default = [
        (name, typ)
        for (name, typ) in register_info
        if (name not in always_default_registers) and (name not in include_registers)
    ]
    register_names_random = register_names_random + list(
        draw(st.sets(st.sampled_from(register_no_default)))
    )

    register_names_default = [
        (name, typ)
        for (name, typ) in register_info
        if name not in register_names_random
    ]
    registers_include = {
        name: draw(hypothesis_from_pydrofoil_type(typ, machine))
        for (name, typ) in register_names_random
    }
    registers_default = {
        name: default_value(typ, machine) for (name, typ) in register_names_default
    }
    return registers_include | registers_default
