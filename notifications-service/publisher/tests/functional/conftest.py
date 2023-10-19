import asyncio
import json
from pathlib import Path

import aio_pika
import aiohttp
import pytest
from dotenv import dotenv_values
from elasticsearch import AsyncElasticsearch
from pydantic import BaseSettings


@pytest.fixture
async def make_publish_request():
    async def inner(queue_name, query_body):
        async with aiohttp.ClientSession() as session:
            url = "http://localhost/api/v1/publish/{queue_name}"
            answers = []
            async with session.post(url, body=query_body) as response:
                body = await response.json()
                status = response.status
                return status

    return inner
