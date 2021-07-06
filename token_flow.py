import configparser
import json
import pprint

import eth_typing
from utils import check_call_for_signatures
from web3 import Web3

pp = pprint.PrettyPrinter(indent=4)

## Config file is used for addresses/ABIs
config = configparser.ConfigParser()
config.read('./utils/config.ini')
excluded_contracts_raw = config['EXCLUDED_CONTRACTS']

weth_address = config['ADDRESSES']['WethAddress']
weth_abi = json.loads(config['ABI']['WETH'])

erc20_transfer_signatures = [Web3.sha3(text='transfer(address,uint256)')[0:4], Web3.sha3(text='transferFrom(address,address,uint256)')[0:4]]

def get_ether_flows(calls, addresses, w3):
    ## TODO: handle cases where ETH is transfered, not WETH
    eth_in = 0
    eth_out = 0

    ## TODO: handle cases where profit is in stables
    # stable_coin_in = 0
    # stable_coin_out = 0

    ## TODO: handle cases where profit is in tokens other than stablecoins and ETH

    weth_contract = w3.eth.contract(abi=weth_abi)
    for call in calls:
        if 'callType' in call['action']:
            if call['action']['to'] == weth_address and check_call_for_signatures(call, erc20_transfer_signatures):
                inputs = weth_contract.decode_function_input(call['action']['input'])
                # pp.pprint(inputs)
                weth_to = inputs[1]['dst'].lower()
                if weth_to in addresses:
                    eth_in = eth_in + inputs[1]['wad']
                
                elif call['action']['from'] in addresses:
                    eth_out = eth_out + inputs[1]['wad']

                ## TODO: check if this handles transferFrom or if that needs its own logic
        else:
            return [0, 0]

    return [eth_out, eth_in]

def get_eoa_and_contract(calls):
    for call in calls:
        if call['traceAddress'] == []:
            return [call['action']['from'], call['action']['to']]

def get_proxies(calls, parent_contract):
    proxies = []

    for call in calls:
        if 'callType' in call['action']:
            if (call['action']['callType'] == 'delegateCall' and call['action']['from'] == parent_contract):
                proxies.append(call['action']['to'])

    return proxies
    
def get_addresses_to_check(calls, eoa, parent_contract):
    addresses_to_check = []

    proxies = get_proxies(calls, parent_contract)
    addresses_to_check.append(eoa)
    addresses_to_check.append(parent_contract)

    for proxy in proxies:
        addresses_to_check.append(proxy)

    return addresses_to_check

def build_excluded_contracts():
    excluded_contracts = []

    for contract in excluded_contracts_raw:
        excluded_contracts.append(excluded_contracts_raw[contract].lower())

    return excluded_contracts