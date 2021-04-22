const Lamden = require('lamden-js');
const Web3 = require('web3');
const axios = require('axios').default;

const low = require('lowdb');
const FileSync = require('lowdb/adapters/FileSync');

const abi = require('./abi/clearinghouse.json')
const conf = require('./conf.json');

const web3 = new Web3(conf.eth.network);


const grabber = require('./block-grabber');


const LAMDEN_CONTRACT_NAME = conf.lamden.contract;
const LAMDEN_NETWORK_INFO = conf.lamden.network;

const lamdenWallet = Lamden.wallet.create_wallet({ sk: conf.lamden.wallet.sk })
const network = new Lamden.Network(LAMDEN_NETWORK_INFO)

function setupDatabse() {     
    // @ts-ignore
    const adapter = new FileSync('./db/db.json');
    const db = low(adapter)
    const lamden_block = db.getState().lastChecked;
    if (!lamden_block) {
        db.defaults({
            "lamden_block": 21327
        }).write()
    }
    return db;
}

function sign(data) {
    // @ts-ignore
    data = web3.utils.soliditySha3('0x' + data);
    return web3.eth.accounts.sign(data, conf.eth.privKey)
}

async function checkBlock(blockNo) {
    const block = await grabber.getBlockDetails(blockNo);
    if (block.subblocks && block.subblocks !== "undefined") {
        for (const sb of block.subblocks) {
            for (const tx of sb.transactions) {
                if (tx.transaction.payload.contract === LAMDEN_CONTRACT_NAME) {
                    if (!tx.result.startsWith('AssertionError(') && tx.status === 0) {
                        if (tx.transaction.payload.function === 'burn') {
                            return tx.result.substring(1, tx.result.length-1)
                        }
                    }
                }
            }
        }
    }
    return 'Not Found';
}

async function submitProof(hashed_abi, signed_abi) {
    const { vk, sk } = lamdenWallet;
    const txInfo = {
        senderVk: vk,
        contractName: LAMDEN_CONTRACT_NAME,
        methodName: "post_proof",
        kwargs: {
            hashed_abi,
            signed_abi 
        },
        stampLimit: 65,
    }
    const tx = new Lamden.TransactionBuilder(LAMDEN_NETWORK_INFO, txInfo)
    await tx.send(sk)
    return tx.checkForTransactionResult()
}

async function main(db) {
    const latestBlock = await grabber.getLatestBlockNumber(); 
    const lastCheckedBlock = db.get('lamden_block').value();
    console.log('Last Block Checked: ', lastCheckedBlock);
    console.log('Latest Block Number: ', latestBlock);

    for (let blockNo = lastCheckedBlock + 1; blockNo <= latestBlock; blockNo++) {
        console.log('Checking: ', blockNo)
        const unSignedABI = await checkBlock(blockNo);
        if (unSignedABI !== 'Not Found') {
            try {
                console.log(unSignedABI)
                let signedABIObj = sign(unSignedABI);
                console.log(signedABIObj)
                const signedABI = signedABIObj.signature;
                const r = await submitProof(unSignedABI, signedABI);

                if (r && r.result && !r.result.startsWith('AssertionError(') && r.status === 0) {
                    console.log('Submitted Sucessfully')
                    db.set('lamden_block', blockNo).write();
                } else {
                    console.log('Ops! There was an error')
                    console.log(r)
                }
            } catch (error) {
                console.log(error)                
            }
        } else {
            db.set('lamden_block', blockNo).write();
        }
    }
}



function wait(timeout=1000) {

    return new Promise((resolve, reject) => {
        setTimeout(resolve, timeout);
    });
}

async function start_process(db) {
    while (true) {
        await wait(1000);
        await main(db)
    }    
}


network.events.on('online', async (online) => { 
    const db = setupDatabse();
    if (online) {
        await start_process(db)
    } else {
        throw new Error('Not Online')
    }
});

network.ping()