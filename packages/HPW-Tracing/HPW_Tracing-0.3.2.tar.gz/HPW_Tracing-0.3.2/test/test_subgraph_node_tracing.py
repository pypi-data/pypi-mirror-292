import pickle
from HPW_Tracing.Tracing import tracing_with_node
from HPW_Tracing.Tracing import create_mhNum_UFID_dict, tracing_with_node
import warnings
import pandas as pd
from time import time
warnings.filterwarnings("ignore")

db = 'C:\PythonProjects\__db'
datawarehouse_infrastrcuture  = r'C:\Users\C21252\City of Houston\WWIP Planning Data Warehouse - General\GIS Database\01_Infrastructure'
forceupdate = False
dict = create_mhNum_UFID_dict(db)


sub_graph = r'C:\Users\C21252\PycharmProjects\Sharepoints\_00_HPW_NetTracing\test\subgraph_test\ls_fm_subgraph_new.pick'
all_nodes = r'C:\Users\C21252\PycharmProjects\Sharepoints\_00_HPW_NetTracing\test\subgraph_test\all_nodes.pick'


with open(sub_graph, 'rb') as f:
    sub_graph = pickle.load(f)

with open(all_nodes, 'rb') as f:
    all_nodes = pickle.load(f)

nodeID = 'temp_59909'  # tracing starting node
direction = 'upstream'  # tracing direction
distance = None

node_dict,edges_df = tracing_with_node(sub_graph, dict, nodeID, direction, distance)