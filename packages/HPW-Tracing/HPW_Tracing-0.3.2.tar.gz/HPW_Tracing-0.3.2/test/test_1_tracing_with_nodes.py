from HPW_Tracing.Build_graphs import iniciate_graph
from HPW_Tracing.Tracing import create_mhNum_UFID_dict, tracing_with_node
import warnings
import pandas as pd
from time import time
warnings.filterwarnings("ignore")

db = r'C:\Users\C21252\City of Houston\HWP-AIAP-TEAM - Documents\General\Working\Peng\Peng Work Final\__tracing_database'
datawarehouse_infrastrcuture  = r'C:\Users\C21252\City of Houston\WWIP Planning Data Warehouse - General\GIS Database\01_Infrastructure'
forceupdate = False
dict = create_mhNum_UFID_dict(db)
G = iniciate_graph(db, datawarehouse_infrastrcuture, forceupdate)

# Case 1 using mh_number
nodeID = 'AS019087'  # tracing starting node
direction = 'upstream'
distance = 2000 #  put None if you want to search the whole network, it will be much faster rather than defining a large distance
# or else you can choose a distance, for example, 1000 ft

node_dict,edges_df = tracing_with_node(G, dict, nodeID, direction, distance)
print(node_dict)
print(edges_df)