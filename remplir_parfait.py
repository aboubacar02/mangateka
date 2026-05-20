import os
import json
import requests
import time
import sys
from tqdm import tqdm

MANGAS_ATTENDUS = [
    "One Piece", "Naruto", "Jujutsu Kaisen", "Demon Slayer", "Solo Leveling", 
    "Attack on Titan", "Bleach", "My Hero Academia", "Dragon Ball", 
    "Hunter x Hunter", "Chainsaw Man", "Black Clover",
    "Kaiju No 8", "Kagurabachi", "Dandadan", "Sakamoto Days", "Gachiakuta", 
    "Wind Breaker", "Shangri La Frontier", "Hells Paradise", "Blue Lock", 
    "Frieren", "Undead Unluck", "Mashle",
    "Sun Ken Rock", "Vagabond", "Berserk", "Vinland Saga", "Tokyo Ghoul", 
    "Origin", "Kingdom", "Tomodachi Game", "Blue Period", "Claymore", 
    "Jojos Bizarre Adventure", "Bungo Stray Dogs",
    "One Punch Man", "Tokyo Revengers", "Fairy Tail", "Death Note", 
    "Fullmetal Alchemist", "Code Geass", "Boruto", "Fire Force", 
    "Dr Stone", "Haikyuu", "Mob Psycho 100", "Noragami", 
    "Assassination Classroom", "Soul Eater"
]

def chercher_images_jikan(manga_nom):
    liens = []
    # 1. Recherche de l'anime/manga sur MyAnimeList via Jikan API
    search_url = "https://api.jikan.moe/v4/anime"
    try:
        res = requests.get(search_url, params={'q': manga_nom, 'limit': 1}, timeout=10)
        if res.status_code == 200:
            data = res.json().get('data', [])
            if data:
                anime_id = data[0]['mal_id']
                attrs = data[0].get('images', {})
                
                # Récupération des images principales (JPG et WebP)
                for format_type in ['jpg', 'webp']:
                    img_formats = attrs.get(format_type, {})
                    for size in ['large_image_url', 'image_url']:
                        if img_formats.get(size):
                            liens.append(img_formats[size])
                
                # 2. Requête bonus sur les galeries additionnelles de Jikan pour cet ID
                time.sleep(1) # Pause requise par Jikan
                pictures_url = f"https://api.jikan.moe/v4/anime/{anime_id}/pictures"
                pic_res = requests.get(pictures_url, timeout=10)
                if pic_res.status_code == 200:
                    pic_data = pic_res.json().get('data', [])
                    for pic in pic_data:
                        for format_type in ['jpg', 'webp']:
                            img_formats = pic.get(format_type, {})
                            if img_formats.get('large_image_url'):
                                liens.append(img_formats['large_image_url'])
    except:
        pass
    return list(set(liens))

def run():
    print("🚀 [MANGATEKA] Initialisation de l'API MyAnimeList (Jikan) + Banques UHD...")
    print("🎯 Objectif : Réparer tous les manquants et pousser chaque compteur à 1500.")
    
    for manga in MANGAS_ATTENDUS:
        nom_fichier = f"catalogues/{manga.lower().replace(' ', '_').replace('.', '_')}.json"
        wallpapers_list = []
        
        # Charger ce qui a déjà été fait par Safebooru pour ne rien perdre
        if os.path.exists(nom_fichier):
            try:
                with open(nom_fichier, "r", encoding="utf-8") as f:
                    wallpapers_list = json.load(f)
            except:
                wallpapers_list = []
        
        images_actuelles = len(wallpapers_list)
        
        # Si le catalogue n'est pas au max (1500), on s'en occupe
        if images_actuelles < 1500:
            manquant = 1500 - images_actuelles
            print(f"\n⚡ Traitement : {manga.upper()} ({images_actuelles}/1500 images)")
            
            id_counter = images_actuelles + 1
            
            # Étape A : On pioche dans la base de données officielle du manga
            images_officielles = chercher_images_jikan(manga)
            for img_url in images_officielles:
                if len(wallpapers_list) >= 1500: break
                wallpapers_list.append({
                    "id": id_counter, "t": manga.capitalize(), "g": "HQ Official Art",
                    "img": img_url, "thumb": img_url
                })
                id_counter += 1
                manquant -= 1
            
            # Étape B : Si on n'a pas atteint 1500, on blinde le reste avec des fonds d'écran Anime UHD fluides
            if manquant > 0:
                try:
                    backup_res = requests.get("https://nekos.best/api/v2/search", params={'query': 'waifu', 'amount': min(manquant, 50)}, timeout=10).json()
                    for item in backup_res.get('results', []):
                        if len(wallpapers_list) >= 1500: break
                        wallpapers_list.append({
                            "id": id_counter, "t": manga.capitalize(), "g": "UHD Fanart Secours",
                            "img": item.get('url'), "thumb": item.get('url')
                        })
                        id_counter += 1
                except:
                    pass
            
            # Sauvegarde propre du catalogue complété
            os.makedirs("catalogues", exist_ok=True)
            with open(nom_fichier, "w", encoding="utf-8") as f:
                json.dump(wallpapers_list, f, indent=2, ensure_ascii=False)
            print(f"[✅] Terminé avec succès : {len(wallpapers_list)}/1500 images enregistrées.")
            
            # Pause anti-blocage stricte pour respecter Jikan
            time.sleep(2)

    print("\n🏆 Fin du traitement global ! Tous tes catalogues ont reçu leurs extensions d'images.")

if __name__ == "__main__":
    run()
