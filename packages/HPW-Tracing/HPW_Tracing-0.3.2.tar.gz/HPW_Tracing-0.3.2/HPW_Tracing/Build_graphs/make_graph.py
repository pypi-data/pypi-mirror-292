import pickle
import networkx as nx
import pandas as pd
import os
from HPW_Tracing.Load_data import load_data
from HPW_Tracing.Build_graphs.network_correction import correct_network
from HPW_Tracing import config





### main function
def iniciate_graph(db_folder: str, datawarehouse: str, update: bool = False) -> nx.DiGraph:
    """
    Create a network graph from the sewer network data and save it to a pickle file.
    if update is True, remove the pre-existing pickle files and recreate those pk files before creating the graph.

    :param db_folder: database folder where the pickle files are saved
    :param datawarehouse: datawarehouse folder where the shapefiles are saved
    :param update: if True, remove the pre-existing pickle files and load the data from the shapefiles
    :return: nx.DiGraph
    """

    _update_config_file(db_folder, datawarehouse)

    db_folder = config.db_folder
    datawarehouse = config.datawarehouse


    # make src folder if it does not exist
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)

    if update:
        print('-' * 50)
        print('Removing the pre-existing pickle files')
        for file in os.listdir(db_folder):
            if file.endswith('.pkl'):
                os.remove(os.path.join(db_folder, file))
        update = False

    if os.path.exists(os.path.join(db_folder, 'network_graph.pkl')):
        print('-' * 50)
        print('Loading the network graph from the pickle file...')
        G = load_graphs_from_pickle(db_folder)
    else:
        print('-' * 50)
        print('Creating the network graph...')
        make_graphs_pickle(db_folder, datawarehouse, update)
        G = load_graphs_from_pickle(db_folder)

    print('-' * 50)
    print('Network graph created successfully.')
    return G


def load_graphs_from_pickle(db_folder: str) -> nx.DiGraph:
    with open(os.path.join(db_folder, 'network_graph.pkl'), 'rb') as handle:
        G = pickle.load(handle)
    return G


def make_graphs_pickle(db_folder: str, datawarehouse: str, update: bool):
    # if the pickle file corrected_network_data.pkl exists, load the corrected network data from the pickle file
    if os.path.exists(os.path.join(db_folder, 'network_data.pkl')):
        print('-' * 50)
        print('Loading the corrected network data from the pickle file...')
        with open(os.path.join(db_folder, 'network_data.pkl'), 'rb') as handle:
            corrected_network_data = pickle.load(handle)
    else:
        # load the data
        gm_shp_gdf, fm_shp_gdf, mh_shp_gdf, cleanout_shp_gdf = load_data(db_folder, datawarehouse, update)

        # correct the network data
        corrected_network_data = correct_network(gm_shp_gdf, fm_shp_gdf, mh_shp_gdf, cleanout_shp_gdf, db_folder)

    # # create a directed graph from the sewer network

    # G = nx.from_pandas_edgelist(corrected_network_data, 'start_mh', 'end_mh', edge_attr=['UFID', 'type', 'length'],
    #                             create_using=nx.DiGraph())
    print('-' * 50)
    print('making graph with the new method')
    G = create_digraph_from_dataframe(corrected_network_data, 'start_mh', 'end_mh',
                                      ['UFID', 'type', 'length'])

    # save G into a pickle file
    with open(os.path.join(db_folder, 'network_graph.pkl'), 'wb') as handle:
        pickle.dump(G, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print('Graph created successfully and saved to the database folder as network_graph.pkl.')


def create_digraph_from_dataframe(df, source_col, target_col, attr_col=None):
    # Initialize an empty directed graph
    G = nx.DiGraph()

    # Iterate over the DataFrame rows
    for idx, row in df.iterrows():
        source = row[source_col]
        target = row[target_col]

        # Add edge with attributes if specified
        if attr_col:
            G.add_edge(source, target, attribute=row[attr_col])
        else:
            G.add_edge(source, target)

    return G


def _update_config_file(db_folder: str, datawarehouse: str, config_file_path: str = 'config.py'):
    """
    Update the config.py file with the provided db_folder and datawarehouse paths.

    :param db_folder: The path to the database folder
    :param datawarehouse: The path to the datawarehouse folder
    :param config_file_path: The path to the config file, defaults to 'config.py'

    """
    # Get the path to the current file's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    db_folder = db_folder.replace('\\', '/')
    datawarehouse = datawarehouse.replace('\\', '/')

    # Construct the path to the config.py file in the Tracing directory
    config_file_path = os.path.join(current_dir, '..', 'config.py')

    # Normalize the path to ensure it's correctly resolved
    config_file_path = os.path.normpath(config_file_path)


    with open(config_file_path, 'w') as config_file:
        config_file.write(f"db_folder = '{db_folder}'\n")
        config_file.write(f"datawarehouse = '{datawarehouse}'\n")

    print(f"Configuration updated in {config_file_path}")