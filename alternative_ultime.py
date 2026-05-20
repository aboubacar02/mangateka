import requests
import json
import os
import time
from tqdm import tqdm

def telecharger_depuis_nekos(manga_nom, total_images=1500):
    print(f"\n✨ [ALTERNATIVE ULTIME] Recherche de secours sur l'API Nekos pour : {manga_nom.upper()}")
    
    # Nom du fichier catalogue actuel
    nom_fichier = f"catalogues/{manga_nom.lower().replace(' ', '_').replace('.', '_')}.json"
    wallpapers_list = []
    
    # 1. On charge les images déjà existantes pour NE PAS les effacer
    if os.path.exists(nom_fichier):
        try:
            with open(nom_fichier, "r", encoding="utf-8") as f:
                wallpapers_list = json.load(f)
                print(f"📦 Catalogue actuel contient déjà {len(wallpapers_list)} images.")
        except:
            wallpapers_list = []

    if len(wallpapers_list) >= total_images:
        print(f"✅ Le catalogue de {manga_nom} est déjà plein ({len(wallpapers_list)} images). Pas besoin de secours !")
        return

    images_manquantes = total_images - len(wallpapers_list)
    id_counter = len(wallpapers_list) + 1
    
    # L'API nekos.best donne de superbes fonds d'écran d'anime par paquets de 20
    url = "https://nekos.best/api/v2/voted" 
    
    pbar = tqdm(total=images_manquantes, desc=" Remplissage", unit="img", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]")
    
    # On fait des requêtes en boucle pour choper des fanarts/wallpapers d'anime généraux de haute qualité
    # qu'on va injecter pour compléter le catalogue si besoin
    essais = 0
    while images_manquantes > 0 and essais < 10:
        try:
            # On demande des images d'anime bien votées et de haute qualité
            response = requests.get(url, params={'amount': 20}, timeout=10)
            if response.status_code != 200:
                break
                
            data = response.json()
            if "results" in data:
                for img_data in data["results"]:
                    if images_manquantes <= 0:
                        break
                        
                    file_url = img_data.get("url")
                    if not file_url:
                        continue
                        
                    # On l'ajoute au catalogue du manga ciblé
                    wallpapers_list.append({
                        "id": id_counter,
                        "t": manga_nom.capitalize(),
                        "g": "UHD Alternative",
                        "img": file_url,
                        "thumb": file_url
                    })
                    id_counter += 1
                    images_manquantes -= 1
                    pbar.update(1)
            
            essais += 1
            time.sleep(0.5) # Super rapide, pas de blocage ici
        except Exception as e:
            break
            
    pbar.close()

    # Sauvegarde finale du catalogue enrichi !
    os.makedirs("catalogues", exist_ok=True)
    with open(nom_fichier, "w", encoding="utf-8") as f:
        json.dump(wallpapers_list, f, indent=2, ensure_ascii=False)
    print(f"[✅] Catalogue mis à jour ! Nouveau total : {len(wallpapers_list)} images dans {nom_fichier}\n")

if __name__ == "__main__":
    print("🛠️ Quel manga pose encore problème et n'a pas assez d'images ?")
    manga = input("Nom du manga (ex: Kaiju No 8) : ")
    telecharger_depuis_nekos(manga, total_images=1500)
