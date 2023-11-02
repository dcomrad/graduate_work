from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

app = FastAPI(
    title='My API',
    docs_url='/api/v1/openapi',
    openapi_url='/api/v1/openapi.json',
    default_response_class=ORJSONResponse,
)
