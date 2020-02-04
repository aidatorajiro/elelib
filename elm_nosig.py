elm_nosig_eval = """

import segwit_addr
import el

def elm_nosig(text, dest_addr, init_amount = 10000, coeff = 3):
    pref = 'tb'
    
    script = b"\x4c" + el.putIntLE(b'', 1, len(text.encode())) + text.encode() + b"\x75\x51"
    
    dest_script = segwit_addr.encode(pref, 0, el.sha256(script))
    
    tx1 = payto(dest_script, init_amount * 0.00000001)['hex']
    
    tx1_hash = broadcast(tx1)
    
    dest_addr_bytes = bytes(segwit_addr.decode(pref, dest_addr)[1])
    
    tx1_parse = el.getTransaction(bytes.fromhex(tx1))[1]
    
    target_out = list(filter(lambda x: x.script == b'\x00\x20' + el.sha256(script), tx1_parse.txouts))[0]
    
    target_out_index = list.index(tx1_parse.txouts, target_out)
    
    tx2_parse = el.TransactionSegwit(2, 0, 1,
      [el.Txin(bytes.fromhex(tx1_hash), target_out_index, b'', 4294967293)],
      [el.Txout(init_amount - coeff*len(script), b'\x00\x14' + dest_addr_bytes)],
      [[script]], 0)
    
    tx2 = el.putTransaction(b'', tx2_parse).hex()
    
    broadcast(tx2)

"""