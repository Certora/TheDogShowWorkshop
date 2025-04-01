use builtin rule sanity; 

/* 

Explain your solutions HERE

*/

methods {
// methods that are envfree - not dependent on the environment 
    function owner() external returns (address) envfree; 
    function totalFeesCollected() external returns (uint256) envfree;
    function nominationFee() external returns (uint256) envfree;
    function categoryCounter() external returns (uint256) envfree;
    function isWinner(address _dog, uint256 _category) external returns (bool) envfree;
}

/**** Integrity rules *****/ 

///@title The initCategory function adds a new category with the given deadline 
rule initCategory_integrity() {
    env e;
    uint256 other; 
    uint40 otherDeadline = currentContract.categories[other].deadline; 
    uint40 _deadline;
    
    uint256 newCategory = initCategory(e, _deadline);
    
    //only owner can add
    assert e.msg.sender == owner();
    assert currentContract.categories[newCategory].deadline == _deadline; 
    // no change to other 
    assert other != newCategory =>  otherDeadline == currentContract.categories[other].deadline;
    // should success to insert new category
    satisfy newCategory > 0; 
}

///@title The Nominate function lists a dog and possibly adds to the collected fees  
rule nominate_integrity(address _dog, uint256 _category) {
    env e; 
    uint256 totalFeesCollectedBefore = totalFeesCollected();
    
    nominate(e, _dog, _category);
    
    assert currentContract.dogs[_dog].listed[_category] && currentContract.dogs[_dog].nominatedBy[_category] == e.msg.sender ;
    // it is possible that fees was collected 
    satisfy totalFeesCollected() > totalFeesCollectedBefore;
}

///@title The vote function ensures a user has not voted before and marks a user as voted.
/// In addition checks that it is possible that the voted dog can become a winner  
rule vote_integrity(address _dog, uint256 _category) {
    env e; 
    bool votedBefore = currentContract.categories[_category].hasVoted[e.msg.sender]; 
    uint256 totalVotesBefore = currentContract.categories[_category].totalVotes;
    uint256 deadline = currentContract.categories[_category].deadline;
    bool listed = currentContract.dogs[_dog].listed[_category];

    vote(e, _dog, _category);
    
    
    bool votedAfter = currentContract.categories[_category].hasVoted[e.msg.sender];
    assert !votedBefore && votedAfter && listed;
    assert deadline > e.block.timestamp; 
    assert currentContract.categories[_category].totalVotes == totalVotesBefore + e.msg.value; 
    uint256 currentWinners = currentContract.categories[_category].winners.length; 
    satisfy currentWinners > 0 && currentContract.categories[_category].winners[require_uint256(currentWinners-1)] == _dog; 
}

///@dev A helper function to compute the prize in a given category 
function computePrize(uint256 _category) returns mathint {
    return currentContract.categories[_category].winners.length == 0 ? 0 :
                currentContract.categories[_category].totalVotes / currentContract.categories[_category].winners.length; 
}


///@title The claim functions distribute prize to the nominator of a winning dog 
rule claim_integrity(address _dog, uint256 _category){
    env e;
    address nominatedBy = currentContract.dogs[_dog].nominatedBy[_category];
    bool claimedBefore = currentContract.dogs[_dog].claimed[_category];
    bool winner = isWinner(_dog, _category);
    uint256 previousBalance = nativeBalances[e.msg.sender]; 
    mathint prize = computePrize(_category); 

    claim(e, _dog, _category);

    bool claimedAfter = currentContract.dogs[_dog].claimed[_category];
    assert nominatedBy == e.msg.sender;
    assert winner && !claimedBefore && claimedAfter;
    assert nativeBalances[e.msg.sender] == previousBalance + prize; 
    satisfy nativeBalances[e.msg.sender] > previousBalance; 
}

///@title The claimFees function collects the current fees to the owner 
rule claimFees_integrity() {
    env e;
    uint256 balanceBefore = nativeBalances[owner()];
    uint256 feesBefore = totalFeesCollected();
    require owner() != currentContract;
    
    claimFees(e);

    assert nativeBalances[owner()] == balanceBefore + feesBefore;
    assert totalFeesCollected() == 0;
    satisfy feesBefore > 0 ;
}

/**** State transition ****/

///@title A prize can be claimed only after the deadline 
rule claimedAfterDeadline(method f, address _dog, uint256 _category) {
    env e;
    calldataarg args;
    require currentContract.dogs[_dog].claimed[_category] => currentContract.categories[_category].deadline <= e.block.timestamp; 
    requireInvariant validCategory(_dog, _category, _);
    
    f(e,args);

    assert currentContract.dogs[_dog].claimed[_category] => currentContract.categories[_category].deadline <= e.block.timestamp; 
}

