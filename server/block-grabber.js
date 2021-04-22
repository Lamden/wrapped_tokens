const axios = require('axios').default;
const axiosRetry = require('axios-retry');

axiosRetry(axios, {
    retries: 3, // number of retries
    retryDelay: (retryCount) => {
        console.log(`retry attempt: ${retryCount}`);
        return 1000; // time interval between retries
    },
});

const baseURL = 'https://testnet-master-1.lamden.io'

async function getLatestBlockNumber() {
    try {
        const { data } = await axios.get(`${baseURL}/latest_block_num`)
        if (!data || !data.latest_block_number) {
            throw new Error('Value is empty');
        }
        return data.latest_block_number;
    } catch (error) {
        throw new Error('Something went wrong');
    }
}

async function getBlockDetails(blockNo) {
    try {
        const { data } = await axios.get(`${baseURL}/blocks?num=${blockNo}`)
        if (!data) {
            throw new Error('Block not recieved');
        }
        return data;
    } catch (error) {
        throw new Error('Something went wrong');
    }
}


module.exports = {
    getLatestBlockNumber,
    getBlockDetails
}