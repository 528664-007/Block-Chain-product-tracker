// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

/// @title Product Tracker - simple supply chain tracker
/// @notice Stores products and their status history (status + location + timestamp)
contract ProductTracker {
    address public owner;
    uint256 public nextProductId = 1;

    struct Status {
        string status;
        string location;
        uint256 timestamp;
    }

    struct Product {
        uint256 id;
        string name;
        string manufacturer;
        uint256 createdAt;
        uint256 statusCount;
        mapping(uint256 => Status) statuses; // index -> Status (0..statusCount-1)
    }

    // product id -> Product
    mapping(uint256 => Product) private products;
    // keep a record of existing products for enumeration
    uint256[] public productIds;

    event ProductCreated(uint256 indexed productId, string name, string manufacturer, uint256 timestamp);
    event StatusAdded(uint256 indexed productId, uint256 statusIndex, string status, string location, uint256 timestamp);

    modifier onlyOwner() {
        require(msg.sender == owner, "only owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function createProduct(string calldata name, string calldata manufacturer) external returns (uint256) {
        uint256 pid = nextProductId++;
        Product storage p = products[pid];
        p.id = pid;
        p.name = name;
        p.manufacturer = manufacturer;
        p.createdAt = block.timestamp;
        p.statusCount = 0;
        productIds.push(pid);

        emit ProductCreated(pid, name, manufacturer, block.timestamp);
        return pid;
    }

    function addStatus(uint256 productId, string calldata status, string calldata location) external returns (uint256) {
        require(productId > 0 && productId < nextProductId, "invalid product");
        Product storage p = products[productId];
        uint256 idx = p.statusCount;
        p.statuses[idx] = Status({status: status, location: location, timestamp: block.timestamp});
        p.statusCount = idx + 1;
        emit StatusAdded(productId, idx, status, location, block.timestamp);
        return idx;
    }

    // getters for product base info
    function getProductInfo(uint256 productId) external view returns (
        uint256 id,
        string memory name,
        string memory manufacturer,
        uint256 createdAt,
        uint256 statusCount
    ) {
        require(productId > 0 && productId < nextProductId, "invalid product");
        Product storage p = products[productId];
        return (p.id, p.name, p.manufacturer, p.createdAt, p.statusCount);
    }

    // getter for a single status entry by index
    function getProductStatus(uint256 productId, uint256 index) external view returns (
        string memory status,
        string memory location,
        uint256 timestamp
    ) {
        require(productId > 0 && productId < nextProductId, "invalid product");
        Product storage p = products[productId];
        require(index < p.statusCount, "invalid status index");
        Status storage s = p.statuses[index];
        return (s.status, s.location, s.timestamp);
    }

    // helper: get number of products
    function getProductCount() external view returns (uint256) {
        return productIds.length;
    }

    // helper: returns product id at index
    function getProductIdByIndex(uint256 index) external view returns (uint256) {
        require(index < productIds.length, "index out of range");
        return productIds[index];
    }
}
