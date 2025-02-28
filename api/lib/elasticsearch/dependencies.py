from typing import Annotated

from fastapi import Depends

from api.lib.elasticsearch import ElasticsearchClient


# Dependency function to return a fresh client per request
def get_candidates_elasticsearch_client():
    return ElasticsearchClient("candidates")


def get_jobs_elasticsearch_client():
    return ElasticsearchClient("jobs")


# Annotated dependencies for injection into routes
CandidatesElasticsearchDep = Annotated[ElasticsearchClient, Depends(get_candidates_elasticsearch_client)]
JobsElasticsearchDep = Annotated[ElasticsearchClient, Depends(get_jobs_elasticsearch_client)]
