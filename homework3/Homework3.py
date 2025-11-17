import argparse
import random
import math
import time
import os

import networkx as nx
import osmnx as ox
import folium
import matplotlib.pyplot as plt

from ortools.constraint_solver import pywrapcp, routing_enums_pb2  # OR-Tools (pip install ortools)

# Yol ağını indirdiğimiz fonksiyon.
def load_graph(place, network_type="drive", simplify=True):
    # Örnek: "Kadıköy, Istanbul, Turkey"
    # network_type: drive, walk, bike gibi olabilir.
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

    # Her adımda şu anki düğüme en yakın olan düğüme gidiyoruz
    while unvisited:
        nxt = min(unvisited, key=lambda x: H[current][x]["weight"])
        total += H[current][nxt]["weight"]
        tour.append(nxt)
        unvisited.remove(nxt)
        current = nxt

    # En sonunda başlangıç noktasına tekrar dönüyoruz
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

# Problemimizin OR-Tools ile çözümünü yapan fonksiyon
def solve_tsp_ortools(H, start_node):
    # OR-Tools index tabanlı çalıştığı için düğümleri 0..N-1 şeklinde mapliyoruz.
    nodes = list(H.nodes())
    index_of = {node: i for i, node in enumerate(nodes)}
    n = len(nodes)

    # Mesafe matrisini oluşturan kısım
    dist_matrix = [[0] * n for _ in range(n)]
    for u, v, data in H.edges(data=True):
        i = index_of[u]
        j = index_of[v]
        # OR-Tools integer bir sayı beklediği için ağırlığı yuvarlayarak int yapıyoruz.
        w = int(round(data["weight"]))
        dist_matrix[i][j] = w
        dist_matrix[j][i] = w

    start_index = index_of[start_node]

    manager = pywrapcp.RoutingIndexManager(n, 1, start_index)
    routing = pywrapcp.RoutingModel(manager)
    
    # OR-Tools her kenarın maliyetini bu fonksiyon ile sorgulatıyor.
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return dist_matrix[from_node][to_node]

    transit_cb_idx = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_cb_idx)

    search_params = pywrapcp.DefaultRoutingSearchParameters()
    # Başlangıç çözümünü hızlı olması için PATH_CHEAPEST_ARC ile üretiyoruz.
    search_params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    solution = routing.SolveWithParameters(search_params)
    if solution is None:
        raise RuntimeError("OR-Tools çözüm bulamadı.")

    # Çözümden turu çıkartan kısım
    index = routing.Start(0)
    route_indices = []
    while not routing.IsEnd(index):
        node_idx = manager.IndexToNode(index)
        route_indices.append(node_idx)
        index = solution.Value(routing.NextVar(index))
    # OR-Tools start_indexe dönerek bitiriyor 

    route_nodes = [nodes[i] for i in route_indices]

    # Tur uzunluğunu H ağırlıklardan hesaplıyoruz.
    total = 0.0
    for u, v in zip(route_nodes[:-1], route_nodes[1:]):
        total += H[u][v]["weight"]

    return route_nodes, total

# çoklu topoloji için karşılaştırma deneyini yapan fonksiyon
def run_comparison_experiments(G, args):
    num_instances = args.instances
    base_seed = args.seed
    n = args.n
    start_index = args.start

    greedy_lengths = []
    ortools_lengths = []
    greedy_times = []
    ortools_times = []
    seeds_used = []

    # seed offset sayacı
    k = 0  

    # İstediğimiz sayıda geçerli instance bulana kadar devam etmesini sağlayan kısım
    while len(greedy_lengths) < num_instances:
        seed = base_seed + k
        k += 1

        # Her deney için yeni bir topoloji seçmemizi sağlayan kısım
        tsp_nodes = pick_nodes(G, n, seed)
        if not (0 <= start_index < len(tsp_nodes)):
            raise ValueError("start index aralık dışında")

        dist = shortest_lengths(G, tsp_nodes)

        # Eğer bazı çiftler arasında hiç yol yoksa (inf mesafe), bu instance'ı atla
        if any(not math.isfinite(d) for d in dist.values()):
            print(f"Instance {len(greedy_lengths)+1:02d} | seed={seed} | SKIPPED (disconnected nodes)")
            continue

        H = build_complete_graph(tsp_nodes, dist)
        start_node = tsp_nodes[start_index]

        # Greedy
        t0 = time.perf_counter()
        tour_greedy, len_greedy = greedy_tour(H, start_node)
        t1 = time.perf_counter()

        # OR-Tools
        t2 = time.perf_counter()
        tour_opt, len_opt = solve_tsp_ortools(H, start_node)
        t3 = time.perf_counter()

        greedy_lengths.append(len_greedy)
        ortools_lengths.append(len_opt)
        greedy_times.append(t1 - t0)
        ortools_times.append(t3 - t2)
        seeds_used.append(seed)

        print(
            f"Instance {len(greedy_lengths):02d} | seed={seed} | "
            f"Greedy={len_greedy/1000:.3f} km | OR-Tools={len_opt/1000:.3f} km"
        )

    # Ortalama değerleri hesaplayan kısım
    avg_g_len = sum(greedy_lengths) / num_instances
    avg_o_len = sum(ortools_lengths) / num_instances
    avg_g_time = sum(greedy_times) / num_instances
    avg_o_time = sum(ortools_times) / num_instances

    print("\n--- Ortalama Sonuçlar ---")
    print(f"Greedy ort. uzunluk:   {avg_g_len/1000:.3f} km")
    print(f"OR-Tools ort. uzunluk: {avg_o_len/1000:.3f} km")
    print(f"Greedy ort. süre:      {avg_g_time:.5f} s")
    print(f"OR-Tools ort. süre:    {avg_o_time:.5f} s")

    # Sonuçları hem tablo hem grafik olarak kaydeden kısım
    save_results_table(
        seeds_used,
        greedy_lengths,
        ortools_lengths,
        greedy_times,
        ortools_times,
        filename="tsp_comparison_table.png"
    )
    save_length_plot(
        greedy_lengths,
        ortools_lengths,
        filename="tsp_comparison_lengths.png"
    )
    save_time_plot(
        greedy_times,
        ortools_times,
        filename="tsp_comparison_times.png"
    )



