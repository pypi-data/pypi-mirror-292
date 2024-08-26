import re

from helpers.Helper import Helper

text = """
const express = require('express');
const app = express();

app.use(express.json());

app.get('/tag/:pathParameter1', (req, res) => {
    // Just comment
    res.sendStatus(200);
});

app.get('/tag/:pathParameter1/page-:pathParameter2', (req, res) => {
    // Query parameters
    const queryParameter1 = req.query.queryParameter1;
    const queryParameter2 = req.query.queryParameter2;

    // Header parameters
    const headerParameter1 = req.headers['headerparameter1'];
    const headerParameter2 = req.headers['headerparameter2'];

    // Body parameters
    const { bodyParameter1, bodyParameter2 } = req.body;

    // Content types and response codes
    if (req.headers['content-type'] === 'application/xml') {
        res.status(415).type('application/xml').send("<response><message>XML format</message></response>");
    } else {
        res.status(200).json({ incomes: 'data' });  // Replace with actual data
    }
});

app.post('/tag/:pathParameter1/page-:pathParameter2/xyz', (req, res) => {
    // Same as above
});

app.get('/tag', (req, res) => {
    res.sendStatus(200);
});

app.listen(3000, () => {
    console.log('Server running on port 3000');
});

"""

# Loop all api matches
apiPattern = r'''((?:.*@ApiResponse\((?:responseCode = )?\"(?P<responseCodes>\d+)\".*\n)|(?:.*@RequestMapping\((?:value = )?\"(?P<paths>(.*?(?P<pathParameters>\{\w+\})?.*?))\".*\n)|(?:.*@RequestMapping.*\(.*method = \{(.*(?P<httpMethods>\.\w+)*?.*)\}.*\n)|(?:.*@RequestMapping.*?\(.*?((?:consumes|produces) = (?P<contentTypes>\{[^}]+\}).*)\n)|(?:.*?(?:public|protected|private) \S+ (?P<functionName>\w+)\(.*\n)|(?:.*@RequestParam\((?:value = )?\"(?P<queryParameters>.*)\".*\n)|(?:.*@RequestHeader\((?:value = )?\"(?P<headerParameters>.*)\".*\n)|(?:.*@RequestBody.*Map<String, Object> (?P<bodyParameters>\w+).*\n)|.*?\n)*?.*\;\n\s*\}'''
