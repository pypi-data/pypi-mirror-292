import re

from helpers.Helper import Helper

text = """
package main

import (
    "net/http"
    "github.com/labstack/echo/v4"
)

func test1(c echo.Context) error {
    pathParameter1 := c.Param("pathParameter1")
    pathParameter2 := c.Param("pathParameter2")

    queryParameter1 := c.QueryParam("queryParameter1")
    queryParameter2 := c.QueryParam("queryParameter2")

    headerParameter1 := c.Request().Header.Get("headerParameter1")
    headerParameter2 := c.Request().Header.Get("headerParameter2")

    var requestBody YourRequestBodyClass
    if err := c.Bind(&requestBody); err != nil {
        return err
    }

    contentType := c.Request().Header.Get("Content-Type")

    switch contentType {
    case "application/xml":
        return c.XML(http.StatusUnsupportedMediaType, "<response><message>XML format</message></response>")
    default:
        return c.JSON(http.StatusOK, incomes) // Replace `incomes` with your data
    }
}

func test2(c echo.Context) error {
    return c.NoContent(http.StatusOK)
}

func main() {
    e := echo.New()
    e.GET("/tag/:pathParameter1", test1)
    e.GET("/tag/:pathParameter1/page-:pathParameter2", test1)
    e.POST("/tag/:pathParameter1/page-:pathParameter2/xyz", test1)
    e.GET("/tag", test2)
    e.Start(":8080")
}


"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
