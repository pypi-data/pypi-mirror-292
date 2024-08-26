import re

from helpers.Helper import Helper

text = """
<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

Route::get('/tag/{pathParameter1}', 'MyController@test1');
Route::match(['get', 'post'], '/tag/{pathParameter1}/page-{pathParameter2}', 'MyController@test1');
Route::get('/tag/{pathParameter1}/page-{pathParameter2}/xyz', 'MyController@test1');

class MyController extends Controller
{
    public function test1(Request $request, $pathParameter1, $pathParameter2)
    {
        $queryParameter1 = $request->query('queryParameter1');
        $queryParameter2 = $request->query('queryParameter2');
        $headerParameter1 = $request->header('headerParameter1');
        $headerParameter2 = $request->header('headerParameter2');
        $bodyParameters = $request->json()->all();

        $contentType = $request->header('Content-Type');
        if ($contentType === 'application/xml') {
            return response("<response><message>XML format</message></response>", 415)
                    ->header('Content-Type', 'application/xml');
        } else {
            return response()->json(['incomes' => $incomes], 200); // Replace `incomes` with your data
        }
    }

    public function test2()
    {
        return response('', 200);
    }
}


"""

# Loop all api matches
apiPattern = r'''((?:.*@ApiResponse\((?:responseCode = )?\"(?P<responseCodes>\d+)\".*\n)|(?:.*@RequestMapping\((?:value = )?\"(?P<paths>(.*?(?P<pathParameters>\{\w+\})?.*?))\".*\n)|(?:.*@RequestMapping.*\(.*method = \{(.*(?P<httpMethods>\.\w+)*?.*)\}.*\n)|(?:.*@RequestMapping.*?\(.*?((?:consumes|produces) = (?P<contentTypes>\{[^}]+\}).*)\n)|(?:.*?(?:public|protected|private) \S+ (?P<functionName>\w+)\(.*\n)|(?:.*@RequestParam\((?:value = )?\"(?P<queryParameters>.*)\".*\n)|(?:.*@RequestHeader\((?:value = )?\"(?P<headerParameters>.*)\".*\n)|(?:.*@RequestBody.*Map<String, Object> (?P<bodyParameters>\w+).*\n)|.*?\n)*?.*\;\n\s*\}'''
