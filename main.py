# this is fixed-database branch


# Import necessary libraries
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any

# Import personalised modules
from database import *
from utils import *
from optimised_manager import *

# Memory optimisation
from memory_profiler import profile

#===================================================================
#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
#===================================================================
"""
TO DO:
    - The drug names list is a list of names, duh, but that is a problem for the graph request which expects drug labels.
        I can use a dictionary to convert them back... but that is gonna be derpy. Better to recompute all of them, and then translate it.
        There should be a difference between 'name' and 'value'. 'value' should be 'label'?

        I can quickly try the dictionary reconversion just to see if it works.
            ^That is what i did. There seems to be a pydantic type error. 
            I need to understand the types of my response and describe that better.

"""


# Create Driver and Connect to database
uri= 'bolt://3.87.61.251:7687'
username= 'neo4j'
password= 'bubble-car-percent'

# Connect to neo4j sandbox
driver = connect_to_neo4j_sandbox(uri, username, password)

# Initialize the FastAPI application
app = FastAPI()

# Serve static files from the "static" directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS middleware setup to allow requests from the specified origins
origins = [
    'http://localhost',
    'http://127.0.0.1:8000',
    'https://primal-hybrid-391911.ew.r.appspot.com', #New for google cloud
    'http://localhost:8080',
    'https://msi-app-b9364c344d37.herokuapp.com',  # Allow your local frontend to access the server

    uri, # add neo4j sandbox graph database uri
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Jinja2 templates with the "templates" directory
templates = Jinja2Templates(directory="templates")

# Instantiate and initialize necessary components for the application
data_path = './data/'
graph_manager = GraphManager(data_path)

map_drug_diffusion_labels_to_indices, map_drug_diffusion_indices_to_labels, map_indication_diffusion_labels_to_indices, map_indication_diffusion_indices_to_labels = load_dictionaries(data_path)


#===================================================================
#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
#===================================================================

def print_types(data, level=0):
    if isinstance(data, dict):
        for key, value in data.items():
            print('  ' * level + f"{key}: {type(value)}")
            print_types(value, level + 1)
    elif isinstance(data, list):
        if data:
            print('  ' * level + f"0: {type(data[0])}")
            print_types(data[0], level + 1)

# Define a Pydantic model for diseases, drugs, and GraphRequest
class Disease(BaseModel):
    value: str
    name: str


class Drug(BaseModel):
    value: str
    name: str


class DrugResponse(BaseModel):
    drug_candidates: List[Drug]
    console_logging_status: str


class DiseaseDrugCandidatesRequest(BaseModel):
    disease_label: str


class GraphRequest(BaseModel):
    disease_label: str
    drug_label: str
    k1: int
    k2: int

class Node(BaseModel):
    node_id: int = Field(..., alias="id")
    label: str
    color: str
    shape: str

class Edge(BaseModel):
    from_node: int = Field(..., alias="from")
    to: int
    arrows: str

class GraphData(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

class GraphResponse(BaseModel):
    MOA_network: GraphData
    console_logging_status: str

#====================================================================================================================
# Define application routes
#====================================================================================================================

@app.get("/", response_class=HTMLResponse)
async def read_items(request: Request):
    """Serve the index.html page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/diseases", response_model= List[Disease])
async def get_diseases():
    """Return a list of diseases"""
    list_of_diseases = [
        {"value": graph_manager.mapping_indication_name_to_label[name], "name": name}
        for name in graph_manager.indication_names_sorted
    ]
    return list_of_diseases


@app.get("/drugs", response_model= List[Drug])
async def get_drugs():
    """Return a list of diseases"""
    list_of_drugs = [
        {"value": graph_manager.mapping_drug_name_to_label[name], "name": name}
        for name in graph_manager.drug_names_sorted if name in graph_manager.mapping_drug_name_to_label
    ]
    return list_of_drugs


@app.post("/drugs_for_disease", response_model= DrugResponse)
async def get_drugs_for_selected_disease(disease_drug_candidates_request: DiseaseDrugCandidatesRequest):
    """Return a list of drugs based on the selected disease"""

    assert isinstance(disease_drug_candidates_request.disease_label, str)


    drug_candidates_names_list, console_logging_status = graph_manager.get_drugs_for_disease_precomputed(chosen_indication_label= disease_drug_candidates_request.disease_label)
    
    # drug_candidates_names_list is a list of strings
    # console_logging_status is a string

    drug_candidates = [
        {"value": name, "name": name}
        for name in drug_candidates_names_list
    ]

    return {"drug_candidates": drug_candidates, "console_logging_status": console_logging_status}


#============================================================================
# Visualise MOA network using vis.js
#============================================================================

@app.post("/graph", response_model=GraphResponse)
async def get_graph_data(request: GraphRequest):
    # Extract parameters from request
    disease_label = request.disease_label
    drug_label = request.drug_label
    k1 = request.k1
    k2 = request.k2

    print(f'disease_label: {disease_label}')
    print(f'drug_label: {drug_label}')
    print(f'k1: {k1}')
    print(f'k2: {k2}')

    # Derpy fix changing drug_label (which is actually a name right now) back into a label.
    drug_label = graph_manager.mapping_all_names_to_labels[drug_label]

    try:

        # Start a new session
        session = driver.session()

        # Retrieve MOA graph data from neo4j sandbox
        MOA_subgraph, MOA_subgraph_node_colors, MOA_subgraph_node_shapes = graph_manager.generate_subgraph_with_database(chosen_indication_label= disease_label, 
                                                                                                       chosen_drug_label= drug_label, 
                                                                                                       num_drug_nodes= k2, 
                                                                                                       num_indication_nodes= k1, 
                                                                                                       map_drug_diffusion_labels_to_indices= map_drug_diffusion_labels_to_indices, 
                                                                                                       map_indication_diffusion_labels_to_indices= map_indication_diffusion_labels_to_indices, 
                                                                                                       session= session)
        
        # Close database session to free up resources
        session.close()

    except Exception as e:
        print(f"\n ERROR: {e} \n") # should probably return this error and log it on console in main.js
        # Create the response
        graph_data = {"nodes": [], "edges": []}
        response = {
            "MOA_network": graph_data,
            "console_logging_status": f'{e}',
        }

        return response
    

    # Convert graph data into a format that vis.js can handle
    graph_data = graph_manager.convert_networkx_to_vis_graph_data(graph=MOA_subgraph,
                                                                  node_colors=MOA_subgraph_node_colors, 
                                                                  node_shapes=MOA_subgraph_node_shapes)

    print_types(graph_data)

    print(f'graph_data: {graph_data}')

    e = 'successfully retrieved subgraph from database'
    # Create the response
    response = {
        "MOA_network": graph_data,
        "console_logging_status": f'{e}',
    }

    return response


