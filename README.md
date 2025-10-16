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
