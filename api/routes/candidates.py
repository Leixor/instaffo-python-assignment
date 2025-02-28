from typing import Annotated, List

from fastapi import APIRouter, HTTPException, Query

from api.lib.elasticsearch.exceptions import IDNotFoundError
from api.models.candidate_models import CandidatePublic
from api.models.job_models import MatchingJob
from api.repositories.candidate_repository import CandidateRepositoryDep

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("/{id}", response_model=CandidatePublic)
async def get_candidate_by_id(id: int, candidate_repository: CandidateRepositoryDep) -> CandidatePublic:
    """Retrieves a candidate by a given id

    Args:
        id (int): candidate id we want to retrieve a candidate for
        candidate_repository (CandidateRepositoryDep): Provides functionality to interact with the candidates index

    Raises:
        HTTPException: Throws a 404 if entity is not found

    Returns:
        CandidatePublic: Currently same fields as the document in the elasticsearch index
    """
    try:
        return await candidate_repository.get_candidate_by_id(id)
    except IDNotFoundError:
        raise HTTPException(status_code=404)


@router.get("/{id}/jobs", response_model=List[MatchingJob])
async def get_jobs_for_candidate(
    id: int,
    candidate_repository: CandidateRepositoryDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> List[MatchingJob]:
    """Returns a list of matchings jobs for the given candidate

    Args:
        id (int): candidate id we want to retrieve a candidate for
        candidate_repository (CandidateRepositoryDep): Provides functionality to interact with the candidates index
        limit (int): maximum number of jobs we want returned

    Raises:
        HTTPException: Throws a 404 if entity is not found

    Returns:
        List[MatchingJob]: List of matchings jobs
    """
    try:
        return await candidate_repository.get_matching_jobs_for_candidate(id, limit)
    except IDNotFoundError:
        raise HTTPException(status_code=404)
