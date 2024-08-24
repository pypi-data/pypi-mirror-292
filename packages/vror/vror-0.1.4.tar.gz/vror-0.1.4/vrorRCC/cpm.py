
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd


def create_graph():
    return nx.DiGraph()

def add_event(graph, task, dependencies={}):
    if task not in graph:
        graph.add_node(task)
    for dep, duration in dependencies.items():
        if dep not in graph:
            graph.add_node(dep)
        graph.add_edge(dep, task, weight=duration)

def find_critical_path(graph):
    critical_path = nx.dag_longest_path(graph, weight='weight')
    critical_path_length = nx.dag_longest_path_length(graph, weight='weight')
    return critical_path, critical_path_length

def visualize_graph(graph):
    pos = nx.spring_layout(graph)
    plt.figure(figsize=(12, 8))
    
    nx.draw(graph, pos, with_labels=True, node_size=2000, node_color='lightblue', font_size=10, font_weight='bold')
    
    edge_labels = {(u, v): f'{d["weight"]}' for u, v, d in graph.edges(data=True)}
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)
    
    critical_path, _ = find_critical_path(graph)
    nx.draw_networkx_edges(graph, pos, edgelist=list(zip(critical_path, critical_path[1:])), edge_color='r', width=2)
    
    plt.title("CPM Diagram")
    plt.show()

    
def compute_te(activities):
    data = []
    for activity, to, tl, tp in activities:
        te = (to + 4 * tp + tl) / 6
        data.append({'Activity': activity, 'TE': te})
    
    df = pd.DataFrame(data)
    return print(df.to_string(index=False))