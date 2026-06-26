from enum import StrEnum

class HostStatus(StrEnum):
    """The reachability state of a scanned host as reported by nmap.

    Attributes:
        UP: The host responded and is up.
        DOWN: The host did not respond and is considered down.
        UNKNOWN: The host's state could not be determined.
    """

    UP = "up"
    DOWN = "down"
    UNKNOWN = "unknown"


class PortStatus(StrEnum):
    """The state of a scanned port as reported by nmap.

    Attributes:
        OPEN: The port is open and accepting connections.
        CLOSED: The port is reachable but no service is listening. FILTERED: The state could not be determined (e.g. firewalled). UNFILTERED: Reachable, but open versus closed could not be determined.
        OPEN_FILTERED: Could not determine whether the port is open or filtered.
        CLOSED_FILTERED: Could not determine whether the port is closed or filtered.
    """

    OPEN = "open"
    CLOSED = "closed"
    FILTERED = "filtered"
    UNFILTERED = "unfiltered"
    OPEN_FILTERED = "open|filtered"
    CLOSED_FILTERED = "closed|filtered"


class Severity(StrEnum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

