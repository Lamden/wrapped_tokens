balances = Hash(default_value=0)
owner = Variable()

@construct
def seed():
    owner.set("con_clearing_house_62")

@export
def mint(amount: float, to: str):
    assert ctx.caller == owner.get(), f'Only owner can mint! Current owner is {owner.get()}, Caller is {ctx.caller}'
    assert amount > 0, 'Cannot mint negative balances!'
    balances[to] += amount

@export
def transfer(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'

    sender = ctx.caller

    assert balances[sender] >= amount, 'Not enough coins to send!'

    balances[sender] -= amount
    balances[to] += amount

@export
def balance_of(account: str):
    return balances[account]

@export
def allowance(Owner: str, spender: str):
    return balances[Owner, spender]


@export
def approve(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'

    sender = ctx.caller
    balances[sender, to] += amount
    return balances[sender, to]


@export
def transfer_from(amount: float, to: str, main_account: str):
    assert amount > 0, 'Cannot send negative balances!'

    sender = ctx.caller

    assert balances[main_account, sender] >= amount, 'Not enough coins approved to send! You have {} and are trying to spend {}'\
        .format(balances[main_account, sender], amount)
    assert balances[main_account] >= amount, 'Not enough coins to send!'

    balances[main_account, sender] -= amount
    balances[main_account] -= amount

    balances[to] += amount

