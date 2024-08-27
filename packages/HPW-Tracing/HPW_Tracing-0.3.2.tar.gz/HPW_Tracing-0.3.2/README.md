## HPW_Tracing - A tracing tool for creating treacable flownetwork based on City of Houston GIS data

### Introduction
This tool is designed to create a traceable flow network based on the City of Houston GIS data. The tool is developed in Python and uses the NetworkX library to create a graph representation of the flow network. The tool is designed to be used in the context of the Houston Public Works (HPW) department, but can be adapted to other contexts as well. The tool is designed to be used in conjunction with the HPW's existing GIS data, which includes information about the city's infrastructure, such as manholes, pipes, and lifstations etc.

### Installation
To install the tool, you need to have Python installed on your system. You can download Python from the official website: https://www.python.org/. Once you have Python installed, you can install the tool by running the following command in your terminal:

```sh
pip install hpw_tracing
```
Please make sure you have the latest version of hpw_tracing by running the following command in your terminal:
```sh
pip install --upgrade hpw_tracing
```

### Tracing Usage
To use the tool, please refer the example notebook in docs folder. 
- if you are just regular user, you only need view example 4 to 7
- if you are developer, you can view all examples

### Creating subgraph or abstract graph
After version 0.1.7, the tool can create subgraph or abstract graph based on the input graph. The subgraph is created based on the input graph and the list of nodes that you want to include in the subgraph. The abstract graph is created based on the input graph and the list of nodes that you want to include in the abstract graph. The abstract graph is a simplified version of the input graph, where the nodes are grouped together based on the input list of nodes. The abstract graph can be used to represent the flow network in a more compact and easy-to-understand way.
- for example, you can create subgraph that only includes waterwater treatment plant and liftstaions to better analyze the flow network between these two types of nodes.

The subgraph example is in its own folder within the doc folder because it contains a detailed step on how to create and use a subgraph. It is recommneded to recreate the ls, flowmeter and wwtp lookup tables everytime you run the notebook, because whenever the db is re-generated, the previously lookup table will be obsolete.