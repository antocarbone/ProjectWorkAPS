// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CIDSmartContract {
    address private owner;

    mapping(uint256 => bool) public cids;

    mapping(uint256 => bool) public isCIDRegistered;

    event CIDRegistered(uint256 indexed cid, bool isValid);
    event CIDModified(uint256 indexed cid, bool newIsValid);

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the university owner of this contract can perform this action.");
        _;
    }

    /**
     * @dev Allows the university owner to register the CID of a new credential.
     * @param _cid The unique identifier for the credential.
     * @param _isValid Initial validity status of the CID.
     */
    function registraCid(
        uint256 _cid,
        bool _isValid
    ) external onlyOwner {
        require(!isCIDRegistered[_cid], "CID is already registered.");
        cids[_cid] = _isValid;
        isCIDRegistered[_cid] = true;
        emit CIDRegistered(_cid, _isValid);
    }

    /**
     * @dev Allows the university owner to modify the validity of a given CID.
     * @param _cid The unique identifier for the credential.
     * @param _newIsValid The new validity status for the CID.
     */
    function modificaCid(
        uint256 _cid,
        bool _newIsValid
    ) external onlyOwner {
        require(isCIDRegistered[_cid], "CID is not registered.");
        cids[_cid] = _newIsValid;
        emit CIDModified(_cid, _newIsValid);
    }

    /**
     * @dev Allows to obtain information about a given CID.
     * This method is typically invoked by the `SmartContractAuthority`.
     * @param _cid The unique identifier for the credential.
     * @return isValid The validity status of the CID.
     */
    function getInfoCid(
        uint256 _cid
    ) external view returns (bool isValid) {
        require(isCIDRegistered[_cid], "CID is not registered.");
        return cids[_cid];
    }
}
