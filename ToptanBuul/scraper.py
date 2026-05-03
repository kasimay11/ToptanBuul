"""
ToptanBuul Scraper
Türkiye'nin 6 büyük toptancı sitesinden fiyat çeker.
"""

import requests
from bs4 import BeautifulSoup
import time
import re
import logging
from dataclasses import dataclass
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Her istekte kullan — bot engeli aşmak için
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

@dataclass
class Product:
    name: str
    price: float
    unit: str
    site: str
    site_url: str
    product_url: str
    image_url: str = ""
    stock: str = "bilinmiyor"
    category: str = "genel"


def temizle_fiyat(fiyat_str: str) -> float:
    """'1.250,90 TL' gibi string'i float'a çevirir."""
    fiyat_str = fiyat_str.strip()
    fiyat_str = re.sub(r"[^\d,\.]", "", fiyat_str)
    # Türk formatı: nokta binlik ayraç, virgül ondalık
    if "," in fiyat_str and "." in fiyat_str:
        fiyat_str = fiyat_str.replace(".", "").replace(",", ".")
    elif "," in fiyat_str:
        fiyat_str = fiyat_str.replace(",", ".")
    try:
        return float(fiyat_str)
    except ValueError:
        return 0.0


def safe_get(url: str, timeout: int = 10) -> Optional[BeautifulSoup]:
    """Hata yönetimli HTTP GET isteği."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        return BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException as e:
        logger.warning(f"İstek başarısız ({url}): {e}")
        return None


# ─────────────────────────────────────────────────────────
# SCRAPER 1 — toptantr.com
# ─────────────────────────────────────────────────────────
def scrape_toptantr(query: str) -> List[Product]:
    url = f"https://www.toptantr.com/search?q={query.replace(' ', '+')}"
    soup = safe_get(url)
    if not soup:
        return []

    products = []
    # Ürün kartları genellikle .product-item veya article içinde
    cards = soup.select(".product-item, .item-card, article.product")

    for card in cards[:10]:
        try:
            name_el = card.select_one(".product-title, .item-name, h3, h2")
            price_el = card.select_one(".price, .product-price, .fiyat")
            link_el = card.select_one("a[href]")
            img_el = card.select_one("img")

            if not name_el or not price_el:
                continue

            name = name_el.get_text(strip=True)
            price = temizle_fiyat(price_el.get_text())
            url_product = link_el["href"] if link_el else ""
            if url_product and not url_product.startswith("http"):
                url_product = "https://www.toptantr.com" + url_product
            img = img_el.get("src", "") if img_el else ""

            if price > 0:
                products.append(Product(
                    name=name, price=price, unit="adet",
                    site="toptantr.com", site_url="https://www.toptantr.com",
                    product_url=url_product, image_url=img,
                    stock="stokta"
                ))
        except Exception as e:
            logger.debug(f"toptantr kart hatası: {e}")
            continue

    logger.info(f"toptantr.com: {len(products)} ürün bulundu")
    return products


# ─────────────────────────────────────────────────────────
# SCRAPER 2 — yenitoptanci.com
# ─────────────────────────────────────────────────────────
def scrape_yenitoptanci(query: str) -> List[Product]:
    url = f"https://yenitoptanci.com/search?query={query.replace(' ', '%20')}"
    soup = safe_get(url)
    if not soup:
        return []

    products = []
    cards = soup.select(".product-card, .urun-kart, .grid-item")

    for card in cards[:10]:
        try:
            name_el = card.select_one("h3, h2, .name, .urun-adi")
            price_el = card.select_one(".price, .fiyat, .urun-fiyat")
            link_el = card.select_one("a")
            img_el = card.select_one("img")

            if not name_el or not price_el:
                continue

            name = name_el.get_text(strip=True)
            price = temizle_fiyat(price_el.get_text())
            url_product = link_el["href"] if link_el else ""
            if url_product and not url_product.startswith("http"):
                url_product = "https://yenitoptanci.com" + url_product

            if price > 0:
                products.append(Product(
                    name=name, price=price, unit="adet",
                    site="yenitoptanci.com", site_url="https://yenitoptanci.com",
                    product_url=url_product,
                    image_url=img_el.get("src", "") if img_el else "",
                    stock="stokta"
                ))
        except Exception as e:
            logger.debug(f"yenitoptanci kart hatası: {e}")
            continue

    logger.info(f"yenitoptanci.com: {len(products)} ürün bulundu")
    return products


# ─────────────────────────────────────────────────────────
# SCRAPER 3 — toptanhane.com
# ─────────────────────────────────────────────────────────
def scrape_toptanhane(query: str) -> List[Product]:
    url = f"https://www.toptanhane.com/arama?q={query.replace(' ', '+')}"
    soup = safe_get(url)
    if not soup:
        return []

    products = []
    cards = soup.select(".product, .prd, li.item")

    for card in cards[:10]:
        try:
            name_el = card.select_one(".prd-name, .product-name, h3")
            price_el = card.select_one(".prd-price, .price, span.fiyat")
            link_el = card.select_one("a")
            img_el = card.select_one("img")
            stock_el = card.select_one(".stock, .stok")

            if not name_el or not price_el:
                continue

            name = name_el.get_text(strip=True)
            price = temizle_fiyat(price_el.get_text())
            stock = "stokta"
            if stock_el:
                stok_txt = stock_el.get_text(strip=True).lower()
                if "yok" in stok_txt or "tükendi" in stok_txt:
                    stock = "stokta yok"
                elif "az" in stok_txt:
                    stock = "az kaldı"

            url_product = link_el["href"] if link_el else ""
            if url_product and not url_product.startswith("http"):
                url_product = "https://www.toptanhane.com" + url_product

            if price > 0:
                products.append(Product(
                    name=name, price=price, unit="adet",
                    site="toptanhane.com", site_url="https://www.toptanhane.com",
                    product_url=url_product,
                    image_url=img_el.get("src", "") if img_el else "",
                    stock=stock
                ))
        except Exception as e:
            logger.debug(f"toptanhane kart hatası: {e}")
            continue

    logger.info(f"toptanhane.com: {len(products)} ürün bulundu")
    return products


# ─────────────────────────────────────────────────────────
# SCRAPER 4 — tahtakaletoptanticaret.com
# ─────────────────────────────────────────────────────────
def scrape_tahtakale(query: str) -> List[Product]:
    url = f"https://www.tahtakaletoptanticaret.com/arama?q={query.replace(' ', '+')}"
    soup = safe_get(url)
    if not soup:
        return []

    products = []
    cards = soup.select(".product-item, .item, .col-product")

    for card in cards[:10]:
        try:
            name_el = card.select_one("h3, h2, .product-title")
            price_el = card.select_one(".price, .fiyat, .urun-fiyat")
            link_el = card.select_one("a[href]")
            img_el = card.select_one("img")

            if not name_el or not price_el:
                continue

            name = name_el.get_text(strip=True)
            price = temizle_fiyat(price_el.get_text())
            url_product = link_el["href"] if link_el else ""
            if url_product and not url_product.startswith("http"):
                url_product = "https://www.tahtakaletoptanticaret.com" + url_product

            if price > 0:
                products.append(Product(
                    name=name, price=price, unit="adet",
                    site="tahtakaletoptanticaret.com",
                    site_url="https://www.tahtakaletoptanticaret.com",
                    product_url=url_product,
                    image_url=img_el.get("src", "") if img_el else "",
                    stock="stokta"
                ))
        except Exception as e:
            logger.debug(f"tahtakale kart hatası: {e}")
            continue

    logger.info(f"tahtakaletoptanticaret.com: {len(products)} ürün bulundu")
    return products


# ─────────────────────────────────────────────────────────
# SCRAPER 5 — toptanara.com
# ─────────────────────────────────────────────────────────
def scrape_toptanara(query: str) -> List[Product]:
    url = f"https://www.toptanara.com/arama/{query.replace(' ', '-')}"
    soup = safe_get(url)
    if not soup:
        return []

    products = []
    cards = soup.select(".product-box, .item-box, div.urun")

    for card in cards[:10]:
        try:
            name_el = card.select_one(".product-name, h3, .name")
            price_el = card.select_one(".price, .fiyat")
            link_el = card.select_one("a[href]")
            img_el = card.select_one("img")

            if not name_el or not price_el:
                continue

            name = name_el.get_text(strip=True)
            price = temizle_fiyat(price_el.get_text())
            url_product = link_el["href"] if link_el else ""
            if url_product and not url_product.startswith("http"):
                url_product = "https://www.toptanara.com" + url_product

            if price > 0:
                products.append(Product(
                    name=name, price=price, unit="adet",
                    site="toptanara.com", site_url="https://www.toptanara.com",
                    product_url=url_product,
                    image_url=img_el.get("src", "") if img_el else "",
                    stock="stokta"
                ))
        except Exception as e:
            logger.debug(f"toptanara kart hatası: {e}")
            continue

    logger.info(f"toptanara.com: {len(products)} ürün bulundu")
    return products


# ─────────────────────────────────────────────────────────
# SCRAPER 6 — toptansatissitesi.com
# ─────────────────────────────────────────────────────────
def scrape_toptansatis(query: str) -> List[Product]:
    url = f"https://www.toptansatissitesi.com/arama?q={query.replace(' ', '+')}"
    soup = safe_get(url)
    if not soup:
        return []

    products = []
    cards = soup.select(".product, .urun-card, .listing-item")

    for card in cards[:10]:
        try:
            name_el = card.select_one("h3, h2, .product-title, .urun-baslik")
            price_el = card.select_one(".price, .fiyat, .toptan-fiyat")
            link_el = card.select_one("a[href]")
            img_el = card.select_one("img")

            if not name_el or not price_el:
                continue

            name = name_el.get_text(strip=True)
            price = temizle_fiyat(price_el.get_text())
            url_product = link_el["href"] if link_el else ""
            if url_product and not url_product.startswith("http"):
                url_product = "https://www.toptansatissitesi.com" + url_product

            if price > 0:
                products.append(Product(
                    name=name, price=price, unit="adet",
                    site="toptansatissitesi.com",
                    site_url="https://www.toptansatissitesi.com",
                    product_url=url_product,
                    image_url=img_el.get("src", "") if img_el else "",
                    stock="stokta"
                ))
        except Exception as e:
            logger.debug(f"toptansatis kart hatası: {e}")
            continue

    logger.info(f"toptansatissitesi.com: {len(products)} ürün bulundu")
    return products


# ─────────────────────────────────────────────────────────
# ANA FONKSİYON — Tüm siteleri paralel tara
# ─────────────────────────────────────────────────────────
SCRAPERS = [
    scrape_toptantr,
    scrape_yenitoptanci,
    scrape_toptanhane,
    scrape_tahtakale,
    scrape_toptanara,
    scrape_toptansatis,
]

def toplu_ara(query: str) -> List[dict]:
    """
    Tüm siteleri paralel olarak tarar, sonuçları fiyata göre sıralar.
    Döndürülen liste JSON'a dönüştürülebilir dict listesidir.
    """
    all_products = []

    # 6 siteyi aynı anda tara (paralel)
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(scraper, query): scraper.__name__ for scraper in SCRAPERS}
        for future in as_completed(futures):
            site_name = futures[future]
            try:
                results = future.result()
                all_products.extend(results)
            except Exception as e:
                logger.error(f"{site_name} hatası: {e}")

    # Fiyata göre sırala (en ucuz önce)
    all_products.sort(key=lambda p: p.price)

    # dict formatına çevir (JSON için)
    return [
        {
            "name": p.name,
            "price": p.price,
            "unit": p.unit,
            "site": p.site,
            "siteUrl": p.site_url,
            "productUrl": p.product_url,
            "imageUrl": p.image_url,
            "stock": p.stock,
            "category": p.category,
        }
        for p in all_products
    ]


def karsilastir(urun_adi: str) -> dict:
    """
    Belirli bir ürün için tüm sitelerden fiyat karşılaştırması yap.
    """
    results = toplu_ara(urun_adi)

    if not results:
        return {"urun": urun_adi, "sonuclar": [], "en_ucuz": None, "en_pahali": None}

    en_ucuz = min(results, key=lambda x: x["price"])
    en_pahali = max(results, key=lambda x: x["price"])
    tasarruf = en_pahali["price"] - en_ucuz["price"]
    tasarruf_yuzde = round((tasarruf / en_pahali["price"]) * 100, 1) if en_pahali["price"] > 0 else 0

    return {
        "urun": urun_adi,
        "sonuclar": results,
        "en_ucuz": en_ucuz,
        "en_pahali": en_pahali,
        "tasarruf_tl": round(tasarruf, 2),
        "tasarruf_yuzde": tasarruf_yuzde,
    }
