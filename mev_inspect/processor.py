from itertools import groupby
from typing import List, Optional

from mev_inspect.schemas import Action, Block, NestedTrace, UnknownAction
from mev_inspect.traces import as_nested_traces


class Processor:
    def __init__(self, inspectors) -> None:
        self.inspectors = inspectors

    def get_transaction_evaluations(self, block: Block) -> List[Action]:
        actions: List[Action] = []

        for _, traces in groupby(block.calls, lambda t: t.transaction_hash):
            nested_traces: List[NestedTrace] = as_nested_traces(traces)

            for nested_trace in nested_traces:
                action = self._inspect_trace(nested_trace)
                actions.append(action)

        return actions

    def _inspect_trace(self, trace: NestedTrace) -> Action:
        action = self._run_inspectors(trace)

        if action is not None:
            return action
        else:
            internal_actions = [
                self._inspect_trace(subtrace) for subtrace in trace.subtraces
            ]

            return UnknownAction(
                trace=trace.trace,
                internal_actions=internal_actions,
            )

    def _run_inspectors(self, trace: NestedTrace) -> Optional[Action]:
        for inspector in self.inspectors:
            action = inspector.inspect(trace)

            if action is not None:
                return action

        return None
