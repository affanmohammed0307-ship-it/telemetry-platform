import networkx as nx
import matplotlib.pyplot as plt

# Build a simple knowledge graph
G = nx.DiGraph()

# Nodes = entities
G.add_node("Engine")
G.add_node("Temperature Sensor")
G.add_node("Battery")
G.add_node("Voltage Sensor")
G.add_node("Telemetry System")

# Edges = relationships
G.add_edge("Temperature Sensor", "Engine", relation="monitors")
G.add_edge("Voltage Sensor", "Battery", relation="monitors")
G.add_edge("Engine", "Telemetry System", relation="sends_data_to")
G.add_edge("Battery", "Telemetry System", relation="sends_data_to")

# Visualize
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color="#00ff88", 
        node_size=2000, font_size=10, arrows=True)
edge_labels = nx.get_edge_attributes(G, 'relation')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
plt.title("Vehicle Sensor Knowledge Graph")
plt.savefig("knowledge_graph.png")
print("Graph saved")