import asyncio
from web3 import Web3, HTTPProvider
import json

# 1 = mainnet, 42 = kovan
ETH_NETWORK_CODE = 42
ETH_NETWORK_STR = 'mainnet' if ETH_NETWORK_CODE == 1 else 'kovan'

CLEARING_HOUSE_ADDRESS = '0x0'
INFURA_KEY = 'abd941592ff140d39dc7af70957aae56'
INFURA_BASE = f'https://{ETH_NETWORK_STR}.infura.io/v3/{INFURA_KEY}'

ABI = json.load('abi.json')


def handle_event(event):
    print(event)
    # and whatever


class EventListener:
    def __init__(self):
        self.client = Web3(HTTPProvider(INFURA_BASE))

        self.clearinghouse = self.client.eth.contract(
            address=CLEARING_HOUSE_ADDRESS,
            abi=ABI
        )

        self.event_filter = self.clearinghouse.events.myEvent.createFilter(fromBlock='latest')

        self.is_running = False

    async def serve(self):
        self.is_running = True

        while self.is_running:
            for event in self.event_filter.get_new_entries():
                handle_event(event)
            await asyncio.sleep(0)

    def stop(self):
        self.is_running = False
