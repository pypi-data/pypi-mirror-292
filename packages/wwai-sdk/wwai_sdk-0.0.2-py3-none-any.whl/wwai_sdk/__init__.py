from wwai_sdk.wwai_client import WwaiClient


def create_client(
        grant_type,
        server="http://ai.api.wwai.wwxckj.com",
        authorization: str = None,
        username=None,
        password=None,
        tenant_code=None,
        client_id=None,
        client_secret=None,
        cache_type="local",
        redis_host=None,
        redis_port=6379,
        redis_password=None,
        redis_db=0
):
    if grant_type == "password":
        authorization = 'Basic d3dhaTptem5lc2hhaXlxam94dGRmdXJwd2NrZ3ZibG5icmt1cQ=='
    if authorization is not None and authorization != "" and not authorization.startswith("Basic "):
        authorization = "Basic " + authorization

    client = WwaiClient(
        grant_type=grant_type,
        server=server,
        authorization=authorization,
        username=username,
        password=password,
        tenant_code=tenant_code,
        client_id=client_id,
        client_secret=client_secret,
        cache_type=cache_type,
        redis_host=redis_host,
        redis_port=redis_port,
        redis_password=redis_password,
        redis_db=redis_db
    )
    return client
