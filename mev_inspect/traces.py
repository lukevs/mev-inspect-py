from typing import List

from mev_inspect.schemas import Trace, NestedTrace


def as_nested_traces(traces: List[Trace]) -> List[NestedTrace]:
    """
    Turns a list of Traces into a a tree of NestedTraces
    using their trace addresses

    Right now this has an exponential runtime because we rescan
    most traces at each level of tree depth

    TODO to write a better implementation
    """

    nested_traces = []

    parent = None
    children: List[Trace] = []

    for trace in traces:
        if parent is None:
            parent = trace
            children = []
            continue

        elif not _is_subtrace(trace, parent):
            nested_traces.append(
                NestedTrace(
                    trace=parent,
                    subtraces=as_nested_traces(children),
                )
            )

            parent = trace
            children = []

        else:
            children.append(trace)

    if parent is not None:
        nested_traces.append(
            NestedTrace(
                trace=parent,
                subtraces=as_nested_traces(children),
            )
        )

    return nested_traces


def _is_subtrace(maybe_subtrace: Trace, parent: Trace):
    if len(maybe_subtrace.trace_address) <= len(parent.trace_address):
        return False

    for index, value in enumerate(parent.trace_address):
        if maybe_subtrace.trace_address[index] != value:
            return False

    return True
