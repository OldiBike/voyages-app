# ✅ AJOUT : Support des variables locales (.env) - À AJOUTER AU DÉBUT
try:
    from dotenv import load_dotenv
    load_dotenv()  # Charge le fichier .env en local
    print("✅ Variables locales chargées depuis .env")
except ImportError:
    print("⚠️ python-dotenv non installé - variables système utilisées (Railway)")
except Exception as e:
    print(f"⚠️ Erreur chargement .env: {e}")

from flask import Flask, render_template_string, request, jsonify, send_file, session, redirect, url_for
import requests
import json
import random
from datetime import datetime
import os
import base64
from urllib.parse import quote_plus
import re
# ✅ MODIFICATION : Importation de la bibliothèque pour analyser le HTML
from bs4 import BeautifulSoup

app = Flask(__name__)

# CONFIGURATION SÉCURITÉ
app.secret_key = os.environ.get('SECRET_KEY', "VoyagesPrivileges2024!SecretKey#SuperLong789")

# Configuration des utilisateurs - SÉCURISÉE avec variables d'environnement
USERS = {
    os.environ.get('USER1_NAME', 'Sam'): os.environ.get('USER1_PASS', 'samuel1205'),
    os.environ.get('USER2_NAME', 'Constantin'): os.environ.get('USER2_PASS', 'standard01')
}

def check_auth():
    """Vérifie si l'utilisateur est connecté"""
    return session.get('authenticated', False)

# Page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in USERS and USERS[username] == password:
            session['authenticated'] = True
            session['username'] = username
            return redirect(url_for('home'))
        else:
            error_msg = "❌ Identifiants incorrects"
            return render_template_string(LOGIN_HTML, error=error_msg)

    return render_template_string(LOGIN_HTML)

# Déconnexion
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

class RealAPIHotelGatherer:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.google_api_key = os.environ.get('GOOGLE_API_KEY')
        if not self.google_api_key:
            print("❌ ERREUR CRITIQUE: Variable GOOGLE_API_KEY manquante")
        else:
            print("✅ Clé API Google chargée")

    def get_real_hotel_photos(self, hotel_name, destination):
        if not self.google_api_key: return []
        try:
            search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            search_params = {'query': f'"{hotel_name}" "{destination}" hotel', 'key': self.google_api_key, 'fields': 'photos,place_id'}
            search_response = requests.get(search_url, params=search_params, timeout=15)
            if search_response.status_code == 200 and (search_data := search_response.json()).get('results'):
                place_id = search_data['results'][0].get('place_id')
                details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                details_params = {'place_id': place_id, 'fields': 'photos', 'key': self.google_api_key}
                details_response = requests.get(details_url, params=details_params, timeout=15)
                if details_response.status_code == 200:
                    photos = details_response.json().get('result', {}).get('photos', [])
                    # ✅ MODIFICATION : Récupérer TOUTES les photos, pas seulement 6
                    return [f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={p.get('photo_reference')}&key={self.google_api_key}" for p in photos if p.get('photo_reference')]
            return []
        except Exception as e:
            print(f"❌ Erreur API Photos: {e}")
            return []

    def get_real_hotel_reviews(self, hotel_name, destination):
        if not self.google_api_key: return {'reviews': [], 'rating': 0, 'total_reviews': 0}
        try:
            search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            search_params = {'query': f'"{hotel_name}" "{destination}" hotel', 'key': self.google_api_key}
            search_response = requests.get(search_url, params=search_params, timeout=15)
            if search_response.status_code == 200 and (search_data := search_response.json()).get('results'):
                place_id = search_data['results'][0].get('place_id')
                details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                details_params = {'place_id': place_id, 'fields': 'reviews,rating,user_ratings_total', 'key': self.google_api_key, 'language': 'fr'}
                details_response = requests.get(details_url, params=details_params, timeout=15)

                if details_response.status_code == 200 and (result := details_response.json().get('result', {})):
                    
                    all_reviews = result.get('reviews', [])
                    
                    sorted_reviews = sorted(all_reviews, key=lambda r: (r.get('rating', 0), r.get('time', 0)), reverse=True)
                    
                    formatted_reviews = [
                        {
                            'rating': '⭐' * r.get('rating', 0), 
                            'author': r.get('author_name', 'Anonyme'), 
                            'text': r.get('text', '')[:400] + '...', 
                            'date': r.get('relative_time_description', '')
                        } 
                        for r in sorted_reviews if r.get('rating', 0) >= 4
                    ]
                    
                    total_reviews_count = result.get('user_ratings_total', 0)
                    
                    return {
                        'reviews': formatted_reviews, 
                        'rating': result.get('rating', 0), 
                        'total_reviews': total_reviews_count
                    }

            return {'reviews': [], 'rating': 0, 'total_reviews': 0}
        except Exception as e:
            print(f"❌ Erreur API Reviews: {e}")
            return {'reviews': [], 'rating': 0, 'total_reviews': 0}

    def get_real_youtube_videos(self, hotel_name, destination):
        if not self.google_api_key: return []
        try:
            youtube_url = "https://www.googleapis.com/youtube/v3/search"
            youtube_params = {'part': 'snippet', 'q': f'"{hotel_name}" "{destination}" hotel review tour', 'type': 'video', 'maxResults': 4, 'order': 'relevance', 'key': self.google_api_key}
            youtube_response = requests.get(youtube_url, params=youtube_params, timeout=15)
            if youtube_response.status_code == 200:
                return [{'id': item['id']['videoId'], 'title': item['snippet']['title']} for item in youtube_response.json().get('items', []) if item.get('id', {}).get('videoId')]
            return []
        except Exception as e:
            print(f"❌ Erreur API YouTube: {e}")
            return []

    def get_attraction_image(self, attraction_name, destination):
        if not self.google_api_key: return None
        print(f"ℹ️ Recherche d'une image réelle pour : {attraction_name} à {destination}")
        try:
            search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            search_params = {'query': f'"{attraction_name}" "{destination}"', 'key': self.google_api_key, 'fields': 'photos'}
            search_response = requests.get(search_url, params=search_params, timeout=15)
            if search_response.status_code == 200:
                search_data = search_response.json()
                if search_data.get('results') and search_data['results'][0].get('photos'):
                    photo_reference = search_data['results'][0]['photos'][0].get('photo_reference')
                    if photo_reference:
                        return f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_reference}&key={self.google_api_key}"
            return None
        except Exception as e:
            print(f"❌ Erreur API Image Attraction: {e}")
            return None

    def get_real_gemini_attractions_and_restaurants(self, destination):
        if not self.google_api_key:
            return {"attractions": [{"name": "Centre-ville", "type": "culture"}], "restaurants": []}
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.google_api_key)
            model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
            prompt = f'Donne-moi 8 points d\'intérêt pour {destination} et une sélection de 3 des meilleurs restaurants. Réponds UNIQUEMENT en JSON: {{"attractions": [{{"name": "Nom", "type": "plage|culture|gastronomie|activite"}}], "restaurants": [{{"name": "Nom du restaurant"}}]}}'
            response = model.generate_content(prompt)
            response_text = response.text.strip().replace("```json", "").replace("```", "").strip()

            try:
                parsed_data = json.loads(response_text)
                return {
                    "attractions": parsed_data.get('attractions', []) if isinstance(parsed_data, dict) else [],
                    "restaurants": parsed_data.get('restaurants', []) if isinstance(parsed_data, dict) else []
                }
            except json.JSONDecodeError:
                print(f"⚠️ Avertissement API Gemini: Erreur de décodage JSON.")
                return {"attractions": [{"name": "Centre-ville", "type": "culture"}], "restaurants": []}
        except Exception as e:
            print(f"❌ Erreur API Gemini: {e}")
            return {"attractions": [{"name": "Centre-ville", "type": "culture"}], "restaurants": []}

    def gather_all_real_data(self, hotel_name, destination):
        gemini_data = self.get_real_gemini_attractions_and_restaurants(destination)
        attractions_list = gemini_data.get("attractions", [])
        restaurants_list = gemini_data.get("restaurants", [])

        attractions_by_category = {'plages': [], 'culture': [], 'gastronomie': [], 'activites': []}
        for attr in attractions_list:
            category = attr.get('type', 'activites').replace('activite', 'activites')
            if category in attractions_by_category:
                attractions_by_category[category].append(attr.get('name', ''))

        cultural_attraction_image = None
        if attractions_by_category.get('culture'):
            first_cultural_attraction = attractions_by_category['culture'][0]
            cultural_attraction_image = self.get_attraction_image(first_cultural_attraction, destination)

        reviews_data = self.get_real_hotel_reviews(hotel_name, destination)

        return {
            'photos': self.get_real_hotel_photos(hotel_name, destination),
            'reviews': reviews_data.get('reviews', []),
            'hotel_rating': reviews_data.get('rating', 0),
            'total_reviews': reviews_data.get('total_reviews', 0),
            'videos': self.get_real_youtube_videos(hotel_name, destination),
            'attractions': attractions_by_category,
            'restaurants': restaurants_list,
            'cultural_attraction_image': cultural_attraction_image
        }


