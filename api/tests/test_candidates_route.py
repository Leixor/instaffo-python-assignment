import pytest
from httpx import AsyncClient

from api.lib.elasticsearch.elastic_search_client import ElasticsearchClient
from api.models.candidate_models import CandidatePublic
from api.models.job_models import JobPublic, MatchingJob

existing_candidate_id = 201
non_existing_candidate_id = 99999

pytestmark = pytest.mark.anyio


class TestGetCandidateById:
    async def test_get_candidate_by_id(self, client: AsyncClient):
        response = await client.get(f"/candidates/{existing_candidate_id}")
        assert response.status_code == 200
        assert response.json() == {
            "top_skills": ["Python", "AWS", "Docker"],
            "other_skills": [],
            "seniority": "junior",
            "salary_expectation": 55000,
        }

    async def test_get_candidate_by_id_not_found(self, client):
        response = await client.get(f"/candidates/{non_existing_candidate_id}")
        assert response.status_code == 404


class TestGetMatchingJobsForCandidate:
    async def test_get_matching_jobs_fulfills_at_least_one_filter(
        self, client: AsyncClient, candidates_es_client: ElasticsearchClient, jobs_es_client: ElasticsearchClient
    ):
        # Setup
        candidate = CandidatePublic.model_validate(await candidates_es_client.get_entity(id=existing_candidate_id))
        limit = 15

        # Asserting that we succesfully retrieve jobs and that the number of jobs is correct
        response = await client.get(f"/candidates/{existing_candidate_id}/jobs?limit={limit}")
        assert response.status_code == 200
        matching_jobs = response.json()
        assert len(matching_jobs) == limit

        for matching_job in matching_jobs:
            matching_job = MatchingJob.model_validate(matching_job)
            job = JobPublic.model_validate(await jobs_es_client.get_entity(id=matching_job.id))

            # All possible conditions
            salary_match = candidate.salary_expectation <= job.max_salary
            seniority_match = candidate.seniority in job.seniorities
            top_skills_match = len(set(candidate.top_skills) & set(job.top_skills)) >= min(2, len(candidate.top_skills))

            # At least one has to be true
            assert salary_match or seniority_match or top_skills_match

    async def test_get_matching_jobs_for_candidate_not_found(self, client: AsyncClient):
        response = await client.get(f"/candidates/{non_existing_candidate_id}/jobs")
        assert response.status_code == 404
