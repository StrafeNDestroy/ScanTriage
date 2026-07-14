from typing import Protocol, Callable
from scantriage.domain.schema import Finding, TriageResult

class TriageModel(Protocol):
    """ Port:  
        Any model that can take in the `Findings` and prompt into 
        trigaging and outputting a TriageResult
    """
    def triage(self, findings: list[Finding]) -> list[tuple[Finding,TriageResult]]:
        ...






