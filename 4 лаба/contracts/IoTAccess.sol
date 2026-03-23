// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract IoTAccess {
    struct Device {
        string deviceId;
        address owner;
        bool exists;
    }

    struct AccessEvent {
        string deviceId;
        address client;
        string actionType;
        uint256 timestamp;
    }

    mapping(string => Device) public devices;
    mapping(string => mapping(address => bool)) public permissions;
    mapping(string => AccessEvent[]) private history;

    event DeviceRegistered(string deviceId, address owner);
    event AccessGranted(string deviceId, address client);
    event AccessRevoked(string deviceId, address client);
    event AccessRecorded(string deviceId, address client, string actionType, uint256 timestamp);

    modifier onlyOwner(string memory deviceId) {
        require(devices[deviceId].exists, "Device not found");
        require(devices[deviceId].owner == msg.sender, "Not owner");
        _;
    }

    function registerDevice(string memory deviceId) external {
        require(!devices[deviceId].exists, "Already registered");

        devices[deviceId] = Device({
            deviceId: deviceId,
            owner: msg.sender,
            exists: true
        });

        emit DeviceRegistered(deviceId, msg.sender);
    }

    function grantAccess(string memory deviceId, address client) external onlyOwner(deviceId) {
        permissions[deviceId][client] = true;
        emit AccessGranted(deviceId, client);
    }

    function revokeAccess(string memory deviceId, address client) external onlyOwner(deviceId) {
        permissions[deviceId][client] = false;
        emit AccessRevoked(deviceId, client);
    }

    function recordAccess(string memory deviceId, string memory actionType) external {
        require(devices[deviceId].exists, "Device not found");
        require(permissions[deviceId][msg.sender], "Access denied");

        history[deviceId].push(
            AccessEvent({
                deviceId: deviceId,
                client: msg.sender,
                actionType: actionType,
                timestamp: block.timestamp
            })
        );

        emit AccessRecorded(deviceId, msg.sender, actionType, block.timestamp);
    }

    function getHistoryCount(string memory deviceId) external view returns (uint256) {
        return history[deviceId].length;
    }

    function getHistoryItem(string memory deviceId, uint256 index)
        external
        view
        returns (
            string memory,
            address,
            string memory,
            uint256
        )
    {
        AccessEvent memory item = history[deviceId][index];
        return (item.deviceId, item.client, item.actionType, item.timestamp);
    }

    function hasAccess(string memory deviceId, address client) external view returns (bool) {
        return permissions[deviceId][client];
    }
}