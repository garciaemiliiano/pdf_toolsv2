#!/bin/bash
echo "Server encendiendo... "
docker run -p 8000:8000 pdf_tools
#docker run -d -p 8000:8000 -t pdf_tools