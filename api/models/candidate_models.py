from typing import List

from pydantic import BaseModel

from api.models.matching_models import BaseMatching


class CandidatePublic(BaseModel):
    """
    We could differentiate between a resource model exclusive api communication and a model for the es document itself. Right now they are the same and just ommited to keep it simpler for now.
    """

    top_skills: List[str]
    other_skills: List[str]
    seniority: str
    salary_expectation: int


class MatchingCandidate(BaseMatching):
    """
    Just inheriting now cause later on we could have different looking matchings depending on
    the desired output of the apis, else we could use BaseMatching directly
    """
