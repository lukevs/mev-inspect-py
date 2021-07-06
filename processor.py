from web3.main import Web3
import token_flow

import configparser
## Config file is used for addresses/ABIs
config = configparser.ConfigParser()
config.read('./utils/config.ini')
excluded_contracts = config['EXCLUDED_CONTRACTS']

import pprint
pp = pprint.PrettyPrinter(indent=4)

class Processor:
    def __init__(self, base_provider, inspectors) -> None:
        self.base_provider = base_provider
        self.inspectors = inspectors
        self.excluded_contracts = token_flow.build_excluded_contracts() # build a list of contracts to exclude from our token flow analysis, e.g. routers and aggregators

    def get_transaction_evaluations(self, block_data):
        print("Beginning inspection of block")
        for transaction_hash in block_data.transaction_hashes:
            print("\nInspecting:", transaction_hash)
            
            calls = block_data.get_filtered_calls(transaction_hash)

            ## "Actions" will be objects that contain information about calls that have been classified
            total_actions = []
            for inspector in self.inspectors:
                actions = inspector.inspect(calls) ## Inspect on each of our inspectors (right now its just two uniswaps)
                if actions != []: ## Make sure that the action is not empty
                    total_actions.append(actions)

            print("Inspection done, received", len(total_actions), "actions")
            [eoa, contract] = token_flow.get_eoa_and_contract(calls) # Get the eoa and contract from the right call
            addresses_to_check = token_flow.get_addresses_to_check(calls, eoa, contract) # Build a list of addresses (EOA, Contract, Proxies) to check for token flows
            
            if contract in self.excluded_contracts:
                print("Not checking this transaction's profit as the contract is in the list of excluded contracts")
            else:
                [calls_eth_out, calls_eth_in] = token_flow.get_ether_flows(calls, addresses_to_check, Web3(self.base_provider)) ## get the eth flows in and out
                print("ETH Out:", calls_eth_out)
                print("ETH In : ", calls_eth_in)
                print("Profit :", calls_eth_in - calls_eth_out)