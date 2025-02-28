from typing import Annotated, List

from fastapi import APIRouter, HTTPException, Query

from api.lib.elasticsearch.exceptions import IDNotFoundError
from api.models.candidate_models import MatchingCandidate
from api.models.job_models import JobPublic
from api.repositories.job_repository import JobRepositoryDep

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{id}", response_model=JobPublic)
async def get_job(id: int, job_repository: JobRepositoryDep) -> JobPublic:
    """Retrieves a job by a given id

    Args:
        id (int): job id we want to retrieve a job for
        job_repository (JobRepositoryDep): Provides functionality to interact with the job index

    Raises:
        HTTPException: Throws a 404 if entity is not found

    Returns:
        JobPublic: Currently same fields as the document in the elasticsearch index
    """
    try:
        return await job_repository.get_job_by_id(id)
    except IDNotFoundError:
        raise HTTPException(status_code=404)


@router.get("/{id}/candidates", response_model=List[MatchingCandidate])
async def get_jobs_for_candidate(
    id: int,
    job_repository: JobRepositoryDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> List[MatchingCandidate]:
    """Returns a list of matchings jobs for the given candidate

    Args:
        id (int): job id we want to retrieve a job for
        job_repository (JobRepositoryDep): Provides functionality to interact with the job index
        limit (int): maximum number of candidates we want returned

    Raises:
        HTTPException: Throws a 404 if entity is not found

    Returns:
        List[MatchingCandidate]: List of matchings candidates
    """
    try:
        return await job_repository.get_matching_candidates_for_job(id, limit)
    except IDNotFoundError:
        raise HTTPException(status_code=404)
