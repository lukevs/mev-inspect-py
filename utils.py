from hexbytes.main import HexBytes

def check_call_for_signatures(call, signatures):
    ## used for checking a call for an array of signatures

    if (call['action']['input'] == None):
        return False
    
    ## By default set this to False
    signature_present_boolean = False
    
    ## Iterate over all signatures, and if our call matches any of them set it to True
    for signature in signatures:
        # print(signature)
        # print("Desired signature:", str(signature))
        # print("Actual", HexBytes(call['action']['input']))

        if HexBytes(call['action']['input']).startswith(signature):
            ## Note that we are turning the input into hex bytes here, which seems to be fine
            ## Working with strings was doing weird things
            signature_present_boolean = True

    return signature_present_boolean


def check_call_for_signature(call, signature):
    ## used for checking a single signature, not an array
    
    if (call['action']['input'] == None):
        return False
    
    ## If our call matches the signature return true

    if HexBytes(call['action']['input']).startswith(signature):
        ## Note that we are turning the input into hex bytes here, which seems to be fine
        ## Working with strings was doing weird things
        return True


def sub_call_match(call, trace_call_address):
    if trace_call_address == call['traceAddress'][0:len(trace_call_address)]:
        return True