LOGIN_HTML = """
<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>🔐 Connexion</title><style>body{font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin:0; padding:20px; min-height:100vh; display:flex; align-items:center; justify-content:center;}.login-container{background:white; border-radius:20px; box-shadow:0 20px 40px rgba(0,0,0,0.1); padding:40px; width:400px; text-align:center;}.login-header h1{font-size: 2em;}.form-group{margin-bottom:20px; text-align:left;}label{display:block; margin-bottom:8px; font-weight:600;}input{width:100%; padding:12px; border:2px solid #e1e5e9; border-radius:8px; font-size:16px; box-sizing:border-box;}input:focus{outline:none; border-color:#3B82F6;}.login-btn{background: linear-gradient(45deg, #3B82F6, #60A5FA); color:white; border:none; padding:15px 40px; border-radius:25px; font-size:18px; font-weight:600; cursor:pointer; width:100%;}.error{color:#dc3545; margin-top:15px; font-weight:600;}.logo{max-width:200px; margin-bottom:20px;}</style></head><body><div class="login-container"><div class="login-header"><img src="https://static.wixstatic.com/media/5ca515_449af35c8bea462986caf4fd28e02398~mv2.png" alt="Logo" class="logo"><h1>🔐 Connexion</h1></div><form method="POST"><div class="form-group"><label for="username">👤 Nom d'utilisateur</label><input type="text" id="username" name="username" required></div><div class="form-group"><label for="password">🔑 Mot de passe</label><input type="password" id="password" name="password" required></div><button type="submit" class="login-btn">🚀 Se connecter</button>{% if error %}<div class="error">{{ error }}</div>{% endif %}</form></div></body></html>
"""


