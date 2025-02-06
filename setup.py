from dotenv import load_dotenv
import os
from Neo4jManager import Neo4jManager
import pandas as pd
from utils.data_utils import cleanup_dataframe

load_dotenv()

neo4j_manager = Neo4jManager()

DATA_PATH = os.environ.get("DATA_PATH", 'onto_x.csv')
df = pd.read_csv(DATA_PATH)
df = cleanup_dataframe(df)

elements = df.apply(
    lambda row: {'class_id': row["Class ID"], 'preferred_label': row["Preferred Label"], 'parents': row['Parents']},
    axis=1).tolist()

all_element_ids = df["Class ID"].tolist()

all_parent_ids = list(
    set([item for sublist in df['Parents'].dropna().tolist() for item in sublist if item is not None]))

unknown_label_ids = [parent_id for parent_id in all_parent_ids if parent_id not in all_element_ids]

for element in elements:
    if not neo4j_manager.check_if_exists(element['class_id']):
        neo4j_manager.add_element(class_id=element['class_id'], preferred_label=element['preferred_label'])

for unknown_label_id in unknown_label_ids:
    if not neo4j_manager.check_if_exists(unknown_label_id):
        neo4j_manager.add_element(class_id=unknown_label_id, preferred_label=f'UNKNOWN_LABEL_{unknown_label_id}')

for element in elements:
    if element['parents'] is not None:
        for parent_id in element['parents'] :
            neo4j_manager.create_relationship(element['class_id'], parent_id)


