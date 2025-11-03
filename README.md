# BLM5026_Homeworks
Bilgisayar Oyunlarında Yapay Zeka dersinin ödevleri için açıldı.

## Homework 1
### def generate_points fonksiyonu
Bu fonksiyon rastgele (x,y) ikilileri üretir.
n kaç tane ikili üretileceğini belirler. Width ve height değerlerin hangi aralıkta olacağını belirler.
seed aynı seed ile çalıştırıldığında tekrar aynı noktaları oluşturabilmesi içindir.

### def build_graph fonksiyonu
Bu fonksiyon, ürettiğimiz (x,y) ikililerini alıp bunlar ile bir grafik oluşturuyor.
Ayrıca bu fonksiyon içerisinde iki node arasındaki mesafe hesaplanarak o kenarın ağırlığı (weight) olarak atanıyor.

### def greedy_tour fonksiyonu
Bu fonksiyon, ödevde bizden asıl istenilen sezgisel yaklaşımın algoritmasını(En yakın komşu) barındırıyor.
Öncelikle bütün node'lar unvisited setine ekleniyor. tour listesi gezilen sırayı tutuyor. current o an içerisindeki node'u tutuyor. total ise toplam yol uzunluğu hesabında kullanılıyor.
Algoritma daha ziyaret edilmemiş tüm noktaları tek tek kontrol eder. Her birine olan mesafeyi(weight) alır ve mesafesi en ksıa olanı en iyi seçenek olarak seçer.
Seçilen nokta tour.append ile tura eklenir, unvisited.remove ile ziyaret edilmemişlerden ise silinir. total+ işlemi ile toplam mesafeye eklenir ve şu anki konum olarak seçilerek döngü devam ettirilir.
Tüm noktalar ziyaret edildikten sonra ise döngü başlangıç noktasına döner ve bitirilir.

### def draw_tour(G, pos, tour) Fonksiyonu
Bu fonksiyon grafiğimizi ve algoritmamızın bulunduğu turu görselleştirmek içindir. Matplotlib ve networkx kütüphaneleri burada çalışır. Önce bütün grafiği gri renk ile çizer. Bu sayede bir noktadan oluşabilecek tüm yollar görselleştirilmiş olur. Daha sonrasında algoritmanın seçtiği yol kırmızı ile çizilir ve böylece tur görselleştirilmiş olur. Node’lar ise mavi renkle gösterilir ve hem node sıra sayısı(rastgele oluşturulurken oluşturulma sırası) hem de koordinatları node üstünde gösterilir. Oluşturulan grafiğin başlık kısmına tur uzunluğu eklenir.

### if __name__ == "__main__": Fonksiyonu
Bu kısım programı çalıştırıldığında ilk olarak devreye giren ana fonksiyonumuzdur. Komut satırından argparse aracılığıyla parametreler alınır.
Buradaki parametreler:
•	--n: Nokta sayısı
•	--width ve --height: Noktaların üretileceği koordinat aralıkları
•	--seed: Rastgele sayı üreteci için sabit değer (aynı sonucu almak için)
•	--start: Başlangıç noktası indeksi
Bu parametreler alındıktan sonra sırasıyla:
1.	generate_points fonksiyonuyla noktalar üretilir.
2.	build_graph fonksiyonuyla grafik oluşturulur.
3.	greedy_tour fonksiyonuyla gezilecek rota hesaplanır.
4.	Tur ve toplam uzunluk ekrana yazdırılır.
5.	draw_tour fonksiyonuyla son tur görselleştirilir.
Bu yapı sayesinde tüm işlemler sırayla otomatik olarak yapılır ve yalnızca parametreler değiştirilerek farklı örnekler çalıştırabilir.

## Homework 2
### def load_graph(place, network_type="drive", simplify=True) Fonksiyonu
Bu fonksiyon, OpenStreetMap verilerini kullanarak seçtiğimiz bölgenin gerçek yol ağını indirir. place parametresi şehir veya bölge adını belirtir (örneğin: "Nilüfer, Bursa, Turkey" gibi). network_type parametresi indireceğimiz ağın türünü belirler; "drive" araç yollarını, "walk" yaya yollarını, "bike" ise bisiklet yollarını temsil eder.
osmnx.graph_from_place() fonksiyonu bu bilgileri kullanarak yol ağını indirir ve NetworkX MultiDiGraph formatında döndürür. Bu graf içinde her düğüm (node) gerçek bir coğrafi konumu temsil eder ve kenar (edge) uzunlukları metre cinsindendir.

### def pick_nodes(G, n, seed) Fonksiyonu
Bu fonksiyon, indirilen yol grafı üzerinde rastgele n tane düğüm seçmek için kullanılır. seed değeri aynı tutulduğunda, her çalıştırmada aynı düğümler seçilir (reproducibility). Fonksiyon önce grafın tüm düğümlerini list(G.nodes()) ile alır. Daha sonra random.Random(seed) ile rastgele seçim yapılır. Eğer istenen n değeri grafın düğüm sayısından fazlaysa, hata mesajı döndürülür. Sonuç olarak TSP’de kullanılacak belirli sayıda gerçek konuma (node) sahip oluruz.


