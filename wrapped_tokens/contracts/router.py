supported_tokens = Hash()
owner = Variable()

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

@construct
def seed():
    owner.set(ctx.caller)


def unpack_uint256(uint, decimals):
    i = int(uint, 16)
    reduced_i = i / (10 ** decimals)
    return reduced_i

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
def burn():
    pass

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
