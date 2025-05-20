
# april 29

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

would be cool for testing to be able to create sailtypes

# may 13

`_pydrofoil.sailtypes.Unit` fehlt!

# may 20

Unterschied zwischen types.ITYPE (nimmt viele parameter, aber der Typ ist "tuple") und C_ADDI_HINT (nimmt einen bitvector als parameter). Dies ist eine Diskrepanz zwischen Python und Sail.

read_register/write_register bonus feature "did you mean"

BUG: pydrofoil.bitvector.__bool__ gibt True zurück, selbst für den 0 bitvector