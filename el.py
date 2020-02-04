# electron crypto library

import segwit_addr
from collections import namedtuple

class ParseException(Exception):
  pass

class GenerateException(Exception):
  pass

def getStr(st, byte_length):
  if len(st) < byte_length:
    raise ParseException("getStr failed")
  return (st[byte_length:], st[:byte_length])

def getStrReversed(st, byte_length):
  (st, data) = getStr(st, byte_length)
  return (st, data[::-1])

def putStr(st, data):
  return st + data

def putStrReversed(st, data):
  return st + data[::-1]

def getIntLE(st, byte_length):
  (st, data) = getStr(st, byte_length)
  num = int.from_bytes(data, 'little')
  return (st, num)

def putIntLE(st, byte_length, num):
  data = num.to_bytes(byte_length, 'little')
  return st + data

def getConst(st, data):
  if not st[:len(data)] == data:
    raise ParseException("getConst match failed")
  return (st[len(data):], data)

putConst = putStr

def getOr(st, *funcs):
  for f in funcs:
    try:
      (st, ret) = f(st)
      return (st, ret)
    except ParseException:
      pass
  raise ParseException("getOr all failed")

def getThen(st, *funcs):
  for f in funcs:
    (st, ret) = f(st)
  return (st, ret)

def putThen(st, *funcs):
  for f in funcs:
    st = f(st)
  return st

def getLoop(st, func, num):
  retlist = []
  for i in range(num):
    (st, ret) = func(st)
    retlist.append(ret)
  return (st, retlist)

def putMap(st, func, arglist):
  return putThen(st, *map(lambda x: c(func, x), arglist))

# make a function with no arguments other than st.
def c(func, *args):
  return (lambda st: func(st, *args))

def getVI(st):
  return getOr(st,
    c(getThen, c(getConst, b"\xff"), c(getIntLE, 8)),
    c(getThen, c(getConst, b"\xfe"), c(getIntLE, 4)),
    c(getThen, c(getConst, b"\xfd"), c(getIntLE, 2)),
    c(getIntLE, 1)
  )

def putVI(st, num):
  if num <= 0xfc:
    return putIntLE(st, 1, num)
  elif num <= 0xffff:
    return putIntLE(putStr(st, b"\xfd"), 2, num)
  elif num <= 0xffffffff:
    return putIntLE(putStr(st, b"\xfe"), 4, num)
  elif num <= 0xffffffffffffffff:
    return putIntLE(putStr(st, b"\xff"), 8, num)
  else:
    raise GenerateException("putVI int too big")

Txin = namedtuple("Txin", ("hash", "index", "script", "seqno"))

def getTxin(st):
  (st, hash) = getStrReversed(st, 32)
  (st, index) = getIntLE(st, 4)
  (st, vi) = getVI(st)
  (st, script) = getStr(st, vi)
  (st, seqno) = getIntLE(st, 4)
  return (st, Txin(hash, index, script, seqno))

def putTxin(st, txin):
  st = putStrReversed(st, txin.hash)
  st = putIntLE(st, 4, txin.index)
  st = putVI(st, len(txin.script))
  st = putStr(st, txin.script)
  st = putIntLE(st, 4, txin.seqno)
  return st

Txout = namedtuple("Txout", ("amount", "script"))

def getTxout(st):
  (st, amount) = getIntLE(st, 8)
  (st, vi) = getVI(st)
  (st, script) = getStr(st, vi)
  return (st, Txout(amount, script))

def putTxout(st, txout):
  st = putIntLE(st, 8, txout.amount)
  st = putVI(st, len(txout.script))
  st = putStr(st, txout.script)
  return st

def getWitness(st, num_fields):
  def getItem(st):
    (st, vi) = getVI(st)
    return getStr(st, vi)
  
  def getField(st):
    (st, vi) = getVI(st)
    return getLoop(st, getItem, vi)
  
  return getLoop(st, getField, num_fields)

def putWitness(st, witness):
  for field in witness:
    st = putVI(st, len(field))
    for item in field:
      st = putVI(st, len(item))
      st = putStr(st, item)
  return st

TransactionSegwit = namedtuple("TransactionSegwit", ("version", "marker", "flag", "txins", "txouts", "witness", "locktime"))

TransactionNormal = namedtuple("TransactionNormal", ("version", "txins", "txouts", "locktime"))

def getTransaction(st):
  (st, version) = getIntLE(st, 4)
  isSegwit = (getIntLE(st, 1)[1] == 0)
  if isSegwit:
    (st, marker) = getIntLE(st, 1)
    (st, flag) = getIntLE(st, 1)
  (st, numTxins) = getVI(st)
  (st, txins) = getLoop(st, getTxin, numTxins)
  (st, numTxouts) = getVI(st)
  (st, txouts) = getLoop(st, getTxout, numTxouts)
  if isSegwit:
    (st, witness) = getWitness(st, numTxins)
  (st, locktime) = getIntLE(st, 4)
  if isSegwit:
    return (st, TransactionSegwit(version, marker, flag, txins, txouts, witness, locktime))
  else:
    return (st, TransactionNormal(version, txins, txouts, locktime))

