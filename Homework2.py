import argparse
import random
import math
import networkx as nx
import osmnx as ox
import folium
import os

# Yol ağını indirdiğimiz fonksiyon.
def load_graph(place, network_type="drive", simplify=True):

    return ox.graph_from_place(place, network_type=network_type, simplify=simplify)

# Rastgele düğüm seçmek için fonksiyon
def pick_nodes(G, n, seed):
    rng = random.Random(seed)
    nodes = list(G.nodes())
    if n > len(nodes):
        raise ValueError("n, graf düğümlerinden büyük olamaz.")
    return rng.sample(nodes, k=n)

# Seçilen düğümlerin arasındaki en kısa mesafeyi hesapla
def shortest_lengths(G, nodes):
    dist = {}
    for i, u in enumerate(nodes):
        lengths = nx.single_source_dijkstra_path_length(G, u, weight="length")
        for v in nodes[i+1:]:
            d = lengths.get(v, float("inf"))
            dist[(u, v)] = d
            dist[(v, u)] = d
    return dist

# Problemimizin tam grafını oluşturan fonksiyon
def build_complete_graph(nodes, dist):
    H = nx.Graph()
    H.add_nodes_from(nodes)
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            u, v = nodes[i], nodes[j]
            d = dist[(u, v)]
            if math.isfinite(d):
                H.add_edge(u, v, weight=d)
    return H

# Greedy algoritması turumuz
def greedy_tour(H, start):
    unvisited = set(H.nodes())
    tour = [start]
    unvisited.remove(start)
    total = 0.0
    current = start

    while unvisited:
        nxt = min(unvisited, key=lambda x: H[current][x]["weight"])
        total += H[current][nxt]["weight"]
        tour.append(nxt)
        unvisited.remove(nxt)
        current = nxt

    total += H[current][start]["weight"]
    tour.append(start)
    return tour, total

# Foliumda harita çizimi için fonksiyon
def draw_folium_map(G, tour, out_html="tsp_greedy_realmap.html"):

# Merkez için (lat (latitude), lon (longitude)) ortalaması alıyoruz
    uniq = list(dict.fromkeys(tour))
    lat = sum(G.nodes[n]["y"] for n in uniq) / len(uniq)
    lon = sum(G.nodes[n]["x"] for n in uniq) / len(uniq)
    m = folium.Map(location=(lat, lon), zoom_start=13, control_scale=True)

    # Burada Nodelarımıza marker ekliyoruz 
    for i, node in enumerate(tour[:-1], start=1):
        y, x = G.nodes[node]["y"], G.nodes[node]["x"]
        folium.Marker(
            location=(y, x),
            tooltip=f"P{i}",
            popup=f"P{i}<br>lat={y:.6f}, lon={x:.6f}"
        ).add_to(m)

    # Gerçek yolları tur olarak çiziyoruz. (kırmızı renkle)
    for u, v in zip(tour[:-1], tour[1:]):
        route = nx.shortest_path(G, u, v, weight="length")
        coords = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in route]
        folium.PolyLine(coords, color="red", weight=5, opacity=0.85).add_to(m)

# Aynı isimde dosyaları üzerine yazmaması için dosya sonunda numaralandırma yapan fonksiyon
    base, ext = os.path.splitext(out_html)
    i = 1
    new_name = out_html
    while os.path.exists(new_name):
        new_name = f"{base}_{i}{ext}"
        i += 1


    m.save(new_name)
    return new_name

def main():
# Burası konsol üzerinden kodumuzu çalıştırırken düğüm sayısı, seed gibi değerleri değiştirebilmek için olan kısım
    parser = argparse.ArgumentParser(description="Gerçek harita üzerinde Traveling Salesman Problemi çözümü (nearest neighbor) ")
    parser.add_argument("--place", default="Nilüfer, Bursa, Turkey", help="İlçe/il/ülke adı (OSM için)")
    parser.add_argument("--type", default="drive", choices=["drive", "walk", "bike"], help="Nodelar arasında neyle gezeceğiz?")
    parser.add_argument("--n", type=int, default=5, help="TSP düğüm sayısı")
    parser.add_argument("--seed", type=int, default=9, help="Seed")
    parser.add_argument("--start", type=int, default=0, help="Başlangıç düğümü indexi")
    parser.add_argument("--out", default="tsp_greedy_realmap.html", help="HTML dosyası")
    args = parser.parse_args()

    print(f"'{args.place}' yol ağı indiriliyor, Gezi türü: {args.type}")
    G = load_graph(args.place, network_type=args.type)

# Düğümleri seç
    tsp_nodes = pick_nodes(G, args.n, args.seed)
    if not (0 <= args.start < len(tsp_nodes)):
        raise ValueError("start indexi aralık dışında")

# İkili nodelarımız arasındaki en kısa mesafeyi kesapla
    dist = shortest_lengths(G, tsp_nodes)

# Grafı oluştur
    H = build_complete_graph(tsp_nodes, dist)

# Greedy turumuzu oluştur
    start_node = tsp_nodes[args.start]
    tour, total_m = greedy_tour(H, start_node)
    print(f"Tur uzunluğu ≈ {total_m/1000:.3f} km")
    print(f"Tur sırası (node id): {tour}")

# Foliumda haritayı çiz
    out_file = draw_folium_map(G, tour, out_html=args.out)
    print(f"Kaydedildi: {out_file}")

if __name__ == "__main__":
    main()
