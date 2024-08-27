from HPW_Tracing.Build_graphs import iniciate_graph

db = 'C:\\PythonProjects\\__db'
datawarehouse_infrastrcuture = 'C:\\Users\\C21252\\City of Houston\\WWIP Planning Data Warehouse - General\GIS Database\\01_Infrastructure'
forceupdate = False

G = iniciate_graph(db, datawarehouse_infrastrcuture, forceupdate)
