import pytest
from pydrofoilhypothesis import pydrofoilhypothesis
import _pydrofoil

from hypothesis import given, strategies as st

m = _pydrofoil.RISCV64()


class PydrofoilStrategies(pydrofoilhypothesis.BasePydrofoilStrategies):
    def gen_bitvector(self, draw, typ):
        return _pydrofoil.bitvector(typ.width, 0)

    def gen_bigbitvector(self, draw, width):
        return _pydrofoil.bitvector(80, 0)

    def gen_FVec(self, draw, typ, machine):
        return "FVec"

    def gen_bool(self, draw):
        return True

    def gen_MachineInt(self, draw):
        return 0

    def gen_Int(self, draw):
        return 0

    def gen_String(self, draw):
        return ""

    def gen_Enum(self, draw, typ):
        return typ.elements[0]

    def gen_Tuple(self, draw, strategies):
        return tuple([0, 0, 0, 0])

    def gen_Struct(self, draw, name, strategies, machine):
        return "Struct"

    def gen_Union(self, draw, classes, strategies, machine):
        return "Union"

    def gen_Vec(self, draw, strategy):
        return "Vec"

    def gen_Unit(self, draw):
        return 1

    def gen_genericbitvector(self, draw):
        return _pydrofoil.bitvector(1, 0)

    # _____________________________________________________


pst = PydrofoilStrategies(m)

typ = m.lowlevel.bit_str.sail_type.arguments[0]
bitvector_width_1_strategy = pst.hypothesis_from_pydrofoil_type(typ)


@given(bitvector_width_1_strategy)
def test_bitvector_width_1(val):
    # bitvector width 1
    assert isinstance(val, _pydrofoil.bitvector)
    assert val == 0
    assert len(val) == 1


bigBitvetortyp = m.lowlevel.wV.sail_type.arguments[1]
bigBitvetor_strategy = pst.hypothesis_from_pydrofoil_type(bigBitvetortyp)


@given(bigBitvetor_strategy)
def test_BigBitvetor(val):
    assert isinstance(val, _pydrofoil.bitvector)
    assert len(val) >= 80
    assert val.unsigned() == 0


typ = m.lowlevel.bool_bit_backwards.sail_type.result
bool_strategy = pst.hypothesis_from_pydrofoil_type(typ)


@given(bool_strategy)
def test_generate_bool(val):
    assert val == True


typ = m.lowlevel.wF.sail_type.arguments[0]
machineInt_strategy = pst.hypothesis_from_pydrofoil_type(typ)


@given(machineInt_strategy)
def test_generate_MachineInt(val):
    assert val == 0


inttyp = m.lowlevel.process_vm.sail_type.arguments[2]
intstrategy = pst.hypothesis_from_pydrofoil_type(inttyp)


@given(intstrategy)
def test_generate_Int(val):
    assert val == 0


Stringtyp = m.types.exception.sail_type.constructors[1][1]
Stringstrategy = pst.hypothesis_from_pydrofoil_type(Stringtyp)


@given(Stringstrategy)
def test_generate_String(val):
    assert val == ""


enum_typ = m.lowlevel.vitype_mnemonic_forwards.sail_type.arguments[0]
enum_strategy = pst.hypothesis_from_pydrofoil_type(enum_typ)


@given(enum_strategy)
def test_generate_Enum(val):
    assert val in enum_typ.elements


typ = m.lowlevel.wX.sail_type.result  # Unit
unit_strategy = pst.hypothesis_from_pydrofoil_type(typ)


@given(unit_strategy)
def test_generate_Unit(val):
    assert val is (1)


uniontyp = m.lowlevel.encdec_backwards.sail_type.result
constructors = dict(uniontyp.constructors)
tupletyp = constructors["ITYPE"]
tuplestrategy = pst.hypothesis_from_pydrofoil_type(tupletyp)


@given(tuplestrategy)
def test_generate_Tuple(t):
    assert t == (0, 0, 0, 0)


uniontyp2 = m.types.PTW_Result.sail_type


@given(pst.hypothesis_from_pydrofoil_type(uniontyp2))
def test_other_union_not_changed(ptw_result):
    assert ptw_result == "Union"


structtyp = m.lowlevel.encdec_mul_op_backwards.sail_type.result
structstrategy = pst.hypothesis_from_pydrofoil_type(structtyp)


@given(structstrategy)
def test_generate_Struct(val):
    assert val == "Struct"


vectyp = m.lowlevel.write_vmask.sail_type.arguments[2]
vecstrategy = pst.hypothesis_from_pydrofoil_type(vectyp)


@given(vecstrategy)
def test_generate_Vec(val):
    assert val == "Vec"


genericbitvectortyp = (
    getattr(m.lowlevel, "MemoryOpResult_add_meta<b>")
    .sail_type.arguments[0]
    .constructors[1][1]
)
genericbitvectorstrategy = pst.hypothesis_from_pydrofoil_type(genericbitvectortyp)


@given(genericbitvectorstrategy)
def test_generate_GenericBitVector(val):
    assert len(val) == 1
    assert val.unsigned() == 0


FVecTyp = dict(m.register_info())["mhpmevent"]
FVecStrategy = pst.hypothesis_from_pydrofoil_type(FVecTyp)


@given(FVecStrategy)
def test_FVec(val):
    assert val == "FVec"


# _____________________________________________________


class PydrofoilStrategies1(pydrofoilhypothesis.BasePydrofoilStrategies):
    def union_ast(self, draw, typ):
        return self.machine.types.ILLEGAL(16)

    def struct_Explicit_access_kind(self, draw, name, strategies, machine):
        return "!!!!"


pst = PydrofoilStrategies1(m)

uniontyp = m.lowlevel.encdec_backwards.sail_type.result
assert uniontyp.name == "ast"


@given(pst.hypothesis_from_pydrofoil_type(uniontyp))
def test_customize_ast(ast):
    assert isinstance(ast, m.types.ILLEGAL)


uniontyp2 = m.types.PTW_Result.sail_type


@given(pst.hypothesis_from_pydrofoil_type(uniontyp2))
def test_other_union_not_changed(ptw_result):
    assert isinstance(ptw_result, m.types.PTW_Result)


structtyp = m.types.Explicit_access_kind.sail_type
structstrategy = pst.hypothesis_from_pydrofoil_type(structtyp)


@given(structstrategy)
def test_generate_Struct(val):
    assert val == "!!!!"


structtyp = m.lowlevel.encdec_mul_op_backwards.sail_type.result
structstrategy = pst.hypothesis_from_pydrofoil_type(structtyp)


@given(structstrategy)
def test_generate_Struct(val):
    assert val.sail_type == structtyp
    assert val.high in (False, True)
    assert val.signed_rs1 in (False, True)
    assert val.signed_rs2 in (False, True)