def putTransaction(st, transaction):
  if type(transaction) == TransactionSegwit:
    isSegwit = True
  elif type(transaction) == TransactionNormal:
    isSegwit = False
  st = putIntLE(st, 4, transaction.version)
  if isSegwit:
    st = putIntLE(st, 1, transaction.marker)
    st = putIntLE(st, 1, transaction.flag)
  st = putVI(st, len(transaction.txins))
  st = putMap(st, putTxin, transaction.txins)
  st = putVI(st, len(transaction.txouts))
  st = putMap(st, putTxout, transaction.txouts)
  if isSegwit:
    st = putWitness(st, transaction.witness)
  st = putIntLE(st, 4, transaction.locktime)
  return st

SIGHASH_ALL = 1
SIGHASH_NONE = 2
SIGHASH_SINGLE = 3
SIGHASH_ANYONECANPAY = 0x80

def sha256d(x):
  return sha256(sha256(x))

# the transaction to be signed,
# hashtype,
# index of the txin to be signed,
# the amount of previous txout associated with the txin,
# lock script (or redeem script if you use P2SH) of the txout (must be either '\x00\x14{20-byte pubkey hash}' or '\x00\x20{32-byte script hash}'),
# witness script of the txout (i.e. original data for the 32-byte script hash, P2WPKH only.),
# position of last executed codeseparator before calling this function (required if prevout_witness_script contains 0xab - OP_CODESEPARATOR. Can be None or -1 if there is no codeseparator executed)
def witness_digest(transaction, hashtype, txin_index, prevout_amount, prevout_script, prevout_witness_script=None, last_codeseparator_pos=None):
  # serialization funcs
  def outpoint(txin):
    return putStrReversed(b'', txin.hash) + putIntLE(b'', 4, txin.index)
    
  def sequence(txin):
    return putIntLE(b'', 4, txin.seqno)
    
  def txout_whole(txout):
    return putTxout(b'', txout)
  
  version = putIntLE(b'', 4, transaction.version)
  hashPrevouts = b"\00" * 32
  hashSequence = b"\00" * 32
  hashOutputs = b"\00" * 32
  
  if not hashtype & SIGHASH_ANYONECANPAY:
    hashPrevouts = sha256d(b''.join(map(outpoint, transaction.txins)))
  
  if (not (hashtype & SIGHASH_ANYONECANPAY)) and ((hashtype & 0x1f) != SIGHASH_SINGLE) and ((hashtype & 0x1f) != SIGHASH_NONE):
    hashSequence = sha256d(b''.join(map(sequence, transaction.txins)))
  
  if ((hashtype & 0x1f) != SIGHASH_SINGLE) and ((hashtype & 0x1f) != SIGHASH_NONE):
    hashOutputs = sha256d(b''.join(map(txout_whole, transaction.txouts)))
  elif (hashtype & 0x1f) == SIGHASH_SINGLE and txin_index < len(transaction.txouts):
    hashOutputs = sha256d(txout_whole(transaction.txouts[txin_index]))
  
  if len(prevout_script) == 22 and prevout_script.startswith(b'\x00\x14'):  # P2WPKH
     scriptCode = b"\x19\x76\xa9\x14" + prevout_script[2:] + b"\x88\xac"
  elif len(prevout_script) == 34 and prevout_script.startswith(b'\x00\x20'):  # P2WSH
    if prevout_script[2:] != sha256(prevout_witness_script):
      raise Exception("assertion failed: prevout_script[2:] != sha256(prevout_witness_script)")
    if last_codeseparator_pos != None and last_codeseparator_pos >= 0:
      if prevout_witness_script[last_codeseparator_pos] != 0xab:
        raise Exception("assertion failed: prevout_witness_script[last_codeseparator_pos] != 0xab")
      scriptCodePre = prevout_witness_script[last_codeseparator_pos + 1:]
    else:
      scriptCodePre = prevout_witness_script
    scriptCode = putVI(b'', len(scriptCodePre)) + scriptCodePre
  else:
    raise Exception("prevout_script must be formatted in following forms: '\x00\x14{20-byte pubkey hash}' or '\x00\x20{32-byte script hash}'")
  
  data_to_hash = [
    version,
    hashPrevouts,
    hashSequence,
    outpoint(transaction.txins[txin_index]),
    scriptCode,
    putIntLE(b'', 8, prevout_amount),
    sequence(transaction.txins[txin_index]),
    hashOutputs,
    putIntLE(b'', 4, transaction.locktime),
    putIntLE(b'', 4, hashtype)
  ]
  
  print(data_to_hash)
  
  return sha256d(b''.join(data_to_hash))

import hashlib

def sha256(text):
  return hashlib.sha256(text).digest()
