from HPW_Tracing.Build_graphs import iniciate_graph
from HPW_Tracing.Tracing import tracing_between_links
import warnings
import pandas as pd
from time import time
warnings.filterwarnings("ignore")

db = 'C:\PythonProjects\__db'
datawarehouse_infrastrcuture  = r'C:\Users\C21252\City of Houston\WWIP Planning Data Warehouse - General\GIS Database\01_Infrastructure'
forceupdate = False
G = iniciate_graph(db, datawarehouse_infrastrcuture, forceupdate)

start_link = '2509894'
end_link = '2509500'
nodes, edges = tracing_between_links(G, start_link, end_link)