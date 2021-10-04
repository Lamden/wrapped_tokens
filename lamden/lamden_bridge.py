def lamden_bridge():
    import currency

    nonces = Hash(default_value=0)
    proofs = Hash()

    owner = Variable()
    token_address = Variable()
    token_decimals = Variable()

    HEX_BYTES = 64

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

        int(a, 16)  # Throws error if not hex string

        return left_pad(a)

    def pack_int(i):
        i = int(i)
        h = hex(i)[2:]
        return left_pad(h)

    @construct
    def seed(contract_address='0x0', decimals=18):
        owner.set(ctx.caller)
        token_address.set(contract_address)
        token_decimals.set(decimals)


    @export
    def deposit(amount: float, ethereum_address: str):
        currency.transfer_from(amount=amount, to=ctx.this, main_account=ctx.caller)

        packed_token = pack_eth_address(token_address.get())
        packed_amount = pack_amount(amount, token_decimals.get())
        packed_nonce = pack_int(nonces[ethereum_address] + 1)
        packed_address = pack_eth_address(ethereum_address)

        nonces[ethereum_address] += 1

        abi = packed_token + packed_amount + packed_nonce + packed_address

        _hash = hashlib.sha3(abi)


    @export
    def withdraw(amount: float, to: str)
        assert ctx.caller == owner.get(), 'Only the owner can call!'
        currency.transfer(amount=amount, to=to)


    @export
    def post_proof(hashed_abi, signed_abi):
        assert ctx.caller == owner.get(), 'Only owner can call!'
        proofs[hashed_abi] = signed_abi
