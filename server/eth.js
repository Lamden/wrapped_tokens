// @ts-check
const Web3 = require('web3');
const Lamden = require('lamden-js');

const abi = require('./abi/clearinghouse.json')
const conf = require('./conf.json');

const web3 = new Web3(conf.eth.network);
const ETH_CONTRACT_ADDRESS = conf.eth.contract_address;
const LAMDEN_CONTRACT_NAME = conf.lamden.contract;
const LAMDEN_NETWORK_INFO = conf.lamden.network;

async function mintTokens(tokenAddress, receiver, amount) {
    const { vk, sk } = conf.lamden.wallet;
    const txInfo = {
        senderVk: vk,
        contractName: LAMDEN_CONTRACT_NAME,
        methodName: "mint",
        kwargs: {
            ethereum_contract: tokenAddress,
            amount: amount,
            lamden_wallet: receiver
        },
        stampLimit: 65,
    }
    console.log('tx', txInfo);
    const tx = new Lamden.TransactionBuilder(LAMDEN_NETWORK_INFO, txInfo)
    const r = await tx.send(sk)
    console.log(r);
    return tx.checkForTransactionResult()
}


async function ethEventListener(){
    console.log(ETH_CONTRACT_ADDRESS)
    const contract = new web3.eth.Contract(abi, ETH_CONTRACT_ADDRESS);
    contract.events.TokensWrapped()
    .on('data', async (event) => {
        console.log(event.returnValues)
        const { token, receiver, amount } = event.returnValues;
        const res = await mintTokens(token, receiver, '0x' + web3.utils.toBN(amount).toString('hex'));
        console.log(res);
    })
    .on('error', console.error);
}

ethEventListener()