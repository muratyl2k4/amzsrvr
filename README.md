# Amazon Price & Profit Analysis Worker

Bu proje, farklı Amazon pazarlarındaki ASIN’lerin alış-satış fiyatlarını, maliyetlerini ve kar oranlarını **otomatik olarak hesaplayıp veritabanına kaydeden** bir **main worker ve Keepa worker ekosistemini** içerir.

Proje hem büyük veri kümelerinde yüksek performans sağlayacak şekilde **threading ile paralel çalışır**, hem de farklı pazarlar için **maliyet, kar ve döviz çevirimi hesaplarını optimize eder**.

---

## 📁 Dosya Yapısı

| Dosya              | Açıklama                                                                                                                                                                                                                                                                                              |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `main_worker.py`   | ASIN bazlı işlem akışını yönetir, threading ile paralel işleme yapar, verileri **main dataframe’de** toplar ve sonuçları veritabanına yazar.                                                                                                                                                          |
| `keepaWorker.py`   | Keepa verilerini işler, minimum alış fiyatını belirler, cost/profit/ratio hesaplamalarını yapar ve veritabanına kaydeder.                                                                                                                                                                             |
| `MyMarketPlace.py` | Her pazar için API credentials, currency tipi ve shipping cost bilgilerini içerir. USD dışındaki pazarlarda **kur çevirimi** sağlar.                                                                                                                                                                  |
| `MarketDB.py`      | Veritabanı tablolarını temsil eder: <br>• `notcompleted`: henüz işlenmemiş ASIN’ler <br>• `keepaexcel`: Keepa verisi <br>• `completed_asin`: tamamlanan ASIN’ler <br>• `completed_keepa`: tamamlanan Keepa ASIN’leri <br>• `remote_completedX`: İşlenmiş sonuçların kaydedildiği pazar bazlı tablolar |

---

## 🗄️ Veritabanı Alanları

| Alan              | Açıklama                                                              |
| ----------------- | --------------------------------------------------------------------- |
| Title             | Ürünün başlığı (Keepa veya Catalog’dan)                               |
| Asin              | ASIN kodu                                                             |
| SalesRank         | Satış sıralaması                                                      |
| Drop_Count        | Son 30 günde satış sıralamasındaki düşüş sayısı                       |
| Buy_Price         | Minimum alış fiyatı (FBA, FBM, Buy Box karşılaştırması ile seçilmiş)  |
| Sale_Price        | Minimum satış fiyatı (FBA, FBM, Buy Box karşılaştırması ile seçilmiş) |
| Ratio             | Satış fiyatı / maliyet oranı                                          |
| Cost              | Toplam maliyet (alış fiyatı + shipping + sabit ek)                    |
| Profit            | Kar (vergi, komisyon, paketleme dahil)                                |
| Profit_Percentage | Kar yüzdesi (Profit / Cost)                                           |
| Sales_Info        | Satış bilgisi (isteğe bağlı)                                          |
| Date              | Hesaplama tarihi                                                      |
| Fba_Seller_Count  | Amazon tarafından satılan FBA satıcı sayısı                           |
| Is_Buybox_Fba     | BuyBox kazanan FBA satıcı kontrolü (True/False)                       |
| Amazon_Current    | Amazon’un kendi satış fiyatı                                          |
| Lbs               | Ürünün ağırlığı (pound cinsinden, cubic veya actual weight)           |
| Error_Code        | İşlem sırasında hata oluştu mu (True/False)                           |

---

## 🔢 Matematiksel Hesaplamalar ve İşlem Mantığı

### 1️⃣ Minimum Alış Fiyatı (Buy_Price)

* Keepa veya Catalog verisinden alınır.
* FBA, FBM, Buy Box fiyatları karşılaştırılır, en düşük seçilir:

```
Buy_Price = min(Buy_Price_BB, Buy_Price_FBA, Buy_Price_FBM)
```

* PackageDimensions varsa, volumetric weight veya actual weight hesaplanır:

```
lbs_cubic = (Height * Length * Width) / 135
lbs = max(lbs_weight, lbs_cubic)
```

---

### 2️⃣ Satış Fiyatı (Sale_Price)

* Keepa verisi kullanılır.
* Minimum satış fiyatı:

```
Sale_Price = min(Sale_Price_BB, Sale_Price_FBA, Sale_Price_FBM)
```

---

### 3️⃣ Maliyet Hesabı (Cost / MALIYET)

