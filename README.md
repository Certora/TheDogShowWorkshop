
# Certora EthDenver 2025 Challenge  

Welcome to the Certora ETHDenver 2025 Challenge! Your goal is to find a buggy version of `BestDogVoting` that is not detected by the provided formal verification rules but still qualifies as a high-severity issue.

To be considered a high-severity bug, the issue must impact either:
1. Voting outcomes, or 
2. The assets collected/distributed. 

The buggy version must implement the same functions as the original contract while introducing a critical flaw.

## Challenge rules

### 1. Submit a Missing Spec

To submit a missing specification, follow these steps:

1. **Create mutations**: Add mutations to the mutations folder.

    - A mutation is a one-line change (one semicolon). It can be:

    - A modification of an existing line.

    - An insertion of a new line.

    - A removal of an existing line.

2. **Run `certoraMutate` and submit your results**.

    - For example, in this [mutation report](https://mutation-testing.certora.com/?id=967292c9-ce5e-4495-9a08-770cff7fde69&anonymousKey=a3a0b7ec-c27b-44df-b11c-49213338da57BestDogVoting_M1), 
    [BestDogVoting_M1](https://github.com/Certora/TheDogShow/blob/main/mutations/BestDogVoting_M1.sol) 
    and [BestDogVoting_M2](https://github.com/Certora/TheDogShow/blob/main/mutations/BestDogVoting_M2.sol) are caught by the rules.
    [BestDogVoting_M3](https://github.com/Certora/TheDogShow/blob/main/mutations/BestDogVoting_M3.sol) is not caught by the rules. However, since it is a gas optimization issue, it does not qualify as a missed bug.

---

### 2. Earn Extra Points

Go beyond just finding a missing bug—help improve the rules!

1. **Fix the spec** to also capture the missing bug.
2. **Submit a `certoraMutate`** run with the updated spec.

## Running the Verification

1. Install the Python SDK
    ```sh
    pip install certora-cli
    ```

2. Run Verification
    From this directory, execute:
    ```sh
    certoraRun certora.conf
    ```

3. Run `certoraMutate`
    To run `certoraMutate`:
    1. Add mutations to the `mutations` folder.
    2. Execute `certoraMutate certora.conf`

## Submission Deadline

Ensure your submission is completed before the deadline. Late submissions will not be considered.


## Need Help?

If you encounter issues or have questions, check out our detailed [installation guide](https://docs.certora.com/en/latest/docs/user-guide/getting-started/install.html).

Good luck, and happy hacking! 🚀
