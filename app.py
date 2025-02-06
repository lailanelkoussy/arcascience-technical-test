from fastapi import FastAPI
import pandas as pd
import os
from dotenv import load_dotenv
from utils.data_utils import cleanup_dataframe

from pydantic import BaseModel

from GraphDatabaseManager import GraphDatabaseManager
from Neo4jManager import Neo4jManager


class SearchRequest(BaseModel):
    class_id: str


# Loading environment variables
load_dotenv()

DATA_PATH = os.environ.get("DATA_PATH", 'onto_x.csv')
graph_db = GraphDatabaseManager()
df = pd.read_csv(DATA_PATH)
df = cleanup_dataframe(df)
graph_db.import_data(df)

neo4j_manager = Neo4jManager()

app = FastAPI()



@app.post('/graph-db/ontology')
async def get_class_ontology(request: SearchRequest):
    result = graph_db.query(request.class_id)
    return result

@app.post('/neo4j/ontology')
async def get_class_ontology(request: SearchRequest):
    result = neo4j_manager.query(request.class_id)
    return result