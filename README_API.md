# 📡 Süper Lig Veri Botu - API Kurulum Rehberi

## 🎯 Gerçek Veri Çekmek İçin 3 Seçenek

### SEÇENEK 1: API-Football (ÖNERİLEN) ⭐⭐⭐⭐⭐

**En güvenilir ve profesyonel çözüm**

1. **Ücretsiz API Key Alın:**
   - https://www.api-football.com/ adresine gidin
   - "Sign Up" ile ücretsiz hesap oluşturun
   - Dashboard'dan API key'inizi kopyalayın
   - Ücretsiz plan: 100 istek/gün (yeterli!)

2. **API Key'i Ayarlayın:**
   ```bash
   # Linux/Mac
   export API_FOOTBALL_KEY=sizin_api_key_iniz
   
   # Windows PowerShell
   $env:API_FOOTBALL_KEY="sizin_api_key_iniz"
   
   # Veya fetcher.py dosyasına direkt yazın:
   # self.api_key = "sizin_api_key_iniz"
   ```

3. **Bot'u Çalıştırın:**
   ```bash
   python3 fetcher.py
   ```

**Avantajları:**
- ✅ Gerçek zamanlı veriler
- ✅ Tüm maçlar, kadrolar, istatistikler
- ✅ Stadyum bilgileri, logolar
- ✅ Güvenilir ve hızlı
- ✅ Resmi API

---

### SEÇENEK 2: Web Scraping (Ücretsiz ama Kısıtlı) ⭐⭐

Mackolik, NTV Spor, TRT Spor sitelerinden veri çeker.

**Sorunlar:**
- ❌ Siteler sık değişiyor
- ❌ Cloudflare koruması
- ❌ Yasal gri alan
- ❌ Veriler her zaman güncel değil

---

### SEÇENEK 3: Yedek Veri Modu ⭐

Hiçbir kaynak çalışmazsa otomatik devreye girer.

- ✅ 114 gerçekçi maç sonucu
- ✅ Tam puan durumu
- ✅ Sezon boyunca çalışır

---

## 🚀 Hızlı Başlangıç

```bash
# 1. API key al (5 dakika)
# https://dashboard.api-football.com/

# 2. API key'i ayarla
export API_FOOTBALL_KEY=abc123xyz

# 3. Bot'u çalıştır
python3 fetcher.py

# 4. HTML'i aç
# index.html'i tarayıcıda aç
```

---

## 📊 Veri Formatı

```json
{
  "last_updated": "2025-01-15 14:30:00",
  "matches": [
    {
      "date": "2025-01-14",
      "time": "19:00",
      "home_team": "Galatasaray",
      "away_team": "Fenerbahçe",
      "home_score": "2",
      "away_score": "1",
      "status": "FT",
      "venue": "NEF Stadyumu",
      "league": "Süper Lig",
      "round": "Hafta 20",
      "home_logo": "https://...",
      "away_logo": "https://..."
    }
  ],
  "standings": [...]
}
```

---

## 🔧 Sorun Giderme

**Problem:** "API key bulunamadı" hatası
**Çözüm:** 
```bash
export API_FOOTBALL_KEY=sizin_key_iniz
python3 fetcher.py
```

**Problem:** Web scraping çalışmıyor
**Çözüm:** API-Football kullanın veya yedek veri modunu bekleyin

**Problem:** Veriler eski
**Çözüm:** `python3 fetcher.py` tekrar çalıştırın

---

## 📱 Canlı Veri Akışı

```
┌─────────────────┐
│  API-Football   │ (Öncelikli)
│  v3.football... │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Mackolik.com   │ (Yedek 1)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  NTV Spor       │ (Yedek 2)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  TRT Spor       │ (Yedek 3)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Gerçekçi Veri  │ (Son çare)
│  (114 maç)      │
└─────────────────┘
```

---

## 💡 İpuçları

1. **API Key Güvenliği:** Key'inizi asla public repo'ya pushlamayın!
2. **Otomasyon:** Cron job ile her saat başı güncelleyin
3. **Cache:** JSON dosyasını cache olarak kullanın
4. **Rate Limit:** API-Football 100 istek/gün limiti var

---

## 📞 Destek

- API-Football Dökümantasyon: https://www.api-football.com/documentation-v3
- Örnek Kodlar: fetcher.py dosyasına bakın

