# Standalone version simple electrum client.
# compatible: Electrum==3.3.8

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
wallet_path = os.path.join(wallet_dir, "wallet_lib2")
if not os.path.exists(wallet_path):
    create_new_wallet(path=wallet_path, segwit=True)

# open wallet
storage = WalletStorage(wallet_path)
wallet = Wallet(storage)
wallet.start_network(network)
# daemon.add_wallet(wallet)

# set up commands
commands = Commands(config, wallet=wallet, network=network)

def create_func(key):
    def f(*args):
        return commands._run(key, args, lambda: "")
    return f

command_set = {}

for k in known_commands.keys():
    command_set[k] = create_func(k)

import elm_nosig
import elm_sig

# do whatever you want