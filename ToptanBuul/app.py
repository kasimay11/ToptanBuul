"""
ToptanBuul — Flask API Sunucu
Çalıştırmak için: python app.py
Sonra tarayıcıda: http://localhost:5000
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import logging
from scraper import toplu_ara, karsilastir

HERE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
CORS(app)  # Frontend'den erişime izin ver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────
# Anasayfa — Frontend'i serve et
# ─────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(HERE, "index.html")


# ─────────────────────────────────────────────────────────
# API: Ürün Arama
# Kullanım: GET /api/search?q=şeker
# ─────────────────────────────────────────────────────────
@app.route("/api/search")
def search():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Arama terimi giriniz", "results": []}), 400

    if len(query) < 2:
        return jsonify({"error": "En az 2 karakter girin", "results": []}), 400

    logger.info(f"Arama: '{query}'")

    try:
        results = toplu_ara(query)
        return jsonify({
            "query": query,
            "count": len(results),
            "results": results
        })
    except Exception as e:
        logger.error(f"Arama hatası: {e}")
        return jsonify({"error": "Arama sırasında hata oluştu", "results": []}), 500


# ─────────────────────────────────────────────────────────
# API: Fiyat Karşılaştırma
# Kullanım: GET /api/compare?name=şeker
# ─────────────────────────────────────────────────────────
@app.route("/api/compare")
def compare():
    name = request.args.get("name", "").strip()

    if not name:
        return jsonify({"error": "Ürün adı giriniz"}), 400

    logger.info(f"Karşılaştırma: '{name}'")

    try:
        result = karsilastir(name)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Karşılaştırma hatası: {e}")
        return jsonify({"error": "Karşılaştırma sırasında hata oluştu"}), 500


# ─────────────────────────────────────────────────────────
# API: Kategoriler
# Kullanım: GET /api/categories
# ─────────────────────────────────────────────────────────
@app.route("/api/categories")
def categories():
    return jsonify({
        "categories": [
            {"id": "gida", "label": "Gıda & İçecek", "icon": "🛒"},
            {"id": "temizlik", "label": "Temizlik Ürünleri", "icon": "🧹"},
            {"id": "kirtasiye", "label": "Kırtasiye", "icon": "📄"},
            {"id": "tekstil", "label": "Tekstil & Giyim", "icon": "👕"},
            {"id": "elektronik", "label": "Elektronik", "icon": "⚡"},
            {"id": "kozmetik", "label": "Kozmetik & Bakım", "icon": "💄"},
            {"id": "ev", "label": "Ev & Mutfak", "icon": "🏠"},
            {"id": "ambalaj", "label": "Ambalaj", "icon": "📦"},
        ]
    })


# ─────────────────────────────────────────────────────────
# API: Sağlık Kontrolü
# ─────────────────────────────────────────────────────────
@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "version": "1.0.0"})


if __name__ == "__main__":
    print("=" * 50)
    print("  ToptanBuul Sunucu Başlatılıyor...")
    print("  Adres: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=5000)
