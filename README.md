# How to run the application 

## Build the docker 
docker build -t wmt-puneet-girdhar-file-metadata:0.0.1 .

## Run the container
docker run -it -p 5000:5000 wmt-puneet-girdhar-file-metadata:0.0.1

## Check if urls are working
1. Check Json http://127.0.0.1:5000/json
2. Check CSV http://127.0.0.1:5000/csv

## check the file interview.csv
docker exec -it wmt-puneet-girdhar-file-metadata:0.0.1 bash
ls /app

