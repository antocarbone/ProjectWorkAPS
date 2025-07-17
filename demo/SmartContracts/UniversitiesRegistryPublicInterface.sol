// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface ISmartContractAuthorityPublic {
    function getUniversityInfo(
        string memory _uid
    ) external view returns (
        bytes memory pub_key_modulus,
        bytes memory pub_key_exponent,
        bool isRevoked,
        address sidContractAddress,
        address cidContractAddress
    );

    function verificaSid(
        string memory _uid,
        uint128 _sid
    ) external view returns (
        bytes memory pub_key_modulus,
        bytes memory pub_key_exponent,
        bool isValid
    );

    function verificaCid(
        string memory _uid,
        uint256 _cid
    ) external view returns (bool isValid);
}
