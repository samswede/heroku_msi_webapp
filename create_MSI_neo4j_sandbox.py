import numpy as np
from database import (
    load_MSI_csv_into_neo4j,
)
from neo4j import GraphDatabase, basic_auth
from neo4j.exceptions import Neo4jError, ServiceUnavailable



def add_MSI_to_neo4j_sandbox(uri, username, password):
    # Connect to neo4j sandbox
    MSI_driver = GraphDatabase.driver(
        uri,
        auth=basic_auth(username, password))
    
    try:
        # Verify connectivity
        MSI_driver.verify_connectivity()
        print("Successfully connected to the database.")
    except ServiceUnavailable as e:
      print(f"Failed to connect to the database due to a network issue: {e}")
    except Neo4jError as e:
        print(f"Failed to connect to the database: {e}")
        return

    # Start a new session
    session = MSI_driver.session()

    # Define raw csv file paths from github repo
    nodes_csv_path = 'https://raw.githubusercontent.com/samswede/MSI_webapp_3/optimised-memory/data/nodes.csv'
    edges_csv_path = 'https://raw.githubusercontent.com/samswede/MSI_webapp_3/optimised-memory/data/edges.csv'

    
    try:
        # Test load_csv_into_neo4j
        load_MSI_csv_into_neo4j(nodes_csv_path= nodes_csv_path, edges_csv_path= edges_csv_path, session= session)
    except Neo4jError as e:
        print(f"An error occurred: {e}")
    finally:
        # Don't forget to close the session when you're done to free up resources!
        session.close()

if __name__ == "__main__":
    
    """
    
    """

    uri= 'bolt://54.174.97.172:7687'
    username= 'neo4j'
    password= 'octobers-links-seals'
    add_MSI_to_neo4j_sandbox(uri, username, password)
