# wrapped_tokens
Working repo for wrapped ERC20 -> Lamden token facilities

## General Workflow / Userflow

### Ethereum -> Lamden
1. User initiates a `deposit` on the Ethereum side. They supply the token and the amount to deposit.
  * This calls `transferFrom` the caller and stores the token inside the Ethereum custodian.
  * An Ethereum event is then emitted on the blockchain.
2. The Ethereum event is picked up by a web monitor. This web monitor has the operator keys for the Ethereum and Lamden smart contracts.
  * The token address, token amount, and Lamden public key is parsed from the event.
  * A transaction is issued on a Lamden contract that mints a new token associated with the ERC20 token deposited to the Lamden public key provided.
3. Workflow over.

### Lamden -> Ethereum
1. User initiates a `burn` transaction on the Lamden side. This transfers tokens from the user to the operator and destroys them.
2. The smart contract returns the Ethereum ABI that needs to be signed.
3. The operator listens for this response, and then signs the ABI with it's Ethereum signing key.
4. The operator then submits a transaction to the Lamden side which stores the signature on chain.
5. The user sees this signature on chain, takes it, and uses it as the arguments for the Ethereum `withdraw` function.
  * The withdraw function unpacks the arguments and validates the sender is correct and the nonce is correct.
  * It also cryptographically validates that the operator signed the payload and not someone else.
  * If this is correct, the amount of tokens in the signature is issued to the sender.

### Adding support for tokens
1. A user deploys a wrapped version of a token on Lamden. It must adhere to the smart contract specifications.
2. The user calls `add_token` on the Lamden `router.py` contract with the corresponding arguments. This then creates a logical link between an Ethereum address that is emitted on the blockchain and a Lamden smart contract that conforms to the standard provided.
  * They provide the name of the contract they made. It is checked for adherence to the protocol.
  * Right now, the contract expects the operator to be the only one adding tokens. This is because there is no way to manage if people sabotage tokens with bad smart contracts somehow.
  * Assuming everything is good, the link is made. The address has to be whitelabeled on the Ethereum side by calling the correct function.
