#!/bin/bash
CWD="`pwd`";
for req in `cat requests`
do
    curl -X PUT $req 
done
