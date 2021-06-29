from web3 import Web3
import configparser
import json
import utils

## Config file is used for addresses/ABIs
config = configparser.ConfigParser()
config.read('./utils/config.ini')

## Load up the ABIs and addresses to make them easier to handle
uniswap_router_abi = json.loads(config['ABI']['UniswapV2Router'])
uniswap_router_address = (config['ADDRESSES']['UniswapV2Router'])
sushiswap_router_address = (config['ADDRESSES']['SushiswapV2Router'])

uniswap_pair_abi = json.loads(config['ABI']['UniswapV2Pair'])

class UniswapInspector:
    def __init__(self, base_provider) -> None:
        self.w3 = Web3(base_provider)
        
        self.trading_functions = self.get_trading_functions()
        self.uniswap_v2_router_contract = self.w3.eth.contract(abi=uniswap_router_abi, address=uniswap_router_address)
        self.uniswap_router_trade_signatures = self.get_router_signatures()

        self.uniswap_v2_pair_contract = self.w3.eth.contract(abi=uniswap_pair_abi)
        self.uniswap_v2_pair_swap_signature = Web3.sha3(text='swap(uint256,uint256,address,bytes)')[0:4]
        # Alternative returned as a string, not hexbytes: (self.uniswap_v2_pair_contract.functions.swap(0, 0, uniswap_router_address, "").selector) ## Note the address here doesn't matter, but it must be filled out
        self.uniswap_v2_pair_reserves_signature = Web3.sha3(text='getReserves()')[0:4]
         # Alternative returned as a string, not hexbytes: self.uniswap_v2_pair_contract.functions.getReserves().selector ## Called "checksigs" in mev-inpsect.ts

        print("Built Uniswap inspector")
    
    def get_trading_functions(self):
        ## Gets all functions used for swapping
        result = []
       
        ## For each entry in the ABI
        for abi in uniswap_router_abi:
            ## Check to see if the entry is a function and if it is if the function's name starts with swap
            if abi['type'] == 'function' and abi['name'].startswith('swap'):
                ## If so add it to our array
                result.append(abi['name'])
        
        return result

    def get_router_signatures(self):
        ## Gets the selector / function signatures of all the router swap functions
        result = []
       
        ## For each entry in the ABI
        for abi in uniswap_router_abi:
            ## Check to see if the entry is a function and if it is if the function's name starts with swap
            if abi['type'] == 'function' and abi['name'].startswith('swap'):
                ## Add a parantheses
                function = abi['name'] + '('
                
                ## For each input in the function's input
                for input in abi['inputs']:
                    
                    ## Concat them into a string with commas
                    function = function + input['internalType'] + ','

                ## Take off the last comma, add a ')' to close the parentheses
                function = function[:-1] + ')'  

                ## The result looks like this: 'swapETHForExactTokens(uint256,address[],address,uint256)'

                ## Take the first 4 bytes of the sha3 hash of the above string.
                selector = (Web3.sha3(text=function)[0:4])

                ## Add that to an array
                result.append(selector)

        return result

    def inspect(self, calls):
        # print("Inspecting calls for Uniswappy trades")
        result = []

        ## Identifies trades that go directly to the Uniswap router
        for trade_call in self.get_router_trade_calls(calls):
            sub_calls_of_trade = []
            for call in calls:
                if call['transactionHash'] == trade_call['transactionHash'] and utils.sub_call_match(call, trade_call['traceAddress']):
                    ## The intention here is to get the sub calls that correspond to a trade.
                    sub_calls_of_trade.append(call)
            
            if len(sub_calls_of_trade) == 0:
                ## Consider a Uniswap router call-tree calling back into Uniswap Router. We cull parts of the call tree as we process it
                print("Removed a recursive call")
                continue
            
            ## We know this is a trade on Uniswap, now let's decode it to understand its inputs
            trade_inputs = self.uniswap_v2_router_contract.decode_function_input(data = trade_call['action']['input'])
            args = trade_inputs[1]
            to = args['to']
            path = args['path']
            source_token = path[0].lower()
            dest_token = path[len(path) - 1].lower()

            ## This can probably be turned into a terniary but I can't remember how to do that and I'm on a plane
            provider = ''
            if trade_call['action']['to'] == uniswap_router_address.lower():
                provider = uniswap_router_address
            elif trade_call['action']['to'] == sushiswap_router_address.lower():
                provider = sushiswap_router_address

            ## Create a structured object for the results
            action = {
                'provider': provider,
                'action_type': 'tbd',  #     type: ACTION_TYPE.TRADE,
                'action_calls': sub_calls_of_trade,
                'transaction_hash': trade_call['transactionHash'],
                'subcall': trade_call,
                'status': 'tbd'  #     status: tradeCall.reverted ? ACTION_STATUS.REVERTED : ACTION_STATUS.SUCCESS,
            }

            ## TODO:
            ## implement "action" data structure
            ## implement the "token tracker" from inspect-ts
            ## get action_types
            ## get trade status (did it revert?)
            ## get what the result of the trade was, currently this only *identifies* a trade

            result.append(action)

        ## Identified trades that go directly to pairs
        for pair_trade_call in self.get_pair_trade_calls(calls):
            sub_calls_of_pair_trade = []

            for call in calls:
                if call['transactionHash'] == pair_trade_call['transactionHash'] and utils.sub_call_match(call, pair_trade_call['traceAddress']):
                    ## The intention here is to get the sub calls that correspond to a trade.
                    sub_calls_of_pair_trade.append(call)

            action = {
                'provider': uniswap_router_address, # TBD
                'action_type': 'tbd',  #     type: ACTION_TYPE.TRADE, also TBD
                'action_calls': sub_calls_of_pair_trade,
                'transaction_hash': pair_trade_call['transactionHash'],
                'subcall': pair_trade_call,
                'status': 'tbd'  #     status: tradeCall.reverted ? ACTION_STATUS.REVERTED : ACTION_STATUS.SUCCESS,
            }

            ## TODO:
            ## implement "action" data structure
            ## implement the "token tracker" from inspect-ts
            ## get action_types
            ## get trade status (did it revert?)
            ## get what the result of the trade was, currently this only *identifies* a trade

            result.append(action)
        
        ## Identifies "pre-flights" that check reserves before trading
        for check_reserves_call in self.get_pair_reserves_calls(calls):
            sub_calls_of_check_reserves_call = []

            for call in calls:
                if call['transactionHash'] == check_reserves_call['transactionHash'] and utils.sub_call_match(call, check_reserves_call['traceAddress']):
                    ## The intention here is to get the sub calls that correspond to a trade.
                    sub_calls_of_check_reserves_call.append(call)

            action = {
                'provider': uniswap_router_address, # TBD
                'action_type': 'tbd',  #     type: ACTION_TYPE.TRADE, also TBD
                'action_calls': sub_calls_of_check_reserves_call,
                'transaction_hash': check_reserves_call['transactionHash'],
                'subcall': check_reserves_call,
                'status': 'tbd'  #     ACTION_STATUS.CHECKED,
            }

            result.append(action)
        
        return result

   
    def get_router_trade_calls(self, calls):
        ## Identifies the calls match the desired signatures (PLURAL), which in this case are the v2 routers trade functions, as well as aren't create/create2/suicides
        
        trade_calls = []
        for call in self.filter_call_types(calls):
            if (call['action']['to'] == uniswap_router_address.lower() or call['action']['to'] == sushiswap_router_address.lower()) and utils.check_call_for_signatures(call, self.uniswap_router_trade_signatures):
                trade_calls.append(call)

        return trade_calls

    
    def get_pair_trade_calls(self, calls):
        ## Identifies the calls match the desired signature (NOT PLURAL), which in this case is the v2 pair swap function, as well as aren't create/create2/suicides
        
        trade_calls = []
        for call in self.filter_call_types(calls):
            if (utils.check_call_for_signature(call, self.uniswap_v2_pair_swap_signature)):
                trade_calls.append(call)

        return trade_calls
    
    def get_pair_reserves_calls(self, calls):
        ## Identifies the calls match the desired signature (NOT PLURAL), which in this case is the v2 pair get reserves function, as well as aren't create/create2/suicides or delegateCalls

        trade_calls = []
        for call in self.filter_call_types(calls):
            if (call['type'] != 'delegateCall' and utils.check_call_for_signature(call, self.uniswap_v2_pair_reserves_signature)):
                trade_calls.append(call)

        return trade_calls

    def filter_call_types(self, calls):
        # Filters out some calls that we don't want
        result =[]

        for call in calls:
            if (call['type']!= 'suicide' and call['type'] != 'create' and call['type'] != 'create2'):
                result.append(call)

        return result