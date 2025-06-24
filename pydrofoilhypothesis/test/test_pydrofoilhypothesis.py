import pytest
from pydrofoilhypothesis import pydrofoilhypothesis
import _pydrofoil

from hypothesis import given, strategies as st, example

m = _pydrofoil.RISCV64()
typ = m.lowlevel.bit_str.sail_type.arguments[0]
bitvector_width_1_strategy = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(typ, m)


@given(bitvector_width_1_strategy)
def test_bitvector_width_1(val):
    # bitvector width 1
    assert isinstance(val, _pydrofoil.bitvector)
    assert val == 1 or val == 0
    assert len(val) == 1


typ2 = m.lowlevel.encdec_backwards.sail_type.arguments[0]
bitvector_width_32_strategy = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(
    typ2, m
)


@given(bitvector_width_32_strategy)
def test_bitvector_width_32(val):
    assert isinstance(val, _pydrofoil.bitvector)
    assert 0 <= val.unsigned() <= 2 ** 32 - 1
    assert len(val) == 32


bigBitvetortyp = m.lowlevel.wV.sail_type.arguments[1]
bigBitvetor_strategy = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(
    bigBitvetortyp, m
)


@given(bigBitvetor_strategy)
def test_BigBitvetor(val):
    assert isinstance(val, _pydrofoil.bitvector)
    assert len(val) >= 32


typ = m.lowlevel.bool_bit_backwards.sail_type.result
bool_strategy = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(typ, m)


@given(bool_strategy)
def test_generate_bool(val):
    assert val in (False, True)


typ = m.lowlevel.wF.sail_type.arguments[0]
machineInt_strategy = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(typ, m)


@given(machineInt_strategy)
def test_generate_MachineInt(val):
    assert -(2 ** 63) <= val <= 2 ** 63 - 1


inttyp = m.lowlevel.process_vm.sail_type.arguments[2]
intstrategy = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(inttyp, m)


@given(intstrategy)
def test_generate_Int(val):
    assert val <= 0 or val >= 0


Stringtyp = m.types.exception.sail_type.constructors[1][1]
Stringstrategy = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(Stringtyp, m)


@given(Stringstrategy)
def test_generate_String(val):
    assert all(ord(c) <= 127 for c in val)


enum_typ = m.lowlevel.vitype_mnemonic_forwards.sail_type.arguments[0]
enum_strategy = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(enum_typ, m)


@given(enum_strategy)
def test_generate_Enum(val):
    assert val in enum_typ.elements


typ = m.lowlevel.wX.sail_type.result  # Unit
unit_strategy = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(typ, m)


@given(unit_strategy)
def test_generate_Unit(val):
    assert val is ()


uniontyp = m.lowlevel.encdec_backwards.sail_type.result
constructors = dict(uniontyp.constructors)
tupletyp = constructors["ITYPE"]
tuplestrategy = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(tupletyp, m)


@given(tuplestrategy)
def test_generate_Tuple(t):

    imm, reg1, reg2, operation_name = t
    assert len(imm) == 12
    assert 0 <= imm.unsigned() < 2 ** 12
    assert len(reg1) == len(reg2) == 5
    assert 0 <= reg1.unsigned() < 2 ** 5
    assert 0 <= reg2.unsigned() < 2 ** 5
    assert operation_name in (
        "RISCV_ADDI",
        "RISCV_SLTI",
        "RISCV_SLTIU",
        "RISCV_XORI",
        "RISCV_ORI",
        "RISCV_ANDI",
    )


unionstrategy = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(uniontyp, m)
unionnames = [name for (name, tuples) in uniontyp.constructors]


@given(unionstrategy)
def test_generate_Union(val):
    assert val.__class__.__name__ in unionnames
    assert isinstance(val, m.types.ast)
    
uniontyp2 = m.types.PTW_Result.sail_type
unionstrategy2 = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(uniontyp2, m)

@given(unionstrategy2)
def test_other_union_not_changed(ptw_result):
    assert isinstance(ptw_result, m.types.PTW_Result)


structtyp = m.lowlevel.encdec_mul_op_backwards.sail_type.result
structstrategy = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(structtyp, m)


@given(structstrategy)
def test_generate_Struct(val):
    assert val.sail_type == structtyp
    assert val.high in (False, True)
    assert val.signed_rs1 in (False, True)
    assert val.signed_rs2 in (False, True)


vectyp = m.lowlevel.write_vmask.sail_type.arguments[2]
vecstrategy = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(vectyp, m)


