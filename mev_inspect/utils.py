from hexbytes.main import HexBytes

from mev_inspect.schemas import Trace


def check_call_for_signature(trace: Trace, signatures) -> bool:
    if trace.action["input"] == None:
        return False

    ## Iterate over all signatures, and if our call matches any of them set it to True
    for signature in signatures:
        if HexBytes(trace.action["input"]).startswith((signature)):
            ## Note that we are turning the input into hex bytes here, which seems to be fine
            ## Working with strings was doing weird things
            return True

    return False
