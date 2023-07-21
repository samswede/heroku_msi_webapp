# from py2neo import Graph
# import networkx as nx
# import pandas as pd
# import gzip
# import numpy as np
# import gc
import csv
import requests
from neo4j import GraphDatabase, basic_auth
from neo4j.exceptions import Neo4jError, ServiceUnavailable


def connect_to_neo4j_sandbox(uri, username, password):
    # Connect to neo4j sandbox
    driver = GraphDatabase.driver(
        uri,
        auth=basic_auth(username, password))
    
    try:
        # Verify connectivity
        driver.verify_connectivity()
        print("Successfully connected to the database.")
    except ServiceUnavailable as e:
      print(f"Failed to connect to the database due to a network issue: {e}")
    except Neo4jError as e:
        print(f"Failed to connect to the database: {e}")
        return
    
    return driver

def load_MSI_csv_into_neo4j(nodes_csv_path, edges_csv_path, session, batch_size=50000):
    """
    This function loads data from CSV files into a Neo4j database in batches.

    The function first creates an index on the 'node' property of the 'Entity' label.
    This index speeds up the MATCH operations that are used later in the function.

    After creating the index, the function reads the nodes CSV file from the specified URL.
    It reads the data in batches, with each batch containing a specified number of rows.
    For each batch, it creates a Neo4j transaction and runs a Cypher query to add the nodes
    from the batch to the database. After running the query, it commits the transaction.

    The Cypher query used for the nodes uses the MERGE command to ensure that each node is 
    only added once. If a node with the same 'node' property already exists, the query simply 
    updates its 'type' property.

    The function repeats a similar process for the edges CSV file. For each batch of data,
    it creates a transaction and runs a Cypher query to add the edges from the batch to the 
    database. The query matches nodes based on their 'node' property, and then creates 
    a 'CONNECTED_TO' relationship between them.

    For each successful commit of a batch, the function prints a message indicating 
    that the batch has been committed.

    Parameters:
    nodes_csv_path (str): The URL of the nodes CSV file.
    edges_csv_path (str): The URL of the edges CSV file.
    session (neo4j.Session): The Neo4j session to use for the transactions.
    batch_size (int): The number of rows to include in each batch. Default is 50000.
    """
    # Create an index on the 'node' property of the 'Entity' label
    create_index_query = "CREATE INDEX entity_node_index FOR (n:Entity) ON (n.node)"
    session.run(create_index_query)
    
    # Define the Cypher queries
    nodes_query = """
    UNWIND $batch AS row
    MERGE (:Entity {node: row.node, type: row.type})
    """
    
    edges_query = """
    UNWIND $batch AS row
    MATCH (source:Entity {node: row.source})
    MATCH (target:Entity {node: row.target})
    MERGE (source)-[:CONNECTED_TO]->(target)
    """
    
    # Load the nodes
    response = requests.get(nodes_csv_path)
    response.raise_for_status()  # Raise an exception if the request failed
    reader = csv.DictReader(response.text.splitlines())
    batch = []
    for i, row in enumerate(reader, start=1):
        batch.append(row)
        if i % batch_size == 0:
            with session.begin_transaction() as tx:
                tx.run(nodes_query, {"batch": batch})
            print(f"Committed nodes batch {i // batch_size}")
            batch = []
    if batch:  # Don't forget the last batch
        with session.begin_transaction() as tx:
            tx.run(nodes_query, {"batch": batch})
        print(f"Committed final nodes batch ({len(batch)} rows)")

    # Load the edges
    response = requests.get(edges_csv_path)
    response.raise_for_status()  # Raise an exception if the request failed
    reader = csv.DictReader(response.text.splitlines())
    batch = []
    for i, row in enumerate(reader, start=1):
        batch.append(row)
        if i % batch_size == 0:
            with session.begin_transaction() as tx:
                tx.run(edges_query, {"batch": batch})
            print(f"Committed edges batch {i // batch_size}")
            batch = []
    if batch:  # Don't forget the last batch
        with session.begin_transaction() as tx:
            tx.run(edges_query, {"batch": batch})
        print(f"Committed final edges batch ({len(batch)} rows)")


def load_csv_into_neo4j(csv_url, profile_type, session, batch_size=100):
    """
    This function loads data from a CSV file into a Neo4j database in batches.

    The function reads the CSV file from the specified URL.
    It reads the data in batches, with each batch containing a specified number of rows.
    For each batch, it creates a Neo4j transaction and runs a Cypher query to add the nodes
    from the batch to the database. After running the query, it commits the transaction.

    Parameters:
    csv_url (str): The URL of the CSV file.
    profile_type (str): The label to use for the nodes in the Neo4j database.
    session (neo4j.Session): The Neo4j session to use for the transactions.
    batch_size (int): The number of rows to include in each batch. Default is 50000.
    """
    print(f"Starting to load {csv_url} \n into Neo4j as {profile_type}...")

    # Define the Cypher query for loading CSV data
    query = """
        UNWIND $batch AS row
        CREATE (n:{})
        SET n.arrayProperty = row.arrayProperty
    """.format(profile_type)

    # Load the CSV file
    response = requests.get(csv_url)

    response.raise_for_status()  # Raise an exception if the request failed
    reader = csv.DictReader(response.text.splitlines())
    batch = []

    for i, row in enumerate(reader, start=1):
        # Create a sorted array from the dictionary items, excluding 'index' and 'label'
        arrayProperty = [value for key, value in sorted(row.items()) if key not in ['index', 'label']]
        # Convert the values to floats
        arrayProperty = list(map(float, arrayProperty))
        batch.append({'arrayProperty': arrayProperty})
        if i % batch_size == 0:
            #print(f'beginning transaction')
            with session.begin_transaction() as tx:
                tx.run(query, {"batch": batch})
            print(f"Committed {profile_type} batch {i // batch_size}")
            batch = []
    if batch:  # Don't forget the last batch
        with session.begin_transaction() as tx:
            tx.run(query, {"batch": batch})
        print(f"Committed final {profile_type} batch ({len(batch)} rows)")

    print(f"Finished loading {csv_url} into Neo4j.")