# Matplotlib ile tabloyu görsel olarak kaydetmemize yarayan fonksiyon
def save_results_table(seeds, greedy_lengths, ortools_lengths, greedy_times, ortools_times, filename):
    num_instances = len(seeds)
    fig, ax = plt.subplots(figsize=(10, min(0.4 * num_instances + 1, 12)))
    ax.axis('off')

    header = ["Inst", "Seed", "Greedy (km)", "OR-Tools (km)", "Greedy time (s)", "OR time (s)", "G/OR oranı"]
    rows = []
    for i in range(num_instances):
        g_km = greedy_lengths[i] / 1000.0
        o_km = ortools_lengths[i] / 1000.0
        ratio = g_km / o_km if o_km > 0 else float("inf")
        rows.append([
            i + 1,
            seeds[i],
            f"{g_km:.3f}",
            f"{o_km:.3f}",
            f"{greedy_times[i]:.6f}",
            f"{ortools_times[i]:.6f}",
            f"{ratio:.3f}",
        ])

    table = ax.table(cellText=rows, colLabels=header, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.2)

    fig.tight_layout()
    fig.savefig(filename, dpi=200)
    plt.close(fig)
    print(f"Tablo kaydedildi: {filename}")

# Tur uzunluklarını çizip kaydeden fonksiyon
def save_length_plot(greedy_lengths, ortools_lengths, filename):
    num_instances = len(greedy_lengths)
    x = list(range(1, num_instances + 1))

#  Her instance için Greedy ve OR-Tools tur uzunluklarını km cinsinden çizip PNG olarak kaydediyoruz
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x, [g/1000 for g in greedy_lengths], marker="o", label="Greedy (km)")
    ax.plot(x, [o/1000 for o in ortools_lengths], marker="o", label="OR-Tools (km)")
    ax.set_xlabel("Instance")
    ax.set_ylabel("Tour length (km)")
    ax.set_title("Greedy vs OR-Tools Tour Lengths")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.4)

    fig.tight_layout()
    fig.savefig(filename, dpi=200)
    plt.close(fig)
    print(f"Uzunluk grafiği kaydedildi: {filename}")

# Çalışma sürelerini çizip kaydeden fonksiyon
def save_time_plot(greedy_times, ortools_times, filename):
    num_instances = len(greedy_times)
    x = list(range(1, num_instances + 1))

# Bu sefer her instance için Greedy ve OR-Tools çalışma sürelerini saniye cinsinden çizip PNG olarak kaydediyoruz
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x, greedy_times, marker="o", label="Greedy time (s)")
    ax.plot(x, ortools_times, marker="o", label="OR-Tools time (s)")
    ax.set_xlabel("Instance")
    ax.set_ylabel("Runtime (s)")
    ax.set_title("Greedy vs OR-Tools Runtimes")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.4)

    fig.tight_layout()
    fig.savefig(filename, dpi=200)
    plt.close(fig)
    print(f"Zaman grafiği kaydedildi: {filename}")


def main():
    # Burası konsol üzerinden kodumuzu çalıştırırken düğüm sayısı, seed gibi değerleri değiştirebilmek için olan kısım
    parser = argparse.ArgumentParser(description="Real Map TSP (Greedy vs OR-Tools) with osmnx + folium")
    parser.add_argument("--place", default="Nilüfer, Bursa, Turkey", help="Şehir/bölge adı (OSM)")
    parser.add_argument("--type", default="drive", choices=["drive", "walk", "bike"], help="Ağ türü")
    parser.add_argument("--n", type=int, default=5, help="TSP düğüm sayısı")
    parser.add_argument("--seed", type=int, default=9, help="Seed")
    parser.add_argument("--start", type=int, default=0, help="Başlangıç düğümü indeksi (0..n-1)")
    parser.add_argument("--out", default="tsp_greedy_realmap.html", help="Çıktı HTML dosyası")
    # Assignment 3 için ek parametreler
    parser.add_argument("--compare", action="store_true",help="Greedy vs OR-Tools karşılaştırmasını çalıştır")
    parser.add_argument("--instances", type=int, default=30,help="Karşılaştırma için kaç farklı topoloji üretilecek")
    args = parser.parse_args()

    print(f"[+] '{args.place}' yol ağı indiriliyor ({args.type})...")
    G = load_graph(args.place, network_type=args.type)

    if args.compare:
        # Assignment 3: çoklu deney ve karşılaştırma
        run_comparison_experiments(G, args)
    else:
        # Düğümleri seç
        tsp_nodes = pick_nodes(G, args.n, args.seed)
        if not (0 <= args.start < len(tsp_nodes)):
            raise ValueError("start index aralık dışında")

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
        print(f"Kaydedildi: {out_file}  (tarayıcıda aç)")

if __name__ == "__main__":
    main()
