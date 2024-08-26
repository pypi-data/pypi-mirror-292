import re

from helpers.Helper import Helper

text = """
    from fastapi import FastAPI, Request, Header, Body
    from typing import Optional
    from fastapi.responses import JSONResponse, PlainTextResponse

    app = FastAPI()

    @app.get("/tag/{pathParameter1}")
    async def test1(pathParameter1: str):
        # Just comment
        return {"message": "OK"}

    @app.route("/tag/{pathParameter1}/page-{pathParameter2}", methods=["GET", "POST"])
    @app.get("/tag/{pathParameter1}/page-{pathParameter2}/xyz")
    async def test1(
        pathParameter1: str,
        pathParameter2: int,
        queryParameter1: Optional[str] = None,
        queryParameter2: Optional[str] = None,
        headerParameter1: Optional[str] = Header(None),
        headerParameter2: Optional[str] = Header(None),
        requestBody: Optional[dict] = Body(None),
        request: Request
    ):
        content_type = request.headers.get('Content-Type')
        if content_type == 'application/xml':
            return PlainTextResponse(content="<response><message>XML format</message></response>", media_type='application/xml', status_code=415)
        else:
            return JSONResponse(content={"incomes": "data"})  # Replace with actual data

    @app.get("/tag")
    async def test2():
        return {"message": "OK"}

"""

# Loop all api matches
apiPattern = r'''((?:@app\.(?P<httpMethods>\w+)(?P<paths>.*)\n)|(?:def (?P<functionName>\w+)\(\n)|(?:\s*(?P<pathParameters>\w+): \w+,\n)|(?:\s*(?P<queryParameters>\w+):.*= Query.*\n)|(?:\s*(?P<headerParameters>\w+):.*= Header.*\n)|(?:\s*(?P<bodyParameters>\w+):.*= Body.*\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .*, (?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@app\.route|\Z)'''
