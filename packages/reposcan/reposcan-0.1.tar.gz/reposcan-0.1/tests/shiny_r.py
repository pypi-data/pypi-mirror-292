import re

from helpers.Helper import Helper

text = """
library(shiny)

ui <- fluidPage(
  # UI elements here
)

server <- function(input, output, session) {
  observe({
    req(input$pathParameter1)
    req(input$pathParameter2)
    
    # Query parameters
    queryParameter1 <- input$queryParameter1
    queryParameter2 <- input$queryParameter2
    
    # Header parameters
    headerParameter1 <- req(headers()$headerParameter1)
    headerParameter2 <- req(headers()$headerParameter2)
    
    # Body parameters
    bodyParameter1 <- req(input$bodyParameter1)
    bodyParameter2 <- req(input$bodyParameter2)
    
    # Content types and response codes
    if (req(input$content_type) == "application/xml") {
      return(list(content = "<response><message>XML format</message></response>", status = 415))
    } else if (req(input$content_type) == "application/json") {
      return(list(content = jsonlite::toJSON(incomes), status = 200))
    } else {
      return(list(content = jsonlite::toJSON(incomes), status = 200))
    }
  })
}

shinyApp(ui, server)

"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
