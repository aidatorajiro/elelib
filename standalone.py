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
config = SimpleConfig({"testnet": True, "fee_per_kb": 1000, "dynamic_fees": False})

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

command_set = {}

def funcgen(key):
    def func(*args, **kwargs):
        return commands._run(key, args, wallet_path=wallet_path, **kwargs)
    return func

for key in known_commands.keys():
    command_set[key] = funcgen(key)

import elm_nosig

print((command_set['createnewaddress'])())
# print(commands._run('createnewaddress', [], wallet_path=wallet_path))

#@log_exceptions
#async def f():

#    print(commands.__dict__)

    # print(await commands.getbalance(wallet_path=wallet_path))

    # print(await commands.createnewaddress(wallet_path=wallet_path))

    # print(await commands.getunusedaddress(wallet_path=wallet_path))

    # tx = await commands.payto("????", 0.00000001, wallet_path=wallet_path)

    # print(await commands.broadcast(tx))

#asyncio.run_coroutine_threadsafe(f(), loop)