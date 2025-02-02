# arcascience-technical-test
This repository contains a data engineering test for ArcaScience. 

# Setting up 

Python 3.11
Docker 


# Downloading Neo4j 

```shell
docker pull neo4j:5.26.1 

docker run \
    --restart always \
    --publish=7474:7474 --publish=7687:7687 \
    --env NEO4J_AUTH=neo4j/your_password \
    neo4j:5.26.1
    
    ```



Reading and understanding exercise + data exploration : 10 minutes
Building Graph database: started at 8:40 pm 

I suppose, in this case, that existing relationships are fixed. This is to allow precalculations to be done at startup time, to maximise efficiency. 

In the case of modifications, there could be a way to add code to modify. 