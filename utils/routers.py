import time
from typing import Callable
import json
import pprint
from fastapi import Request, Response
from fastapi.routing import APIRoute


def custom_serializer(obj):
    if isinstance(obj, bytes):
        return obj.decode('utf-8')
    else:
        return str(obj)


class TimedRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:                
            start = time.perf_counter()
            response: Response = await original_route_handler(request)
            duration = time.perf_counter() - start

            response.headers["X-Response-Time"] = str(duration)

            request_body = await request.body()
            print(request.scope)
            
            with open("request_log.json", "a") as log_file:
                log_data = {
                    "method": request.method,
                    "url": str(request.url),
                    "headers": dict(request.headers),
                    "request_body": json.loads(request_body) if request_body else None,
                    "response_body": json.loads(response.body),
                    "scope": request.scope,
                }
                log_file.write(json.dumps(request.scope, default=custom_serializer) + "\n")

            print(f"route duration: {duration}")
            print(f"route response: {response}")
            print(f"route response headers: {response.headers}")
            print(f"route response body: {response.body}")
            return response

        return custom_route_handler
