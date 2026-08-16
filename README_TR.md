# ⚽ Süper Lig Analiz Merkezi - Canlı Veri Botu

## 🎯 Özellikler

- **Canlı Maç Simülasyonu**: Gerçekçi maç sonuçları ve canlı skorlar
- **Dinamik Puan Durumu**: 20 takım için güncel puan tablosu
- **Otomatik Güncelleme**: Her çalıştırmada yeni veriler üretilir
- **API Desteği**: Football-Data.org API entegrasyonu (API anahtarı ile)
- **Responsive Tasarım**: Mobil uyumlu HTML arayüz

## 🚀 Kullanım

### 1. Botu Çalıştırın

```bash
# Python botunu doğrudan çalıştırın
python fetcher.py

# Veya bash scriptini kullanın
./run_bot.sh
```

### 2. HTML Sayfasını Açın

`index.html` dosyasını tarayıcınızda açın. Veriler otomatik olarak yüklenecektir.

### 3. Canlı Veriler İçin (Opsiyonel)

Football-Data.org'dan ücretsiz API anahtarı alın:
1. https://www.football-data.org/client/register adresinden kayıt olun
2. API anahtarınızı `fetcher.py` dosyasında `api_key` değişkenine ekleyin:

```python
api_key = "SIZIN_API_ANAHTARINIZ"
```

## 📊 Veri Yapısı

Bot şu verileri üretir:

- **Maçlar**: Son 7 günün maç sonuçları + canlı maçlar
- **Puan Durumu**: 20 takım için sıralama, oynanan, kazanılan, beraberlik, kaybedilen, puan
- **Analiz**: Sistem durumu ve maç özetleri

## 🔄 Otomatik Güncelleme

HTML sayfası her 60 saniyede bir verileri otomatik yeniler:

```javascript
setInterval(loadData, 60000);
```

## 🛠️ Kurulum

Gereksinimler:
- Python 3.6+
- Modern bir web tarayıcısı

```bash
# Botu çalıştır
python fetcher.py

# HTML sayfasını aç
# index.html dosyasını tarayıcıda açın
```

## 📝 Notlar

- API erişimi yoksa otomatik olarak simülasyon modu aktif olur
- Simülasyon modunda gerçekçi rastgele veriler üretilir
- Her çalıştırmada farklı maç sonuçları ve puan durumları oluşur

## 📄 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.
