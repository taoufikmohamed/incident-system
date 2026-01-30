from typing_extensions import TypedDict

class Incident(TypedDict):
    host: str
    source: str
    event_id: int
    level: str
    message: str
    timestamp: str