* Kur ve shipping eklenir:

```
Cost = (Buy_Price + Shipping_Cost + 1) * Currency_Rate
```

* Currency Rate USD dışı pazarlarda güncel döviz kuru olarak alınır.
* +1 sabiti, handling ve ek maliyetleri temsil eder.

---

### 4️⃣ Kar Oranı (Ratio / ORAN)

```
Ratio = Sale_Price / Cost
```

* Minimum Ratio 1.5. Altındaki ASIN’ler işlem dışı bırakılır.

---

### 5️⃣ Kar Hesabı (Profit / KAR)

* Basit pazarlarda (US, CA, JA, AU):

```
Profit = Sale_Price - Referral_Fee - Pick_Pack_Fee - Cost
```

* AB pazarı (FR, DE):

```
Profit = (5/6) * Sale_Price - 1.2 * Referral_Fee - 1.2 * Pick_Pack_Fee - Cost
```

* UK pazarı:

```
Profit = Sale_Price - 1.2 * Referral_Fee - 1.2 * Pick_Pack_Fee - Cost
```

---

### 6️⃣ Kar Yüzdesi (Profit_Percentage / KAR_YUZDE)

```
Profit_Percentage = Profit / Cost
```

* Hem tabloya yazılır, hem işlenmiş ASIN seçiminde kullanılır.

---

## 🧵 Threading ve Paralel İşlem Mantığı

* Her ASIN ayrı thread ile işlenir.
* Thread grupları:

```python
t1 = threading.Thread(target=get_Buy_Price)
t2 = threading.Thread(target=get_Sell_Price)
t3 = threading.Thread(target=calculate)

t1.start()
t2.start()
t3.start()

t1.join()
t2.join()
t3.join()
```

* Bu yöntem, büyük veri setlerinde **hesaplamaları hızlandırır**.

---

## ⚠️ Hata Kodları ve Kontroller

| Kod     | Açıklama                  |
| ------- | ------------------------- |
| -8888   | Package Dimensions hatası |
| -777777 | Low Ratio                 |
| -666666 | Unauthorized              |
| -555555 | Invalid Input             |
| -444444 | Fees Estimate hatası      |
| -333333 | Buybox Prices hatası      |
| -222222 | Lowest Prices hatası      |
| -111111 | Credential yok            |

* Hata oluşan ASIN’ler `Error_Code = True` olarak işaretlenir ve bir sonraki işlemde tekrar değerlendirilmez.

---

## 🛠 Keepa Worker İş Akışı

1. Keepa verisi alınır (`Buy_Price_FBA`, `Buy_Price_FBM`, `Buy_Price_BB`).
2. Minimum fiyat hesaplanır.
3. Target pazar fiyatları alınır (`Sale_Price_FBA`, `Sale_Price_FBM`, `Sale_Price_BB`).
4. Maliyet, Ratio, Kar ve Kar Yüzdesi hesaplanır.
5. Veriler veritabanına güncellenir:

   * `remote_completedX` tablosuna insert/update
   * `remote_keepaexcelX` tablosundan silme

---

## 💡 Örnek Kod Parçacıkları

### Minimum Alış Fiyatı Hesaplama

```python
buy_prices = [price_bb, price_fba, price_fbm]
buy_price = min([p for p in buy_prices if p > 0])
```

### Cost & Profit Hesaplama

```python
cost = (buy_price + shipping_cost + 1) * currency_rate
profit = sale_price - referral_fee - pick_pack_fee - cost
ratio = sale_price / cost
profit_percentage = profit / cost
```

### Threading Mantığı

```python
threads = []
for func in [get_Buy_Price, get_Sell_Price, calculate]:
    t = threading.Thread(target=func)
    t.start()
    threads.append(t)

for t in threads:
    t.join()
```

---

## ✅ Özet

* **Main Worker:** ASIN’leri paralel işleyip matematiksel hesaplamaları yapar.
* **Keepa Worker:** Keepa verilerini toplar, minimum fiyatı seçer ve profit/cost hesaplar.
* **Matematik:** Cost, Profit, Ratio ve Profit_Percentage tüm pazarlar için optimize edilmiştir.
* **Threading:** Her ASIN ayrı thread ile işlenir; büyük veri kümelerinde yüksek performans sağlar.
* **Veritabanı:** İşlenmiş veriler `completed` tablolarına yazılır, Keepa tablosu temizlenir, Error_Code kontrolü ile güvenli işleme yapılır.
