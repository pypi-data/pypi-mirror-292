from typing import Dict, List, Optional

from pydantic import BaseModel

class V1Job(BaseModel):
    id: str
    owner_id: str
    type: str
    status: str
    runtime: str
    name: str
    namespace: Optional[str] = None
    logs: Optional[str] = None
    result: Optional[str] = None
    created: float
    updated: float
    finished: float
    metadata: Dict[str, str] = {}


class V1Jobs(BaseModel):
    jobs: List[V1Job]


class V1UserProfile(BaseModel):
    email: str
    display_name: Optional[str] = None
    handle: Optional[str] = None
    picture: Optional[str] = None
    created: Optional[int] = None
    updated: Optional[int] = None
    token: Optional[str] = None