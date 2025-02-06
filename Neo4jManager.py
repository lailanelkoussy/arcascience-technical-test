from dotenv import load_dotenv
from utils.logger_utils import setup_logger
import logging
from neo4j import GraphDatabase
import os

# Load environment variables from .env file
load_dotenv()

# Logger configuration
LOGGER_NAME = 'NEO4J_MANAGER_LOGGER'
setup_logger(LOGGER_NAME)


class Neo4jManager:
    """
    A class to manage interactions with a Neo4j database.
    Handles connection, queries, and operations on nodes and relationships.
    """

    def __init__(self):
        """
        Initializes the Neo4jManager class by setting up the database connection and session.
        """
        self.logger = logging.getLogger(LOGGER_NAME)
        self.logger.info("Initializing Neo4jManager")
        URI = os.getenv('NEO4J_URI')
        AUTH = (os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))

        # Establish connection to Neo4j database
        self.driver = GraphDatabase.driver(URI, auth=AUTH)
        self.driver.verify_connectivity()

        # Create a session using the specified database
        self.session = self.driver.session()
        self.logger.info("Neo4j connection established successfully")

    def __del__(self):
        """
        Destructor to close the database session and driver when the instance is deleted.
        """
        self.logger.info("Closing Neo4j session and driver")
        self.session.close()
        self.driver.close()

    def execute_query(self, query: str, parameters=None):
        """
        Executes a Cypher query with optional parameters.

        :param query: The Cypher query string.
        :param parameters: A dictionary of parameters for the query.
        :return: The result of the query execution.
        """
        return self.session.run(query, parameters)

    def add_element(self, class_id: str, preferred_label: str):
        """
        Adds a node to the database with the given class_id and preferred_label.

        :param class_id: Unique identifier for the node.
        :param preferred_label: Label for the node.
        """
        self.logger.info(f"Adding node with class_id: {class_id}, preferred_label: {preferred_label}")
        create_node_query = """ CREATE (n:Node {class_id: $class_id, preferred_label: $preferred_label})"""
        self.execute_query(create_node_query, {'class_id': class_id, 'preferred_label': preferred_label})

    def create_relationship(self, class_id_child: str, class_id_parent: str):
        """
        Creates a unique parent-child relationship between two nodes.

        :param class_id_child: The class_id of the child node.
        :param class_id_parent: The class_id of the parent node.
        """
        self.logger.info(f"Creating relationship: {class_id_child} -> {class_id_parent}")
        query = """
                MATCH (a {class_id: $class_id_parent}), (b {class_id: $class_id_child})
                MERGE (a)-[r:PARENT_OF]->(b)
                RETURN r
                """
        self.execute_query(query,
                           {"class_id_parent": class_id_parent, "class_id_child": class_id_child})

    def get_ancestors(self, class_id: str) -> dict:
        """
        Retrieves all ancestor nodes of a given node.

        :param class_id: The class_id of the node whose ancestors are to be retrieved.
        :return: A dictionary with ancestor names as keys and distances as values.
        """
        self.logger.info(f"Fetching ancestors for class_id: {class_id}")
        query = """
        MATCH (descendant:Node {class_id: $class_id})<-[:PARENT_OF*]-(ancestor)
        RETURN ancestor.preferred_label AS ancestor, length(shortestPath((ancestor)-[:PARENT_OF*]-(descendant))) AS distance
        """
        results = self.execute_query(query, parameters={'class_id': class_id})
        return {record["ancestor"]: record["distance"] for record in results}

    def get_descendants(self, class_id: str) -> dict:
        """
        Retrieves all descendant nodes of a given node.

        :param class_id: The class_id of the node whose descendants are to be retrieved.
        :return: A dictionary with descendant names as keys and distances as values.
        """
        self.logger.info(f"Fetching descendants for class_id: {class_id}")
        query = """
        MATCH (ancestor:Node {class_id: $class_id})-[:PARENT_OF*]->(descendant)
        RETURN descendant.preferred_label AS descendant, length(shortestPath((ancestor)-[:PARENT_OF*]->(descendant))) AS distance
        """
        results = self.execute_query(query, parameters={'class_id': class_id})
        return {record["descendant"]: record["distance"] for record in results}

    def check_if_exists(self, class_id: str) -> bool:
        """
        Checks if a node with the given class_id exists in the database.

        :param class_id: The class_id to check.
        :return: True if the node exists, otherwise False.
        """
        self.logger.info(f"Checking if node exists with class_id: {class_id}")
        query = """
        MATCH (n {class_id: $class_id})
        RETURN COUNT(n) > 0 AS exists
        """
        result = self.execute_query(query, {"class_id": class_id})
        record = result.single()
        exists = record["exists"] if record else False
        self.logger.info(f"Node exists: {exists}")
        return exists

    def query(self, class_id: str):
        descendants = self.get_descendants(class_id)
        ancestors = self.get_ancestors(class_id)
        descendants.update(ancestors)
        return descendants
