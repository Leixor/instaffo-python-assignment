from pydantic import BaseModel


class BaseMatching(BaseModel):
    """Represents the most important attributes of a matching between a job and a candidate"""

    id: int
    relevance_score: float
