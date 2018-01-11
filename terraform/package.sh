#! /bin/bash
rm package.zip  > /dev/null 2>&1 
cd ..
zip -r package.zip app README.md > /dev/null 2>&1 
echo {"\"package\"":"\"$(base64 -i package.zip)\""}