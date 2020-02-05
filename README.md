# Electrum fun library

fun library for electrum. have fun!

## Library used

segwiit_addr.py - Copyright (c) 2017 Pieter Wuille

## how to use

In electrum console:

```python
import sys
sys.path.append("/path/to/clone/directory")
import segwit_addr
import el
from elm import elm_nosig, elm_sig
```

## API reference

Note that you need segwit wallet to call these functions.

### elm\_nosig

- args: *command_set*, *text*, *dest\_addr*, *coeff* = 10, *len_offset* = 100, *final_amount* = 1000

Please set *command_set* to `globals()` in the console.

1. Send *coeff* \* (len(*script*) + *len_offset*) + *final_amount* to an address with script "OP_PUSHDATA < *text* > OP_DROP OP_TRUE" (*script*). Via P2WSH.
2. From the address, send (*final_amount*) to *dest\_addr*.

### elm\_sig

- args: *command_set*, *text*, *dest\_addr*, *coeff* = 10, *len_offset* = 100, *final_amount* = 1000

Please set *command_set* to `globals()` in the console.

1. Create an address(*tmp\_addr*)
2. Send *coeff* \* (len(*script*) + *len_offset*) + *final_amount* to an address with script "OP_PUSHDATA < *text* > OP_DROP OP_DUP OP_HASH160 < pubKeyHash of *tmp\_addr* > OP_EQUALVERIFY OP_CHECKSIG" (*script*). Via P2WSH.
3. From the address, send (*final_amount*) to *dest\_addr*, using the private key of the address generated in 1.