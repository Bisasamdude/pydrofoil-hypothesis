
# april 29

DONE
```
>>>> m.lowlevel.bit_str.sail_type.arguments[0]
<_pydrofoil.types.SmallFixedBitVector object at 0x00007f33ebebc7d0>
```

but:

```
import _pydrofoil.types
```

raises exception

# may 6

pydoc _pydrofoil.sailtypes is not helpful

PARTLY DONE
would be cool for testing to be able to create sailtypes

# may 13


`_pydrofoil.sailtypes.Unit` fehlt!

# may 20

Unterschied zwischen types.ITYPE (nimmt viele parameter, aber der Typ ist "tuple") und C_ADDI_HINT (nimmt einen bitvector als parameter). Dies ist eine Diskrepanz zwischen Python und Sail.

read_register/write_register bonus feature "did you mean"

DONE
BUG: pydrofoil.bitvector.__bool__ gibt True zurück, selbst für den 0 bitvector

# may 27

BUG: _pydrofoil.bitvector(65536, 18446744073709551616)

_pydrofoil.sailtypes.Vec fehlt

sail-function should have a name

machines brauchen eine reset-funktion

# June 10

Some<TLB> should be instantiatable with a struct instance

# July 8

```
(bitvector(64, 0x0000000000000000), bitvector(64, 0x0000000000000000), bitvector(64, 0x0000000000000000), 9223372036854775808, False, ())
(Pdb) cls
<class 'PTW_Success'>
throws overflowerror
```