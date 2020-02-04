from el import *

class ErrorData:
  pass

Error = ErrorData()

test_vectors = [

    getStr(b"abcdefg", 2)    == (b'cdefg', b'ab'),
    getStr(b"ab", 2)         == (b'', b'ab'),
    getStr(b"a", 2)          == Error,
    getIntLE(b"abc", 2)      == (b'c', 25185),
    getConst(b"test", b"t")  == (b'est', b't'),
    getConst(b"test", b"ta") == Error,
    getVI(b"\xfd\x07\x00")   == (b'', 7),
    getVI(b"\x07")           == (b'', 7),
    
    getOr(b"test", c(getConst, b"ta"), c(getConst, b"te"))   == (b'st', b'te'),
    getThen(b"1231234", c(getIntLE, 3), c(getConst, b"1"))   == (b'234', b'1'),
    getThen(b"1231234", c(getIntLE, 3), c(getConst, b"13"))  == Error,
    getLoop(b"aaaaa", c(getConst, b"a"), 4)                  == (b'a', [b'a', b'a', b'a', b'a']),
    
    
    putStr(b"aa", b"bbb")          == b'aabbb',
    putIntLE(b"11", 3, 5263698)    == b'11RQP',
    putThen(b'abc', c(putConst, b'd')  == c(putConst, b'e'))  , b'abcde',
    putMap(b'xyz', putVI, [7, 6, 5])   == b'xyz\x07\x06\x05',
    putVI(b'abc', 12345678)        == b'abc\xfeNa\xbc\x00',

    el.witness_digest(el.getTransaction(bytes.fromhex('0100000002fff7f7881a8099afa6940d42d1e7f6362bec38171ea3edf433541db4e4ad969f0000000000eeffffffef51e1b804cc89d182d279655c3aa89e815b1b309fe287d9b2b55d57b90ec68a0100000000ffffffff02202cb206000000001976a9148280b37df378db99f66f85c95a783a76ac7a6d5988ac9093510d000000001976a9143bde42dbee7e4dbe6a21b2d50ce2f0167faa815988ac11000000'))[1],1, 1, 600000000, bytes.fromhex("00141d0f172a0ecb48aee1be1f2687d2963ae33f71a1"))== b'\xc3z\xf3\x11\x16\xd1\xb2|\xafh\xaa\xe9\xe3\xac\x82\xf1Gy)\x01M[\x91vW\xd0\xebIG\x8c\xb6p',

    el.witness_digest(el.getTransaction(bytes.fromhex('0100000001db6b1b20aa0fd7b23880be2ecbd4a98130974cf4748fb66092ac4d3ceb1a54770100000000feffffff02b8b4eb0b000000001976a914a457b684d7f0d539a46a45bbc043f35b59d0d96388ac0008af2f000000001976a914fd270b1ee6abcaea97fea7ad0402e8bd8ad6d77c88ac92040000'))[1],1, 0, 1000000000, bytes.fromhex('001479091972186c449eb1ded22b78e40d009bdf0089')) == b'd\xf3\xb0\xf4\xdd+\xb3\xaa\x1c\xe8Vm"\x0c\xc7M\xda\x9d\xf9}\x84\x90\xcc\x81\xd8\x9ds\\\x92\xe5\x9f\xb6',
    
    el.witness_digest(el.getTransaction(bytes.fromhex('0100000002fe3dc9208094f3ffd12645477b3dc56f60ec4fa8e6f5d67c565d1c6b9216b36e0000000000ffffffff0815cf020f013ed6cf91d29f4202e8a58726b1ac6c79da47c23d1bee0a6925f80000000000ffffffff0100f2052a010000001976a914a30741f8145e5acadf23f751864167f32e0963f788ac00000000'))[1],3, 1, 4900000000, bytes.fromhex('00205d1b56b63d714eebe542309525f484b7e9d6f686b3781b6f61ef925d66d6f6a0'), bytes.fromhex('21026dccc749adc2a9d0d89497ac511f760f45c47dc5ed9cf352a58ac706453880aeadab210255a9626aebf5e29c0e6538428ba0d1dcf6ca98ffdf086aa8ced5e0d0215ea465ac'), 35) == b'\xfe\xf7\xbdt\x9c\xceq\x0c\\\x05+\xd7\x96\xdf\x1a\xf0\xd95\xe5\x9c\xeacsbh\xbc\xbe-!4\xfcG'
]


