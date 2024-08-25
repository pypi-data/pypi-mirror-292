import json
import xml.etree.ElementTree as ET

def build_elements(data):
    """
    Builds the elements dictionary from the HS3 data.

    Args:
        data (dict): HS3 data loaded from JSON.

    Returns:
        dict: Dictionary of elements from functions, distributions, and domains.
    """
    elements = {}
    for e in data.get("functions", []):
        elements[e["name"]] = e
    for e in data.get("distributions", []):
        elements[e["name"]] = e
    for d in data.get("domains", []):
        for v in d["axes"]:
            elements[v["name"]] = v
    return elements

def build_graph_model(data, likelihood, elements):
    """
    Builds the graph model based on the selected likelihood or the entire data.

    Args:
        data (dict): HS3 data loaded from JSON.
        likelihood (dict or None): The selected likelihood, or None.
        elements (dict): Dictionary of elements.

    Returns:
        dict: The graph model represented as a dictionary of sets.
    """
    model = {}
    if likelihood:
        dists = likelihood.get("distributions", []) + likelihood.get("aux_distributions", [])
        for dist in dists:
            if dist in elements:
                fill_graph(model, elements[dist], elements)
    else:
        for d in data.get("distributions", []):
            fill_graph(model, d, elements)
    return model

def write_graphml(model, outfile, likelihood=None):
    """
    Writes the graph model to a GraphML file.

    Args:
        model (dict): The graph model.
        outfile (str): Path to the output GraphML file.
        likelihood (dict or None): The selected likelihood, or None.

    Returns:
        None
    """
    # Create the root element without the namespace prefix
    data = ET.Element("graphml")
    
    # Manually add the necessary namespace and schema declarations as attributes
    data.set("xmlns", "http://graphml.graphdrawing.org/xmlns")
    data.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    data.set("xsi:schemaLocation", "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd")
    
    # Create the graph element
    graph = ET.SubElement(data, "graph")
    graph.set("id", "model")
    graph.set("edgedefault", "directed")

    nodes = []

    # Add nodes to the graph
    if likelihood:
        lh = ET.SubElement(graph, "node")
        lh.set("id", likelihood["name"])
        nodes.append(lh)

    for name in model.keys():
        node = ET.SubElement(graph, "node")
        node.set("id", name)
        nodes.append(node)
            
    # Add edges to the graph
    for client, serverlist in model.items():
        for server in serverlist:
            edge = ET.SubElement(graph, "edge")
            edge.set("source", str(server))
            edge.set("target", str(client))

    # Add edges connecting distributions to the likelihood node, if applicable
    if likelihood:
        for dist in likelihood.get("distributions", []) + likelihood.get("aux_distributions", []):
            edge = ET.SubElement(graph, "edge")
            edge.set("source", str(dist))
            edge.set("target", likelihood["name"])

    # Write the tree to the output file
    with open(outfile, "wb") as f:
        tree = ET.ElementTree(data)
        tree.write(f, encoding='utf-8', xml_declaration=True)

def collect_strings(d,skipName):
    """
    Recursively collects unique strings from a dictionary.

    Args:
        d (dict): The input dictionary.
        skipName (bool): Whether to skip collecting strings from the "name" key.

    Returns:
        set: A set of unique strings collected from the dictionary.
    """
    values = set()
    for k,v in d.items():
        if skipName and k == "name": continue        
        elif type(v) == list:
            for e in v:
                if type(e) == str:
                    values.add(e)
                if type(e) == dict:
                    values = values.union(collect_strings(e,False))
        elif type(v) == dict:
            values = values.union(collect_strings(v,False))
        else:
            values.add(str(v))
    return values
    
def fill_graph(model,element,elements):
    """
    Fills a graph model recursively with the provided element and all its dependents

    Args:
        model (dict): The graph model.
        element (dict): The current element.
        elements (dict): Dictionary of elements.

    Returns:
        None
    """
    name = element["name"]
    if name in model.keys():
        return
    model[name] = set()
    values = collect_strings(element,True)

    for k in elements.keys():
        for v in values:
            if k in v:
                model[element["name"]].add(k)
                fill_graph(model,elements[k],elements)
