from fastapi import Request


def get_req_id(request: Request) -> str:
    return request.state.req_id
