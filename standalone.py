# Standalone version simple electrum client.

import os
import sys
import asyncio

from electrum.simple_config import SimpleConfig
from electrum import constants
from electrum.daemon import Daemon
from electrum.storage import WalletStorage
from electrum.wallet import Wallet, create_new_wallet
from electrum.commands import Commands, known_commands
from electrum.network import filter_protocol, Network
from electrum.util import create_and_start_event_loop, log_exceptions
from electrum.simple_config import SimpleConfig

loop, stopping_fut, loop_thread = create_and_start_event_loop()

# use ~/.electrum/testnet as datadir
config = SimpleConfig({"testnet": True, "fee_per_kb": 5000, "dynamic_fees": False})

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
    create_new_wallet(path=wallet_path, config=config)

# open wallet
storage = WalletStorage(wallet_path)
wallet = Wallet(storage, config=config)
wallet.start_network(network)
daemon.add_wallet(wallet)

# set up commands
commands = Commands(config=config, daemon=daemon, network=network)

def payto(*args):
    return {'hex': commands._run('payto', args, wallet_path=wallet_path)}

def broadcast(*args):
    return commands._run('broadcast', args)

def createnewaddress(*args):
    return commands._run('createnewaddress', args, wallet_path=wallet_path)

def getprivatekeys(*args):
    return commands._run('getprivatekeys', args, wallet_path=wallet_path)

command_set = {
    'payto': payto,
    'broadcast': broadcast,
    'createnewaddress': createnewaddress,
    'getprivatekeys': getprivatekeys
}

import elm_nosig
import elm_sig

print("elm_sig starting....")

elm_sig.elm_sig(command_set, "びっとこいん　めもようし　あどれす　ビットコインメモ用紙アドレス bitcoinメモ用紙アドレス", "tb.......", 20000, 10)

print("elm_sig completed....")