INTERFACE_HTML = r"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Générateur de Pages Voyage</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/litepicker/dist/css/litepicker.css"/>
    <style>
        body {font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 20px; min-height: 100vh;}
        .container {max-width: 800px; margin: 0 auto; background: white; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); overflow: hidden;}
        .header {background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%); color: white; padding: 20px 30px; text-align: center;}
        .header-logo {height: 40px; margin-bottom: 10px;}
        .user-info {text-align: right; margin-top: 10px; font-size: 14px;}
        .user-info a {color: white; margin-left: 15px; text-decoration: none; background: rgba(255,255,255,0.2); padding: 5px 10px; border-radius: 15px;}
        .form-container {padding: 40px;}
        .form-group {margin-bottom: 25px; width: 100%;}
        label {display: block; margin-bottom: 8px; font-weight: 600; color: #333;}
        input, select, textarea {width: 100%; padding: 12px; border: 2px solid #e1e5e9; border-radius: 8px; font-size: 16px; box-sizing: border-box;}
        input[type="checkbox"] { width: auto; }
        input:focus, select:focus, textarea:focus {outline: none; border-color: #3B82F6;}
        textarea {font-family: 'Segoe UI', sans-serif; resize: vertical; min-height: 80px;}
        #date_range, #cancellation_date {cursor: pointer; background-color: white;}
        .input-with-button {display: flex; align-items: center; gap: 10px;}
        .search-btn {padding: 8px 12px; font-size: 14px; font-weight: 600; background-color: #e0e0e0; border: 1px solid #ccc; border-radius: 8px; cursor: pointer;}
        .form-row {display: flex; gap: 20px;}
        .generate-btn {background: linear-gradient(45deg, #ff6b6b, #ee5a24); color: white; border: none; padding: 15px 40px; border-radius: 25px; font-size: 18px; font-weight: 600; cursor: pointer; width: 100%;}
        .loading {display: none; text-align: center; padding: 30px;}
        .loading-spinner {border: 4px solid #f3f3f3; border-top: 4px solid #3B82F6; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 20px;}
        @keyframes spin {0% {transform: rotate(0deg);} 100% {transform: rotate(360deg);}}
        .result {display: none; padding: 30px; background: #f8f9fa; border-top: 1px solid #e1e5e9;}
        .success {color: #28a745; font-size: 18px; font-weight: 600; text-align: center;}
        .error {color: #dc3545; font-size: 18px; font-weight: 600;}
        .button-container {margin-top: 20px; display: flex; gap: 15px; justify-content: center; flex-wrap: wrap; align-items: center;}
        .download-btn, .view-btn, .edit-btn, .html-code-btn, .reset-btn {color: white; border: none; padding: 12px 30px; border-radius: 8px; font-size: 16px; text-decoration: none; cursor: pointer;}
        .download-btn {background: #28a745;}
        .view-btn {background: #3B82F6;}
        .edit-btn {background: #ffc107; color: #333;}
        .html-code-btn {background: #6c757d;}
        .reset-btn { background: #9ca3af; padding: 8px 12px; font-size: 20px; line-height: 1; }
        .video-edit-form { margin-top: 20px; display: flex; gap: 10px; align-items: center; padding: 15px; background-color: #e9ecef; border-radius: 10px;}
        .video-edit-form input { flex-grow: 1; }
        .video-edit-form button { padding: 12px 20px; color: white; border-radius: 8px; border: none; cursor: pointer; font-size: 16px; white-space: nowrap; }
        .stats {display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-top: 20px;}
        .stat-item {background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1);}
        .stat-number {font-size: 24px; font-weight: bold; color: #3B82F6;}
        .stat-label {color: #666; font-size: 14px;}
        .pac-container {z-index: 10000 !important;}
        h3.section-divider {text-align: center; border-bottom: 2px solid #e1e5e9; line-height: 0.1em; margin: 35px 0 25px;}
        h3.section-divider span { background:#fff; padding:0 10px; color: #aaa; font-size: 0.9em; text-transform: uppercase;}
        .modal { display: none; position: fixed; z-index: 1; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.4); justify-content: center; align-items: center; }
        .modal-content { background-color: #fefefe; margin: auto; padding: 20px; border: 1px solid #888; width: 80%; max-width: 700px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.3); position: relative; }
        .close-button { color: #aaa; float: right; font-size: 28px; font-weight: bold; }
        .close-button:hover, .close-button:focus { color: black; text-decoration: none; cursor: pointer; }
        .html-textarea { width: 100%; height: 400px; border: 1px solid #ccc; padding: 10px; font-family: monospace; white-space: pre; overflow: auto; resize: vertical; border-radius: 5px; }
        @media (max-width: 768px) {.form-row {flex-direction: column; gap: 0;} .form-container {padding: 20px;}}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="https://static.wixstatic.com/media/5ca515_449af35c8bea462986caf4fd28e02398~mv2.png" alt="Logo" class="header-logo">
            <p>Générateur de présentation</p>
            <div class="user-info"><span>👤 Connecté : {{ username }}</span><a href="/logout">🚪 Déconnexion</a></div>
        </div>
        <div class="form-container">
            <form id="voyageForm">
                <h3 class="section-divider"><span>Détails du Séjour</span></h3>
                <div class="form-row">
                    <div class="form-group"><label for="hotel_name">🏨 Nom de l'hôtel</label><input type="text" id="hotel_name" name="hotel_name" required placeholder="Saisir un nom d'hôtel..."></div>
                    <div class="form-group"><label for="destination">📍 Destination</label><input type="text" id="destination" name="destination" required placeholder="Saisir une destination..."></div>
                </div>
                <div class="form-row">
                    <div class="form-group" style="width: 100%;"><label for="date_range">🗓️ Période du séjour</label><input type="text" id="date_range" readonly placeholder="Cliquez pour choisir les dates"><input type="hidden" id="date_start" name="date_start"><input type="hidden" id="date_end" name="date_end"></div>
                </div>
                <div class="form-row">
                    <div class="form-group"><label for="stars">⭐ Catégorie de l'hôtel</label><select id="stars" name="stars"><option value="3">3⭐</option><option value="4" selected>4⭐</option><option value="5">5⭐</option></select></div>
                    <div class="form-group"><label for="num_people">👥 Nombre de personnes</label><input type="number" id="num_people" name="num_people" value="2" min="1"></div>
                </div>

                <h3 class="section-divider"><span>Détails du Vol & Transferts</span></h3>
                <div class="form-row">
                    <div class="form-group"><label for="departure_city">✈️ Aéroport de départ</label><input type="text" id="departure_city" name="departure_city" placeholder="Saisir un aéroport..."></div>
                    <div class="form-group"><label for="arrival_airport">🛬 Aéroport d'arrivée</label><input type="text" id="arrival_airport" name="arrival_airport" placeholder="Saisir un aéroport..."></div>
                </div>
                <div class="form-row">
                    <div class="form-group"><label for="flight_price">💰 Prix du vol (€)</label><div class="input-with-button"><input type="number" id="flight_price" name="flight_price" value="0"><button type="button" id="searchFlightsBtn" class="search-btn" title="Rechercher sur Google Flights">🔎</button></div></div>
                    <div class="form-group"><label for="transfer_cost">🚐 Coût des Transferts (€)</label><input type="number" id="transfer_cost" name="transfer_cost" value="0"></div>
                </div>
                <div class="form-row">
                    <div class="form-group"><label for="car_rental_cost">🚗 Voiture de location (€)</label><input type="number" id="car_rental_cost" name="car_rental_cost" value="0"></div>
                </div>

                <h3 class="section-divider"><span>Détails du Prix</span></h3>
                <div class="form-row">
                    <div class="form-group">
                        <label for="price">💰 Votre tarif (€)</label>
                        <input type="number" id="price" name="price" required placeholder="ex: 2400">
                    </div>
                    <div class="form-group">
                        <label for="booking_price">💳 Tarif Hôtel Seul (€)</label>
                        <div class="input-with-button">
                            <input type="number" id="booking_price" name="booking_price" required placeholder="ex: 2800">
                            <button type="button" id="searchBookingBtn" class="search-btn" title="Rechercher sur Booking.com">🔎</button>
                        </div>
                    </div>
                </div>
                
                <div class="form-group">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <div style="display: flex; align-items: center; flex-shrink: 0;">
                            <input type="checkbox" id="has_cancellation" name="has_cancellation">
                            <label for="has_cancellation" style="margin-bottom: 0;">Annulation gratuite</label>
                        </div>
                        <div id="cancellation_date_wrapper" style="display: none; flex-grow: 1;">
                            <input type="text" id="cancellation_date" name="cancellation_date" readonly placeholder="Jusqu'au...">
                        </div>
                    </div>
                </div>

                <div class="form-group">
                    <label>🍽️ Surcoût Pension</label>
                    <div class="input-with-button">
                        <input type="number" id="surcharge_cost" name="surcharge_cost" value="0">
                        <select id="surcharge_type" name="surcharge_type">
                            <option>Petit déjeuner</option><option>Demi pension</option><option selected>Pension complète</option><option>All-In</option>
                        </select>
                    </div>
                </div>
                
                <h3 class="section-divider"><span>Services Exclusifs</span></h3>
                <div class="form-group">
                    <label for="exclusive_services">🎁 Services Exclusifs Inclus</label>
                    <textarea id="exclusive_services" name="exclusive_services" placeholder="ex: Accès au lounge VIP de l'aéroport
Une bouteille de champagne en chambre
Check-out tardif jusqu'à 14h"></textarea>
                </div>

                <div class="form-group">
                    <button type="button" id="toggleInstagramBtn" class="search-btn" style="width: auto; background-color: #f0f0f0; display: inline-flex; align-items: center; gap: 8px;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-instagram" viewBox="0 0 16 16"><path d="M8 0C5.829 0 5.556.01 4.703.048 3.85.088 3.269.222 2.76.42a3.9 3.9 0 0 0-1.417.923A3.9 3.9 0 0 0 .42 2.76C.222 3.268.087 3.85.048 4.703.01 5.555 0 5.827 0 8s.01 2.444.048 3.297c.04.852.174 1.433.372 1.942.205.526.478.972.923 1.417.444.445.89.719 1.416.923.51.198 1.09.333 1.942.372C5.555 15.99 5.827 16 8 16s2.444-.01 3.297-.048c.852-.04 1.433-.174 1.942-.372.526-.205.972-.478 1.417-.923.445-.444.718-.891.923-1.417.198-.51.333-1.09.372-1.942C15.99 10.445 16 10.173 16 8s-.01-2.444-.048-3.297c-.04-.852-.174-1.433-.372-1.942a3.9 3.9 0 0 0-.923-1.417A3.9 3.9 0 0 0 13.24.42c-.51-.198-1.09-.333-1.942-.372C10.445.01 10.173 0 8 0zm0 1.442c2.136 0 2.389.007 3.232.046.78.035 1.204.166 1.486.275.373.145.64.319.92.599s.453.546.598.92c.11.282.24.705.275 1.486.039.843.047 1.096.047 3.232s-.008 2.389-.047 3.232c-.035.78-.166 1.203-.275 1.486a2.5 2.5 0 0 1-.598.92 2.5 2.5 0 0 1-.92.598c-.282.11-.705.24-1.486.275-.843.038-1.096.047-3.232.047s-2.389-.008-3.232-.047c-.78-.035-1.203-.166-1.486-.275a2.5 2.5 0 0 1-.92-.598 2.5 2.5 0 0 1-.598-.92c-.11-.282-.24-.705-.275-1.486-.038-.843-.046-1.096-.046-3.232s.008-2.389.046-3.232c.035-.78.166-1.204.275-1.486.145-.373.319-.64.599-.92s.546-.453.92-.598c.282-.11.705-.24 1.486-.275.843-.039 1.096-.046 3.232-.046zM8 4.865a3.135 3.135 0 1 0 0 6.27 3.135 3.135 0 0 0 0-6.27zm0 5.143a2.008 2.008 0 1 1 0-4.016 2.008 2.008 0 0 1 0 4.016zm6.406-4.848a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5z"/></svg>
                        <span>Ajouter un profil Instagram (Optionnel)</span>
                    </button>
                    <div id="instagram_wrapper" style="display:none; margin-top: 15px;">
                        <label for="instagram_handle">👤 Nom d'utilisateur ou URL du profil Instagram</label>
                        <input type="text" id="instagram_handle" name="instagram_handle" placeholder="ex: hotel_marbella ou https://instagram.com/hotel_marbella">
                    </div>
                </div>

                <button type="submit" class="generate-btn">🚀 Générer</button>
            </form>
        </div>
        <div class="loading" id="loading"><div class="loading-spinner"></div><h3>🔄 Appels API sécurisés...</h3></div>
        <div class="result" id="result"></div>
    </div>

    <div id="htmlCodeModal" class="modal">
        <div class="modal-content">
            <span class="close-button">×</span>
            <h2>Code HTML de la Fiche Voyage</h2>
            <textarea id="htmlCodeDisplay" class="html-textarea" readonly></textarea>
<button id="copyHtmlCodeBtn" class="html-code-btn" style="margin-top: 15px;">📋 Copier le code</button>
<div id="copyStatus" style="text-align:center; font-size: 14px; color: green; margin-top: 5px;"></div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/litepicker/dist/litepicker.js"></script>
    <script>
        function getYouTubeId(url) {
            const regExp = /^.*(?:http(?:s)?:\/\/)?(?:www\.)?(?:m\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=|embed\/|v\/|shorts\/)?([a-zA-Z0-9_-]{11})(?:\S+)?$/;
            const match = url.match(regExp);
            return (match && match[1].length === 11) ? match[1] : null;
        }

        function initializeApp() {
            const formatDate = (d) => {
                const year = d.getFullYear();
                const month = String(d.getMonth() + 1).padStart(2, '0');
                const day = String(d.getDate()).padStart(2, '0');
                return `${year}-${month}-${day}`;
            };

            new Litepicker({
                element: document.getElementById('date_range'),
                singleMode: false, lang: 'fr-FR', format: 'DD MMMM YYYY',
                setup: (picker) => {
                    picker.on('selected', (date1, date2) => {
                        document.getElementById('date_start').value = formatDate(date1.dateInstance);
                        document.getElementById('date_end').value = formatDate(date2.dateInstance);
                    });
                },
            });

            new Litepicker({
                element: document.getElementById('cancellation_date'),
                singleMode: true,
                lang: 'fr-FR',
                format: 'DD MMMM YYYY'
            });

            const cancellationCheckbox = document.getElementById('has_cancellation');
            const cancellationDateWrapper = document.getElementById('cancellation_date_wrapper');
            cancellationCheckbox.addEventListener('change', function() {
                if (this.checked) {
                    cancellationDateWrapper.style.display = 'block';
                } else {
                    cancellationDateWrapper.style.display = 'none';
                }
            });

            // ✅ NOUVELLE FEATURE : Logique JS pour le bouton Instagram
            document.getElementById('toggleInstagramBtn').addEventListener('click', function() {
                const wrapper = document.getElementById('instagram_wrapper');
                const isVisible = wrapper.style.display === 'block';
                wrapper.style.display = isVisible ? 'none' : 'block';
            });

            const hotelInput = document.getElementById('hotel_name');
            const destinationInput = document.getElementById('destination');
            const starsSelect = document.getElementById('stars');
            const departureInput = document.getElementById('departure_city');
            const arrivalInput = document.getElementById('arrival_airport');
            const flightPriceInput = document.getElementById('flight_price');
            
            const toggleAirportRequirement = () => {
                const price = parseFloat(flightPriceInput.value) || 0;
                const required = price > 0;
                departureInput.required = required;
                arrivalInput.required = required;
            };
            flightPriceInput.addEventListener('input', toggleAirportRequirement);
            toggleAirportRequirement();

            new google.maps.places.Autocomplete(departureInput, { types: ['airport'] });
            new google.maps.places.Autocomplete(arrivalInput, { types: ['airport'] });
            const destinationAutocomplete = new google.maps.places.Autocomplete(destinationInput, { types: ['(regions)'], fields: ['geometry', 'name'] });
            const hotelAutocomplete = new google.maps.places.Autocomplete(hotelInput, { types: ['lodging'] });
            hotelAutocomplete.setFields(['name', 'rating', 'address_components']);
            destinationAutocomplete.addListener('place_changed', () => {
                const place = destinationAutocomplete.getPlace();
                if (place.geometry && place.geometry.viewport) hotelAutocomplete.setBounds(place.geometry.viewport);
            });
            hotelAutocomplete.addListener('place_changed', () => {
                const hotelPlace = hotelAutocomplete.getPlace();
                if (hotelPlace.address_components) {
                    let city = '', country = '';
                    for (const component of hotelPlace.address_components) {
                        if (component.types.includes('locality')) city = component.long_name;
                        if (component.types.includes('country')) country = component.long_name;
                    }
                    if (city && country) destinationInput.value = `${city}, ${country}`;
                }
                if (hotelPlace && hotelPlace.rating) {
                    const rating = parseFloat(hotelPlace.rating);
                    if (rating >= 4.8) starsSelect.value = '5';
                    else if (rating >= 3.8) starsSelect.value = '4';
                    else starsSelect.value = '3';
                }
            });
            document.getElementById('searchBookingBtn').addEventListener('click', () => {
                const hotelName = hotelInput.value;
                const checkinDate = document.getElementById('date_start').value;
                const checkoutDate = document.getElementById('date_end').value;
                if (!hotelName || !checkinDate || !checkoutDate) return alert("Veuillez sélectionner un hôtel et des dates.");
                const bookingUrl = `https://www.booking.com/searchresults.html?ss=${encodeURIComponent(hotelName)}&checkin=${checkinDate}&checkout=${checkoutDate}&group_adults=2&no_rooms=1`;
                window.open(bookingUrl, '_blank');
            });

            document.getElementById('searchFlightsBtn').addEventListener('click', () => {
                const departureText = departureInput.value;
                const arrivalText = arrivalInput.value;
                const checkinDate = document.getElementById('date_start').value;
                const checkoutDate = document.getElementById('date_end').value;

                if (!departureText || !arrivalText || !checkinDate || !checkoutDate) {
                    return alert("Veuillez sélectionner les aéroports de départ, d'arrivée et les dates.");
                }

                const flightsUrl = `https://www.google.com/flights?hl=fr&q=vols+de+${encodeURIComponent(departureText)}+à+${encodeURIComponent(arrivalText)}+le+${checkinDate}+retour+le+${checkoutDate}`;
                window.open(flightsUrl, '_blank');
            });

            document.getElementById('voyageForm').addEventListener('submit', function(e) {
                e.preventDefault();
                const formData = new FormData(this);
                const data = Object.fromEntries(formData);
                if (!data.date_start || !data.date_end) return alert("Veuillez sélectionner une période de séjour.");

                document.getElementById('loading').style.display = 'block';
                document.getElementById('result').style.display = 'none';

                fetch('/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('loading').style.display = 'none';
                    const resultDiv = document.getElementById('result');
                    resultDiv.style.display = 'block';

                    if (data.success) {
                        resultDiv.innerHTML = `
                            <div class="success">✅ Page générée !</div>
                            <div class="stats">
                                <div class="stat-item"><div class="stat-number">${data.real_photos_count}</div><div class="stat-label">Photos</div></div>
                                <div class="stat-item"><div class="stat-number">${data.real_videos_count}</div><div class="stat-label">Vidéos</div></div>
                                <div class="stat-item"><div class="stat-number">${data.real_reviews_count}</div><div class="stat-label">Avis</div></div>
                                <div class="stat-item"><div class="stat-number">${data.real_attractions_count}</div><div class="stat-label">Attractions</div></div>
                                <div class="stat-item"><div class="stat-number">${data.savings}€</div><div class="stat-label">Économies</div></div>
                            </div>
                            <div class="button-container">
                                <a href="/download/${data.filename}" class="download-btn">📥 Télécharger</a>
                                <a href="/view/${data.filename}" class="view-btn" target="_blank">👁️ Ouvrir</a>
                                <a href="#" id="editVideoBtn" class="edit-btn">✏️ Modifier Vidéo</a>
                                <button type="button" id="htmlCodeBtn" class="html-code-btn">📄 Code HTML</button>
                                <button type="button" id="resetFormBtn" class="reset-btn" title="Nouvelle recherche">🔄</button>
                            </div>
                            <div id="videoEditContainer" class="video-edit-form" style="display:none;">
                                <input type="text" id="newVideoUrl" placeholder="Coller la nouvelle URL YouTube ici...">
                                <button id="submitVideoChange" style="background-color: #28a745;">Valider</button>
                                <button id="deleteVideoBtn" style="background-color: #dc3545;">Pas de Vidéo</button>
                            </div>
                            <div id="editConfirmation" style="font-weight: bold; text-align: center; margin-top: 15px;"></div>`;

                        document.getElementById('resetFormBtn').addEventListener('click', () => {
                            document.getElementById('voyageForm').reset();
                            cancellationDateWrapper.style.display = 'none';
                            document.getElementById('result').style.display = 'none';
                            document.querySelector('.form-container').scrollIntoView({ behavior: 'smooth' });
                        });
                        
                        document.getElementById('editVideoBtn').addEventListener('click', (e) => {
                            e.preventDefault();
                            document.getElementById('videoEditContainer').style.display = 'flex';
                            e.target.style.display = 'none';
                        });

                        document.getElementById('submitVideoChange').addEventListener('click', () => {
                            const newUrl = document.getElementById('newVideoUrl').value;
                            const videoId = getYouTubeId(newUrl);
                            if (!videoId) {
                                alert("URL YouTube invalide.");
                                return;
                            }
                            updateVideo({ filename: data.filename, video_id: videoId });
                        });

                        document.getElementById('deleteVideoBtn').addEventListener('click', () => {
                            if (!confirm("Êtes-vous sûr de vouloir supprimer la section vidéo ?")) return;
                            updateVideo({ filename: data.filename, video_id: 'DELETE' });
                        });

                        document.getElementById('htmlCodeBtn').addEventListener('click', () => {
                            fetch(`/view/${data.filename}`).then(response => response.text())
                            .then(htmlContent => {
                                document.getElementById('htmlCodeDisplay').value = htmlContent;
                                document.getElementById('htmlCodeModal').style.display = 'flex';
                            });
                        });
                        document.querySelector('.close-button').addEventListener('click', () => {
                            document.getElementById('htmlCodeModal').style.display = 'none';
                        });
                        document.getElementById('copyHtmlCodeBtn').addEventListener('click', () => {
                            const textarea = document.getElementById('htmlCodeDisplay');
                            textarea.select();
                            document.execCommand("copy");
                            const copyStatus = document.getElementById('copyStatus');
                            copyStatus.textContent = "✅ Code copié !";
                            setTimeout(() => { copyStatus.textContent = ""; }, 2000);
                        });
                        window.addEventListener('click', (event) => {
                            if (event.target == document.getElementById('htmlCodeModal')) {
                                document.getElementById('htmlCodeModal').style.display = 'none';
                            }
                        });

                    } else {
                        resultDiv.innerHTML = `<div class="error">❌ Erreur: ${data.error}</div>`;
                    }
                })
                .catch(error => {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('result').style.display = 'block';
                    document.getElementById('result').innerHTML = `<div class="error">❌ Erreur de connexion: ${error.message}</div>`;
                });
            });

            function updateVideo(payload) {
                const confirmDiv = document.getElementById('editConfirmation');
                confirmDiv.textContent = "Mise à jour...";
                fetch('/update_video', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                })
                .then(res => res.json())
                .then(updateStatus => {
                    if (updateStatus.success) {
                        confirmDiv.textContent = '✅ Opération réussie ! Page mise à jour.';
                        confirmDiv.style.color = 'green';
                        document.getElementById('videoEditContainer').style.display = 'none';
                        document.getElementById('editVideoBtn').style.display = 'inline-block';
                    } else {
                        confirmDiv.textContent = `❌ Erreur: ${updateStatus.error}`;
                        confirmDiv.style.color = 'red';
                        document.getElementById('editVideoBtn').style.display = 'inline-block';
                    }
                });
            }
        }
    </script>
    <script async src="https://maps.googleapis.com/maps/api/js?key={{ google_api_key }}&libraries=places&callback=initializeApp"></script>
</body>
</html>
"""

@app.route('/')
def home():
    if not check_auth():
        return redirect(url_for('login'))

    username = session.get('username', 'Utilisateur')
    google_api_key = os.environ.get('GOOGLE_API_KEY', '')
    return render_template_string(INTERFACE_HTML, username=username, google_api_key=google_api_key)

@app.route('/generate', methods=['POST'])
def generate():
    if not check_auth():
        return jsonify({'success': False, 'error': 'Non autorisé'})

    try:
        data = request.get_json()
        if not data.get('date_start') or not data.get('date_end'):
            raise ValueError("Les dates sont requises.")

        real_gatherer = RealAPIHotelGatherer()
        real_data = real_gatherer.gather_all_real_data(data['hotel_name'], data['destination'])

        try:
            hotel_price = int(data.get('booking_price', 0))
            flight_price = int(data.get('flight_price', 0))
            transfer_cost = int(data.get('transfer_cost', 0))
            surcharge_cost = int(data.get('surcharge_cost', 0))
            your_price = int(data.get('price', 0))
            car_rental_cost = int(data.get('car_rental_cost', 0))

            comparison_total = hotel_price + flight_price + transfer_cost + surcharge_cost + car_rental_cost
            savings = comparison_total - your_price
        except (ValueError, TypeError):
            comparison_total, savings = 0, 0

        html_content = generate_travel_page_real_data(data, real_data, savings, comparison_total)

        filename = f"voyage_secure_{data['hotel_name'].replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = f"./{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return jsonify({
            'success': True, 'filename': filename,
            'real_photos_count': len(real_data['photos']), 'real_videos_count': len(real_data['videos']),
            'real_reviews_count': real_data['total_reviews'],
            'real_attractions_count': sum(len(v) for v in real_data['attractions'].values()),
            'savings': savings
        })

    except Exception as e:
        print(f"❌ Erreur génération: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/update_video', methods=['POST'])
def update_video():
    if not check_auth():
        return jsonify({"success": False, "error": "Non autorisé"})

    try:
        data = request.get_json()
        filename = data.get('filename')
        new_video_id = data.get('video_id')

        if not all([filename, new_video_id]):
            return jsonify({"success": False, "error": "Données manquantes."})

        if '..' in filename or filename.startswith('/'):
            return jsonify({"success": False, "error": "Nom de fichier invalide."})

        filepath = f"./{filename}"
        if not os.path.exists(filepath):
            return jsonify({"success": False, "error": "Fichier non trouvé."})

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        soup = BeautifulSoup(content, 'lxml')
        video_wrapper = soup.find(id='video-section-wrapper')

        if new_video_id == 'DELETE':
            if video_wrapper:
                video_wrapper.decompose()
        else:
            embed_url = f"https://www.youtube.com/embed/{new_video_id}"
            if video_wrapper:
                iframe = video_wrapper.find('iframe')
                if iframe:
                    iframe['src'] = embed_url
                else:
                    return jsonify({"success": False, "error": "Structure interne de la vidéo corrompue."})
            else:
                gallery_section = soup.find(id='gallery-section')
                if not gallery_section:
                    return jsonify({"success": False, "error": "Point d'insertion (galerie) introuvable."})

                video_html_string = f"""
                <div class="instagram-card p-6" id="video-section-wrapper">
                    <h3 class="section-title text-xl mb-4">Vidéo</h3>
                    <div>
                        <h4 class="font-semibold mb-2">Visite de l'hôtel</h4>
                        <div class="video-container aspect-w-16 aspect-h-9">
                        <iframe src="{embed_url}" title="Vidéo" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen="" class="w-full h-full rounded-lg"></iframe>
                        </div>
                    </div>
                </div>"""
                new_video_soup = BeautifulSoup(video_html_string, 'lxml')
                gallery_section.insert_after(new_video_soup)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))

        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Erreur mise à jour vidéo: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route('/download/<filename>')
def download_file(filename):
    if not check_auth(): return redirect(url_for('login'))
    try:
        if '..' in filename or filename.startswith('/'):
            return "Nom de fichier invalide.", 400
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/view/<filename>')
def view_file(filename):
    if not check_auth(): return redirect(url_for('login'))
    try:
        if '..' in filename or filename.startswith('/'):
            return "Nom de fichier invalide.", 400
        return send_file(filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

def generate_travel_page_real_data(data, real_data, savings, comparison_total):

    # ✅ NOUVELLE LOGIQUE : Séparer le nom de l'hôtel de son adresse pour l'affichage
    hotel_name_full = data.get('hotel_name', '')
    hotel_name_parts = hotel_name_full.split(',')
    display_hotel_name = hotel_name_parts[0].strip()
    if len(hotel_name_parts) > 1:
        display_address = ', '.join(hotel_name_parts[1:]).strip()
    else:
        # Si le nom de l'hôtel n'a pas de virgule (pas d'adresse), on utilise le champ destination
        display_address = data.get('destination', '')


    date_start = datetime.strptime(data['date_start'], '%Y-%m-%d').strftime('%d %B %Y')
    date_end = datetime.strptime(data['date_end'], '%Y-%m-%d').strftime('%d %B %Y')

    stars = "⭐" * int(data['stars'])

    num_people = int(data.get('num_people', 2))
    price_for_text = f"pour {num_people} personnes" if num_people > 1 else "pour 1 personne"

    your_price = int(data.get('price', 0))
    price_per_person_text = ""
    if num_people > 0:
        price_per_person = round(your_price / num_people)
        price_per_person_text = f'<p class="text-sm font-light mt-1">soit {price_per_person} € par personne</p>'
    
    # ✅ MODIFICATION : Centrer le texte d'annulation
    cancellation_html = ""
    if data.get('has_cancellation') == 'on' and data.get('cancellation_date'):
        cancellation_date = data.get('cancellation_date')
        cancellation_html = f'<p class="text-xs font-light mt-1 text-center">✓ Annulation gratuite jusqu\'au {cancellation_date}</p>'

    # ✅ NOUVELLE FEATURE : Logique pour le bouton Instagram
    instagram_button_html = ""
    instagram_input = data.get('instagram_handle', '').strip()
    if instagram_input:
        # Regex pour extraire le nom d'utilisateur d'une URL
        match = re.search(r'(?:https?:\/\/)?(?:www\.)?instagram\.com\/([A-Za-z0-9_.-]+)', instagram_input)
        if match:
            username = match.group(1)
        else:
            # Supposer que c'est le nom d'utilisateur, enlever le @ si présent
            username = instagram_input.lstrip('@')
        
        # Générer le bouton si on a un nom d'utilisateur valide
        if username:
            instagram_url = f"https://www.instagram.com/{username}"
            instagram_button_html = f'''
            <a href="{instagram_url}" target="_blank" class="block bg-gradient-to-r from-purple-500 via-pink-500 to-red-500 hover:opacity-90 text-white font-bold py-3 px-6 rounded-full text-center" style="display: inline-flex; align-items: center; justify-content: center; gap: 8px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M8 0C5.829 0 5.556.01 4.703.048 3.85.088 3.269.222 2.76.42a3.9 3.9 0 0 0-1.417.923A3.9 3.9 0 0 0 .42 2.76C.222 3.268.087 3.85.048 4.703.01 5.555 0 5.827 0 8s.01 2.444.048 3.297c.04.852.174 1.433.372 1.942.205.526.478.972.923 1.417.444.445.89.719 1.416.923.51.198 1.09.333 1.942.372C5.555 15.99 5.827 16 8 16s2.444-.01 3.297-.048c.852-.04 1.433-.174 1.942-.372.526-.205.972-.478 1.417-.923.445-.444.718-.891.923-1.417.198-.51.333-1.09.372-1.942C15.99 10.445 16 10.173 16 8s-.01-2.444-.048-3.297c-.04-.852-.174-1.433-.372-1.942a3.9 3.9 0 0 0-.923-1.417A3.9 3.9 0 0 0 13.24.42c-.51-.198-1.09-.333-1.942-.372C10.445.01 10.173 0 8 0M8 4.865a3.135 3.135 0 1 0 0 6.27 3.135 3.135 0 0 0 0-6.27m0 5.143a2.008 2.008 0 1 1 0-4.016 2.008 2.008 0 0 1 0 4.016m6.406-4.848a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5"/></svg>
                Voir sur Instagram
            </a>
            '''

    city_name = data.get('destination', '').split(',')[0].strip()

    exclusive_services = data.get('exclusive_services', '').strip()
    exclusive_services_html = ""
    if exclusive_services:
        formatted_services = exclusive_services.replace('\n', '<br>')
        exclusive_services_html = f"""
        <div class="p-4 mt-4 rounded-lg border-2 border-blue-200 bg-blue-50">
            <h4 class="font-bold text-blue-800 mb-2">Nos Services additionnels offerts</h4>
            <p class="text-sm text-gray-700">{formatted_services}</p>
        </div>
        """

    departure_airport_name = data.get('departure_city', '').split(',')[0]
    arrival_airport_name = data.get('arrival_airport', data['destination']).split(',')[0]
    flight_price = int(data.get('flight_price', 0))
    
    flight_text_html = ""
    flight_inclusion_html = ""
    baggage_inclusion_html = ""

    if flight_price > 0:
        flight_text = f"Vol {departure_airport_name} ↔ {arrival_airport_name}"
        flight_price_text = f"{flight_price}€"
        flight_text_html = f"""<div class="flex justify-between"><span>{flight_text}</span><span class="font-semibold">{flight_price_text}</span></div>"""
        flight_inclusion_html = f"""<div class="flex items-center"><div class="feature-icon bg-blue-500"><i class="fas fa-plane"></i></div><div class="ml-4"><h4 class="font-semibold text-sm">{flight_text}</h4><p class="text-gray-600 text-xs">Aller-retour inclus</p></div></div>"""
        baggage_inclusion_html = """<div class="flex items-center"><div class="feature-icon bg-red-500"><i class="fas fa-suitcase"></i></div><div class="ml-4"><h4 class="font-semibold text-sm">Bagages 10kg</h4><p class="text-gray-600 text-xs">Bagage cabine inclus</p></div></div>"""

    transfer_cost = int(data.get('transfer_cost', 0))
    transfer_text_html = ""
    transfer_inclusion_html = ""
    if transfer_cost > 0:
        transfer_text_html = f"""<div class="flex justify-between"><span>+ Transferts</span><span class="font-semibold">~{transfer_cost}€</span></div>"""
        transfer_inclusion_html = """<div class="flex items-center"><div class="feature-icon bg-green-500"><i class="fas fa-bus"></i></div><div class="ml-4"><h4 class="font-semibold text-sm">Transfert aéroport ↔ hôtel</h4><p class="text-gray-600 text-xs">Prise en charge complète</p></div></div>"""

    surcharge_type = data.get('surcharge_type', '')
    surcharge_cost = int(data.get('surcharge_cost', 0))
    surcharge_text_html = ""
    if surcharge_cost > 0:
        surcharge_text_html = f"""<div class="flex justify-between"><span>+ Surcoût {surcharge_type}</span><span class="font-semibold">~{surcharge_cost}€</span></div>"""

    car_rental_cost = int(data.get('car_rental_cost', 0))
    car_rental_text_html = ""
    car_rental_inclusion_html = ""
    if car_rental_cost > 0:
        car_rental_text_html = f"""<div class="flex justify-between"><span>+ Voiture de location (sans franchise)</span><span class="font-semibold">~{car_rental_cost}€</span></div>"""
        car_rental_inclusion_html = """
        <div class="flex items-center"><div class="feature-icon bg-gray-500"><i class="fas fa-car"></i></div><div class="ml-4"><h4 class="font-semibold text-sm">Voiture de location (sans franchise)</h4><p class="text-gray-600 text-xs">Explorez à votre rythme</p></div></div>
        """

    hotel_price_text = f"{data.get('booking_price', 'N/A')} €"

    comparison_block = f"""
        <div class="flex justify-between"><span>Hôtel ({data.get('stars')}⭐)</span><span class="font-semibold">{hotel_price_text}</span></div>
        {flight_text_html}
        {transfer_text_html}
        {car_rental_text_html}
        {surcharge_text_html}
        <hr class="my-3"><div class="flex justify-between text-base font-bold text-red-600"><span>TOTAL ESTIMÉ</span><span>{comparison_total} €</span></div>
    """
    
    # ✅ NOUVELLE LOGIQUE GALERIE PHOTOS
    total_photos = len(real_data['photos'])
    first_6_photos = real_data['photos'][:6]
    # Galerie principale (6 photos max)
    image_gallery = "".join([f'<div class="image-item"><img src="{url}" alt="Photo de {data["hotel_name"]}"></div>\n' for url in first_6_photos]) if first_6_photos else '<p>Aucune photo disponible.</p>'
    # Bouton "Voir plus" conditionnel
    more_photos_button = ""
    if total_photos > 6:
        more_photos_button = f'''
        <div class="text-center mt-4">
            <button id="voirPlusPhotos" class="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-6 rounded-full transition-colors">
                📸 Voir plus de photos ({total_photos} au total)
            </button>
        </div>'''
    # Toutes les photos pour la modale
    modal_all_photos = "".join([f'<img src="{url}" alt="Photo {i+1} de {data["hotel_name"]}" class="modal-photo">' for i, url in enumerate(real_data['photos'])]) if real_data['photos'] else ''


    video_html_block = ""
    if real_data['videos']:
        embed_url = f"https://www.youtube.com/embed/{real_data['videos'][0]['id']}"
        video_title = real_data['videos'][0]['title']
        video_section_content = f'<div><h4 class="font-semibold mb-2">Visite de l\'hôtel</h4><div class="video-container aspect-w-16 aspect-h-9"><iframe src="{embed_url}" title="{video_title}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen class="w-full h-full rounded-lg"></iframe></div></div>'
        video_html_block = f'<div id="video-section-wrapper" class="instagram-card p-6"><h3 class="section-title text-xl mb-4">Vidéo</h3>{video_section_content}</div>'

    reviews_section = "".join([f'<div class="bg-gray-50 p-4 rounded-lg"><div><span class="font-semibold">{r["author"]}</span> <span class="text-yellow-500">{r["rating"]}</span> <span class="text-gray-500 text-sm float-right">{r.get("date", "")}</span></div><p class="mt-2 text-gray-700">"{r["text"]}"</p></div>' for r in real_data['reviews']])

    destination_section = ""
    if real_data.get('cultural_attraction_image'):
        cultural_attraction_name = real_data['attractions']['culture'][0] if real_data['attractions']['culture'] else ''
        destination_section += f"""
        <div class="mb-6 rounded-lg overflow-hidden shadow-lg">
            <img src="{real_data['cultural_attraction_image']}" alt="Image de {cultural_attraction_name}" class="w-full h-48 object-cover">
            <div class="p-4 bg-gray-50">
                <h4 class="font-bold text-gray-800">Incontournable : {cultural_attraction_name}</h4>
            </div>
        </div>
        """

    if real_data.get('restaurants'):
        restaurants_list_items = "".join([f'<li class="flex items-center"><i class="fas fa-utensils text-yellow-500 mr-3"></i><span>{resto.get("name")}</span></li>' for resto in real_data['restaurants']])
        destination_section += f"""
        <div class="mb-6">
            <h4 class="font-semibold text-lg mb-3 text-gray-800">🍴 Top 3 Restaurants</h4>
            <ul class="space-y-2 text-gray-700">
                {restaurants_list_items}
            </ul>
        </div>
        """

    other_attractions_html = ""
    icons = {'plages': 'fa-water', 'culture': 'fa-monument', 'gastronomie': 'fa-utensils', 'activites': 'fa-map-signs'}
    colors = {'plages': 'bg-blue-500', 'culture': 'bg-purple-500', 'gastronomie': 'bg-green-500', 'activites': 'bg-orange-500'}
    categories = {'plages': 'Plages & Nature', 'culture': 'Culture & Histoire', 'gastronomie': 'Gastronomie Locale', 'activites': 'Activités & Loisirs'}

    attractions_to_display = real_data.get('attractions', {})
    flat_attractions = []
    for category, attractions in attractions_to_display.items():
        start_index = 1 if category == 'culture' and real_data.get('cultural_attraction_image') else 0
        for attraction_name in attractions[start_index:]:
            flat_attractions.append({'name': attraction_name, 'category': category})

    if flat_attractions:
        other_attractions_items = ""
        for attr in flat_attractions[:4]:
             other_attractions_items += f"""
             <div class="flex items-start space-x-3">
                 <div class="feature-icon {colors.get(attr['category'], 'bg-gray-500')}" style="width: 35px; height: 35px; font-size: 16px; flex-shrink: 0;"><i class="fas {icons.get(attr['category'], 'fa-question')}"></i></div>
                 <div>
                     <h5 class="font-semibold text-sm text-gray-800">{attr['name']}</h5>
                     <p class="text-gray-500 text-xs">{categories.get(attr['category'])}</p>
                 </div>
             </div>"""

        destination_section += f"""
        <div>
            <h4 class="font-semibold text-lg mb-3 text-gray-800">À explorer également</h4>
            <div class="space-y-4">
                {other_attractions_items}
            </div>
        </div>
        """

    footer_html = f"""
        <div class="instagram-card p-6 bg-blue-500 text-white text-center">
            <h3 class="text-2xl font-bold mb-2">🌟 Réservez votre évasion !</h3>
            <p>Les places sont très limitées pour cette offre exclusive. Pour garantir votre place :</p>
            <div class="mt-4 flex flex-col sm:flex-row justify-center gap-4">
                <a href="tel:+32488433344" class="block w-full sm:w-auto bg-red-500 hover:bg-red-600 text-white font-bold py-3 px-6 rounded-full">
                    📞 Appeler maintenant
                </a>
                <a href="mailto:voyages-privileges@oldibike.be" class="block w-full sm:w-auto bg-white hover:bg-gray-100 text-blue-500 font-bold py-3 px-6 rounded-full">
                    ✉️ Envoyer un email
                </a>
            </div>
        </div>
        <div class="instagram-card p-6 text-center">
             <h3 class="text-xl font-semibold mb-2">🗓️ Voyagez à vos dates</h3>
             <p class="text-gray-700">Les dates ou la durée de ce séjour ne vous conviennent pas ? Contactez-nous ! Nous pouvons vous créer une offre sur mesure.</p>
             <p class="text-sm text-gray-500 mt-2">Notez que le tarif concurrentiel de cette offre est spécifique à ces dates et conditions.</p>
        </div>
        <div class="instagram-card p-6 text-center">
            <h3 class="text-xl font-semibold mb-4">📞 Contact & Infos</h3>
            <img src="https://static.wixstatic.com/media/5ca515_449af35c8bea462986caf4fd28e02398~mv2.png" alt="Logo Voyages Privilèges" class="h-12 mx-auto mb-4">
            <p class="text-gray-800">📍 Rue Winston Churchill 38, 6180 Courcelles</p>
            <p class="text-gray-800 my-2">📞 <a href="tel:+32488433344" class="text-blue-600">+32 488 43 33 44</a></p>
            <p class="text-gray-800">✉️ <a href="mailto:voyages-privileges@oldibike.be" class="text-blue-600">voyages-privileges@oldibike.be</a></p>
            <hr class="my-4">
            <p class="text-xs text-gray-500">SRL RIDEA (OldiBike)<br>Numéro de société : 1024.916.054 - RC Exploitation : 99730451</p>
        </div>
    """

    html_template = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Voyages Privilèges - {display_hotel_name}</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com?plugins=aspect-ratio"></script>
    <style>
        body {{ font-family: 'Poppins', sans-serif; }} .section-title {{ font-family: 'Playfair Display', serif; }}
        .instagram-card {{ background: white; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); overflow: hidden; }}
        .story-card, .instagram-card + .instagram-card {{ margin-top: 20px; }}
        .story-card {{ background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%); border-radius: 25px; padding: 25px; color: white; text-align: center; box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3); margin-top: 0; }}
        .image-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }}
        .image-item img {{ width: 100%; height: 200px; object-fit: cover; transition: transform 0.3s ease; border-radius: 15px;}}
        .economy-highlight {{ background: linear-gradient(45deg, #ffd700, #ffb347); color: #333; padding: 15px; border-radius: 15px; text-align: center; margin-top: 20px; font-weight: bold;}}
        .feature-icon {{ width: 45px; height: 45px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 18px; flex-shrink: 0; }}
        
        /* ✅ NOUVEAUX STYLES MODALE PHOTOS */
        .modal-photos {{ 
            display: none; position: fixed; top: 0; left: 0; 
            width: 100%; height: 100%; background: rgba(0,0,0,0.95); 
            z-index: 1000; overflow-y: auto; padding: 20px; 
        }}
        .modal-photos-content {{ 
            max-width: 800px; margin: 0 auto; padding-top: 60px; 
        }}
        .close-photos {{ 
            position: fixed; top: 20px; right: 30px; 
            font-size: 40px; color: white; cursor: pointer; 
            z-index: 1001; font-weight: bold;
            width: 50px; height: 50px; display: flex;
            align-items: center; justify-content: center;
            background: rgba(0,0,0,0.5); border-radius: 50%;
        }}
        .close-photos:hover {{ background: rgba(255,255,255,0.2); }}
        .modal-photo {{ 
            width: 100%; margin-bottom: 20px; border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        .photo-counter {{
            position: fixed; top: 20px; left: 30px;
            color: white; background: rgba(0,0,0,0.5);
            padding: 10px 15px; border-radius: 20px;
            font-weight: bold; z-index: 1001;
        }}
        /* Mobile optimisé */
        @media (max-width: 768px) {{
            .close-photos {{ top: 15px; right: 15px; font-size: 30px; width: 40px; height: 40px; }}
            .photo-counter {{ top: 15px; left: 15px; padding: 8px 12px; font-size: 14px; }}
            .modal-photos-content {{ padding-top: 80px; padding-left: 10px; padding-right: 10px; }}
        }}
    </style>
</head>
<body>
    <div style="max-width: 600px; margin: auto; padding: 10px;">
        <div style="text-align: center; padding-top: 20px; padding-bottom: 10px;">
            <img src="https://static.wixstatic.com/media/5ca515_449af35c8bea462986caf4fd28e02398~mv2.png" alt="Logo Voyages Privilèges" style="max-height: 50px; margin: auto;">
        </div>

        <div class="story-card">
            <img src="{real_data['photos'][0] if real_data['photos'] else ''}" alt="{data['hotel_name']}" style="width: 100%; height: 256px; object-fit: cover; border-radius: 8px; margin-bottom: 1rem;">
            <h2 class="text-2xl font-bold">{display_hotel_name} {stars}</h2>
            <p>📍 {display_address}</p>
            <p class="mt-4">🗓️ Du {date_start} au {date_end}</p>
            <div class="text-4xl font-bold mt-2">{data['price']} €</div>
            <p>{price_for_text}</p>
            {price_per_person_text}
            {f'<p class="text-sm mt-2">Note Google: {real_data["hotel_rating"]}/5 ({real_data["total_reviews"]} avis)</p>' if real_data["hotel_rating"] > 0 else ""}
            <div class="mt-4">{instagram_button_html}</div>
        </div>
        <div class="instagram-card p-6">
            <h3 class="section-title text-xl mb-4">Inclus dans votre séjour</h3>
            <div class="space-y-5">
                {flight_inclusion_html}
                {transfer_inclusion_html}
                {car_rental_inclusion_html}
                <div class="flex items-center"><div class="feature-icon bg-purple-500"><i class="fas fa-hotel"></i></div><div class="ml-4"><h4 class="font-semibold text-sm">Hôtel {stars} {display_hotel_name}</h4><p class="text-gray-600 text-xs">Style traditionnel</p></div></div>
                <div class="flex items-center"><div class="feature-icon bg-yellow-500"><i class="fas fa-utensils"></i></div><div class="ml-4"><h4 class="font-semibold text-sm">{data.get('surcharge_type', 'Pension complète')}</h4><p class="text-gray-600 text-xs">Inclus dans le forfait</p></div></div>
                {baggage_inclusion_html}
            </div>
        </div>
        <div class="instagram-card p-6">
            <h3 class="section-title text-xl mb-4">Pourquoi nous choisir ?</h3>
            <div class="p-4 rounded-lg border-2 border-red-200 bg-red-50 mb-4">
                <h4 class="font-bold text-center mb-2">Prix estimé ailleurs</h4>
                <div class="text-sm space-y-1">{comparison_block}</div>
            </div>
            {exclusive_services_html}
            <div class="p-4 rounded-lg bg-green-600 text-white">
                 <h4 class="font-bold text-center mb-2">Notre Offre</h4>
                 <div class="text-center text-2xl font-bold">{data['price']} €</div>
                 {cancellation_html}
            </div>
            <div class="economy-highlight">💰 Vous économisez {savings} € !</div>
        </div>
        
        <div class="instagram-card p-6" id="gallery-section">
            <h3 class="section-title text-xl mb-4">Galerie de photos</h3>
            <div class="image-grid">{image_gallery}</div>
            {more_photos_button}
        </div>
        
        <div id="photosModal" class="modal-photos">
            <span class="close-photos" id="closePhotos">×</span>
            <div class="photo-counter" id="photoCounter">Photo 1 sur {total_photos}</div>
            <div class="modal-photos-content">
                {modal_all_photos}
            </div>
        </div>

        {video_html_block}
        
        <div class="instagram-card p-6">
            <h3 class="section-title text-xl mb-4">Avis des clients</h3>
            <div class="space-y-4">{reviews_section}</div>
        </div>
        <div class="instagram-card p-6">
             <h3 class="section-title text-xl mb-4">Découvrir {city_name}</h3>
             {destination_section}
        </div>

        {footer_html}
    </div>

    <script>
    // ✅ JAVASCRIPT MODALE PHOTOS
    document.addEventListener('DOMContentLoaded', function() {{
        const voirPlusBtn = document.getElementById('voirPlusPhotos');
        const modal = document.getElementById('photosModal');
        const closeBtn = document.getElementById('closePhotos');
        const photoCounter = document.getElementById('photoCounter');
        const modalPhotos = document.querySelectorAll('.modal-photo');

        // Ouvrir la modale
        if (voirPlusBtn) {{
            voirPlusBtn.addEventListener('click', function() {{
                if (modal) modal.style.display = 'block';
                document.body.style.overflow = 'hidden'; // Bloquer scroll
            }});
        }}

        // Fermer la modale
        function closeModal() {{
            if (modal) modal.style.display = 'none';
            document.body.style.overflow = 'auto'; // Restaurer scroll
        }}

        if (closeBtn) {{
            closeBtn.addEventListener('click', closeModal);
        }}

        // Fermer en cliquant à côté
        if (modal) {{
            modal.addEventListener('click', function(e) {{
                if (e.target === modal) {{
                    closeModal();
                }}
            }});
        }}
        
        // Fermer avec Escape
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape' && modal && modal.style.display === 'block') {{
                closeModal();
            }}
        }});

        // Compteur de photos pendant le scroll
        if (modalPhotos.length > 0) {{
            const observer = new IntersectionObserver(function(entries) {{
                entries.forEach(function(entry) {{
                    if (entry.isIntersecting) {{
                        const index = Array.from(modalPhotos).indexOf(entry.target) + 1;
                        if (photoCounter) {{
                            photoCounter.textContent = `Photo ${{index}} sur ${{modalPhotos.length}}`;
                        }}
                    }}
                }});
            }}, {{ threshold: 0.5 }});

            modalPhotos.forEach(function(photo) {{
                observer.observe(photo);
            }});
        }}
    }});
    </script>
</body>
</html>"""
    return html_template

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
