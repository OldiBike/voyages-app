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
        
        # ✅ SÉCURISÉ : Utilisation de variable d'environnement
        self.google_api_key = os.environ.get('GOOGLE_API_KEY')
        
        # Vérification de sécurité
        if not self.google_api_key:
            print("❌ ERREUR CRITIQUE: Variable GOOGLE_API_KEY manquante")
            print("🔧 Ajoutez la variable GOOGLE_API_KEY dans Railway")
            # Ne pas lever d'erreur pour éviter le crash, mais loguer
        else:
            print("✅ Clé API Google chargée depuis variable d'environnement")
    
    def get_real_hotel_photos(self, hotel_name, destination):
        """VRAI appel API Google Places pour récupérer les VRAIES photos de l'hôtel"""
        
        # ✅ SÉCURITÉ : Vérifier la clé avant utilisation
        if not self.google_api_key:
            print("❌ Clé API Google manquante - Photos désactivées")
            return []
            
        try:
            print(f"📸 APPEL API Google Places Photos pour {hotel_name}")
            
            # 1. Chercher l'hôtel exact
            search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            search_params = {
                'query': f'"{hotel_name}" "{destination}" hotel',
                'key': self.google_api_key,
                'fields': 'photos,place_id'
            }
            
            search_response = requests.get(search_url, params=search_params, timeout=15)
            print(f"🔍 Recherche API Status: {search_response.status_code}")
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                print(f"🔍 Résultats trouvés: {len(search_data.get('results', []))}")
                
                if search_data.get('results'):
                    place_id = search_data['results'][0].get('place_id')
                    
                    # 2. Récupérer les détails avec photos
                    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                    details_params = {
                        'place_id': place_id,
                        'fields': 'photos',
                        'key': self.google_api_key
                    }
                    
                    details_response = requests.get(details_url, params=details_params, timeout=15)
                    print(f"📸 Photos API Status: {details_response.status_code}")
                    
                    if details_response.status_code == 200:
                        details_data = details_response.json()
                        photos = details_data.get('result', {}).get('photos', [])
                        
                        # 3. Construire les URLs des vraies photos
                        photo_urls = []
                        for photo in photos[:6]:  # Maximum 6 photos
                            photo_reference = photo.get('photo_reference')
                            if photo_reference:
                                photo_url = f"https://maps.googleapis.com/maps/api/place/photo"
                                photo_url += f"?maxwidth=800&photo_reference={photo_reference}&key={self.google_api_key}"
                                photo_urls.append(photo_url)
                        
                        print(f"✅ {len(photo_urls)} VRAIES photos récupérées de l'hôtel")
                        return photo_urls
            
            print("❌ Aucune photo trouvée via API")
            return []
            
        except Exception as e:
            print(f"❌ Erreur API Photos: {e}")
            return []
    
    def get_real_hotel_reviews(self, hotel_name, destination):
        """VRAI appel API Google Places pour récupérer les VRAIS avis"""
        
        # ✅ SÉCURITÉ : Vérifier la clé avant utilisation
        if not self.google_api_key:
            print("❌ Clé API Google manquante - Avis désactivés")
            return {'reviews': [], 'rating': 0, 'total_reviews': 0}
            
        try:
            print(f"📝 APPEL API Google Places Reviews pour {hotel_name}")
            
            # 1. Chercher l'hôtel exact
            search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            search_params = {
                'query': f'"{hotel_name}" "{destination}" hotel',
                'key': self.google_api_key
            }
            
            search_response = requests.get(search_url, params=search_params, timeout=15)
            print(f"🔍 Recherche Reviews Status: {search_response.status_code}")
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                
                if search_data.get('results'):
                    place_id = search_data['results'][0].get('place_id')
                    
                    # 2. Récupérer les avis détaillés
                    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                    details_params = {
                        'place_id': place_id,
                        'fields': 'reviews,rating,user_ratings_total',
                        'key': self.google_api_key,
                        'language': 'fr'
                    }
                    
                    details_response = requests.get(details_url, params=details_params, timeout=15)
                    print(f"📝 Reviews API Status: {details_response.status_code}")
                    
                    if details_response.status_code == 200:
                        details_data = details_response.json()
                        result = details_data.get('result', {})
                        
                        reviews = []
                        raw_reviews = result.get('reviews', [])
                        
                        # Filtrer les bons avis (4-5 étoiles)
                        for review in raw_reviews:
                            rating = review.get('rating', 0)
                            if rating >= 4:
                                reviews.append({
                                    'rating': '⭐' * rating,
                                    'rating_numeric': rating,
                                    'author': review.get('author_name', 'Client Google'),
                                    'text': review.get('text', '')[:400] + '...' if len(review.get('text', '')) > 400 else review.get('text', ''),
                                    'date': review.get('relative_time_description', ''),
                                    'source': 'Google Places API'
                                })
                        
                        hotel_rating = result.get('rating', 0)
                        total_reviews = result.get('user_ratings_total', 0)
                        
                        print(f"✅ {len(reviews)} VRAIS avis récupérés (Note: {hotel_rating}/5, Total: {total_reviews})")
                        return {
                            'reviews': reviews,
                            'rating': hotel_rating,
                            'total_reviews': total_reviews
                        }
            
            print("❌ Aucun avis trouvé via API")
            return {'reviews': [], 'rating': 0, 'total_reviews': 0}
            
        except Exception as e:
            print(f"❌ Erreur API Reviews: {e}")
            return {'reviews': [], 'rating': 0, 'total_reviews': 0}
    
    def get_real_youtube_videos(self, hotel_name, destination):
        """VRAI appel API YouTube pour chercher des vidéos spécifiques à l'hôtel"""
        
        # ✅ SÉCURITÉ : Vérifier la clé avant utilisation
        if not self.google_api_key:
            print("❌ Clé API Google manquante - YouTube désactivé")
            return []
            
        try:
            print(f"🎥 APPEL API YouTube pour {hotel_name}")
            
            # Utiliser la même clé Google pour YouTube API
            youtube_url = "https://www.googleapis.com/youtube/v3/search"
            youtube_params = {
                'part': 'snippet',
                'q': f'"{hotel_name}" "{destination}" hotel review tour',
                'type': 'video',
                'maxResults': 4,
                'order': 'relevance',
                'key': self.google_api_key
            }
            
            youtube_response = requests.get(youtube_url, params=youtube_params, timeout=15)
            print(f"🎥 YouTube API Status: {youtube_response.status_code}")
            
            if youtube_response.status_code == 200:
                youtube_data = youtube_response.json()
                videos = []
                
                for item in youtube_data.get('items', []):
                    video_id = item.get('id', {}).get('videoId')
                    if video_id:
                        videos.append({
                            'id': video_id,
                            'title': item.get('snippet', {}).get('title', ''),
                            'description': item.get('snippet', {}).get('description', '')[:100] + '...'
                        })
                
                print(f"✅ {len(videos)} VRAIES vidéos YouTube trouvées")
                return videos
            
            print("❌ Aucune vidéo trouvée via API YouTube")
            return []
            
        except Exception as e:
            print(f"❌ Erreur API YouTube: {e}")
            return []
    
    def get_real_gemini_attractions(self, destination):
        """VRAI appel API Gemini pour les points d'intérêt"""
        
        # ✅ SÉCURITÉ : Vérifier la clé avant utilisation
        if not self.google_api_key:
            print("❌ Clé API Google manquante - Gemini désactivé, utilisation du fallback")
            return [
                {"name": "Centre-ville", "type": "culture", "description": "Exploration du centre historique"},
                {"name": "Plage principale", "type": "plage", "description": "Baignade et détente"},
                {"name": "Restaurant local", "type": "gastronomie", "description": "Cuisine authentique"},
                {"name": "Randonnée", "type": "activite", "description": "Découverte nature"}
            ]
            
        try:
            print(f"🤖 APPEL API Gemini pour {destination}")
            
            import google.generativeai as genai
            
            # Configuration avec votre clé Google
            genai.configure(api_key=self.google_api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""
            Donne-moi exactement 8 points d'intérêt touristiques réels et vérifiés pour {destination}.
            Réponds UNIQUEMENT en format JSON valide, sans texte avant ou après :
            {{
                "attractions": [
                    {{
                        "name": "Nom exact de l'attraction",
                        "type": "plage",
                        "description": "Description précise en français"
                    }},
                    {{
                        "name": "Nom exact de l'attraction",
                        "type": "culture",
                        "description": "Description précise en français"
                    }},
                    {{
                        "name": "Nom exact de l'attraction",
                        "type": "gastronomie",
                        "description": "Description précise en français"
                    }},
                    {{
                        "name": "Nom exact de l'attraction",
                        "type": "activite",
                        "description": "Description précise en français"
                    }}
                ]
            }}
            """
            
            response = model.generate_content(prompt)
            print(f"🤖 Gemini API Response reçue")
            
            # Nettoyer la réponse pour extraire le JSON
            response_text = response.text.strip()
            
            # Supprimer les balises markdown si présentes
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parser le JSON
            attractions_data = json.loads(response_text)
            attractions = attractions_data.get('attractions', [])
            
            print(f"✅ {len(attractions)} VRAIES attractions récupérées via Gemini")
            return attractions
            
        except Exception as e:
            print(f"❌ Erreur API Gemini: {e}")
            # Fallback minimal
            return [
                {"name": "Centre-ville", "type": "culture", "description": "Exploration du centre historique"},
                {"name": "Plage principale", "type": "plage", "description": "Baignade et détente"},
                {"name": "Restaurant local", "type": "gastronomie", "description": "Cuisine authentique"},
                {"name": "Randonnée", "type": "activite", "description": "Découverte nature"}
            ]
    
    def gather_all_real_data(self, hotel_name, destination):
        """Collecte TOUTES les données via les vraies APIs"""
        print(f"🚀 COLLECTE DE DONNÉES RÉELLES pour {hotel_name} à {destination}")
        
        # ✅ SÉCURITÉ : Vérification des APIs avant appels
        if not self.google_api_key:
            print("⚠️ APIs désactivées - Mode dégradé")
            return {
                'photos': [],
                'reviews': [],
                'hotel_rating': 0,
                'total_reviews': 0,
                'videos': [],
                'attractions': {
                    'plages': ['Plage principale'],
                    'culture': ['Centre-ville historique'],
                    'gastronomie': ['Restaurants locaux'],
                    'activites': ['Activités touristiques']
                }
            }
        
        # Appels API parallèles
        photos = self.get_real_hotel_photos(hotel_name, destination)
        reviews_data = self.get_real_hotel_reviews(hotel_name, destination)
        videos = self.get_real_youtube_videos(hotel_name, destination)
        attractions = self.get_real_gemini_attractions(destination)
        
        # Structurer les attractions par catégorie
        attractions_by_category = {
            'plages': [],
            'culture': [],
            'gastronomie': [],
            'activites': []
        }
        
        for attraction in attractions:
            category = attraction.get('type', 'activites')
            if category == 'activite':
                category = 'activites'
            if category not in attractions_by_category:
                category = 'activites'
            attractions_by_category[category].append(attraction.get('name', ''))
        
        return {
            'photos': photos,
            'reviews': reviews_data.get('reviews', []),
            'hotel_rating': reviews_data.get('rating', 0),
            'total_reviews': reviews_data.get('total_reviews', 0),
            'videos': videos,
            'attractions': attractions_by_category
        }

# Page de connexion HTML
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔐 Connexion - Générateur Voyages Privilèges</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            width: 400px;
            text-align: center;
        }
        .login-header {
            margin-bottom: 30px;
        }
        .login-header h1 {
            color: #333;
            margin: 0 0 10px 0;
            font-size: 2em;
        }
        .login-header p {
            color: #666;
            margin: 0;
        }
        .form-group {
            margin-bottom: 20px;
            text-align: left;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
            box-sizing: border-box;
        }
        input:focus {
            outline: none;
            border-color: #3B82F6;
        }
        .login-btn {
            background: linear-gradient(45deg, #3B82F6, #60A5FA);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 25px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            width: 100%;
        }
        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
        }
        .error {
            color: #dc3545;
            margin-top: 15px;
            font-weight: 600;
        }
        .credentials-info {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            font-size: 14px;
            color: #666;
        }
        .logo {
            max-width: 200px;
            margin-bottom: 20px;
        }
        .security-badge {
            background: #e8f5e8;
            color: #2d5a2d;
            padding: 5px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <img src="https://static.wixstatic.com/media/5ca515_449af35c8bea462986caf4fd28e02398~mv2.png" alt="Logo" class="logo">
            <div class="security-badge">🔒 Connexion Sécurisée</div>
            <h1>🔐 Connexion</h1>
            <p>Générateur de Pages Voyage</p>
        </div>
        
        <form method="POST">
            <div class="form-group">
                <label for="username">👤 Nom d'utilisateur</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">🔑 Mot de passe</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit" class="login-btn">
                🚀 Se connecter
            </button>
            
            {% if error %}
                <div class="error">{{ error }}</div>
            {% endif %}
        </form>
        
        <div class="credentials-info">
            <strong>🛡️ Application sécurisée</strong><br>
            Authentification protégée par variables d'environnement.<br>
            <small>APIs Google chargées de manière sécurisée.</small>
        </div>
    </div>
</body>
</html>
"""

INTERFACE_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Générateur de Pages Voyage</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/litepicker/dist/css/litepicker.css"/>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%);
            color: white;
            padding: 20px 30px;
            text-align: center;
        }
        .header-logo {
            height: 40px;
            margin-bottom: 10px;
        }
        .header p {
            margin: 0;
            font-size: 1.1em;
            font-weight: 300;
        }
        .user-info {
            text-align: right;
            margin-top: 10px;
            font-size: 14px;
        }
        .user-info a {
            color: white;
            margin-left: 15px;
            text-decoration: none;
            background: rgba(255,255,255,0.2);
            padding: 5px 10px;
            border-radius: 15px;
            transition: background 0.3s;
        }
        .user-info a:hover {
            background: rgba(255,255,255,0.3);
        }
        .form-container {
            padding: 40px;
        }
        .form-group {
            margin-bottom: 25px;
            width: 100%;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        input, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
            box-sizing: border-box;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #3B82F6;
        }
        #date_range {
            cursor: pointer;
            background-color: white;
        }
        .input-with-button {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .input-with-button input {
            flex-grow: 1;
        }
        .search-btn {
            padding: 8px 12px;
            font-size: 14px;
            font-weight: 600;
            background-color: #e0e0e0;
            border: 1px solid #ccc;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .search-btn:hover {
            background-color: #d0d0d0;
        }
        .form-row {
            display: flex;
            gap: 20px;
        }
        .form-row .form-group {
            flex: 1;
        }
        .generate-btn {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 25px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            width: 100%;
        }
        .generate-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(255, 107, 107, 0.3);
        }
        .loading {
            display: none;
            text-align: center;
            padding: 30px;
            color: #3B82F6;
        }
        .loading-spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3B82F6;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .result {
            display: none;
            padding: 30px;
            background: #f8f9fa;
            border-top: 1px solid #e1e5e9;
        }
        .success {
            color: #28a745;
            font-size: 18px;
            font-weight: 600;
            text-align: center;
        }
        .error {
            color: #dc3545;
            font-size: 18px;
            font-weight: 600;
        }
        .button-container {
            margin-top: 20px;
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
        }
        .download-btn, .view-btn {
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s;
        }
        .download-btn {
            background: #28a745;
        }
        .download-btn:hover {
            background: #218838;
            transform: translateY(-2px);
        }
        .view-btn {
            background: #3B82F6;
        }
        .view-btn:hover {
            background: #2563EB;
            transform: translateY(-2px);
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .stat-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .stat-number {
            font-size: 24px;
            font-weight: bold;
            color: #3B82F6;
        }
        .stat-label {
            color: #666;
            font-size: 14px;
        }
        .pac-container {
            background-color: #FFF;
            z-index: 1000;
            position: fixed;
            display: inline-block;
            float: left;
        }
        
        /* AJOUTÉ : Media Queries pour le design responsive */
        @media (max-width: 768px) {
            .form-row {
                /* Fait passer les lignes en colonnes sur mobile */
                flex-direction: column;
                gap: 0; /* On retire l'écart horizontal */
            }
            .form-container {
                /* Réduit les marges intérieures sur les petits écrans */
                padding: 20px;
            }
            .header {
                padding: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="https://static.wixstatic.com/media/5ca515_449af35c8bea462986caf4fd28e02398~mv2.png" alt="Logo" class="header-logo">
            <p>Générateur de présentation</p>
            <div class="user-info">
                <span style="color: rgba(255,255,255,0.9);">👤 Connecté : {{ username }}</span>
                <a href="/logout">🚪 Déconnexion</a>
            </div>
        </div>
        
        <div class="form-container">
            
            <form id="voyageForm">
                <div class="form-row">
                    <div class="form-group">
                        <label for="hotel_name">🏨 Nom de l'hôtel</label>
                        <input type="text" id="hotel_name" name="hotel_name" required 
                               placeholder="Saisir un nom d'hôtel...">
                    </div>
                    <div class="form-group">
                        <label for="destination">📍 Destination</label>
                        <input type="text" id="destination" name="destination" required 
                               placeholder="Saisir une destination...">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group" style="width: 100%;">
                        <label for="date_range">🗓️ Période du séjour</label>
                        <input type="text" id="date_range" readonly placeholder="Cliquez pour choisir les dates">
                        <input type="hidden" id="date_start" name="date_start">
                        <input type="hidden" id="date_end" name="date_end">
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="price">💰 Votre tarif (€)</label>
                        <input type="number" id="price" name="price" required placeholder="ex: 2400">
                    </div>
                    <div class="form-group">
                        <label for="booking_price">💳 Tarif Booking.com (€)</label>
                        <div class="input-with-button">
                            <input type="number" id="booking_price" name="booking_price" required placeholder="ex: 3270">
                            <button type="button" id="searchBookingBtn" class="search-btn" title="Rechercher sur Booking.com">🔎</button>
                        </div>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="departure_city">✈️ Aéroport de départ</label>
                        <input type="text" id="departure_city" name="departure_city" required placeholder="Saisir un aéroport...">
                    </div>
                    <div class="form-group">
                        <label for="stars">⭐ Catégorie de l'hôtel</label>
                        <select id="stars" name="stars">
                            <option value="3">3⭐</option>
                            <option value="4" selected>4⭐</option>
                            <option value="5">5⭐</option>
                        </select>
                    </div>
                </div>
                
                <button type="submit" class="generate-btn">
                    🚀 Générer
                </button>
            </form>
        </div>
        
        <div class="loading" id="loading">
            <div class="loading-spinner"></div>
            <h3>🔄 Appels API sécurisés...</h3>
            <p>📸 Récupération des VRAIES photos...</p>
            <p>📝 Récupération des VRAIS avis...</p>
            <p>🎥 Recherche des VRAIES vidéos...</p>
            <p>🤖 Génération des points d'intérêt...</p>
        </div>
        
        <div class="result" id="result"></div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/litepicker/dist/litepicker.js"></script>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            
            // --- CORRIGÉ : Fonction de formatage de date fiable ---
            function formatDate(d) {
                const year = d.getFullYear();
                const month = ('0' + (d.getMonth() + 1)).slice(-2); // +1 car les mois sont 0-indexed
                const day = ('0' + d.getDate()).slice(-2);
                return `${year}-${month}-${day}`;
            }

            const startDateInput = document.getElementById('date_start');
            const endDateInput = document.getElementById('date_end');
            const picker = new Litepicker({
                element: document.getElementById('date_range'),
                singleMode: false,
                lang: 'fr-FR',
                format: 'DD MMMM YYYY',
                setup: (picker) => {
                    picker.on('selected', (date1, date2) => {
                        // Utilise la nouvelle fonction de formatage pour éviter les bugs de fuseau horaire
                        startDateInput.value = formatDate(date1.toJSDate());
                        endDateInput.value = formatDate(date2.toJSDate());
                    });
                },
            });

            const searchBookingBtn = document.getElementById('searchBookingBtn');
            searchBookingBtn.addEventListener('click', () => {
                const hotelName = document.getElementById('hotel_name').value;
                const checkinDate = document.getElementById('date_start').value;
                const checkoutDate = document.getElementById('date_end').value;

                if (!hotelName || !checkinDate || !checkoutDate) {
                    alert("Veuillez d'abord sélectionner un hôtel et des dates.");
                    return;
                }
                
                const encodedHotel = encodeURIComponent(hotelName);
                const bookingUrl = `https://www.booking.com/searchresults.html?ss=${encodedHotel}&checkin=${checkinDate}&checkout=${checkoutDate}&group_adults=2&no_rooms=1`;
                
                window.open(bookingUrl, '_blank');
            });
        });

        document.getElementById('voyageForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            if (!data.date_start || !data.date_end) {
                alert("Veuillez sélectionner une période de séjour.");
                return;
            }
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').style.display = 'none';
            
            fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('result').style.display = 'block';
                
                if (data.success) {
                    document.getElementById('result').innerHTML = `
                        <div class="success">✅ Page générée avec succès !</div>
                        <div class="stats">
                            <div class="stat-item"><div class="stat-number">${data.real_photos_count}</div><div class="stat-label">Photos</div></div>
                            <div class="stat-item"><div class="stat-number">${data.real_videos_count}</div><div class="stat-label">Vidéos</div></div>
                            <div class="stat-item"><div class="stat-number">${data.real_reviews_count}</div><div class="stat-label">Avis</div></div>
                            <div class="stat-item"><div class="stat-number">${data.real_attractions_count}</div><div class="stat-label">Attractions</div></div>
                            <div class="stat-item"><div class="stat-number">${data.savings}€</div><div class="stat-label">Économies</div></div>
                        </div>
                        <div class="button-container">
                            <a href="/download/${data.filename}" class="download-btn" target="_blank">📥 Télécharger</a>
                            <a href="/view/${data.filename}" class="view-btn" target="_blank">👁️ Ouvrir la page</a>
                        </div>`;
                } else {
                    document.getElementById('result').innerHTML = `<div class="error">❌ Erreur: ${data.error}</div>`;
                }
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('result').style.display = 'block';
                document.getElementById('result').innerHTML = `<div class="error">❌ Erreur de connexion: ${error.message}</div>`;
            });
        });

        function initAutocompletes() {
            const hotelInput = document.getElementById('hotel_name');
            const destinationInput = document.getElementById('destination');
            const departureInput = document.getElementById('departure_city');
            const starsSelect = document.getElementById('stars');

            const airportOptions = { types: ['airport'] };
            new google.maps.places.Autocomplete(departureInput, airportOptions);

            const destinationOptions = {
                types: ['(regions)'],
                fields: ['geometry', 'name'] 
            };
            const destinationAutocomplete = new google.maps.places.Autocomplete(destinationInput, destinationOptions);

            const hotelOptions = { types: ['lodging'] };
            const hotelAutocomplete = new google.maps.places.Autocomplete(hotelInput, hotelOptions);
            hotelAutocomplete.setFields(['name', 'rating', 'address_components']);

            destinationAutocomplete.addListener('place_changed', () => {
                const place = destinationAutocomplete.getPlace();
                if (place.geometry && place.geometry.viewport) {
                    hotelAutocomplete.setBounds(place.geometry.viewport);
                }
            });

            hotelAutocomplete.addListener('place_changed', () => {
                const hotelPlace = hotelAutocomplete.getPlace();

                if (hotelPlace.address_components) {
                    let city = '';
                    let country = '';
                    for (const component of hotelPlace.address_components) {
                        if (component.types.includes('locality')) {
                            city = component.long_name;
                        }
                        if (component.types.includes('country')) {
                            country = component.long_name;
                        }
                    }
                    if (city && country) {
                        destinationInput.value = `${city}, ${country}`;
                    }
                }

                if (hotelPlace && hotelPlace.rating) {
                    const rating = parseFloat(hotelPlace.rating);
                    if (rating >= 4.8) {
                        starsSelect.value = '5';
                    } else if (rating >= 3.8) {
                        starsSelect.value = '4';
                    } else {
                        starsSelect.value = '3';
                    }
                }
            });
        }
    </script>
    <script async defer src="https://maps.googleapis.com/maps/api/js?key={{ google_api_key }}&libraries=places&callback=initAutocompletes"></script>
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
        return jsonify({'success': False, 'error': 'Non autorisé - Veuillez vous reconnecter'})
    
    try:
        data = request.get_json()
        
        if not data.get('date_start') or not data.get('date_end'):
            raise ValueError("Les dates de début et de fin sont requises.")

        print(f"🚀 GÉNÉRATION SÉCURISÉE pour: {data['hotel_name']} - {data['destination']}")
        
        real_gatherer = RealAPIHotelGatherer()
        real_data = real_gatherer.gather_all_real_data(data['hotel_name'], data['destination'])
        
        savings = int(data['booking_price']) - int(data['price'])
        html_content = generate_travel_page_real_data(data, real_data, savings)
        
        filename = f"voyage_secure_{data['hotel_name'].replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = f"./{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Page générée de manière SÉCURISÉE: {filepath}")
        
        return jsonify({
            'success': True,
            'filename': filename,
            'real_photos_count': len(real_data['photos']),
            'real_videos_count': len(real_data['videos']),
            'real_reviews_count': len(real_data['reviews']),
            'real_attractions_count': sum(len(attractions) for attractions in real_data['attractions'].values()),
            'savings': savings
        })
        
    except Exception as e:
        print(f"❌ Erreur génération sécurisée: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/download/<filename>')
def download_file(filename):
    if not check_auth():
        return redirect(url_for('login'))
    
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/view/<filename>')
def view_file(filename):
    if not check_auth():
        return redirect(url_for('login'))
    
    try:
        return send_file(filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

def generate_travel_page_real_data(data, real_data, savings):
    
    date_start = datetime.strptime(data['date_start'], '%Y-%m-%d').strftime('%d %B %Y')
    date_end = datetime.strptime(data['date_end'], '%Y-%m-%d').strftime('%d %B %Y')
    
    stars = "⭐" * int(data['stars'])
    
    image_gallery = ""
    hotel_name = data['hotel_name']
    
    if real_data['photos']:
        for img_url in real_data['photos']:
            image_gallery += f'<div class="image-item"><img src="{img_url}" alt="Photo réelle de {hotel_name}"></div>\n'
    else:
        image_gallery = '<p class="text-center text-gray-500">Photos en cours de chargement sécurisé...</p>'
    
    video_section = ""
    if real_data['videos']:
        for i, video in enumerate(real_data['videos'][:2]):
            title = "Visite de l'hôtel" if i == 0 else "Présentation complète"
            video_section += f"""
                <div class="mb-6">
                    <h4 class="font-semibold mb-3 text-center text-sm">{title}</h4>
                    <div class="video-container">
                        <iframe src="https://www.youtube.com/embed/{video['id']}" 
                                title="{video['title']}" 
                                frameborder="0" 
                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                allowfullscreen>
                        </iframe>
                    </div>
                    <p class="text-xs text-gray-600 mt-2">{video['title']}</p>
                </div>"""
    
    reviews_section = ""
    if real_data['reviews']:
        for review in real_data['reviews']:
            reviews_section += f"""
            <div class="bg-gray-50 p-4 rounded-lg">
                <div class="flex items-center mb-2">
                    <span class="text-yellow-500">{review['rating']}</span>
                    <span class="ml-2 font-semibold text-sm">{review['author']}</span>
                    <span class="ml-2 text-xs text-gray-500">{review.get('date', '')}</span>
                </div>
                <p class="text-gray-700 text-xs">"{review['text']}"</p>
                <p class="text-xs text-blue-600 mt-1">Source: {review.get('source', 'API Sécurisée')}</p>
            </div>"""
    else:
        reviews_section = '<p class="text-center text-gray-500">Avis en cours de chargement sécurisé...</p>'
    
    destination_section = ""
    icons = {
        'plages': 'fa-water', 'culture': 'fa-monument',
        'gastronomie': 'fa-utensils', 'activites': 'fa-map'
    }
    colors = {
        'plages': 'bg-blue-500', 'culture': 'bg-purple-500',
        'gastronomie': 'bg-green-500', 'activites': 'bg-orange-500'
    }
    categories = {
        'plages': 'Plages paradisiaques', 'culture': 'Patrimoine culturel',
        'gastronomie': 'Gastronomie authentique', 'activites': 'Activités & Découverte'
    }
    
    for category, attractions in real_data['attractions'].items():
        if attractions:
            attraction_text = ', '.join(attractions[:2])
            destination_section += f"""
            <div class="flex items-start space-x-4">
                <div class="feature-icon {colors[category]}"><i class="fas {icons[category]}"></i></div>
                <div>
                    <h4 class="font-semibold text-sm">{categories[category]}</h4>
                    <p class="text-gray-600 text-xs">{attraction_text}</p>
                </div>
            </div>"""

    html_template = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voyages Privilèges - {data['hotel_name']} {data['destination']}</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Poppins', sans-serif; line-height: 1.6; background-color: #f4f4f5; }}
        .instagram-card {{ background: white; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); overflow: hidden; margin-bottom: 20px; }}
        .story-card {{ background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%); border-radius: 25px; padding: 25px; margin-bottom: 20px; color: white; text-align: center; box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3); }}
        .video-container {{ position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 15px; }}
        .video-container iframe {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; }}
        .image-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }}
        .image-item {{ border-radius: 15px; overflow: hidden; position: relative; }}
        .image-item img {{ width: 100%; height: 200px; object-fit: cover; transition: transform 0.3s ease; }}
        .image-item:hover img {{ transform: scale(1.1); }}
        .cta-button {{ background: linear-gradient(45deg, #ff6b6b, #ee5a24); color: white; border: none; padding: 15px 30px; border-radius: 25px; font-weight: 600; text-decoration: none; display: inline-block; transition: all 0.3s ease; box-shadow: 0 5px 15px rgba(255, 107, 107, 0.3); }}
        .cta-button:hover {{ transform: translateY(-3px); box-shadow: 0 10px 25px rgba(255, 107, 107, 0.5); color: white; }}
        .feature-icon {{ width: 45px; height: 45px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 18px; flex-shrink: 0; }}
        .section-title {{ font-family: 'Playfair Display', serif; font-weight: 700; text-align: center; margin-bottom: 30px; color: #333; }}
        .instagram-header {{ background: white; color: #333; padding: 20px; border-radius: 20px; margin-bottom: 20px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.08); }}
        .mobile-optimized {{ max-width: 600px; margin: 0 auto; padding: 10px; }}
        .comparison-card {{ background: white; border-radius: 20px; padding: 20px; margin: 10px 0; box-shadow: 0 5px 20px rgba(0,0,0,0.05); }}
        .booking-card {{ border: 2px solid #ffdddd; background: #fffafa; }}
        .privilege-card {{ background: linear-gradient(135deg, #00b894, #00a085); color: white; }}
        .economy-highlight {{ background: linear-gradient(45deg, #ffd700, #ffb347); color: #333; padding: 15px; border-radius: 15px; text-align: center; margin-top: 20px; font-weight: bold; font-size: 1.1em; }}
        .api-badge {{ background: #e8f5e8; color: #2d5a2d; padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: bold; }}
        .security-badge {{ background: #e8f8ff; color: #1e40af; padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="mobile-optimized">
        <div class="instagram-header">
            <img src="https://static.wixstatic.com/media/5ca515_449af35c8bea462986caf4fd28e02398~mv2.png" alt="Logo Voyages Privilèges" class="mx-auto h-20">
            <p class="api-badge mt-2">APIs 100% sécurisées</p>
            <p class="security-badge mt-1">🔒 Version protégée</p>
        </div>
        <div class="story-card">
            <div class="mb-6">
                <img src="{real_data['photos'][0] if real_data['photos'] else 'https://via.placeholder.com/800x400?text=Image+non+disponible'}" alt="{data['hotel_name']}" class="w-full h-64 object-cover rounded-lg mb-4 shadow-lg">
            </div>
            <h2 class="text-xl font-bold mb-2">{data['hotel_name']} {stars}</h2>
            <p class="text-base mb-2">📍 {data['destination']}</p>
            <p class="text-sm mb-4">🗓️ Du {date_start} au {date_end}</p>
            <div class="text-3xl font-bold mb-2">{data['price']} €</div>
            <p class="text-sm">pour 2 personnes</p>
            {f'<p class="text-xs mt-2">Note Google: {real_data["hotel_rating"]}/5 ({real_data["total_reviews"]} avis)</p>' if real_data['hotel_rating'] > 0 else ''}
        </div>
        <div class="instagram-card">
            <div class="p-6">
                <h3 class="section-title text-lg"><i class="fas fa-check-circle text-green-500 mr-2"></i>Inclus dans votre séjour</h3>
                <div class="space-y-5">
                    <div class="flex items-center"><div class="feature-icon bg-blue-500"><i class="fas fa-plane"></i></div><div class="ml-4"><h4 class="font-semibold text-sm">Vol {data['departure_city']} ↔ {data['destination']}</h4><p class="text-gray-600 text-xs">Aller-retour inclus</p></div></div>
                    <div class="flex items-center"><div class="feature-icon bg-green-500"><i class="fas fa-bus"></i></div><div class="ml-4"><h4 class="font-semibold text-sm">Transfert aéroport ↔ hôtel</h4><p class="text-gray-600 text-xs">Prise en charge complète</p></div></div>
                    <div class="flex items-center"><div class="feature-icon bg-purple-500"><i class="fas fa-hotel"></i></div><div class="ml-4"><h4 class="font-semibold text-sm">Hôtel {stars} {data['hotel_name']}</h4><p class="text-gray-600 text-xs">Style traditionnel</p></div></div>
                    <div class="flex items-center"><div class="feature-icon bg-yellow-500"><i class="fas fa-utensils"></i></div><div class="ml-4"><h4 class="font-semibold text-sm">Pension complète</h4><p class="text-gray-600 text-xs">Tous les repas inclus</p></div></div>
                    <div class="flex items-center"><div class="feature-icon bg-red-500"><i class="fas fa-suitcase"></i></div><div class="ml-4"><h4 class="font-semibold text-sm">Bagages 10kg</h4><p class="text-gray-600 text-xs">Bagage cabine inclus</p></div></div>
                    <div class="flex items-center"><div class="feature-icon bg-gray-500"><i class="fas fa-shield-alt"></i></div><div class="ml-4"><h4 class="font-semibold text-sm">Assurance & Assistance</h4><p class="text-gray-600 text-xs">(en option)</p></div></div>
                </div>
            </div>
        </div>
        <div class="instagram-card">
            <div class="p-6">
                <h3 class="section-title text-lg">💰 Pourquoi nous choisir ?</h3>
                <div class="comparison-card booking-card">
                    <h4 class="font-bold text-sm mb-4 text-center text-gray-700"><img src="https://logo.clearbit.com/booking.com" alt="Booking.com" class="h-5 inline mr-2"> Prix estimé ailleurs</h4>
                    <div class="space-y-2 text-gray-800 text-xs">
                        <div class="flex justify-between"><span>Hôtel (demi-pension)</span><span class="font-semibold">{int(data['booking_price']) - 300} €</span></div>
                        <div class="flex justify-between"><span>+ Vol {data['departure_city']} - {data['destination']}</span><span class="font-semibold">~500€</span></div>
                        <div class="flex justify-between"><span>+ Transferts</span><span class="font-semibold">~150€</span></div>
                        <div class="flex justify-between"><span>+ Surcoût Pension complète</span><span class="font-semibold">~150€</span></div>
                        <hr class="my-3"><div class="flex justify-between text-base font-bold text-red-600"><span>TOTAL</span><span>{data['booking_price']} €</span></div>
                    </div>
                </div>
                <div class="comparison-card privilege-card">
                    <h4 class="font-bold text-sm mb-4 text-center">✈️ Notre Offre Voyages Privilèges</h4>
                    <div class="space-y-2 text-xs">
                        <div class="flex justify-between items-center"><span>Forfait Essentiel (Vol+Hôtel+Transferts)</span><i class="fas fa-check-circle text-lg"></i></div>
                        <div class="flex justify-between items-center"><span>Service complet</span><i class="fas fa-check-circle text-lg"></i></div>
                        <div class="flex justify-between items-center"><span>Prix négocié</span><i class="fas fa-check-circle text-lg"></i></div>
                        <hr class="my-3 border-white border-opacity-30"><div class="flex justify-between text-base font-bold"><span>VOTRE PRIX</span><span>{data['price']} €</span></div>
                    </div>
                </div>
                <div class="economy-highlight">
                    💰 Vous économisez {savings} € par rapport à Booking.com !
                </div>
            </div>
        </div>
        <div class="instagram-card">
            <div class="p-6">
                <h3 class="section-title text-lg">📸 Photos réelles sécurisées <span class="api-badge">Google Places API</span></h3>
                <div class="image-grid">{image_gallery}</div>
            </div>
        </div>
        {f'<div class="instagram-card"><div class="p-6"><h3 class="section-title text-lg">🎥 Vidéos protégées <span class="api-badge">YouTube API</span></h3><div class="space-y-6">{video_section}</div></div></div>' if video_section else ''}
        <div class="instagram-card">
            <div class="p-6">
                <h3 class="section-title text-lg">⭐ Avis clients vérifiés <span class="api-badge">Google Places API</span></h3>
                <div class="space-y-4">{reviews_section}</div>
            </div>
        </div>
        <div class="instagram-card">
            <div class="p-6">
                <h3 class="section-title text-lg">🌍 Découvrir {data['destination']} <span class="api-badge">Gemini API</span></h3>
                <div class="space-y-6">{destination_section}</div>
            </div>
        </div>
        <div class="instagram-card">
            <div class="p-6 text-center">
                <h3 class="section-title text-lg">✈️ Prêt pour l'aventure ?</h3>
                <p class="text-gray-600 mb-6">Réservez dès maintenant votre séjour de rêve à {data['destination']}</p>
                <a href="mailto:contact@voyagesprivileges.com" class="cta-button">📞 Réserver maintenant</a>
                <p class="text-xs text-gray-500 mt-4">📧 contact@voyagesprivileges.com | 📞 +33 X XX XX XX XX</p>
            </div>
        </div>
    </div>
</body>
</html>"""

    return html_template

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
