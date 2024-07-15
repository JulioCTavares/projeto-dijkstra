import psycopg2
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import messagebox

# Função para carregar o grafo do banco de dados
def load_graph_from_db():
    conn = psycopg2.connect(
        dbname="grafo",
        user="postgres",
        password="senha123",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()

    # Carregar nós e arestas do banco de dados
    cursor.execute('SELECT id FROM nodes')
    nodes = cursor.fetchall()

    cursor.execute('SELECT source, target, weight FROM edges')
    edges = cursor.fetchall()

    conn.close()

    # Construir o grafo
    graph = nx.Graph()
    for node in nodes:
        graph.add_node(node[0])
    for source, target, weight in edges:
        graph.add_edge(source, target, weight=float(weight))

    return graph

# Função para executar o algoritmo de Dijkstra
def dijkstra(graph, start, end):
    shortest_paths = {start: (None, 0)}
    current_node = start
    visited = set()
    
    while current_node != end:
        visited.add(current_node)
        destinations = graph[current_node]
        weight_to_current_node = shortest_paths[current_node][1]

        for next_node, data in destinations.items():
            weight = data['weight']
            total_weight = weight_to_current_node + weight
            if next_node not in shortest_paths:
                shortest_paths[next_node] = (current_node, total_weight)
            else:
                current_shortest_weight = shortest_paths[next_node][1]
                if current_shortest_weight > total_weight:
                    shortest_paths[next_node] = (current_node, total_weight)
        
        next_destinations = {node: shortest_paths[node] for node in shortest_paths if node not in visited}
        if not next_destinations:
            return "Route not possible"
        current_node = min(next_destinations, key=lambda k: next_destinations[k][1])
        
    path = []
    while current_node is not None:
        path.append(current_node)
        next_node = shortest_paths[current_node][0]
        current_node = next_node
    path = path[::-1]
    return path

# Função para desenhar o grafo e o caminho mais curto
def draw_graph(graph, shortest_path, pos):
    plt.figure(figsize=(10, 10))
    nx.draw(graph, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=10, font_weight='bold')
    edge_labels = nx.get_edge_attributes(graph, 'weight')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

    # Destacar o caminho mais curto
    if shortest_path:
        path_edges = list(zip(shortest_path, shortest_path[1:]))
        nx.draw_networkx_nodes(graph, pos, nodelist=shortest_path, node_color='red')
        nx.draw_networkx_edges(graph, pos, edgelist=path_edges, edge_color='red', width=2)

# Função para integrar o gráfico ao Tkinter
def create_graph_canvas(graph, root, shortest_path, pos):
    fig, ax = plt.subplots(figsize=(10, 10))
    nx.draw(graph, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=10, font_weight='bold', ax=ax)
    edge_labels = nx.get_edge_attributes(graph, 'weight')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, ax=ax)

    # Destacar o caminho mais curto
    if shortest_path:
        path_edges = list(zip(shortest_path, shortest_path[1:]))
        nx.draw_networkx_nodes(graph, pos, nodelist=shortest_path, node_color='red')
        nx.draw_networkx_edges(graph, pos, edgelist=path_edges, edge_color='red', width=2)
    
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    return canvas

# Função para calcular e exibir o caminho mais curto
def calculate_and_show_path(graph, start, end, root, pos):
    try:
        start = int(start)
        end = int(end)
        if start < 1 or start > 452 or end < 1 or end > 452:
            raise ValueError("IDs devem estar no intervalo de 1 a 452")
        shortest_path = dijkstra(graph, start, end)
        if shortest_path == "Route not possible":
            messagebox.showerror("Error", "Route not possible")
        else:
            create_graph_canvas(graph, root, shortest_path, pos)
    except ValueError as e:
        messagebox.showerror("Error", str(e))

# Função principal para executar a aplicação Tkinter
def main():
    root = tk.Tk()
    root.title("Grafo do Banco de Dados")

    graph = load_graph_from_db()
    pos = nx.spring_layout(graph, seed=42)  # Definindo uma semente fixa para o layout

    # Entrada para o nó inicial
    tk.Label(root, text="Nó Inicial (1-452):").pack()
    start_node_entry = tk.Entry(root)
    start_node_entry.pack()

    # Entrada para o nó final
    tk.Label(root, text="Nó Final (1-452):").pack()
    end_node_entry = tk.Entry(root)
    end_node_entry.pack()

    # Botão para calcular o caminho mais curto
    tk.Button(root, text="Calcular Caminho Mais Curto", 
              command=lambda: calculate_and_show_path(graph, start_node_entry.get(), end_node_entry.get(), root, pos)).pack()

    root.mainloop()

if __name__ == "__main__":
    main()
