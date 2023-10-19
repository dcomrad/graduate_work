import asyncpg
import pytest_asyncio
from tests.functional.settings import test_settings


@pytest_asyncio.fixture(scope="session")
async def db_connection():
    postgres = test_settings.postgres
    conn = await asyncpg.connect(
        host=postgres.host,
        port=postgres.port,
        user=postgres.user,
        password=postgres.password,
        database=postgres.db_name,
        server_settings={'search_path': postgres.search_path}
    )
    yield conn
    conn.close()


@pytest_asyncio.fixture(scope='session')
async def make_db_request(db_connection):
    async def inner(method: str, sql: str):
        allowed_methods = {
            'EXECUTE': 'EXECUTE',
            'FETCHALL': 'FETCH',
            'FETCHONE': 'FETCHROW'
        }
        if method not in allowed_methods:
            raise ValueError(f'Method should be one of the allowed: {allowed_methods.keys()}')

        method = allowed_methods[method]
        caller = getattr(db_connection, method.lower())
        return await caller(sql)
    return inner


@pytest_asyncio.fixture(scope='session')
async def clear_data(make_db_request):
    async def inner():
        sql = """
        DELETE FROM "role_permission" CASCADE;
        DELETE FROM "user_role" CASCADE;
        DELETE FROM "access_history" CASCADE;
        DELETE FROM "user" CASCADE;
        DELETE FROM "role" CASCADE;
        DELETE FROM "permission" CASCADE;
        """
        await make_db_request('EXECUTE', sql)
    return inner


@pytest_asyncio.fixture(scope='session', autouse=True)
async def db_init(
        create_user,
        create_role,
        create_permission,
        create_user_role_relation,
        create_role_permission_relation,
        clear_data
):
    hashed_password = 'sha256$4096$24326224313224656e414259665a6d5048495169485036503430664d2e$6a0454bb533a8c7b6cbb4f3b76da05d5ee9a95eb26e17016ea056ab69e036502'
    await create_user(10001, 'test_user_1', hashed_password, False, 'test user with permissions')
    await create_role(10001, 'management_role', 'management role for tests')
    await create_permission(10001, 'access_management', 'access_management permission')
    await create_permission(10002, 'users_management', 'users_management permission')
    await create_user_role_relation(10001, 10001)
    await create_role_permission_relation(10001, 10001)
    await create_role_permission_relation(10001, 10002)
    yield
    await clear_data()


@pytest_asyncio.fixture(scope='session')
async def create_user(make_db_request):
    async def inner(
            id: int,
            login: str,
            hashed_password: str,
            is_superuser: bool = False,
            full_name: str = 'Ivan'
    ):
        sql = f"""
        INSERT INTO "user" VALUES ({id}, '{login}', '{hashed_password}', {is_superuser}, '{full_name}');
        """
        await make_db_request('EXECUTE', sql)

    return inner


@pytest_asyncio.fixture(scope='session')
async def create_role(make_db_request):
    async def inner(
            id: int,
            name: str,
            description: str = 'no_description',
    ):
        sql = f"""
        INSERT INTO "role" VALUES ({id}, '{name}', '{description}');
        """
        await make_db_request('EXECUTE', sql)

    return inner


@pytest_asyncio.fixture(scope='session')
async def create_permission(make_db_request):
    async def inner(
            id: int,
            name: str,
            description: str = 'no_description',
    ):
        sql = f"""
        INSERT INTO "permission" VALUES ({id}, '{name}', '{description}');
        """
        await make_db_request('EXECUTE', sql)

    return inner


@pytest_asyncio.fixture(scope='session')
async def create_user_role_relation(make_db_request):
    async def inner(
            user_id: int,
            role_id: int,
    ):
        sql = f"""INSERT INTO "user_role" VALUES ({user_id}, {role_id});"""
        await make_db_request('EXECUTE', sql)

    return inner


@pytest_asyncio.fixture(scope='session')
async def create_role_permission_relation(make_db_request):
    async def inner(
            role_id: int,
            permission_id: int,
    ):
        sql = f"""INSERT INTO "role_permission" VALUES ({role_id}, {permission_id});"""
        await make_db_request('EXECUTE', sql)

    return inner
