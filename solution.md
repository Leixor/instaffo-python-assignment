# Solution

## How to run my code
You just have to execute `docker compose up -d`

The api and the docs will be available on [localhost:8000](http://localhost:8000) and [localhost:8000/docs](http://localhost:8000/docs) respectively and a test coverage report will be automatically generated into the [tests folder](./api/tests)

## Explanation
### Entrypoint
[main.py](./api/main.py) is the entrypoint that simple serves an app instance and connects the api_router that then in turn serves both routes that are necessary for the task.

### Routes, Repositories and Models
I created [2 separate routers](./api/routes/) that handle the jobs and candidates entities respectively.

The routers each have 2 routes, one "get_by_id" and "get_matching_x_for_y".
The routes themselves only have minimal logic, the real business logic happens in the [repository layer](./api/repositories/) to decouple the concerns of api handling and elasticsearch communication.

[Models](./api/models) are defined separately for pydantic models, currently we use the same model for the api output and the elasticsearch document itself, later on they probably will be 2 separate pydantic models that we have to map then.

### Dockerfile and docker-compose.yml changes
Had to create a simple [Dockerfile](./api/Dockerfile). Just installed poetry and ran poetry install for the most part. Uses fastapi run instead of uvicorn over the cli, as fastapi run uses uvicorn under the hood already, but could also use other servers if wanted.

Than added 2 new services to the [docker-compose.yml](./docker-compose.yml), the api itself and a pod that runs the test and creates the test coverage in the [tests folder](./api/tests/), also saving it to the file system as this folder is mounted to the local file system, so you don't have to look into the docker container itself to see the test coverage etc.

### Formatting, Linting and Typechecking
Pretty standard stack with ruff as formater and linter and pyright for typechecking.

### Tests
Pretty simple tests, can say I struggled a bit with the async event loop in this case as I created the elasticsearch dependency wrong at the beginning, got it running at the end though.

The tests itself are pretty simplistic api integration tests, only showcasing basic fixture usage and assertions for now.
We could mock different parts of the pipeline, but later on we probably would have an elasticsearch instance or something compatible running in the ci/cd pipeline anyway, so it should be fine for now.

## What was ommited?
### Auth
Authentication and Authorization was ommited for one main reason (besides scope of the task). 


**Having an api that returns any given candidate or job by id doesn't make sense with the current information in the documents.***

Besides Authentication which could be implemented with a jwt (if users would be present in a database) or a bearer token for general api safety, Authorization is impossible as long as we can't check if the user is actually authorized. We would have to add user_ids to the specific documents or authorize them through another api.


### Excessive Inheritance
Currently the code has a lot of "seemingly" duplicate code. The routes, repositories and models are mostly copy paste, as are the tests. But in a real life production scenario, having two separte routers with different respositories makes it way more mantainable. Right now there isn't much difference between the 2 routes/repositories etc, but with real candidates and jobs this wil certainly change. More differences in the document structures, different filters and implementations for each etc.

So for this simple task I could have made it work with inheritance, but this wouldn't showcase how I would do it in a real life scenario.


### Factories and custom seeders for the tests
I just used the seeder structure that was already given. This makes testing filters separately over api tests currently not really possible besides cherrypicking one of the given documents. With factories or custom seeders we could create different scenarios for different filters and entities. Just ommited because of scope.