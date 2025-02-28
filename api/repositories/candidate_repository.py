from typing import Annotated, List

from fastapi import Depends, HTTPException

from api.lib.elasticsearch.dependencies import (
    CandidatesElasticsearchDep,
    JobsElasticsearchDep,
)
from api.models.candidate_models import CandidatePublic
from api.models.job_models import MatchingJob


class CandidateRepository:
    """Has functionality for interacting with the candidates entity via elasticsearch in this case."""

    def __init__(
        self,
        candidates_es_client: CandidatesElasticsearchDep,
        jobs_es_client: JobsElasticsearchDep,
    ):
        """
        Args:
            candidates_es_client (CandidatesElasticsearchDep): Elasticsearch instance that can query the candidates index
            jobs_es_client (JobsElasticsearchDep): Elasticsearch instance that can query the jobs index
        """
        self.candidate_es_client = candidates_es_client
        self.enquiries_es_client = jobs_es_client

    async def get_candidate_by_id(self, candidate_id: int) -> CandidatePublic:
        """Returns a candidate for the given id in an api resource compatible format
        We could map the document that we retrieve from elasticsearch into its own pydantic model

        Args:
            candidate_id (int): id of the wanted candidate

        Returns:
            CandidatePublic: candidate in an api compatible format
        """
        return CandidatePublic.model_validate(await self.candidate_es_client.get_entity(id=candidate_id))

    async def get_matching_jobs_for_candidate(self, candidate_id: int, limit: int) -> List[MatchingJob]:
        """Retrieves matching jobs for a given candidate_id.
        Currently filters by salary, seniorty and top_skills of the given candidate.
        Only one of the filters has to be fulfilled.

        Args:
            candidate_id (int): id of the candidate we want fitting jobs for
            limit (int): maximum number of fitting jobs we want returned

        Raises:
            HTTPException: raises a 500 in case that querying or formatting goes wrong

        Returns:
            List[MatchingJob]: a list of matching jobs
        """
        candidate = await self.get_candidate_by_id(candidate_id)

        try:
            jobs = await self.enquiries_es_client.search_with_bool_queries(
                should_queries=self._extract_queries_from_candidate(candidate),
                size=limit,
            )
            return self._extract_jobs_from_es_response(jobs.body)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching jobs: {str(e)}")

    def _extract_queries_from_candidate(self, candidate: CandidatePublic) -> List[dict]:
        """Extracts all relevant query components for our elasticsearch query from the candidate object.
        Currently returns the following filters:
            - salary_match_query
            - seniority_match_query
            - top_skills_query

        Args:
            candidate (CandidatePublic): candidate from which the information for the queries will be extracted

        Returns:
            List[dict]: A list of queries that can be used for a should or must query.
                Could also be done as a named dict or tuple if wanted
        """
        salary_match_query = {"range": {"max_salary": {"gte": candidate.salary_expectation}}}
        seniority_match_query = {"term": {"seniorities": candidate.seniority}}
        top_skill_match_query = {
            "terms_set": {
                "top_skills": {
                    "terms": candidate.top_skills,
                    "minimum_should_match": min(2, len(candidate.top_skills)),
                },
            },
        }

        return [salary_match_query, seniority_match_query, top_skill_match_query]

    def _extract_jobs_from_es_response(self, response: dict) -> List[MatchingJob]:
        """Extracts jobs from a elasticsearch response.

        Args:
            response (dict): An elasticsearch response

        Returns:
            List[MatchingJob]: List of matchings jobs that gets extracted. Contains id and relevant_score for now
        """
        hits = response.get("hits", {}).get("hits", [])

        return [
            MatchingJob.model_validate({"id": job.get("_id"), "relevance_score": job.get("_score")}) for job in hits
        ]


def get_candidate_repository(
    candidates_es_client: CandidatesElasticsearchDep,
    jobs_es_client: JobsElasticsearchDep,
) -> CandidateRepository:
    return CandidateRepository(candidates_es_client, jobs_es_client)


CandidateRepositoryDep = Annotated[CandidateRepository, Depends(get_candidate_repository)]
