// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SIDSmartContract {
    address private owner;

    struct SIDInfo {
        bytes pub_key_modulus;
        bytes pub_key_exponent;
        bool isValid;
    }

    mapping(uint128 => SIDInfo) public sids;
    mapping(uint128 => bool) public isSIDRegistered;

    event SIDRegistered(
        uint128 indexed sid,
        bytes pub_key_modulus,
        bytes pub_key_exponent,
        bool isValid
    );
    
    event SIDModified(
        uint128 indexed sid,
        bytes new_pub_key_modulus,
        bytes new_pub_key_exponent,
        bool newIsValid
    );

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the university owner of this contract can perform this action.");
        _;
    }

    /**
     * @dev Allows the university owner to register a new SID.
     * @param _sid The unique identifier for the student (uint128).
     * @param _pub_key_modulus The RSA public key modulus (bytes).
     * @param _pub_key_exponent The RSA public key exponent (bytes).
     * @param _isValid Initial validity status of the SID.
     */
    function registraSid(
        uint128 _sid,
        bytes memory _pub_key_modulus,
        bytes memory _pub_key_exponent,
        bool _isValid
    ) external onlyOwner {
        require(!isSIDRegistered[_sid], "SID is already registered.");
        sids[_sid] = SIDInfo({
            pub_key_modulus: _pub_key_modulus,
            pub_key_exponent: _pub_key_exponent,
            isValid: _isValid
        });
        isSIDRegistered[_sid] = true;
        emit SIDRegistered(_sid, _pub_key_modulus, _pub_key_exponent, _isValid);
    }

    /**
     * @dev Allows the university owner to modify an existing SID's information.
     * @param _sid The unique identifier for the student (uint128).
     * @param _new_pub_key_modulus The new RSA public key modulus (bytes).
     * @param _new_pub_key_exponent The new RSA public key exponent (bytes).
     * @param _newIsValid The new validity status for the SID.
     */
    function modificaSid(
        uint128 _sid,
        bytes memory _new_pub_key_modulus,
        bytes memory _new_pub_key_exponent,
        bool _newIsValid
    ) external onlyOwner {
        require(isSIDRegistered[_sid], "SID is not registered.");
        SIDInfo storage sidToModify = sids[_sid];
        sidToModify.pub_key_modulus = _new_pub_key_modulus;
        sidToModify.pub_key_exponent = _new_pub_key_exponent;
        sidToModify.isValid = _newIsValid;
        emit SIDModified(_sid, _new_pub_key_modulus, _new_pub_key_exponent, _newIsValid);
    }

    /**
     * @dev Allows to obtain information about a given SID.
     * @param _sid The unique identifier for the student (uint128).
     * @return pub_key_modulus The RSA modulus.
     * @return pub_key_exponent The RSA exponent.
     * @return isValid The validity status of the SID.
     */
    function getInfoSid(
        uint128 _sid
    ) external view returns (
        bytes memory pub_key_modulus,
        bytes memory pub_key_exponent,
        bool isValid
    ) {
        require(isSIDRegistered[_sid], "SID is not registered.");
        SIDInfo storage sidInfo = sids[_sid];
        return (
            sidInfo.pub_key_modulus,
            sidInfo.pub_key_exponent,
            sidInfo.isValid
        );
    }
}
