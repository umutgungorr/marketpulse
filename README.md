# 📊 MarketPulse (PiyasaRadarı)

> **Bilingual (TR/EN) Financial & Asset Intelligence Web Platform**  
> *Borsa İstanbul (BIST), Kripto Paralar ve Küresel Hisseler için Kesin Ayrıştırma, Piyasa Duygu Radarı ve Kişisel Portföy Takip Uygulaması.*

---

## 🌟 Öne Çıkan Özellikler (v0.2.0)

1. **🎯 Katı & Akıllı Sembol Arama (Zero-Junk Search):**
   - Rastgele veya anlamsız aramaları filtreler; çöp sonuç üretmez.
   - Doğrulanmış semboller bulunamadığında popüler varlık önerileri sunar.
2. **🇹🇷 / 🇬🇧 Canlı Çift Dil Desteği (TR / EN):**
   - Tek tıkla tüm arayüz, grafikler, metrikler ve haber duygu kartları anında Türkçe ve İngilizce arasında çevrilir.
3. **🗂️ Hisse & Kripto Kesin Ayrıştırması:**
   - **BIST 100:** THYAO, ASELS, EREGL, GARAN, SASA, TUPRS, KCHOL vb. (F/K, PD/DD, Temettü Verimi %, Hacim).
   - **Kripto Paralar:** BTC, ETH, SOL, AVAX, XRP, BNB vb. (Market Cap, 24s Hacim, Katman 1/DeFi kategorileri).
   - **Küresel (US):** AAPL, NVDA, MSFT, TSLA, AMZN (Nasdaq/NYSE liderleri).
4. **💰 Temettü & Yıllık Pasif Gelir Radarı:**
   - BIST hisselerinin yıllık temettü verimi (%) ve ödeme ayları.
   - Portföy genelinde toplam tahmini yıllık temettü nakit getirisi hesabı.
5. **🛡️ Portföy Sağlık & Risk Çeşitlendirme Skoru (0-100):**
   - Tek varlık yoğunlaşması ve yüksek kripto volatilitesi risklerini analiz edip puan ve uyarılar üretir.
6. **📥 1-Tıkla Excel / CSV Dışa Aktarma:**
   - Tüm açık pozisyonları UTF-8 BOM formatında Excel ve Google E-Tablolar uyumlu CSV olarak indirme.
7. **🧮 Kâr Realizasyonu & Satış Simülatörü:**
   - Belirli bir fiyattan çıkış yapıldığında cebe kalacak net kârı ve kalan lot miktarını önceden hesaplama.
8. **📰 Haber & KAP Bildirimleri Duygu Analizi (Sentiment Radar):**
   - BIST KAP açıklamaları ve küresel finans haberlerini tarayarak **Pozitif (Bullish) / Nötr / Negatif (Bearish)** duygu puanı hesaplar. Özel KAP alt filtresi.
9. **⏰ Fiyat Alarm Sistemi:**
   - Belirlenen hedef fiyat aşıldığında görsel bildirim üreten yerel alarm mekanizması.
10. **⚡ Sıfır Dış Bağımlılık (Zero External Dependencies):**
    - Saf Python standart kütüphanesi (`http.server`, `sqlite3`, `json`) ile inşa edilmiştir. Sıfır kurulum derdi.

---

## 🚀 Hızlı Başlangıç (Quickstart)

```bash
# Depoyu klonlayın ve klasöre girin:
git clone https://github.com/umutgungorr/marketpulse.git
cd marketpulse

# Web uygulamasını başlatın (Kurulum gerektirmez!):
python run.py
```

Tarayıcınızda şu adresi açın:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🧪 Testleri Çalıştırma

```bash
uv run pytest tests -v
```

---

## 📡 REST API Uç Noktaları

| Metot | Uç Nokta | Açıklama |
|:---|:---|:---|
| `GET` | `/api/health` | Servis sağlık durumu |
| `GET` | `/api/indices` | Manşet piyasa endeksleri (BIST 100, BTC.D, SPX, Dolar/TL) |
| `GET` | `/api/assets?type=bist\|crypto\|global` | Varlıkları ve anlık fiyatları listele |
| `GET` | `/api/search?q={query}&type={category}` | Katı sembol ve şirket araması |
| `GET` | `/api/chart/{symbol}?timeframe=1D\|1W\|1M\|1Y` | Geçmiş mum/çizgi grafik serisi |
| `GET` | `/api/news?symbol={symbol}` | Duygu skorlu haber akışı ve KAP duyuruları |
| `GET` | `/api/portfolio` | Portföy özeti, toplam değer ve kâr/zarar |
| `POST` | `/api/portfolio` | Yeni pozisyon ekle (`symbol`, `quantity`, `buy_price`) |
| `DELETE` | `/api/portfolio/{id}` | Pozisyonu sil |
| `GET` | `/api/alerts` | Fiyat alarmlarını listele |
| `POST` | `/api/alerts` | Fiyat alarmı oluştur (`symbol`, `target_price`, `condition`) |

---

## 📄 Lisans
Bu proje [MIT Lisansı](LICENSE) ile korunmaktadır.
