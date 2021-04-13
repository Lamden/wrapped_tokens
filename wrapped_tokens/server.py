import asyncio
from web3 import Web3, HTTPProvider
import json

import ssl
from sanic import Sanic
from sanic import response

# 1 = mainnet, 42 = kovan
ETH_NETWORK_CODE = 42
ETH_NETWORK_STR = 'mainnet' if ETH_NETWORK_CODE == 1 else 'kovan'

CLEARING_HOUSE_ADDRESS = '0x0'
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

        self.event_filter = self.clearinghouse.events.TokensWrapped.createFilter(fromBlock='latest')

        self.is_running = False

    async def serve(self):
        self.is_running = True

        while self.is_running:
            for event in self.event_filter.get_new_entries():
                handle_event(event)
            await asyncio.sleep(0)

    def stop(self):
        self.is_running = False

    def mint_tokens(self):
        pass


class WebServer:
    def __init__(self, port=8080, ssl_port=443, ssl_enabled=False,
                 ssl_cert_file='~/.ssh/server.csr',
                 ssl_key_file='~/.ssh/server.key',
                 debug=True, access_log=False,
                 ):

        # Setup base Sanic class and CORS
        self.app = Sanic(__name__)
        self.app.config.update({
            'REQUEST_MAX_SIZE': 10000,
            'REQUEST_TIMEOUT': 5
        })
        #self.cors = CORS(self.app, automatic_options=True)

        self.static_headers = {}

        self.port = port

        self.ssl_port = ssl_port
        self.ssl_enabled = ssl_enabled
        self.context = None

        # Create the SSL Context if needed
        if self.ssl_enabled:
            self.context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
            self.context.load_cert_chain(ssl_cert_file, keyfile=ssl_key_file)

        # Store other Sanic constants for when server starts
        self.debug = debug
        self.access_log = access_log

        # Main controller class
        self.controller = EventListener()

        # Add Routes
        self.app.add_route(self.start_swap, '/start', methods=['POST'])
        self.app.add_route(self.lookup_uuid, '/lookup', methods=['GET'])

    async def start(self):
        # Start server with SSL enabled or not
        asyncio.ensure_future(self.controller.serve())
        await self.app.create_server(
            host='0.0.0.0',
            port=self.port,
            debug=self.debug,
            access_log=self.access_log,
            return_asyncio_server=True)

    @staticmethod
    def valid_eth_address(address):
        if len(address) != 42:
            return False

        if address[:2] != '0x':
            return False

        try:
            int(address, 16)
        except ValueError:
            return False

        return True

    @staticmethod
    def valid_lamden_address(address):
        if len(address) != 64:
            return False

        try:
            int(address, 16)
        except:
            return False

        return True

    async def burn(self, request):
        ethereum_contract = request.args.get('ethereum_contract')
        ethereum_address = request.args.get('ethereum_address')
        lamden_address = request.args.get('lamden_address')
        amount = request.args.get('amount')

        return response.json(res, status=200)
