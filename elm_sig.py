import segwit_addr
import el

def sign_tx_hash(hash, address, hashtype):
    privkey = bitcoin.deserialize_privkey(getprivatekeys(address))[1]
    return electrum.ecc.ECPrivkey(privkey).sign(bytes.fromhex(hash), electrum.ecc.der_sig_from_r_and_s, electrum.ecc.get_r_and_s_from_der_sig) + hashtype.to_bytes(1, 'little')

def elm_sig(text, dest_addr, init_amount = 10000, coeff = 3):
    pref = 'tb'
    
    tmp_addr = createnewaddress()
    
    tmp_addr_bytes = bytes(segwit_addr.decode(pref, tmp_addr)[1])
    
    script = b"\x4c" + el.putIntLE(b'', 1, len(text.encode())) + text.encode() + b"\x75\x76\xA9\x14" + tmp_addr_bytes + b"\x88\xAC"
    
    dest_script = segwit_addr.encode(pref, 0, el.sha256(script))
    
    tx1 = payto(dest_script, init_amount * 0.00000001)['hex']
    
    tx1_hash = broadcast(tx1)
    
    dest_addr_bytes = bytes(segwit_addr.decode(pref, dest_addr)[1])
    
    tx1_parse = el.getTransaction(bytes.fromhex(tx1))[1]
    
    target_out = list(filter(lambda x: x.script == b'\x00\x20' + el.sha256(script), tx1_parse.txouts))[0]
    
    target_out_index = list.index(tx1_parse.txouts, target_out)
    
    tx2_parse = el.TransactionSegwit(2, 0, 1, [el.Txin(bytes.fromhex(tx1_hash), target_out_index, b'', 4294967293)], [el.Txout(init_amount - coeff*len(script), b'\x00\x14' + dest_addr_bytes)], [[script]], 0)
    
    tx2 = el.putTransaction(b'', tx2_parse).hex()
    
    broadcast(tx2)