I = importlib

# Enforceable interface
token_interface = [
    I.Func('transfer', args=('amount', 'to')),
    I.Func('mint', args=('amount', 'to')),
    I.Func('allowance', args=('owner', 'spender')),
    I.Func('approve', args=('amount', 'to')),
    I.Func('transfer_from', args=('amount', 'to', 'main_account'))
]

sniffer = ForeignVariable(contract='currency', variable='owner')

supported_tokens = Hash()
nonces = Hash(default_value=0)
owner = Variable()

HEX_BYTES = 64

@construct
def seed():
    owner.set(ctx.caller)


def left_pad(s):
    while len(s) < HEX_BYTES:
        s = f'0{s}'

    if len(s) > HEX_BYTES:
        s = s[:HEX_BYTES]

    return s


def unpack_uint256(uint, decimals):
    i = int(uint, 16)
    reduced_i = i / (10 ** decimals)
    return reduced_i


def pack_amount(amount, decimals):
    i = int(amount * (10 ** decimals))
    h = hex(i)[2:]
    return left_pad(h)


def pack_eth_address(address):
    assert address.startswith('0x'), 'Invalid Ethereum prefix'
    a = address[2:]

    assert len(a) == 40, 'Invalid address length'

    int(a, 16) # Throws error if not hex string

    return left_pad(a)


def pack_int(i):
    i = int(i)
    h = hex(i)[2:]
    return left_pad(h)


@export
def mint(ethereum_contract, amount):
    assert ctx.caller == owner.get(), 'Only owner can call!'
    assert supported_tokens[ethereum_contract] is not None, 'Invalid Ethereum Token!'

    decimals = supported_tokens[ethereum_contract, 'decimals']

    assert decimals is not None, 'Unexpected decimal error'

    unpacked_amount = unpack_uint256(amount, decimals)

    token = I.import_module(supported_tokens[ethereum_contract])

    assert I.enforce_interface(token, token_interface), 'Invalid token interface!'

    token.mint(amount=unpacked_amount, to=ctx.caller)


@export
def burn(ethereum_contract, ethereum_address, lamden_address, amount):
    assert ctx.caller == owner.get(), 'Only owner can call!'
    assert supported_tokens[ethereum_contract] is not None, 'Invalid Ethereum Token!'

    token = I.import_module(supported_tokens[ethereum_contract])

    assert I.enforce_interface(token, token_interface), 'Invalid token interface!'

    token.transfer_from(amount=amount, to=ctx.this, main_account=lamden_address)

    packed_token = pack_eth_address(ethereum_contract)
    packed_amount = pack_amount(amount, supported_tokens[ethereum_contract, 'decimals'])
    packed_nonce = pack_int(nonces[ethereum_address] + 1)
    packed_address = pack_eth_address(ethereum_address)

    nonces[ethereum_address] += 1

    return packed_token + packed_amount + packed_nonce + packed_address


@export
def add_token(ethereum_contract, lamden_contract, decimals):
    assert supported_tokens[ethereum_contract] is None, 'Token already supported'
    assert ctx.caller == owner.get(), 'Only owner can call!'

    token = I.import_module(lamden_contract)

    assert I.enforce_interface(token, token_interface), 'Invalid token interface!'

    sniffer.contract = lamden_contract

    assert sniffer.get() == owner.get(), 'Token owner must be the clearinghouse owner.'

    supported_tokens[ethereum_contract] = lamden_contract
    supported_tokens[ethereum_contract, 'decimals'] = decimals
