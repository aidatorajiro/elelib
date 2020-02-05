import electrum
import segwit_addr
import el
import electrum.bitcoin as bitcoin

# Sign transaction digest. return tuple(pubkey, sig).
def sign_tx_hash(hash, privkey, hashtype):
    key = electrum.ecc.ECPrivkey(privkey)
    return (key.get_public_key_bytes(), key.sign_transaction(hash) + hashtype.to_bytes(1, 'little'))

def elm_nosig(command_set, text, dest_addr, coeff = 10, len_offset = 100, final_amount = 1000):
    payto = command_set['payto']
    broadcast = command_set['broadcast']
    
    pref = dest_addr[:2]
    
    script = putPushdata(b"", text.encode()) + b"\x75\x51"
    init_amount = coeff*(len(script) + len_offset) + final_amount
    
    dest_script = segwit_addr.encode(pref, 0, el.sha256(script))
    
    tx1 = payto(dest_script, init_amount * 0.00000001)['hex']
    
    tx1_hash = broadcast(tx1)
    
    dest_addr_bytes = bytes(segwit_addr.decode(pref, dest_addr)[1])
    
    tx1_parse = el.getTransaction(bytes.fromhex(tx1))[1]
    
    target_out = list(filter(lambda x: x.script == b'\x00\x20' + el.sha256(script), tx1_parse.txouts))[0]
    
    target_out_index = list.index(tx1_parse.txouts, target_out)
    
    tx2_parse = el.TransactionSegwit(2, 0, 1,
      [el.Txin(bytes.fromhex(tx1_hash), target_out_index, b'', 4294967293)],
      [el.Txout(final_amount, b'\x00\x14' + dest_addr_bytes)],
      [[script]], 0)
    
    tx2 = el.putTransaction(b'', tx2_parse).hex()
    
    broadcast(tx2)

def elm_sig(command_set, text, dest_addr, coeff = 10, len_offset = 100, final_amount = 1000):
    payto = command_set['payto']
    broadcast = command_set['broadcast']
    createnewaddress = command_set['createnewaddress']
    getprivatekeys = command_set['getprivatekeys']

    pref = dest_addr[:2]
    
    tmp_addr = createnewaddress()
    
    tmp_addr_bytes = bytes(segwit_addr.decode(pref, tmp_addr)[1])
    
    script = el.putPushdata(b"", text.encode()) + b"\x75\x76\xA9\x14" + tmp_addr_bytes + b"\x88\xAC"
    init_amount = coeff*(len(script) + len_offset) + final_amount
    
    dest_script = segwit_addr.encode(pref, 0, el.sha256(script))
    
    tx1 = payto(dest_script, init_amount * 0.00000001)['hex']
    
    tx1_hash = broadcast(tx1)
    
    dest_addr_bytes = bytes(segwit_addr.decode(pref, dest_addr)[1])
    
    tx1_parse = el.getTransaction(bytes.fromhex(tx1))[1]
    
    target_out = list(filter(lambda x: x.script == b'\x00\x20' + el.sha256(script), tx1_parse.txouts))[0]
    
    target_out_index = list.index(tx1_parse.txouts, target_out)
    
    hashtype = el.SIGHASH_ALL
    
    tx2_parse = el.TransactionSegwit(2, 0, 1, [el.Txin(bytes.fromhex(tx1_hash), target_out_index, b'', 4294967293)], [el.Txout(final_amount, b'\x00\x14' + dest_addr_bytes)], [[script]], 0)
    
    txdigest = el.witness_digest(tx2_parse, hashtype, 0, init_amount, b'\x00\x20' + el.sha256(script), script)
    
    txsign = sign_tx_hash(txdigest, bitcoin.deserialize_privkey(getprivatekeys(tmp_addr))[1], hashtype)
    
    tx2_parse_signed = el.TransactionSegwit(2, 0, 1, [el.Txin(bytes.fromhex(tx1_hash), target_out_index, b'', 4294967293)], [el.Txout(final_amount, b'\x00\x14' + dest_addr_bytes)], [[txsign[1], txsign[0], script]], 0)
    
    tx2 = el.putTransaction(b'', tx2_parse_signed).hex()
    
    broadcast(tx2)

import re

def elm_getdata(tx):
    scr = tx.witness[0][-1]
    match = re.match(b"^([\x01-\x4e].+?)\x75\x76\xA9\x14.{20}\x88\xAC$", scr)
    if match == None:
        raise el.ParseException("elm_getdata parse error")
    (_, data) = el.getPushdata(match[1])
    return data
