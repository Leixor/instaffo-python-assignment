from typing import Annotated, List

from fastapi import Depends, HTTPException

from api.lib.elasticsearch.dependencies import (
    CandidatesElasticsearchDep,
    JobsElasticsearchDep,
)
from api.models.candidate_models import MatchingCandidate
from api.models.job_models import JobPublic


class JobRepository:
    """Has functionality for interacting with the jobs entity via elasticsearch in this case."""

    def __init__(
        self,
        candidates_es_client: CandidatesElasticsearchDep,
        jobs_es_client: JobsElasticsearchDep,
    ):
        self.candidate_es_client = candidates_es_client
        self.enquiries_es_client = jobs_es_client

    async def get_job_by_id(self, job_id: int) -> JobPublic:
        """Returns a job for the given id in an api resource compatible format
        We could map the document that we retrieve from elasticsearch into its own pydantic model

        Args:
            job_id (int): id of the wanted job

        Returns:
            JobPublic: job in an api compatible format
        """
        return JobPublic.model_validate(await self.enquiries_es_client.get_entity(id=job_id))

    async def get_matching_candidates_for_job(self, job_id: int, limit: int) -> List[MatchingCandidate]:
        """Retrieves matching candidates for a given job_id.
        Currently filters by salary, seniorty and top_skills of the given job.
        Only one of the filters has to be fulfilled.

        Args:
            job_id (int): id of the job we want fitting candidates for
            limit (int): maximum number of fitting candidates we want returned

        Raises:
            HTTPException: raises a 500 in case that querying or formatting goes wrong

        Returns:
            List[MatchingCandidate]: a list of matching candidates
        """
        job = await self.get_job_by_id(job_id)

        try:
            jobs = await self.candidate_es_client.search_with_bool_queries(
                should_queries=self._extract_queries_from_job(job),
                size=limit,
            )
            return self._extract_candidates_from_es_response(jobs.body)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching jobs: {str(e)}")

    def _extract_queries_from_job(self, job: JobPublic):
        """Extracts all relevant query components for our elasticsearch query from the job object.
        Currently returns the following filters:
            - salary_match_query
            - seniority_match_query
            - top_skills_query

        Args:
            job (JobPublic): job from which the information for the queries will be extracted

        Returns:
            List[dict]: A list of queries that can be used for a should or must query.
                Could also be done as a named dict or tuple if wanted
        """
        salary_match_query = {"range": {"salary_expectation": {"lte": job.max_salary}}}
        seniority_match_query = {"terms": {"seniority": job.seniorities}}
        top_skill_match_query = {
            "terms_set": {
                "top_skills": {"terms": job.top_skills, "minimum_should_match": min(2, len(job.top_skills))},
            },
        }

        return [salary_match_query, seniority_match_query, top_skill_match_query]

    def _extract_candidates_from_es_response(self, response: dict) -> List[MatchingCandidate]:
        """Extracts candidates from a elasticsearch response.

        Args:
            response (dict): An elasticsearch response

        Returns:
            List[MatchingCandidate]: List of matchings candidates that gets extracted. Contains id and relevant_score for now
        """
        hits = response.get("hits", {}).get("hits", [])

        return [
            MatchingCandidate.model_validate({"id": job.get("_id"), "relevance_score": job.get("_score")})
            for job in hits
        ]


def get_job_repository(
    candidates_es_client: CandidatesElasticsearchDep,
    jobs_es_client: JobsElasticsearchDep,
) -> JobRepository:
    return JobRepository(candidates_es_client, jobs_es_client)


JobRepositoryDep = Annotated[JobRepository, Depends(get_job_repository)]
