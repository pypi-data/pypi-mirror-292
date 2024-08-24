import asyncio
import json
import os

import httpx

from .endpoint import Endpoint


class Gateway:
    '''
    A class to interact with a gateway server for registering endpoints.
    '''

    def __init__(
        self, host: str | None = None, port: int | None = None, token: str | None = None
    ) -> None:
        '''
        Initializes the Gateway with the specified host, port, and token.

        Args:
            host (str | None):
                The host address of the gateway.
                If None, uses the environment variable 'GATEWAY_HOST'.
                If the environment variable is not set, defaults to 'localhost'.
            port (int | None):
                The port number of the gateway.
                If None, uses the environment variable 'GATEWAY_PORT'.
                If the environment variable is not set, defaults to 10000.
            token (str | None):
                The authentication token for the gateway.
                If None, uses the environment variable 'GATEWAY_TOKEN'.
                If the environment variable is not set, defaults to 'token'.
        '''

        self.host: str = host if host else os.getenv('GATEWAY_HOST', 'localhost')
        self.port: int = port if port else int(os.getenv('GATEWAY_PORT', '10000'))
        self.token: str = token if token else os.getenv('GATEWAY_TOKEN', 'token')
        self.register_endpoints_path: str = 'register-endpoints'

    @property
    def url(self) -> str:
        '''
        Constructs the base URL for the gateway server.

        Returns:
            str: The base URL for the gateway server.
        '''

        return f'http://{self.host}:{self.port}/'

    @property
    def register_endpoints_url(self) -> str:
        '''
        Constructs the full URL for endpoint registration.

        Returns:
            str: The full URL for the endpoint registration path.
        '''

        return f'{self.url}{self.register_endpoints_path}'

    async def register_endpoints(
        self, endpoints: list[Endpoint], interval: int | None = 10
    ) -> None:
        '''
        Continuously registers the specified endpoints with the gateway at regular intervals.

        Args:
            endpoints (list[Endpoint]):
                A list of Endpoint objects to be registered.
            interval (int | None):
                The time interval in seconds between registration attempts.
                If None, registration will be attempted only once.

        Raises:
            Exception:
                If an error occurs during registration.
        '''

        while True:
            try:
                print(f'Gateway url: {self.url}')
                print(f'Gateway token: {self.token}')
                print('Endpoints:')
                [print(f'   - {endpoint}') for endpoint in endpoints]

                async with httpx.AsyncClient() as client:
                    client.headers = {'X-Gateway-Token': self.token}
                    client.follow_redirects = False
                    response: httpx.Response = await client.request(
                        method='POST',
                        url=self.url,
                        content=json.dumps([e.model_dump() for e in endpoints]),
                    )

                    if not response.status_code == 200:
                        if interval is None:
                            print(f'Gateway error : {response.json()}')
                        else:
                            print(
                                f'Gateway error : {response.json()}, retry after {interval} seconds'
                            )
                        continue

                    print(f'Sending Endpoints to Gateway, next in {interval} seconds')
            except Exception as e:
                if interval is None:
                    print(f'Gateway Exception: {e}')
                else:
                    print(f'Gateway Exception: {e}, retry after {interval} seconds')

            if interval is None:
                break
            await asyncio.sleep(interval)
