# Certora Take-Home Exercise — FV Researcher Application

Welcome, and thank you for your interest in the [Formal Verification Researcher](https://www.certora.com/careers/formal-verification-researcher) position at Certora!

This take-home exercise is designed to evaluate your understanding of smart contract verification, your ability to reason about specifications, and your skill in identifying and expressing critical correctness properties.

---

## 🧠 Objective

Your goal is to install and run the Certora Prover, understand a simple Solidity smart contract and its associated formal specification, and complete three short formal verification tasks.

---

## 📦 Setup Instructions

### 1. Clone the Repository

Start by forking and cloning this repository into a **private** GitHub repository. This will be your work space for the exercise. You can do this however you prefer, the important part is that your work space is private. Here's one way to do it via `ssh`:

```bash
git clone --bare <this-repo> # create a bare clone
cd <this-repo>
# create a private github repository <name-of-your-private-github-repo>
git push --mirror git@github.com:<your_username>/<name-of-your-private-github-repo>.git #mirror push against your private repo
cd ..
rm -rf <this-repo> #remove your bare clone
cd ~/<project>
git clone git@github.com:<your_username>/<name-of-your-private-github-repo>.git #clone your private repo
```

### 2. Install the Certora CLI

Follow the instructions in the [Certora installation guide](https://docs.certora.com/en/latest/docs/user-guide/getting-started/install.html).

Note: We recommend installing and using [`solc-select`](https://github.com/crytic/solc-select) for Solidity version control which can be easily installed via `brew`or `pip3`. To run this project make sure to install and use a Solidity version >= 0.8.0, e.g. 

```bash
solc-select install 0.8.21
solc-select use 0.8.21
```

Make sure you can successfully run the prover with `certoraRun`.


### 3. Run the Provided Specification

To verify the contract using the existing specification, run:

```bash
certoraRun dogVoting.conf
```

This will run the Certora Prover on `BestDogVoting.sol` using the provided rules.

---

## 📁 Repository Structure
```bash
.
├── contracts/
│   └── BestDogVoting.sol          # Solidity contract (original)
│   └── BestDogVotingBug1.sol      # Solidity contract for Exercise 1
│   └── BestDogVotingBug2.sol      # Solidity contract for Exercise 2 and 3
├── specs/
│   └── BestDogVoting.spec     # Formal specification
├── dogVoting.conf             # Prover configuration file to run on original contract
├── dogVotingBug1.conf         # Prover configuration file to run on BestDogVotingBug1.sol
├── dogVotingBug2.conf         # Prover configuration file to run on BestDogVotingBug2.sol
└── README.md                  # This file
```

---

## 📌 The Exercises

### Exercise 1: Inject a Bug That *Is Caught*

- **Goal**: Modify the contract `BestDogVotingBug1.sol` to introduce a **critical bug** that affects either:
  - Voting outcomes, or
  - Collected/distributed assets

- This bug **must be detected** by the current specification (i.e., the Prover should report a violation).
- Run the updated contract using:
```bash
certoraRun dogVotingBug1.conf
```

- **📦 Deliverable**:
  - Submit the buggy version of the contract as `BestDogVotingBug1.sol`
  - Write a short description of the bug you introduced and provide the run link from Certora Prover showing the violated specification in the comments of `BestDogVotingBug1.sol`

### Exercise 2: Inject a Bug That *Is NOT Caught*

- **Goal**: Modify the contract  `BestDogVotingBug2.sol` to introduce another **critical bug**, but this time the bug should **not be detected** by the current specification.

- This simulates a scenario where the spec is incomplete or missing an important rule.
- Run the updated contract using:
```bash
certoraRun dogVotingBug2.conf
```

- **📦 Deliverable**:
  - Submit the buggy version of the contract as `BestDogVotingBug2.sol`.
  - Describe the bug and explain why it is not caught by the spec in the comments of `BestDogVotingBug2.sol`
  - Provide a run link from Certora Prover showing that the specifications in `BestDogVoting.spec` are not violated when verifying this contract in the comments of `BestDogVotingBug2.sol`

### ✍️ Exercise 3: Add a Rule That Catches the Bug from #2

- **Goal**: Extend the formal specification to **detect** the bug from Exercise 2.
  - Add a new rule that verifies an important security property that will also catch the bug.
  - Your rule should be **general** — it must express a valid correctness property and not be tailored to your specific bug.
  - Bonus points for parametric rules or invariants. 

- Run the updated spec using:

```bash
certoraRun dogVotingBug2.conf
```

- **✅ Expected result**:
    - The rule **passes** on the correct (original) contract  
    - The rule **fails** on the buggy version from Exercise 2

- **📦 Deliverable**
    - Submit the updated `.spec` file 
    - Provide a brief explanation of the rule and what correctness property it captures as a comment to your spec
    - Include a two run links to the Certora Prover showing that the rule passes on `BestDogVoting.sol` and is violated on `BestDogVotingBug2.sol` in the comments of your explanation. 

### ✍️ Exercise 4: Spec Completeness Check
- **Goal**: Additional specifications review:
  - Check the code and the spec
  - Is our spec complete?
  - Which other security properties can you think of?
 
- **📦 Deliverable**
    - Submit an additional `extra.spec` file with additional properties that have not been part of our spec but are still important specifications and security properties for the DogVoting contract. 
    - Provide a brief explanation of each new rule as a comment and what high-level correctness property it captures.
    - Include a run link to the Certora Prover showing that the rule passes on `BestDogVoting.sol` in the comments of your explanation. 

---

## 📤 Submission Instructions

Submit your completed take-home by inviting us to your private repository:

Invite the following people: 
- @paminacert
- @shoham-certora
- @nd-certora

Your submission should include:
- The updated files `BestDogVotingBug1.sol` and `BestDogVotingBug2.sol` with your bugs. 
- Descriptions of your bugs for Exercises 1 and 2
- The updated spec for Exercise 3
- Certora Prover run links showing the prover results for Exercises 1, 2 and 3. 
You can add this information as comments in the beginning of the spec file. 

Make sure to notify your Certora HR liaison of completing the tasks via e-mail.

