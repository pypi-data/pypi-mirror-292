import re

from helpers.Helper import Helper

text = """
<?php

namespace App\Controllers;

use CodeIgniter\HTTP\RequestInterface;
use CodeIgniter\HTTP\ResponseInterface;

class MyController extends BaseController
{
    public function test1($pathParameter1, $pathParameter2 = null)
    {
        $queryParameter1 = $this->request->getGet('queryParameter1');
        $queryParameter2 = $this->request->getGet('queryParameter2');
        $headerParameter1 = $this->request->getHeader('headerParameter1');
        $headerParameter2 = $this->request->getHeader('headerParameter2');
        $bodyParameters = $this->request->getJSON(true);

        $contentType = $this->request->getHeaderLine('Content-Type');
        if ($contentType === 'application/xml') {
            return $this->response->setBody("<response><message>XML format</message></response>")
                                  ->setHeader('Content-Type', 'application/xml')
                                  ->setStatusCode(415);
        } else {
            return $this->response->setJSON(['incomes' => $incomes]) // Replace `incomes` with your data
                                  ->setStatusCode(200);
        }
    }

    public function test2()
    {
        return $this->response->setStatusCode(200);
    }
}

"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
