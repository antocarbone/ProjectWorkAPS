// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SIDSmartContract {
    address private owner;

    struct SIDInfo {
        string publicKey;
        string uid;
        bool isValid;
    }

    mapping(uint128 => SIDInfo) public sids;

    mapping(uint128 => bool) public isSIDRegistered;

    event SIDRegistered(uint128 indexed sid, string publicKey, string uid, bool isValid);
    event SIDModified(uint128 indexed sid, string newPublicKey, string newUid, bool newIsValid);

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
     * @param _publicKey The public key associated with the SID.
     * @param _uid The string identifier (e.g. username or university id).
     * @param _isValid Initial validity status of the SID.
     */
    function registraSid(
        uint128 _sid,
        string memory _publicKey,
        string memory _uid,
        bool _isValid
    ) external onlyOwner {
        require(!isSIDRegistered[_sid], "SID is already registered.");
        sids[_sid] = SIDInfo({
            publicKey: _publicKey,
            uid: _uid,
            isValid: _isValid
        });
        isSIDRegistered[_sid] = true;
        emit SIDRegistered(_sid, _publicKey, _uid, _isValid);
    }

    /**
     * @dev Allows the university owner to modify an existing SID's information.
     * @param _sid The unique identifier for the student (uint128).
     * @param _newPublicKey The new public key to associate with the SID.
     * @param _newUid The new string identifier (uid).
     * @param _newIsValid The new validity status for the SID.
     */
    function modificaSid(
        uint128 _sid,
        string memory _newPublicKey,
        string memory _newUid,
        bool _newIsValid
    ) external onlyOwner {
        require(isSIDRegistered[_sid], "SID is not registered.");
        SIDInfo storage sidToModify = sids[_sid];
        sidToModify.publicKey = _newPublicKey;
        sidToModify.uid = _newUid;
        sidToModify.isValid = _newIsValid;
        emit SIDModified(_sid, _newPublicKey, _newUid, _newIsValid);
    }

    /**
     * @dev Allows to obtain information about a given SID.
     * This method is typically invoked by the `SmartContractAuthority`.
     * @param _sid The unique identifier for the student (uint128).
     * @return publicKey The public key associated with the SID.
     * @return uid The string UID associated with the SID.
     * @return isValid The validity status of the SID.
     */
    function getInfoSid(
        uint128 _sid
    ) external view returns (string memory publicKey, string memory uid, bool isValid) {
        require(isSIDRegistered[_sid], "SID is not registered.");
        SIDInfo storage sidInfo = sids[_sid];
        return (sidInfo.publicKey, sidInfo.uid, sidInfo.isValid);
    }
}
