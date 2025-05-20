const { Web3 } = require('web3');
const web3 = new Web3('http://127.0.0.1:7545');

const contractAddress = '0xd99F05A7Db6b2C8dAddd2Cf1B3C74cac6E9bf979';
const abi = [
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "user",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "id",
				"type": "string"
			}
		],
		"name": "Registered",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_user",
				"type": "address"
			}
		],
		"name": "getID",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_id",
				"type": "string"
			}
		],
		"name": "register",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_user",
				"type": "address"
			},
			{
				"internalType": "string",
				"name": "_id",
				"type": "string"
			}
		],
		"name": "verify",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]

async function interactWithContract() {
  const accounts = await web3.eth.getAccounts();
  const fromAccount = accounts[0];
  const contract = new web3.eth.Contract(abi, contractAddress);

  const myID = "user123"; // ID scelto liberamente

  // Chiamata alla funzione register
  await contract.methods.register(myID).send({ from: fromAccount });
  console.log("✅ ID registrato:", myID);

  // Ottieni l'ID associato
  const storedID = await contract.methods.getID(fromAccount).call();
  console.log("🔎 ID salvato nel contratto:", storedID);

  // Verifica se corrisponde
  const isCorrect = await contract.methods.verify(fromAccount, myID).call();
  console.log("✅ Verifica riuscita?", isCorrect);
}

interactWithContract().catch(console.error);