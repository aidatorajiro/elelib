# Standalone version simple electrum client.
# compatible: Electrum==3.3.8. please download it from official releases.

# Please set log address and texts you want to upload
log_address = "tb1..."

text_to_upload = set(open("texts.txt").read().split('\n'))

import os
import sys
import asyncio
import time

from electrum.simple_config import SimpleConfig
from electrum import constants
from electrum.daemon import Daemon
from electrum.storage import WalletStorage
from electrum.wallet import Wallet, create_new_wallet
from electrum.commands import Commands, known_commands
from electrum.network import filter_protocol, Network
from electrum.util import create_and_start_event_loop, log_exceptions
from electrum.simple_config import SimpleConfig

# use ~/.electrum/testnet as datadir
config = SimpleConfig({"testnet": True, "fee_per_kb": 10000, "dynamic_fees": False})

# set testnet magic bytes
constants.set_testnet()

# set up daemon
daemon = Daemon(config, listen_jsonrpc=False)
network = daemon.network

# get wallet on disk
wallet_dir = os.path.dirname(config.get_wallet_path())
print("Wallet dir: "+ wallet_dir)
wallet_path = os.path.join(wallet_dir, "wallet_lib")
if not os.path.exists(wallet_path):
    create_new_wallet(path=wallet_path, segwit=True)

# open wallet
storage = WalletStorage(wallet_path)
wallet = Wallet(storage)
wallet.start_network(network)

# set up commands
commands = Commands(config, wallet=wallet, network=network)

def create_func(key):
    def f(*args):
        return commands._run(key, args, lambda: "")
    return f

command_set = {}

for k in known_commands.keys():
    command_set[k] = create_func(k)

import elm
import el

getaddresshistory = command_set['getaddresshistory']
gettransaction = command_set['gettransaction']
getbalance = command_set['getbalance']

import random

def wait_until_confirmed():
    while "unconfirmed" in getbalance():
        print("wait until confirm: " + str(getbalance()))
        time.sleep(10)

# wait_until_confirmed()

for text in text_to_upload:
    time.sleep(10)
    print(getbalance())
    
    data_uploaded = set()
    
    history = getaddresshistory(log_address)
    for h in history:
        txid = h['tx_hash']
        tx = gettransaction(txid)
        (_, tx_parsed) = el.getTransaction(bytes.fromhex(tx['hex']))
        try:
            data = elm.elm_getdata(tx_parsed)
            data_uploaded.add(data)
        except Exception as e:
            print("Parse Error: " + str(e))
    
    if text.encode() in data_uploaded:
        continue

    print(text)

    current_target = text
    
    try:
        elm.elm_sig(command_set, current_target, log_address)
    except Exception as e:
        print(e)

print("finished!")