### def shortest_lengths(G, nodes) Fonksiyonu
Bu fonksiyon, seçilen TSP düğümleri arasındaki en kısa yolların mesafesini metre olarak hesaplar. Her bir kaynak düğüm (u) için nx.single_source_dijkstra_path_length() kullanılarak diğer düğümlere olan en kısa mesafeyi buluruz. Burada kullanılan ağırlık (weight) parametresi "length" olup, yol ağındaki gerçek kenar uzunluklarını ifade eder. Fonksiyon her iki yönü de (u, v) ve (v, u) olacak şekilde sözlüğe kaydeder. Bu yapı sayesinde her iki düğüm arası mesafeye sonradan hızlıca erişebiliriz. Sonuç olarak, TSP’nin tam grafını kurarken kullanılacak mesafe bilgileri bu fonksiyonla elde edilir.

### def build_complete_graph(nodes, dist) Fonksiyonu
Bu fonksiyon, TSP problemimiz için tam bir graf oluşturur. Burada her iki düğüm çifti (u, v) bir kenarla birbirine bağlanır. (her kenarın ağırlığı, shortest_lengths fonksiyonundan gelen mesafedir). Eğer mesafe değeri (weight) sonlu bir sayıysa (math.isfinite(d)), kenar graf yapısına eklenir. Sonuç olarak her düğüm diğer tüm düğümlerle bağlantılı hale gelir ve her bağlantı gerçek hayattaki yol mesafesini temsil eder.

### def greedy_tour(H, start) Fonksiyonu
Bu fonksiyon birinci ödevde kullandığım En Yakın Komşu (Greedy / Nearest Neighbor) yaklaşımını uygular. Amaç, verilen başlangıç düğümünden (start) başlayarak her seferinde en yakın komşuya gidip tüm düğümleri gezmek ve sonra başlangıç noktasına geri dönmektir.
1.	Tüm düğümler unvisited kümesine alınır.
2.	tour listesinde gezilen düğümlerin sırasını tutar.
3.	current değişkeni o an bulunduğumuz düğümü, total ise toplam yol uzunluğunu tutar.
4.	Döngü içinde her defasında o an bulunduğumuz düğümden daha ziyaret edilmemiş düğümler arasında en kısa mesafede olan seçilir. 
Bu işlem min(unvisited, key=lambda x: H[current][x]["weight"]) satırı ile yapılır.
5.	Seçilen düğüm tour listesine eklenir, unvisited listesinden çıkarılır ve mesafesi total değerine eklenir.
6.	Tüm düğümler gezildikten sonra, algoritma son olarak başlangıç noktasına döner ve turunu tamamlar.

### def draw_folium_map(G, tour, out_html="tsp_greedy_realmap.html") Fonksiyonu
Bu fonksiyon, oluşturulan TSP turunu gerçek harita üzerinde görselleştirmeye yarar. Folium kütüphanesi kullanarak HTML formatında bir harita oluşturulur.
1.	Önce haritanın merkezini bulmak için tüm düğümlerin ortalama koordinatlarını (latitude, longitude) alır.
2.	Her düğüm için haritada bir marker oluşturulur. Üzerine tıkladığımızda o noktanın ismini ve koordinatlarını görüntüleyebiliriz.
3.	Sonrasında, turda yer alan ardışık düğümler için nx.shortest_path() fonksiyonu kullanılarak gerçek yol güzergâhı çıkarılır. Bu yollar kırmızı çizgilerle harita üzerinde gösterilir.
4.	Eğer aynı isimde bir HTML dosyası zaten varsa, program yeni bir dosya ismi oluşturur.
Sonuç olarak tur, gerçek yollar üzerinde kırmızı renkte çizilerek görsel olarak gösterilir ve HTML dosyası olarak kaydedilir.

### def main() Fonksiyonu
Bu kısım, programın ana çalışma bölümüdür. Komut satırından gelen parametreleri argparse kütüphanesiyle alır. Bu parametreler:
•	--place: İndirilecek olan harita bölgesi (örneğin: “Nilüfer, Bursa, Turkey”)
•	--type: Ağ türü (“drive”, “walk”, “bike”)
•	--n: Rastgele seçilecek düğüm sayısı
•	--seed: Rastgelelik tohumu (aynı sonuçları tekrar üretmek için)
•	--start: Başlangıç düğümü indeksi
•	--out: Oluşturulacak HTML dosyasının ismi
Program sırasıyla şu işlemleri yapar:
1.	load_graph() fonksiyonuyla seçilen bölgenin yol ağını indirir.
2.	pick_nodes() ile graf içinden rastgele n adet düğüm seçer.
3.	shortest_lengths() fonksiyonuyla seçilen düğümler arasındaki en kısa mesafeleri hesaplar.
4.	build_complete_graph() ile TSP’nin tam grafını oluşturur.
5.	greedy_tour() ile en yakın komşu algoritmasını uygulayarak turu oluşturur.
6.	draw_folium_map() fonksiyonunu çağırarak turu gerçek harita üzerinde görselleştirir.
7.	Tur uzunluğunu kilometre cinsinden ekrana yazdırır ve oluşturduğu HTML dosyasının adını terminalde gösterir.

