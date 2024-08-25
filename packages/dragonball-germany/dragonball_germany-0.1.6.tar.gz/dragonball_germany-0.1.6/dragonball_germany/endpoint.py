from pydantic import BaseModel


class Endpoint(BaseModel):
    '''
    Represents an endpoint for a service.

    Attributes:
        service_name (str):
            The name of the service that the endpoint belongs to.
        port (int):
            The port number on which the service is available. Default is 10000
        path (str):
            The path of the endpoint within the service.
        method (str):
            The HTTP method used for requests to the endpoint (e.g., 'GET', 'POST').
        required_session (bool):
            Indicates whether a session is required to access this endpoint. Default is True.
    '''

    service_name: str
    port: int = 10000
    path: str
    method: str
    required_session: bool = True
