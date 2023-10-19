import orjson


def orjson_dumps(v, *, default):  # noqa:VNE001
    return orjson.dumps(v, default=default).decode()


class JSONMixin:
    json_loads = orjson.loads
    json_dumps = orjson_dumps
