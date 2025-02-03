import logging
from utils.logger_utils import setup_logger
import pandas as pd
import numpy as np


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
        self.distances = None

        # Load database if it exists
        if os.path.exists(self.db_file):
            self.load_database()

    def save_database(self):
        data = {
            "nodes": [node.to_dict() for node in self.nodes],
            "elements": {key: node.to_dict() for key, node in self.elements.items()},
            "adjacency": self.adjacency.tolist() if self.adjacency is not None else None,
            "distances": self.distances.tolist() if self.distances is not None else None
        }
        
        with open(self.db_file, "w") as f:
            json.dump(data, f, indent=4)
        self.logger.info("Database saved successfully.")

    def load_database(self):
        try:
            with open(self.db_file, "r") as f:
                data = json.load(f)
            
            self.nodes = [Node.from_dict(node_data) for node_data in data["nodes"]]
            self.elements = {key: Node.from_dict(node_data) for key, node_data in data["elements"].items()}
            self.adjacency = np.array(data["adjacency"]) if data["adjacency"] is not None else None
            self.distances = np.array(data["distances"]) if data["distances"] is not None else None
            
            self.logger.info("Database loaded successfully.")
        except Exception as e:
            self.logger.error(f"Failed to load database: {e}")

    def __del__(self):
        self.save_database()
        

    def _create_adjacency_matrix(self):
        self.logger.info('Creating adjacency matrix')
        n = len(self.nodes)
        self.adjacency = np.zeros((n, n), dtype=int)

        # Iterate over all elements and fill the matrix
        for i in range(n):
            node = self.nodes[i]
            if node.parents is not None :
                parent_nodes_id = [self.get_element_index_by_class_id(class_id) for class_id in node.parents]
                for j in parent_nodes_id:
                    self.adjacency[j,i] = 1  # There's a directed edge from parents (j) to children (i)


    def _calculate_distances(self):
        self.logger.info('Calculating distances')
        n = self.adjacency.shape[0]
        self.distances = np.matrix(np.ones((n,n)) * np.inf)
        np.fill_diagonal(self.distances, 0)  # Distance from a node to itself is 0

        # Floyd-Warshall algorithm
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if self.distances[i,j] > self.distances[i,k] + self.distances[k,j]:
                        self.distances[i,j] = self.distances[i,k] + self.distances[k,j]


    def query(self, class_id: str):
        self.logger.info(f'Querying database for element : {self.elements[class_id].preferred_label}')
        index_id = self.get_element_index_by_class_id(class_id)
        n = len(self.nodes)
        distance_dict = {self.nodes[j].preferred_label: self.distances[index_id][j] for j in range(n)}
        return distance_dict


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

        # Here we are isolating said 'parent' ids that have not been defined to be able to remove them
        all_class_ids = list(
            set([item for sublist in df['Parents'].dropna().tolist() for item in sublist if item is not None]))

        for class_id in all_class_ids:
            if class_id not in self.elements:
                for node_id, node in self.elements.items():
                    if node.parents is not None:
                        if class_id in node.parents:
                            node.parents.remove(class_id)

        # Building the adjacency matrix
        self._create_adjacency_matrix()

        # Building the distance matrix
        # The decision to create the distances matrix has been made due to the relatively small number of entries
        # specifically in this database vs the potentially large number of queries. The choice is made easier due to
        # the static nature of the database. If the data were dynamic, this could still be a feasible option, but more
        # code would need to be implemented to accommodate for incoming data changes and additions.
        # This decision will allow for O(1) complexity at query time.
        self._calculate_distances()



def cleanup_dataframe(df):
    df.Parents = df.Parents.astype(str)
    df.Parents.loc[df.Parents.str.match('nan') ] = None
    df.Parents = df.Parents.str.split('|')

    return df


def main():

    graph_db = GraphDatabaseManager()
    df = pd.read_csv('onto_x.csv')
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