@given(vecstrategy)
def test_generate_Vec(val):
    assert isinstance(val, list)
    for element in val:
        assert element is True or element is False

genericbitvectortyp = getattr(m.lowlevel, 'MemoryOpResult_add_meta<b>').sail_type.arguments[0].constructors[1][1]
genericbitvectorstrategy = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(genericbitvectortyp, m)

@given(genericbitvectorstrategy)
def test_generate_GenericBitVector(val):
    assert isinstance(val, _pydrofoil.bitvector)
    



    

registerStrucTyp=[typ for (name,typ) in m.register_info() if name == 'misa']
registerStrucStrategy=pydrofoilhypothesis.hypothesis_from_pydrofoil_type(registerStrucTyp[0], m)
@given(registerStrucStrategy)
def test_registerStruc(val):
    assert isinstance(val, _pydrofoil.bitvector)
    assert len(val) == 64

FVecTyp = dict(m.register_info())['mhpmevent']
FVecStrategy = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(FVecTyp, m)

@given(FVecStrategy)
def test_FVec(val):
    assert len(val) == 32
    assert all(isinstance(element, _pydrofoil.bitvector) for element in val)
    assert {len(element) for element in val} == {64}


FVecTypTLB = dict(m.register_info())['tlb']
FVecTLBStrategy = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(FVecTypTLB, m)

@given(FVecTLBStrategy)
def test_FVecTLB(val):
    assert len(val) == 64

def test_default_register_values():
    for name, typ in m.register_info():
        pydrofoilhypothesis.default_value(typ, m) # does not crash

def test_default_register_values2():
    for name, typ in m.register_info():
        typ_default = pydrofoilhypothesis.default_value(typ, m) 
        typ_normal = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(typ, m).example()
        assert typ_default.__class__ == typ_normal.__class__

include_registers = [name for (name, typ) in m.register_info()[0:5]]
always_default_registers = [name for (name, typ) in m.register_info()[7:8]]
@given(pydrofoilhypothesis.random_register_values(m, include_registers, always_default_registers))    
def test_random_register_values(values):
    assert len(values) == len(m.register_info())
    for name, value in values.items():
        m.write_register(name, value)
        assert m.read_register(name) == value


@st.composite
def random_register_values_random_include_exclude(draw, machine):
    include_registers = draw(st.lists(st.sampled_from([name for (name, typ) in m.register_info()])))
    always_default_registers = draw(st.lists(st.sampled_from([name for (name, typ) in m.register_info()])))
    values = draw(pydrofoilhypothesis.random_register_values(machine, include_registers, always_default_registers))
    return values
    

        
@given(random_register_values_random_include_exclude(m))    
def test_random_register_values_random_include_exclude(values):
    assert len(values) == len(m.register_info())
    for name, value in values.items():
        m.write_register(name, value)
        assert m.read_register(name) == value
    

def _find_all_sail_types():
    typs = set()
    for name in dir(m.types):
        value = getattr(m.types, name)
        if hasattr(value, 'sail_type'):
            typs.add(value.sail_type)
    for name in dir(m.lowlevel):
        value = getattr(m.lowlevel, name)
        for typ in value.sail_type.arguments:
            typs.add(typ)
        typs.add(value.sail_type.result)
    typs = list(typs)
    typs.sort(key=lambda element: len(str(element)))
    return typs

sailtyps = _find_all_sail_types()

def test_smoke_all_functions():
    unsupported_types = set()
    for funcname in dir(m.lowlevel):
        func = getattr(m.lowlevel, funcname)
        for argtype in func.sail_type.arguments:
            try:
                pydrofoilhypothesis.hypothesis_from_pydrofoil_type(argtype, m)
            except AssertionError:
                print(funcname, argtype)
                unsupported_types.add(argtype)
    assert not unsupported_types

def test_smoke_all_classes():
    unsupported_types = set()
    for typename in dir(m.types):
        cls = getattr(m.types, typename)
        
        if not hasattr(cls, 'sail_type'):
            continue
        typ = cls.sail_type
        try:
            pydrofoilhypothesis.hypothesis_from_pydrofoil_type(typ, m)
        except AssertionError:
            print(typename, typ)
            unsupported_types.add(typ)
    assert not unsupported_types

@given(st.data())
def test_smoke_more(data):
    typ = data.draw(st.sampled_from(sailtyps))
    value = data.draw(pydrofoilhypothesis.hypothesis_from_pydrofoil_type(typ, m))
    pydrofoilhypothesis.default_value(typ, m)
    
    
