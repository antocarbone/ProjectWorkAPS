// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SmartContractAuthority {
    address private owner;

    struct UniversityInfo {
        string uid;
        bytes pub_key_modulus;
        bytes pub_key_exponent;
        bool isRevoked;
        address sidContractAddress;
        address cidContractAddress;
    }

    mapping(string => UniversityInfo) public universities;
    mapping(string => bool) public isUniversityRegistered;

    event UniversityRegistered(
        string indexed uid,
        bytes pub_key_modulus,
        bytes pub_key_exponent,
        address sidContract,
        address cidContract
    );

    event UniversityInfoModified(
        string indexed uid,
        bytes new_pub_key_modulus,
        bytes new_pub_key_exponent,
        bool newIsRevoked,
        address newSidContract,
        address newCidContract
    );

    event UniversityRevokeStatusChanged(string indexed uid, bool newIsRevoked);

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the Smart Contract Authority can perform this action.");
        _;
    }

    function registraUniversita(
        string memory _uid,
        bytes memory _pub_key_modulus,
        bytes memory _pub_key_exponent,
        bool _isRevoked,
        address _sidContractAddress,
        address _cidContractAddress
    ) external onlyOwner {
        require(!isUniversityRegistered[_uid], "University with this UID is already registered.");
        universities[_uid] = UniversityInfo({
            uid: _uid,
            pub_key_modulus: _pub_key_modulus,
            pub_key_exponent: _pub_key_exponent,
            isRevoked: _isRevoked,
            sidContractAddress: _sidContractAddress,
            cidContractAddress: _cidContractAddress
        });
        isUniversityRegistered[_uid] = true;
        emit UniversityRegistered(_uid, _pub_key_modulus, _pub_key_exponent, _sidContractAddress, _cidContractAddress);
    }

    function modificaInfoUniversita(
        string memory _uid,
        bytes memory _new_pub_key_modulus,
        bytes memory _new_pub_key_exponent,
        bool _newIsRevoked,
        address _newSidContractAddress,
        address _newCidContractAddress
    ) external onlyOwner {
        require(isUniversityRegistered[_uid], "University with this UID is not registered.");
        UniversityInfo storage uni = universities[_uid];
        uni.pub_key_modulus = _new_pub_key_modulus;
        uni.pub_key_exponent = _new_pub_key_exponent;
        uni.isRevoked = _newIsRevoked;
        uni.sidContractAddress = _newSidContractAddress;
        uni.cidContractAddress = _newCidContractAddress;
        emit UniversityInfoModified(_uid, _new_pub_key_modulus, _new_pub_key_exponent, _newIsRevoked, _newSidContractAddress, _newCidContractAddress);
    }

    function setRevokeStatusUniversita(
        string memory _uid,
        bool _newIsRevoked
    ) external onlyOwner {
        require(isUniversityRegistered[_uid], "University with this UID is not registered.");
        universities[_uid].isRevoked = _newIsRevoked;
        emit UniversityRevokeStatusChanged(_uid, _newIsRevoked);
    }

    function getUniversityInfo(
        string memory _uid
    ) external view returns (
        bytes memory pub_key_modulus,
        bytes memory pub_key_exponent,
        bool isRevoked,
        address sidContractAddress,
        address cidContractAddress
    ) {
        require(isUniversityRegistered[_uid], "University with this UID is not registered.");
        UniversityInfo storage uni = universities[_uid];
        return (
            uni.pub_key_modulus,
            uni.pub_key_exponent,
            uni.isRevoked,
            uni.sidContractAddress,
            uni.cidContractAddress
        );
    }

    function verificaSid(
        string memory _uid,
        uint128 _sid
    ) external view returns (
        bytes memory pub_key_modulus,
        bytes memory pub_key_exponent,
        bool isValid
    ) {
        require(isUniversityRegistered[_uid], "University with this UID is not registered.");
        UniversityInfo storage uni = universities[_uid];
        require(!uni.isRevoked, "University is revoked.");

        (pub_key_modulus, pub_key_exponent, isValid) =
            ISIDSmartContract(uni.sidContractAddress).getInfoSid(_sid);

        return (pub_key_modulus, pub_key_exponent, isValid);
    }

    function verificaCid(
        string memory _uid,
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
    function getInfoSid(
        uint128 sid
    ) external view returns (
        bytes memory pub_key_modulus,
        bytes memory pub_key_exponent,
        bool isValid
    );
}

interface ICIDSmartContract {
    function getInfoCid(uint256 cid) external view returns (bool isValid);
}
