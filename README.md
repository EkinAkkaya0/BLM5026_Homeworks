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

