import logging
from utils.logger_utils import setup_logger
from utils.data_utils import cleanup_dataframe
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from collections import deque


class Node:
    def __init__(self, class_id, preferred_label, parents):
        self.class_id = class_id
        self.preferred_label = preferred_label
        self.parents = parents

    def to_dict(self):
        return {
            "class_id": self.class_id,
            "preferred_label": self.preferred_label,
            "parents": self.parents
        }

    @staticmethod
    def from_dict(data):
        return Node(data["class_id"], data["preferred_label"], data["parents"])

    def get_parents_ids(self):
        return self.parents


class GraphDatabaseManager:
    def __init__(self, db_file="graph_database.json"):
        self.logger_name = 'GRAPH_DATABASE_LOGGER'
        setup_logger(self.logger_name)
        self.logger = logging.getLogger(self.logger_name)
        self.nodes = []
        self.elements = {}
        self.adjacency = None

    def _create_adjacency_matrix(self):
        self.logger.info('Creating adjacency matrix')
        n = len(self.nodes)
        self.adjacency = np.zeros((n, n), dtype=int)

        # Iterate over all elements and fill the matrix
        for i in range(n):
            node = self.nodes[i]
            if node.parents is not None:
                parent_nodes_id = [self.get_element_index_by_class_id(class_id) for class_id in node.parents]
                for j in parent_nodes_id:
                    self.adjacency[j, i] = 1  # There's a directed edge from parents (j) to children (i)

    def query(self, class_id: str):
        if class_id in self.elements:
            self.logger.info(f'Querying database for element : {self.elements[class_id].preferred_label}')
            index_id = self.get_element_index_by_class_id(class_id)
            n = len(self.nodes)
            distances = [-1] * n  # -1 indicates no path to that node
            distances[index_id] = 0  # Distance to itself is 0

            queue = deque([index_id])

            while queue:
                current = queue.popleft()

                # Explore all neighbors
                for neighbor in range(n):
                    if self.adjacency[current, neighbor] == 1 and distances[neighbor] == -1:
                        # If there's an edge and the node hasn't been visited
                        distances[neighbor] = distances[current] + 1
                        queue.append(neighbor)

            distance_dict = {self.nodes[j].preferred_label: distances[j] for j in range(n)}
            cleaned_distance = {label: distance_dict[label] for label in distance_dict if distance_dict[label] > -1}
            return cleaned_distance
        else:
            self.logger.error('Queried ID does not exist')

    def get_element_index_by_class_id(self, class_id):
        return list(self.elements.keys()).index(class_id)

    def import_data(self, df: pd.DataFrame):
        self.logger.info('Beginning data import')
        # Here it is assumed that the following columns exist in the dataframe : Class ID, Preferred Label, Parents
        # We create a node list so that we have number indexes for class ids, this will be useful for the adjacency matrix we will build.
        self.logger.info('Creating nodes')
        self.nodes = df.apply(lambda row: Node(class_id=row["Class ID"], preferred_label=row["Preferred Label"],
                                               parents=row['Parents']), axis=1).tolist()

        # A dictionary representation to be able to query elements
        # The list elements are used as to share the same elements, not to have several copies, and save memory
        self.logger.info('Creating elements dictionary')
        self.elements = {element.class_id: element for element in self.nodes}

        # There are some element ids that are present in parent lists but not defined, we choose to remove them,
        # as they will not be helpful in calculating distances (if it is only a common parent, as these are directed
        # graphs, we cannot go through them to get to other nodes)
        # (If they were 'children', they would appear as a row element)

        # Here we are isolating said 'parent' ids that have not been defined to be able to complete our list

        all_class_ids = list(
            set([item for sublist in df['Parents'].dropna().tolist() for item in sublist if item is not None]))


        for class_id in all_class_ids:
            if class_id not in self.elements:
                self.nodes.append(Node(class_id=class_id, preferred_label='UNKNOWN_LABEL', parents=[]))
                self.elements[class_id] = self.nodes[-1]


        # Building the adjacency matrix
        self._create_adjacency_matrix()





def main():
    #Loading environment variables
    load_dotenv()

    DATA_PATH = os.environ.get("DATA_PATH",'onto_x.csv')
    graph_db = GraphDatabaseManager()
    df = pd.read_csv(DATA_PATH)
    df = cleanup_dataframe(df)
    graph_db.import_data(df)

    while True:
        entity_id = input("Enter Class ID to query (or 'exit' to quit): ")
        if entity_id.lower() == 'exit':
            break
        result = graph_db.query(entity_id)
        print(result)


if __name__ == "__main__":
    main()