///@title Once a dog was nominated the nominator can not be changed  
rule persistentNominatedBy(method f, address _dog, uint256 _category) {
    env e;
    calldataarg args;
    address before =  currentContract.dogs[_dog].nominatedBy[_category]; 
    requireInvariant nominatedIsListed(_dog, _category);
    
    f(e,args);
    
    address after =  currentContract.dogs[_dog].nominatedBy[_category]; 
    
    assert  before == after || ( before == 0 && after == e.msg.sender && f.selector == sig:nominate(address,uint256).selector ); 
}

/**** Valid state *****/ 

///@title Cases where the category must be valid  
invariant validCategory(address _dog, uint256 _category, address user)
    (currentContract.dogs[_dog].claimed[_category]  ||
    currentContract.dogs[_dog].nominatedBy[_category] != 0 || 
    currentContract.dogs[_dog].listed[_category] ||
    currentContract.categories[_category].totalVotes > 0 ||
    currentContract.categories[_category].currentWinningPoints > 0 ||
    currentContract.categories[_category].deadline > 0 ||
    currentContract.categories[_category].votesPerDog[_dog] > 0  || 
    currentContract.categories[_category].hasVoted[user] ) 
    => _category < categoryCounter();


///@title If a dog is nominated by someone then it must be listed 
invariant nominatedIsListed(address _dog, uint256 _category)
    currentContract.dogs[_dog].nominatedBy[_category] != 0 => currentContract.dogs[_dog].listed[_category];

///@title If a dog has votes then it must be listed 
invariant votedDogIsListed(address _dog, uint256 _category)
    currentContract.categories[_category].votesPerDog[_dog] > 0 => currentContract.dogs[_dog].listed[_category];

///@title Current winner point is greater-equal to the votes of any dog  
invariant currentWinningPointsIsMax(address _dog, uint256 _category)
    currentContract.categories[_category].votesPerDog[_dog] <= currentContract.categories[_category].currentWinningPoints;

///@title A winning dog has the current winning points  
invariant winnerHasMaxPoints(address _dog, uint256 _category)
    isWinner(_dog, _category) =>  
            currentContract.categories[_category].votesPerDog[_dog] == currentContract.categories[_category].currentWinningPoints; 

///@title There can be up to 10 winners per category
invariant maxWinners(uint256 _category)
    currentContract.categories[_category].winners.length <= 10;

/**** High level rules *****/ 

///@dev Ghost to represent the count of currentContract.dogs[dog].listed[category] for all dogs and categories 
ghost mathint countAllNominated {
    init_state axiom countAllNominated == 0 ;
    axiom countAllNominated >= 0;
}

///@dev Ghost to represent the sum of currentContract.categories[category].totalVotes for all categories 
ghost mathint sumTotalVotes {
    init_state axiom sumTotalVotes == 0 ;
    axiom sumTotalVotes >= 0;
}

///@dev Ghost to represent the sum of computePrize(category) for all claimed prizes
ghost mathint sumAmountClaimed {
    init_state axiom sumAmountClaimed == 0 ;
    axiom sumAmountClaimed >= 0;
}

///@dev updates to ghost variables on the corresponding sstore operations 
hook Sstore  currentContract.dogs[KEY address dog].listed[KEY uint256 category] bool value {
    countAllNominated = countAllNominated + (value ? 1 : 0); 
}

hook Sstore currentContract.categories[KEY uint256 category].totalVotes uint256 newValue (uint256 oldValue) {
    sumTotalVotes = sumTotalVotes + newValue - oldValue ;
}

hook Sstore  currentContract.dogs[KEY address dog].claimed[KEY uint256 category] bool flag {
    if(flag) {
        sumAmountClaimed = sumAmountClaimed + computePrize(category);
    }
}

///@title The total fees collected do not exceed the total nomination fees over all time 
invariant totalFees() 
    totalFeesCollected()  <= countAllNominated * nominationFee(); 

///@title The total eth held by the contract is at least the fees collected + the total votes - the already claimed prizes 
invariant solvency() 
    nativeBalances[currentContract] >= totalFeesCollected() + (sumTotalVotes - sumAmountClaimed) 
    { 
        preserved with (env e) {
            require e.msg.sender != currentContract;
            requireInvariant totalFees();
        } 
    }                  
   