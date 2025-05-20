// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SID {
    // Mappatura da indirizzo a ID (stringa)
    mapping(address => string) private ids;

    // Evento emesso al momento della registrazione
    event Registered(address indexed user, string id);

    // Registrazione di un ID (solo una volta per indirizzo)
    function register(string memory _id) external {
        require(bytes(ids[msg.sender]).length == 0, "ID gia' registrato");
        ids[msg.sender] = _id;
        emit Registered(msg.sender, _id);
    }

    // Ottieni l'ID associato a un indirizzo
    function getID(address _user) external view returns (string memory) {
        return ids[_user];
    }

    // Verifica se un indirizzo ha registrato un certo ID
    function verify(address _user, string memory _id) external view returns (bool) {
        return keccak256(bytes(ids[_user])) == keccak256(bytes(_id));
    }
}
