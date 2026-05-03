# ToptanBuul — Küçük Esnaf Toptan Fiyat Karşılaştırma Sistemi

## Proje Nedir?
6 büyük Türk toptancı sitesini taran, ürün fiyatlarını karşılaştıran ve en ucuzu gösteren bir web uygulaması.

---

## Klasör Yapısı
```
toptan_fiyat_projesi/
├── README.md              ← bu dosya
├── backend/
│   ├── app.py             ← Flask API sunucu
│   ├── scraper.py         ← Tüm scraper mantığı
│   └── requirements.txt   ← Python paketleri
└── frontend/
    └── index.html         ← Web arayüzü
```

---

## Kurulum (Adım Adım)

### 1. Python Kur
https://python.org adresinden Python 3.11+ indir ve kur.

### 2. Projeyi Aç
```bash
cd toptan_fiyat_projesi/backend
```

### 3. Paketleri Yükle
```bash
pip install -r requirements.txt
```

### 4. Sunucuyu Başlat
```bash
python app.py
```

### 5. Siteyi Aç
Tarayıcında `http://localhost:5000` adresine git.

---

## Desteklenen Siteler
| Site | Durum |
|------|-------|
| toptantr.com | ✓ Aktif |
| yenitoptanci.com | ✓ Aktif |
| toptanhane.com | ✓ Aktif |
| tahtakaletoptanticaret.com | ✓ Aktif |
| toptanara.com | ✓ Aktif |
| toptansatissitesi.com | ✓ Aktif |

---

## API Endpoint'leri
| Endpoint | Açıklama |
|----------|----------|
| `GET /api/search?q=şeker` | Ürün ara |
| `GET /api/compare?name=şeker` | Fiyat karşılaştır |
| `GET /api/categories` | Kategorileri listele |

---

## Önemli Not
Web scraping bazı sitelerin kullanım koşullarına aykırı olabilir.
Ticari kullanım öncesi sitelerin ToS (kullanım koşulları) sayfasını oku.
