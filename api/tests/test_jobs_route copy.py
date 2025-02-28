import pytest
from httpx import AsyncClient

from api.lib.elasticsearch.elastic_search_client import ElasticsearchClient
from api.models.candidate_models import CandidatePublic, MatchingCandidate
from api.models.job_models import JobPublic

existing_job_id = 1
non_existing_job_id = 99999

pytestmark = pytest.mark.anyio


class TestGetJobById:
    async def test_get_job_by_id(
        self,
        client: AsyncClient,
    ):
        response = await client.get(f"/jobs/{existing_job_id}")
        assert response.status_code == 200
        assert response.json() == {
            "top_skills": ["C#", "WPF", "Angular"],
            "other_skills": [
                ".NET",
                "Agile Softwareentwicklung",
                "Clean Code Development",
                "Software Engineering",
                "Softwareentwicklung",
                "Cuda",
                "Bildverarbeitung",
                "HL7",
                "Dicom",
                "Algorithmen",
            ],
            "seniorities": ["midlevel", "senior"],
            "max_salary": 75000,
        }

    async def test_get_job_by_id_not_found(self, client):
        response = await client.get(f"/jobs/{non_existing_job_id}")
        assert response.status_code == 404


class TestGetMatchingCandidatesForJob:
    async def test_get_matching_jobs_fulfills_at_least_one_filter(
        self, client: AsyncClient, candidates_es_client: ElasticsearchClient, jobs_es_client: ElasticsearchClient
    ):
        """Checks that the limit and the overall query conditions work.
        This test could be improved by:
            - Using factories or custom seeders to only match certain entities with certain filters, currently we don't test individual filters but just overall
            - Test the min 2 skills conditions for top_skills
            - Test behaviour when
        """
        # Setup
        job = JobPublic.model_validate(await jobs_es_client.get_entity(id=existing_job_id))
        limit = 15

        # Asserting that we succesfully retrieve candidates and that the number of candidates is correct
        response = await client.get(f"/jobs/{existing_job_id}/candidates?limit={limit}")
        assert response.status_code == 200
        matching_candidates = response.json()
        assert len(matching_candidates) == limit

        for matching_candidate in matching_candidates:
            matching_candidate = MatchingCandidate.model_validate(matching_candidate)
            candidate = CandidatePublic.model_validate(await candidates_es_client.get_entity(id=matching_candidate.id))

            # All possible conditions
            salary_match = candidate.salary_expectation <= job.max_salary
            seniority_match = candidate.seniority in job.seniorities
            top_skills_match = len(set(candidate.top_skills) & set(job.top_skills)) >= min(2, len(candidate.top_skills))

            # At least one has to be true
            assert salary_match or seniority_match or top_skills_match

    async def test_get_matching_jobs_for_candidate_not_found(self, client: AsyncClient):
        response = await client.get(f"/jobs/{non_existing_job_id}/candidates")
        assert response.status_code == 404
