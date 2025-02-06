# arcascience-technical-test
This repository contains a data engineering test for ArcaScience. 

The project requires building a relationship hierarchy based on a CSV file.



# Setting up 

## Prerequisites
- Python 3.11 or later
- Docker 
- Jupyter (if wanting to run the exploration code)

## Setting up the environment 

To run the environment, it suffices to run the following command : 

```bash
pip install -r requirements.txt 
```


# Running the CLI tool 

Run the script by executing : 

```bash
python GraphDatabaseManager.py
```

# Option 1: Setting up the FastAPI endpoint 

Set up the endpoint by executing : 

Run Neo4J by running : 

```bash 
docker run \
    --restart always \
    --publish=7474:7474 --publish=7687:7687 \
    --env NEO4J_AUTH=neo4j/your_password \
    neo4j:5.26.2
```

```bash
python setup.py 
uvicorn app:app --port=8080
```

You can change username and password by changing the command credentials and changing the `NEO4J_USER`
`NEO4J_PASSWORD` in the `.env` file accordingly. 

You are able to access a test interface by visiting http://127.0.0.1:8080/docs on your browser. 


# Building and running the docker image 
Run the following command to build and run the images: 

```bash
docker-compose up --build
```

You can still access the test interface by visiting http://127.0.0.1:8080/docs on your browser. 

# Presenting the work 
Firstly, there is an exploration folder containing a jupyter notebook that allowed me to discover the data in a quick 
and hands on way. 

The main logic for the code is divided into two sections. 
The first part is contained in the `GraphDatabaseManager.py` file. In it contains a class which reads and parses the 
csv file. After this, it creates an adjacency matrix representation for the data. At query time, a breadth-first search is done to all possible neighbors, and a dictionary is returned with only the elements 'within reach' of the element.

This is a more 'hands-on' approach. 


The second part of the code is contained in the `Neo4jManager.py` file which interfaces with a Neo4J graph database. 
The database is populated at startup using the `setup.py` script. 


The endpoints allow to interact with both solutions. This allows for comparison. 

## Breakdown of the time taken

- Reading and understanding exercise + data exploration : 10 minutes
- Building Graph database manager: started at 3h30
- Creating fastapi and requirements.txt + dockerfile : 40 minutes
- Implementing Neo4J + docker-compose: 4h
- Writing README: 15 minutes

## Possible improvements 

- The use of a graph database would be extremely helpful for scalability purposes. 
- It would also be interesting to explore the possible addition of endpoints that would add/modify relationships and elements. 

