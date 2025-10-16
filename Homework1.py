import random
import argparse
import math
import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict

Point = Tuple[int, int]

# random bir şekilde ikililerden oluşan bir array oluşturma
def generate_points(n, width, height, seed) -> List[Point]:

    rng = random.Random(seed)
    return [(rng.randrange(-width,width), rng.randrange(-height, height)) for _ in range(n)]


def build_graph(points: List[Point]) -> tuple[nx.Graph, Dict[Point, Point]]:
    
    G = nx.Graph()
    # arrayimizdeki ikilileri node olarak G grafımıza ekleme
    G.add_nodes_from(points)
    # Buradaki for döngüsü ile yukarıda oluşturduğumuz node'lar arasındaki mesafeyi hesaplıyoruz.
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            u = points[i]
            v = points[j]
            distance = math.hypot(u[0] - v[0], u[1] - v[1])
            G.add_edge(u, v, weight = distance)
    # Bu kod satırı grafiği gerçek koordinatlara göre çizmemizi sağlıyor.
    pos = {p: p for p in points}
    return G, pos


def greedy_tour(G: nx.Graph, start: Point) -> tuple[List[Point], float]:

    unvisited = set(G.nodes())
    tour = [start]
    unvisited.remove(start)
    total = 0.0
    current = start

    while unvisited:
        nxt, best = None, float("inf")
        for cand in unvisited:
            w = G[current][cand]["weight"]
            if w < best:
                best, nxt = w, cand
        tour.append(nxt)
        unvisited.remove(nxt)
        total += best
        current = nxt

    total += G[current][start]["weight"]
    tour.append(start)
    return tour, total


def draw_tour(G: nx.Graph, pos: Dict[Point, Point], tour: List[Point]):
    
    #edge_labels = {(u, v): f"{d['weight']:.3f}" for u, v, d in G.edges(data=True)}
    # i sıra numarası, p ise noktanın x ve y değeri
    labels = {p: f"P{i}\n{p}" for i, p in enumerate(G.nodes, start=1)}
    tour_edges = list(zip(tour[:-1], tour[1:]))
    
    plt.figure(figsize=(8, 8))
    
    # Tüm grafiği çiz. 
    nx.draw(G, pos, with_labels=False, node_color="gray", edge_color="gray", alpha=0.7)
    #nx.draw_networkx_edge_labels(G, pos, font_size=7, edge_labels = edge_labels, label_pos=0.5)
    
    # node'ları mavi olarak çiz.
    nx.draw_networkx_nodes(G, pos, node_color="lightblue", node_size=600, edgecolors="black", linewidths=0.4)
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=6)
    
    # Greedy algoritmasının seçtiği yolu kırmızı ile çiz.
    nx.draw_networkx_edges(G, pos, edgelist=tour_edges, width=1.4, edge_color="red")
    
    plt.title(f"Greedy TSP (start=P1) | Tour length ≈ {sum(G[a][b]['weight'] for a,b in tour_edges):.3f}")
    plt.show()


if __name__ == "__main__":
    #Parametreler
    parser = argparse.ArgumentParser(description="Greedy TSP Visualization")
    parser.add_argument("--n", type=int, default=15, help="number of nodes")
    parser.add_argument("--width", type=int, default=100, help="max x coordinate range")
    parser.add_argument("--height", type=int, default=100, help="max y coordinate range")
    parser.add_argument("--seed", type=int, default=4, help="random seed")
    # İlk noktadan arama başlar.
    parser.add_argument("--start", type=int, default=0, help="start node index")
    args = parser.parse_args()
    
    points = generate_points(n=args.n, width=args.width, height=args.height, seed=args.seed) # Node'larımızı oluşturuyoruz.
    G, pos = build_graph(points) # oluşturduğumuz node'larla tam bir grafik hazırlıyoruz.
    start_node = points[args.start] #İlk noktayı başlangıç node'u olarak atıyoruz.
    tour, tour_len = greedy_tour(G, start_node)
    print("Tour:", tour)
    print("Tour Lenght:", round(tour_len, 3))
    
    draw_tour(G, pos, tour)
    







