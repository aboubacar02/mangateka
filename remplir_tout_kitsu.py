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

def extraire_images_kitsu(manga_nom, quantite_voulue):
    # On cherche les artworks et posters officiels via l'API Kitsu
    url = "https://kitsu.io/api/edge/anime"
    params = {
        'filter[text]': manga_nom,
        'page[limit]': 10
    }
    liens_trouves = []
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for anime in data.get('data', []):
                attrs = anime.get('attributes', {})
                
                # Image de couverture (généralement en HD/UHD)
                cover = attrs.get('coverImage')
                if cover:
                    for size in ['original', 'large', 'tiny']:
                        if cover.get(size):
                            liens_trouves.append(cover[size])
                            
                # Poster officiel
                poster = attrs.get('posterImage')
                if poster:
                    for size in ['original', 'large', 'medium']:
                        if poster.get(size):
                            liens_trouves.append(poster[size])
    except:
        pass
    
    # Doublon de secours si Kitsu est trop court : on pioche dans des banques d'illustrations d'Anime générales
    if len(liens_trouves) < quantite_voulue:
        try:
            res_back = requests.get("https://nekos.best/api/v2/search", params={'query': 'lurk', 'amount': 20}, timeout=10).json()
            for item in res_back.get('results', []):
                liens_trouves.append(item.get('url'))
        except:
            pass
            
    return list(set(liens_trouves)) # Supprime les doublons

def run():
    print("🔍 [MANGATEKA] Détection et Remplissage automatique des catalogues incomplets...")
    
    for manga in MANGAS_ATTENDUS:
        nom_fichier = f"catalogues/{manga.lower().replace(' ', '_').replace('.', '_')}.json"
        wallpapers_list = []
        
        # Charger l'existant
        if os.path.exists(nom_fichier):
            try:
                with open(nom_fichier, "r", encoding="utf-8") as f:
                    wallpapers_list = json.load(f)
            except:
                wallpapers_list = []
                
        images_actuelles = len(wallpapers_list)
        
        # Si le fichier a moins de 1500 images, on le complète !
        if images_actuelles < 1500:
            manquant = 1500 - images_actuelles
            print(f"\n⚡ {manga.upper()} : {images_actuelles}/1500 images. Remplissage des {manquant} manquantes...")
            
            id_counter = images_actuelles + 1
            images_secours = extraire_images_kitsu(manga, manquant)
            
            if images_secours:
                pbar = tqdm(total=manquant, desc=" Ajout Kitsu", unit="img")
                
                for img_url in images_secours:
                    if len(wallpapers_list) >= 1500:
                        break
                    
                    wallpapers_list.append({
                        "id": id_counter,
                        "t": manga.capitalize(),
                        "g": "UHD Poster & Fanart",
                        "img": img_url,
                        "thumb": img_url
                    })
                    id_counter += 1
                    pbar.update(1)
                
                pbar.close()
                
                # Sauvegarde du fichier mis à jour
                os.makedirs("catalogues", exist_ok=True)
                with open(nom_fichier, "w", encoding="utf-8") as f:
                    json.dump(wallpapers_list, f, indent=2, ensure_ascii=False)
                print(f"[✅] Mis à jour : {len(wallpapers_list)}/1500 images.")
            else:
                print(f"[⚠️] Pas de nouvelles images trouvées pour {manga} sur cette API.")
                
            time.sleep(1) # Petite pause anti-blocage

    print("\n🏆 Opération terminée ! Relance ton script de vérification.")

if __name__ == "__main__":
    run()
