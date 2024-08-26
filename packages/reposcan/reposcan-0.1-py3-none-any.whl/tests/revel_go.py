import re

from helpers.Helper import Helper

text = """
package controllers

import (
    "net/http"
    "github.com/revel/revel"
)

type MyController struct {
    revel.Controller
}

func (c MyController) Test1(pathParameter1 string, pathParameter2 int) revel.Result {
    queryParameter1 := c.Params.Get("queryParameter1")
    queryParameter2 := c.Params.Get("queryParameter2")

    headerParameter1 := c.Request.Header.Get("headerParameter1")
    headerParameter2 := c.Request.Header.Get("headerParameter2")

    var requestBody YourRequestBodyClass
    if err := c.Params.BindJSON(&requestBody); err != nil {
        return c.BadRequest(err)
    }

    contentType := c.Request.Header.Get("Content-Type")

    switch contentType {
    case "application/xml":
        return c.RenderText("<response><message>XML format</message></response>").Code(415)
    default:
        return c.RenderJSON(incomes) // Replace `incomes` with your data
    }
}

func (c MyController) Test2() revel.Result {
    return c.RenderText("")
}

"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
