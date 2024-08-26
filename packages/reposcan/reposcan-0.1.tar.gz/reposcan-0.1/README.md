- Classify into different modules:
/scanners: all scanners such as JavaScanner, CSharpScanner, FileScanner
/exporters: all exporters such as CSVExporter, xLSXExporter, FileExporter
/data: repo.csv, api.csv, summaryapi.json
/tests: all unit tests
reposcan.py: main function where can start the program

- Extract into a code file into apis, extract an api into lines, extract a line into groups
+ Use finditer to extract apis, lines, non repeated groups, use findall to extract repeated groups
+ Using optional operators to extract optional and mandatory groups
+ Extract these groups: scanType, project, domain, repository, branches, filePath, extension, language, framework, apiType, baseUrl, functionName, lineNumber, timeStamp, keywords, httpMethods, paths, pathParameters, queryParameters, headerParameters, bodyParameters, contentTypes, responseCodes
+ Extract file supported: CSV, XLSX

- Usage: reposcan.py <repoFilePath> <apiFilePath> <summaryAPIFilePath>, for example: reposcan.py .\data\repo.csv .\data\api.csv .\data\summaryapi.json
