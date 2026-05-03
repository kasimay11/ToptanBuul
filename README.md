# 🛒 ToptanBuul — B2B Akıllı Tedarik Asistanı

![Hackathon](https://img.shields.io/badge/Hackathon-Projesi-success) ![Python](https://img.shields.io/badge/Python-3.x-blue) ![Flask](https://img.shields.io/badge/Flask-API-lightgrey)

**ToptanBuul**, KOBİ'lerin ve işletmelerin satın alma süreçlerindeki zaman kaybını ve yüksek maliyetleri ortadan kaldırmak için tasarlanmış bir B2B fiyat karşılaştırma ve sepet optimizasyon motorudur.

## 🎯 Problem ve Çözüm
İşletmeler her ay onlarca farklı kalemi tedarik ederken; farklı toptancı platformları arasında manuel fiyat karşılaştırması yapmak saatler sürer ve kâr marjlarını eritir. 
**ToptanBuul**, kullanıcının aradığı ürünleri Türkiye'nin önde gelen toptancı sitelerinde **eşzamanlı (multithread)** olarak tarar, fiyatları normalize eder ve saniyeler içinde en ucuz rotayı oluşturarak doğrudan ürün detay sayfalarına yönlendirir.

## ✨ Öne Çıkan Özellikler
- **Eşzamanlı Tarama Motoru (Multithreading):** Geleneksel ardışık kazıma (scraping) yerine `concurrent.futures` kullanılarak 6+ site aynı anda taranır. Arama süresi %70 oranında düşürülmüştür.
- **Kurşun Geçirmez Link Birleştirici:** Ürün URL'leri tespit edilirken `urljoin` ve akıllı DOM analizi kullanılarak kullanıcılar kırık linkler yerine doğrudan hedeflenen ürünün sepete ekleme sayfasına yönlendirilir.
- **Fiyat Normalizasyonu:** Sitelerden gelen "1.250,50 TL", "₺486" gibi karmaşık fiyat formatları Regex (Düzenli İfadeler) ile saf matematiksel verilere dönüştürülür.
- **Yüksek Hata Toleransı (Fallback Mekanizması):** Herhangi bir toptancı sitesinin çökmesi veya bot korumasına alması durumunda sistem kilitlenmez; Timeout koruması ve Akıllı Demo Veri üretici sayesinde kesintisiz çalışmaya devam eder.
- **Modüler API Mimarisi:** Frontend ve Backend birbirinden tamamen bağımsız çalışacak şekilde `Flask REST API` olarak tasarlanmıştır.

## 🛠️ Teknoloji Yığını
- **Backend:** Python, Flask, BeautifulSoup4, Requests
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
- **Mimari:** RESTful API, Multithreading, Modüler Yapı (app.py & scraper.py)

## 🚀 Nasıl Çalıştırılır?

1. Repoyu bilgisayarınıza klonlayın:
   ```bash
   git clone https://github.com/kasimay11/ToptanBuul.git
