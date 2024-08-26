import re

from helpers.Helper import Helper

text = """
    // GET /tag/{tag}/page-{page}
    [HttpGet("{tag}/page-{page:int}")]
    // GET /tag/{tag}/page-{page}
    [HttpPost("{tag}/page-{page:long}")]
    // GET /tag/{tag}/page-{page}/xyz
    [HttpGet("{tag}/page-{page:float}/xyz")]
    public IActionResult Test1([FromRoute] string tag, [FromRoute] int? page, [FromQuery] string queryParameter1, [FromQuery] string queryParameter2)
    {
        // Query parameters
        // Query parameters are automatically bound to method parameters

        // Header parameters
        var headerParameter1 = Request.Headers["headerParameter1"].ToString();
        var headerParameter2 = Request.Headers["headerParameter2"].ToString();

        // Body parameters (only if request method is POST and body is present)
        string bodyParameter1 = null;
        string bodyParameter2 = null;
        if (HttpContext.Request.Method == "POST")
        {
            using (var reader = new StreamReader(Request.Body))
            {
                var body = reader.ReadToEnd();
                var jsonBody = JsonSerializer.Deserialize<Dictionary<string, string>>(body);
                jsonBody?.TryGetValue("bodyParameter1", out bodyParameter1);
                jsonBody?.TryGetValue("bodyParameter2", out bodyParameter2);
            }
        }

        // Content types and response codes
        if (Request.ContentType == "application/html")
        {
            return Content("<response><message>XML format is not supported yet</message></response>", "application/xml", System.Text.Encoding.UTF8);
        }
        else if (Request.ContentType == "application/json")
        {
            return Ok(incomes); // Return JSON response
        }
        else
        {
            return StatusCode(415, "Unsupported Media Type");
        }
    }

    // GET /tag/{tag}
    [HttpGet("{tag}")]
    public IActionResult Test2([FromRoute] string tag)
    {
        // Implementation for this route
        return Ok();
    }
"""

# Loop all api matches
apiPattern = r'''((?:\/\/\ \S+ (?P<paths>\S+)\n)|(?:\[Http(?P<httpMethods>\w+)(.*(?P<pathParameters>\{[^{}]+\}))*?.*\n)|(?:.*return StatusCode\((?P<responseCodes>\d+).*\n)|(?:(?:public|protected|private) \S+ (?P<functionName>\w+).*?\n)|.*?\n)*?.*?(?=\n\n\s*\/\/\ |\Z)'''
apiMatches = re.finditer(apiPattern, text)
apiMatches = [apiMatch for apiMatch in apiMatches if apiMatch.group(0).strip() != ""]
linePatterns = Helper.getLinePatterns(apiPattern)

# Loop all api blocks
for index, apiMatch in enumerate(apiMatches):
    apiMatchResult = []

    # Loop all line patterns for each api block
    for linePattern in linePatterns:
        lineRegex = re.compile(linePattern)
        groupPatterns = Helper.getGroupPatterns(linePattern)
        groupIndexes = {groupIndex : groupName for groupName, groupIndex in lineRegex.groupindex.items()}
        lineMatches = lineRegex.findall(apiMatch.group(0))
        # Loop all line matches for each line pattern
        for lineMatch in lineMatches:
            dict = {}
            if not isinstance(lineMatch, (list, tuple, set, frozenset, range)): # When it is an element, it should be created in a list as well
                lineMatch = [lineMatch]

            # Loop all groups for each line match
            for groupName, groupIndex in lineRegex.groupindex.items():
                if groupPatterns[groupName] + "*?" in linePattern and groupIndex >= 2:
                    dict[groupName] = re.findall(groupPatterns[groupName], lineMatch[groupIndex - 2])
                else:
                    dict[groupName] = lineMatch[groupIndex - 1]
                
            # Add it into api match result
            apiMatchResult.append(dict)
    apiMatchResult = Helper.unionedDictionary(apiMatchResult)
    if apiMatchResult and ("paths" in apiMatchResult or "httpMethods" in apiMatchResult):
        print(apiMatchResult)