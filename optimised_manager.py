import pandas as pd
import numpy as np
import networkx as nx

from memory_profiler import profile

import pickle
import gzip




class GraphManager:
    #@profile
    def __init__(self, data_path):

        #self.load_MSI_graph()
        self.load_dicts(data_path)
        self.load_mapping_all_labels_to_names(data_path)
        self.load_node_types(data_path)

        # Load drug candidates
        self.load_drug_candidates(data_path)

        #data_path = './data/'
        drug_filename = 'all_top_100_drug_nodes.pkl'
        indication_filename = 'all_top_100_indication_nodes.pkl'
        self.top_100_node_labels_for_each_indication = self.load_list_of_lists(data_path, indication_filename)
        self.top_100_node_labels_for_each_drug = self.load_list_of_lists(data_path, drug_filename)

        self.mapping_all_names_to_labels = self.invert_dict(self.mapping_all_labels_to_names)
        
    #@profile
    def load_MSI_graph(self):
        self.MSI = nx.read_graphml("MSI_graph.graphml")
        pass
    
    #@profile
    def load_mapping_all_labels_to_names(self, data_path):
        with gzip.open(f'{data_path}mapping_all_labels_to_names.pkl.gz', 'rb') as f:
            self.mapping_all_labels_to_names = pickle.load(f)
    
    #@profile
    def load_node_types(self, data_path):
        with gzip.open(f'{data_path}node_types.pkl.gz', 'rb') as f:
            self.node_types = pickle.load(f)

    #@profile
    def load_dicts(self, data_path):
        dict_names = ["mapping_label_to_index", "mapping_index_to_label", "mapping_drug_label_to_name", 
                      "mapping_indication_label_to_name", "mapping_drug_name_to_label", "mapping_indication_name_to_label",
                      "drug_names_sorted", "indication_names_sorted"]

        for name in dict_names:
            with gzip.open(f'{data_path}{name}.pkl.gz', 'rb') as f:
                setattr(self, name, pickle.load(f))

    def load_list_of_lists(self, filepath, filename):
        with open(filepath + filename, 'rb') as f:
            return pickle.load(f)

    #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
    # Drug Candidates
    #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& 

    def load_drug_candidates(self, data_path):
        self.all_drug_candidates = pd.read_csv(f'{data_path}drug_candidates.csv')

    def get_drugs_for_disease_precomputed(self, chosen_indication_label):
        # Filter the DataFrame for the rows where the first column (indication label) matches the chosen indication label
        matching_rows = self.all_drug_candidates[self.all_drug_candidates.iloc[:, 0] == chosen_indication_label]
        
        # If there are any matching rows, return the drug candidates
        if len(matching_rows) > 0:
            # The drug candidates are in the other columns of the DataFrame
            # We convert the DataFrame slice to a list and exclude the first element (the indication label)
            list_of_drug_candidate_names = matching_rows.iloc[0, 1:].tolist()

            # Convert NaNs into a string called 'Unnamed entity'
            list_of_drug_candidate_names = ['Unnamed entity' if type(name) is not str else name for name in list_of_drug_candidate_names]

            console_logging_status = 'successfully located matching row via get_drugs_for_disease_precomputed()'
            return list_of_drug_candidate_names, console_logging_status
        else:
            console_logging_status = 'error: no matching rows located via get_drugs_for_disease_precomputed()'
            return [], console_logging_status
        
    #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
    # Subgraph
    #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

    #@profile
    def get_top_k_nodes(self, diffusion_profile, k):
        """
        Get the top k nodes from a diffusion profile.
        Input: 
        - diffusion_profile (numpy array): The diffusion values for each node in the graph.
        The array index corresponds to the node index in the graph.
        - k (int): The number of nodes to return.
        
        Output: 
        - list of str: The labels of the top k nodes.
        """

        # Get the indices of the top k nodes
        top_k_indices = np.argsort(diffusion_profile)[-k:]
        
        # Convert indices to labels
        top_k_labels = [self.mapping_index_to_label[i] for i in top_k_indices]
        
        return top_k_labels

    def get_top_k_drug_node_labels(self, drug_index, k_node_labels):
        top_k_drug_node_labels= self.top_100_node_labels_for_each_drug[drug_index][-k_node_labels:] # (k_node_labels -1)
        return top_k_drug_node_labels

    def get_top_k_indication_node_labels(self, indication_index, k_node_labels):
        top_k_indication_node_labels= self.top_100_node_labels_for_each_indication[indication_index][-k_node_labels:] # (k_node_labels -1)
        return top_k_indication_node_labels

    #@profile
    # def create_subgraph(self, top_k_node_labels):
    #     """
    #     Create a subgraph from the top k nodes and draw it.
        
    #     Input: 
    #     - top_k_node_labels (list of str): The labels of the nodes to include in the subgraph.

    #     Output:
    #     - nx.Graph: The subgraph containing only the top k nodes.
    #     - dict: A dictionary mapping node labels to colors.
    #     """
    #     # Check if input is valid
    #     assert isinstance(top_k_node_labels, list), "top_k_node_labels must be a list"
    #     #assert all(isinstance(node, (str, int)) for node in top_k_node_labels), "All elements in top_k_node_labels must be strings or integers"
    
    #     # Create a subgraph from the top k nodes
    #     subgraph = self.MSI.subgraph(top_k_node_labels)
        
    #     # Create a dictionary for node colors
    #     node_colors, node_shapes = self.get_node_colors_and_shapes(subgraph)

    #     return subgraph, node_colors, node_shapes
    
    def get_node_colors_and_shapes(self, subgraph):

        # Create a dictionary for node colors
        node_colors = {}
        node_shapes = {}
        for node in subgraph.nodes():
            if self.node_types[node] == 'protein':
                node_colors[node] = '#7F8C8D '  # dark grey color for proteins
                node_shapes[node] = 'ellipse'  # circle for proteins
            elif self.node_types[node] == 'bio':
                node_colors[node] = '#2ECC71'  # green, #2ECC71 color for biological functions
                node_shapes[node] = 'box'  # square for biological functions
            elif self.node_types[node] == 'drug':
                node_colors[node] = '#439AD9'  # blue, #03A9F4 color for drugs
                node_shapes[node] = 'triangle'  # triangle for drugs
            elif self.node_types[node] == 'indication':
                node_colors[node] = '#DD614A'  # red, #F44336, #DD614A color for indications
                node_shapes[node] = 'triangleDown'  # triangle for indications


        return node_colors, node_shapes
    
    def generate_subgraph_with_database(self, chosen_indication_label, chosen_drug_label, num_drug_nodes, num_indication_nodes, map_drug_diffusion_labels_to_indices, map_indication_diffusion_labels_to_indices, session):

        drug_index = map_drug_diffusion_labels_to_indices[chosen_drug_label]
        indication_index = map_indication_diffusion_labels_to_indices[chosen_indication_label]

        top_k_nodes_drug_subgraph = self.get_top_k_drug_node_labels(drug_index, num_drug_nodes)
        top_k_nodes_indication_subgraph = self.get_top_k_indication_node_labels(indication_index, num_indication_nodes)

        # Find top_k_nodes from diffusion profile
        top_k_nodes_MOA_subgraph = top_k_nodes_drug_subgraph + top_k_nodes_indication_subgraph

        # Define a Cypher query to get the subgraph data
        top_k_nodes_MOA_subgraph = self.convert_numbers_to_strings(top_k_nodes_MOA_subgraph)
        print(f'top_k_nodes_MOA_subgraph: {top_k_nodes_MOA_subgraph}')

        cypher_query = f"""
        MATCH (n)
        WHERE n.node IN {top_k_nodes_MOA_subgraph}
        OPTIONAL MATCH (n)-[r]->(m)
        WHERE m.node IN {top_k_nodes_MOA_subgraph}
        RETURN n, r, m
        """

        print(f'cypher_query: {cypher_query}')

        # Execute the Cypher query
        result = session.run(cypher_query)

        print(f'result: {result}')
        # Convert the result to a networkx graph
        MOA_subgraph = self.convert_neo4j_result_to_networkx_graph(result)

        print(f'MOA_subgraph: {MOA_subgraph}')
        print(f'MOA_subgraph.nodes(): {MOA_subgraph.nodes()}')

        # Get node colors and shapes
        MOA_subgraph_node_colors, MOA_subgraph_node_shapes = self.get_node_colors_and_shapes(MOA_subgraph)

        return MOA_subgraph, MOA_subgraph_node_colors, MOA_subgraph_node_shapes
    
    def convert_numbers_to_strings(self, input_list):
        return [str(item) for item in input_list]

    def convert_strings_to_numbers(self, input_list):
        return [int(item) if item.isdigit() else item for item in input_list]


    def convert_if_digit_string(self, value):
        return int(value) if str(value).isdigit() else value

    def result_generator(self, result):
        for record in result:
            # Get the nodes from the record and convert them if they are digit strings
            node_n = self.convert_if_digit_string(record['n']['node']) if record['n'] is not None else None
            node_m = self.convert_if_digit_string(record['m']['node']) if record['m'] is not None else None

            # Get the relationship from the record, if it exists
            relationship = record['r'] if 'r' in record.keys() and record['r'] is not None else None

            # If there's a relationship, yield the nodes and the relationship
            if relationship is not None and node_n is not None and node_m is not None:
                yield node_n, node_m, relationship

    def convert_neo4j_result_to_networkx_graph(self, result):
        # Create a generator from the result
        generator = self.result_generator(result)

        # Build the NetworkX graph from the generator
        graph = nx.Graph()
        for n, m, r in generator:
            graph.add_node(n)
            graph.add_node(m)
            if r is not None:  # Add the edge only if there's a relationship
                graph.add_edge(n, m, **r)

        return graph

    def convert_networkx_to_vis_graph_data(self, graph, node_colors, node_shapes):
        # Create a list of nodes and edges
        nodes = [{"id": self.mapping_label_to_index[node_label], 
                "label": f'{self.mapping_all_labels_to_names[node_label]}',
                "color": node_colors[node_label],
                "shape": node_shapes[node_label]
                } 
                for node_label in graph.nodes]
        
        edges = [{"from": self.mapping_label_to_index[edge[0]], 
                "to": self.mapping_label_to_index[edge[1]],
                "arrows": "to"
                } 
                for edge in graph.edges]

        # Return the graph data
        return {"nodes": nodes, "edges": edges}
    
    def invert_dict(self, dictionary):
        return {v: k for k, v in dictionary.items()}
    

