import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse


app = FastAPI(
    title='My API',
    docs_url='/api/v1/openapi',
    openapi_url='/api/v1/openapi.json',
    default_response_class=ORJSONResponse,
)


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=9900,
    )
