from web3 import Web3
from eth_account.account import Account

from eth_account.messages import encode_defunct

private_key = bytes.fromhex('c0878732e5e71459cf2730973866f02b2f8934babce27dfe36918f4580fdeb66')

message = encode_defunct(text='test')

a = Account.privateKeyToAccount(private_key=private_key)
a.sign_message(message)

print(message)

w = Web3()

signed_message = w3.eth.account.sign_message('test', private_key)