from HPW_Tracing.Build_graphs import iniciate_graph
from HPW_Tracing.Tracing import create_mhNum_UFID_dict, tracing_with_link
import warnings
import pandas as pd
from time import time
warnings.filterwarnings("ignore")

db = 'C:\PythonProjects\__db'
datawarehouse_infrastrcuture  = r'C:\Users\C21252\City of Houston\WWIP Planning Data Warehouse - General\GIS Database\01_Infrastructure'
forceupdate = False
dict = create_mhNum_UFID_dict(db)
G = iniciate_graph(db, datawarehouse_infrastrcuture, forceupdate)


linkID  = '7590964' # link ID
distance = None  # search withing 1000000 ft,  put None if you want to search the whole network
direction = 'downstream'

node_dict,edges_df = tracing_with_link(G, dict, linkID, direction, distance)