from http import HTTPStatus

import pytest


@pytest.mark.parametrize(
    "queue_name, query_body",
    [
        (
            "important",
            {
                "template_id": "9ab9df5e-c1a8-49fe-aca3-2462fdfc58e8",
                "receivers": [
                    "d05a3d39-622e-4da9-9a89-850b53ccea4d",
                    "528e7dc0-4998-41ad-8228-23de6fe7d9f0",
                    "e8106412-0cb9-422c-b5c3-0353a010f0a8",
                ],
                "vars": {"movie_id": "c05a3d39-622e-4da9-9a89-850b53ccea4d"},
                "type": "email",
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_actor(make_publish_request, queue_name: str, query_body: dict):
    status = await make_publish_request(queue_name, query_body)
    assert status == HTTPStatus.OK
