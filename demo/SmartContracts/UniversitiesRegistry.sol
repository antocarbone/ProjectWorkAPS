// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SmartContractAuthority {
    address private owner;

    struct UniversityInfo {
        uint256 uid;
        string publicKey;
        bool isRevoked;
        address sidContractAddress;
        address cidContractAddress;
    }

    mapping(uint256 => UniversityInfo) public universities;
    mapping(uint256 => bool) public isUniversityRegistered;

    event UniversityRegistered(uint256 indexed uid, string publicKey, address sidContract, address cidContract);
    event UniversityInfoModified(uint256 indexed uid, string newPublicKey, bool newIsRevoked, address newSidContract, address newCidContract);
    event UniversityRevokeStatusChanged(uint256 indexed uid, bool newIsRevoked);

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the Smart Contract Authority can perform this action.");
        _;
    }

    function registraUniversita(
        uint256 _uid,
        string memory _publicKey,
        bool _isRevoked,
        address _sidContractAddress,
        address _cidContractAddress
    ) external onlyOwner {
        require(!isUniversityRegistered[_uid], "University with this UID is already registered.");
        universities[_uid] = UniversityInfo({
            uid: _uid,
            publicKey: _publicKey,
            isRevoked: _isRevoked,
            sidContractAddress: _sidContractAddress,
            cidContractAddress: _cidContractAddress
        });
        isUniversityRegistered[_uid] = true;
        emit UniversityRegistered(_uid, _publicKey, _sidContractAddress, _cidContractAddress);
    }

    function modificaInfoUniversita(
        uint256 _uid,
        string memory _newPublicKey,
        bool _newIsRevoked,
        address _newSidContractAddress,
        address _newCidContractAddress
    ) external onlyOwner {
        require(isUniversityRegistered[_uid], "University with this UID is not registered.");
        UniversityInfo storage uni = universities[_uid];
        uni.publicKey = _newPublicKey;
        uni.isRevoked = _newIsRevoked;
        uni.sidContractAddress = _newSidContractAddress;
        uni.cidContractAddress = _newCidContractAddress;
        emit UniversityInfoModified(_uid, _newPublicKey, _newIsRevoked, _newSidContractAddress, _newCidContractAddress);
    }

    function setRevokeStatusUniversita(
        uint256 _uid,
        bool _newIsRevoked
    ) external onlyOwner {
        require(isUniversityRegistered[_uid], "University with this UID is not registered.");
        universities[_uid].isRevoked = _newIsRevoked;
        emit UniversityRevokeStatusChanged(_uid, _newIsRevoked);
    }

    function getUniversityInfo(
        uint256 _uid
    ) external view returns (string memory publicKey, bool isRevoked, address sidContractAddress, address cidContractAddress) {
        require(isUniversityRegistered[_uid], "University with this UID is not registered.");
        UniversityInfo storage uni = universities[_uid];
        return (uni.publicKey, uni.isRevoked, uni.sidContractAddress, uni.cidContractAddress);
    }

    /**
     * @dev Verifica un SID registrato da un'università accreditata.
     * @param _uid L'identificativo della università.
     * @param _sid Il SID dello studente (uint128).
     * @return publicKey La chiave pubblica associata.
     * @return uid L'identificativo testuale dello studente.
     * @return isValid Lo stato di validità.
     */
    function verificaSid(
        uint256 _uid,
        uint128 _sid
    ) external view returns (string memory publicKey, string memory uid, bool isValid) {
        require(isUniversityRegistered[_uid], "University with this UID is not registered.");
        UniversityInfo storage uni = universities[_uid];
        require(!uni.isRevoked, "University is revoked.");

        (publicKey, uid, isValid) = ISIDSmartContract(uni.sidContractAddress).getInfoSid(_sid);
        return (publicKey, uid, isValid);
    }

    /**
     * @dev Verifica la validità di un CID registrato da un'università.
     * @param _uid L'identificativo dell'università.
     * @param _cid Il CID (ora uint256).
     * @return isValid Stato di validità.
     */
    function verificaCid(
        uint256 _uid,
        uint256 _cid
    ) external view returns (bool isValid) {
        require(isUniversityRegistered[_uid], "University with this UID is not registered.");
        UniversityInfo storage uni = universities[_uid];
        require(!uni.isRevoked, "University is revoked.");

        isValid = ICIDSmartContract(uni.cidContractAddress).getInfoCid(_cid);
        return isValid;
    }
}

interface ISIDSmartContract {
    function getInfoSid(uint128 sid) external view returns (string memory publicKey, string memory uid, bool isValid);
}

interface ICIDSmartContract {
    function getInfoCid(uint256 cid) external view returns (bool isValid);
}
