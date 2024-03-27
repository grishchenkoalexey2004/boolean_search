:: don't forget to replace docs_shortened for docs and queries_shortened for queries
docker run -it  --rm --name boolean-search -v %~dp0:/boolean_search -w /boolean_search python:3.12-alpine python hw_boolean_search.py ^
    --queries_file /boolean_search/data/queries_shortened.txt ^
    --objects_file  /boolean_search/data/objects.numerate.txt ^
    --docs_file /boolean_search/data/docs_shortened.txt ^
    --submission_file /boolean_search/output.csv
