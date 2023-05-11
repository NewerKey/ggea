import fastapi


async def http_exc_500_internal_server_error(msg: str) -> Exception:
    """
    The HyperText Transfer Protocol (HTTP) 400 Bad Request response status code indicates that the server
    cannot or will not process the request due to something that is perceivedto be a client error
    (for example, malformed request syntax, invalid request message framing, or deceptive request routing).
    """  
    return fastapi.HTTPException(
        status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=msg,
    )