import re

from helpers.Helper import Helper

text = """
package main

import (
    "net/http"
    "github.com/gin-gonic/gin"
)

func test1(c *gin.Context) {
    pathParameter1 := c.Param("pathParameter1")
    pathParameter2 := c.Param("pathParameter2")

    queryParameter1 := c.DefaultQuery("queryParameter1", "")
    queryParameter2 := c.DefaultQuery("queryParameter2", "")

    headerParameter1 := c.Request.Header.Get("headerParameter1")
    headerParameter2 := c.Request.Header.Get("headerParameter2")

    var requestBody YourRequestBodyClass
    if err := c.BindJSON(&requestBody); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    contentType := c.Request.Header.Get("Content-Type")

    switch contentType {
    case "application/xml":
        c.XML(http.StatusUnsupportedMediaType, "<response><message>XML format</message></response>")
    default:
        c.JSON(http.StatusOK, incomes) // Replace `incomes` with your data
    }
}

func test2(c *gin.Context) {
    c.Status(http.StatusOK)
}

func main() {
    r := gin.Default()
    r.GET("/tag/:pathParameter1", test1)
    r.GET("/tag/:pathParameter1/page-:pathParameter2", test1)
    r.POST("/tag/:pathParameter1/page-:pathParameter2/xyz", test1)
    r.GET("/tag", test2)
    r.Run()
}

"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
