# mev-inspect-py

MEV-inspect-py is a script which "inspects" an Ethereum block, or range of blocks, and tries to identify and analyze transactions which extract MEV. For example, it will identify and quantify arbitrage trades which capture profit from mispricing across two DEXes in a single transaction.

MEV-inspect-py is currently a work in progress that builds on the work done in MEV-inspect-rs. In the coming weeks we will release a foundation from which contributors can add new inspectors.

In its current, unfinished, form MEV-Inspect-PY consists of:
- block.py: a tool for getting the data necessary to perform inspections. The first time a block is inspected it will be cached in `./cache/block_number.json` for future use. This greatly speeds up backfilling.
- processor.py: manages different inspectors and evaluating transactions. Specifically it will inspect each transacti through all inspectors to try and identify what that transaction was doing. Then it will use token_flow.py to figure out how much profit was made or not.
- inspector_uniswap.py: looks for instances of when calls from a transaction have interacted with the uniswap router, a uniswap pair contract directly, or performed a reserve check.
- token_flow.py: estimates the profit of a series of calls from a transaction by looking at WETH going in and out of some set of transactions. In the future this will also inspect ETH and stablecoin flows.
- utils.py: a series of utility functions used across different parts of mev-inspect
- testing_file.py: a file I made to put all of this together and test it.

# Using MEV-Inspect-PY
```
Usage: python3 testing_file.py [OPTIONS]

Optional arguments:
  -b, --block              the block number you are inspecting
  -r, --rpc                the rpc endpoint of an erigon of parity archive node
```

For a test block please try block number `12768559`. Transaction [0xcc118d2795c9196c9398b47a2f443dd0d54b1d265b4b4e400d956bc1a7f467a9](https://etherscan.io/tx/0xcc118d2795c9196c9398b47a2f443dd0d54b1d265b4b4e400d956bc1a7f467a9) is an arbitrage transaction.
