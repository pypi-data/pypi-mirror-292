from typing import Optional
from pydantic import BaseModel


class ConfFetcherRequest(BaseModel):
    job_id: str
    customer_id: str
    merge_with: Optional[str] = None
