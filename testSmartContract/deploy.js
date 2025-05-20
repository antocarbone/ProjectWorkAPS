const { Web3 } = require('web3');
const fs = require('fs');
const path = require('path');

// Connect to Ganache
const web3 = new Web3('http://127.0.0.1:7545');

async function deploy() {
    // Load ABI and Bytecode
    const abiPath = path.join(__dirname, 'SID_ABI.json');
    const bytecodePath = path.join(__dirname, 'SID_Bytecode.bin');
    const abi = JSON.parse(fs.readFileSync(abiPath, 'utf8'));
    const bytecode = fs.readFileSync(bytecodePath, 'utf8');

    // Get Ganache accounts
    const accounts = await web3.eth.getAccounts();
    
    const deployerAccount = accounts[0]; // Use the first account for deployment

    console.log("Deploying contract from account:", deployerAccount);

    // Create a contract instance
    const contract = new web3.eth.Contract(abi);

    // Deploy the contract
    const deployedContract = await contract.deploy({ data: '0x' + bytecode })
        .send({ from: deployerAccount, gas: 1500000, gasPrice: '30000000000' });

    console.log("Contract deployed at address:", deployedContract.options.address);
}

deploy().catch(err => console.error("Deployment failed:", err));
