// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract BestDogVoting {
    // The contract owner (only owner can add new categories)
    address public owner;

    // Fixed nomination fee (set in the constructor)
    uint256 public nominationFee;

    // Total fees collected from nominations
    uint256 public totalFeesCollected;

    // Category counter for generating incremental category IDs
    uint256 public categoryCounter;

    // ---------------------------
    // Data Structures
    // ---------------------------
    
    // Dog struct now holds per-category nomination details:
    // - listed: whether the dog has been nominated in that category.
    // - claimed: whether the reward has been claimed for that category.
    // - nominatedBy: the address that nominated the dog for that category.
    struct Dog {
        mapping(uint256 => bool) listed;
        mapping(uint256 => bool) claimed;
        mapping(uint256 => address) nominatedBy;
    }

    // Mapping from dog address to its Dog struct.
    mapping(address => Dog) private dogs;

    // The Category struct tracks:
    // - totalVotes: total funds contributed via votes (used for reward splitting)
    // - currentWinningPoints: the highest vote total in the category
    // - deadline: the voting deadline (as a uint40 timestamp)
    // - nominatedDogs: array of dog addresses nominated in this category
    // - winners: array of dog addresses that have the highest vote total (could be >1 if tied)
    // - votesPerDog: mapping from dog address to its total vote amount
    // - hasVoted: mapping to track if an address has already voted in this category
    struct Category {
        uint256 totalVotes;
        uint256 currentWinningPoints;
        uint40 deadline;
        address[] winners;
        mapping(address => uint256) votesPerDog;
        mapping(address => bool) hasVoted;
    }

    // Mapping from category ID to its Category struct.
    mapping(uint256 => Category) public categories;

    // ---------------------------
    // Events (for easier tracking)
    // ---------------------------
    event CategoryInitialized(uint256 indexed categoryId, uint40 deadline);
    event DogNominated(address indexed dog, uint256 indexed category, address nominator);
    event Voted(address indexed voter, address indexed dog, uint256 indexed category, uint256 amount);
    event RewardClaimed(address indexed dog, uint256 indexed category, uint256 reward);
    event FeesClaimed(address indexed owner, uint256 amount);

    // ---------------------------
    // Modifiers
    // ---------------------------
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    // ---------------------------
    // Constructor
    // ---------------------------
    constructor(uint256 _nominationFee) {
        owner = msg.sender;
        nominationFee = _nominationFee;
    }

    // ---------------------------
    // Category Initialization
    // ---------------------------
    /// @notice Initializes a new category with a given deadline.
    /// @dev Only the contract owner can call this function.
    /// @param _deadline The timestamp (uint40) until which voting is allowed.
    /// @return categoryId The id assigned to the newly created category.
    function initCategory(uint40 _deadline) external onlyOwner returns (uint256 categoryId) {
        categoryId = categoryCounter;
        categoryCounter++;
        Category storage cat = categories[categoryId];
        cat.deadline = _deadline;
        emit CategoryInitialized(categoryId, _deadline);
    }

    // ---------------------------
    // Nomination Function
    // ---------------------------
    /// @notice Nominate a dog (address) to a given category.
    /// @dev The caller must pay exactly the nomination fee.
    /// @param _dog The address representing the dog.
    /// @param _category The id of the category.
    function nominate(address _dog, uint256 _category) external payable {
        require(msg.value == nominationFee, "Incorrect nomination fee");
        require(_category < categoryCounter, "Category does not exist");

        // Accumulate the nomination fee.
        totalFeesCollected += msg.value;

        Dog storage d = dogs[_dog];
        // Ensure the dog hasn't already been nominated in this category.
        require(!d.listed[_category], "Dog already nominated in this category");

        // Record the nominator for this category.
        d.nominatedBy[_category] = msg.sender;
        d.listed[_category] = true;

        emit DogNominated(_dog, _category, msg.sender);
    }

    // ---------------------------
    // Voting Function
    // ---------------------------
    /// @notice Vote for a nominated dog in a category.
    /// @dev Each address can vote only once per category. The vote amount (msg.value) counts as points.
    /// @param _dog The dog (address) you are voting for.
    /// @param _category The category id.
    function vote(address _dog, uint256 _category) external payable {
        require(msg.value > 0, "Any voting price");
        require(_category < categoryCounter, "Category does not exist");
        Category storage cat = categories[_category];
        require(block.timestamp < cat.deadline, "Voting period has ended");

        // Each address may only vote once in this category.
        require(!cat.hasVoted[msg.sender], "Already voted in this category");

        Dog storage d = dogs[_dog];
        require(d.listed[_category], "Dog not nominated in this category");

        // Mark that the voter has cast their vote.
        cat.hasVoted[msg.sender] = true;

        // Increase the dog's vote total by msg.value.
        cat.votesPerDog[_dog] += msg.value;

        // Increase the total funds collected for the category.
        cat.totalVotes += msg.value;

        uint256 dogVotes = cat.votesPerDog[_dog];
        if (dogVotes > cat.currentWinningPoints) {
            // This dog is now the sole leader.
            cat.currentWinningPoints = dogVotes;

            // Reset winners to only include this dog.
            delete cat.winners;
            cat.winners.push(_dog);
        } else if (dogVotes == cat.currentWinningPoints) {
            cat.winners.push(_dog);
        }

        emit Voted(msg.sender, _dog, _category, msg.value);
    }

    // ---------------------------
    // Claiming Rewards
    // ---------------------------
    /// @notice Claim the reward for a winning dog in a category.
    /// @dev msg.sender must be the nominator of the dog in that category.
    ///      The reward is split equally among winners.
    /// @param _dog The dog (address) for which the reward is claimed.
    /// @param _category The category id.
    function claim(address _dog, uint256 _category) external {
        require(_category < categoryCounter, "Category does not exist");
        Category storage cat = categories[_category];
        require(block.timestamp >= cat.deadline, "Voting period not ended");

        Dog storage d = dogs[_dog];
        require(d.listed[_category], "Dog not nominated in this category");

        // Ensure that the caller is the nominator for this dog in the specified category.
        require(d.nominatedBy[_category] == msg.sender, "Not the nominator for this dog in this category");
        require(!d.claimed[_category], "Reward already claimed for this category");

        // Verify that the dog is among the winners.
        require(isWinner(_dog, _category), "Dog is not a winner in this category");

        uint256 numWinners = cat.winners.length;
        require(numWinners > 0, "No winners in this category");
        
        // Calculate reward: total funds divided equally among winners.
        uint256 reward = cat.totalVotes / numWinners;

        // Mark the reward as claimed for this category.
        d.claimed[_category] = true;

        // Transfer the reward to the nominator.
        (bool success, ) = msg.sender.call{value: reward}("");
        require(success, "Reward transfer failed");

        emit RewardClaimed(_dog, _category, reward);
    }

    // ---------------------------
    // Owner Fee Claim Function
    // ---------------------------
    /// @notice Claim the accumulated nomination fees.
    /// @dev Only the contract owner can call this function.
    function claimFees() external onlyOwner {
        //mutations don't check totalFees
        //require(totalFeesCollected > 0, "No fees to claim");
        uint256 amount = totalFeesCollected;
        totalFeesCollected = 0;
        (bool success, ) = owner.call{value: amount}("");
        require(success, "Fee transfer failed");
        emit FeesClaimed(owner, amount);
    }

    // ---------------------------
    // Check Winning Dog Function
    // ---------------------------
    /// @notice Check if a dog is a winner in a category.
    /// @param _dog The dog (address) to check.
    /// @param _category The category id.
    /// @return _isWinner True if _dog is a winner in _category.
    function isWinner(address _dog, uint256 _category) public view returns (bool _isWinner) {
        Category storage cat = categories[_category];
        for (uint256 i = 0; i < cat.winners.length; i++) {
            if (cat.winners[i] == _dog) {
                _isWinner = true;
                break;
            }
        }
    }
}