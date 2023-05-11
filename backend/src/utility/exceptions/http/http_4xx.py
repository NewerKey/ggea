import fastapi


async def http_exc_400_bad_request(msg: str) -> Exception:
    """
    The HyperText Transfer Protocol (HTTP) 400 Bad Request response status code indicates that the server
    cannot or will not process the request due to something that is perceivedto be a client error
    (for example, malformed request syntax, invalid request message framing, or deceptive request routing).
    """  
    return fastapi.HTTPException(
        status_code=fastapi.status.HTTP_400_BAD_REQUEST,
        detail=msg,
    )

async def http_exc_401_unauthorized_request(msg: str) -> Exception:
    """
    The HyperText Transfer Protocol (HTTP) 401 Unauthorized response status code indicates that the client
    request has not been completed because it lacks valid authentication credentials for the requested resource.
    """
    return fastapi.HTTPException(
        status_code=fastapi.status.HTTP_400_BAD_REQUEST,
        detail=msg,
    )

async def http_exc_403_forbidden_request(msg: str) -> Exception:
    """
    The HTTP 403 Forbidden response status code indicates that the server understands the request but refuses to authorize it.
    """
    return fastapi.HTTPException(
        status_code=fastapi.status.HTTP_403_FORBIDDEN,
        detail=msg,
    )

async def http_exc_404_resource_not_found(msg: str) -> Exception:
    """
    The HTTP 404 Not Found response status code indicates that the server cannot find the requested resource.
    """
    return fastapi.HTTPException(
        status_code=fastapi.status.HTTP_404_NOT_FOUND,
        detail=msg,
    )