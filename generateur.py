import os
import sys
import subprocess
import json
import time
import requests  # install automatique plus bas

# Installation automatique de requests si absent
try:
    import requests
except ImportError:
    print("Installation de 'requests'...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

BIBLIOTHEQUE = {
    "Naruto": "Shonen", "One Piece": "Shonen", "Jujutsu Kaisen": "Shonen",
    "Demon Slayer": "Shonen", "Dragon Ball": "Shonen", "Bleach": "Shonen",
    "Hunter x Hunter": "Shonen", "Tokyo Ghoul": "Seinen", "Attack on Titan": "Shonen",
    "Fullmetal Alchemist": "Shonen", "Death Note": "Shonen", "My Hero Academia": "Shonen",
    "Chainsaw Man": "Shonen", "Vinland Saga": "Seinen", "Berserk": "Seinen",
    "Black Clover": "Shonen", "Fire Force": "Shonen", "Dr. Stone": "Shonen",
    "Blue Lock": "Sport", "Haikyuu": "Sport", "Slam Dunk": "Sport",
    "Cowboy Bebop": "Classique", "Neon Genesis Evangelion": "Classique",
    "JoJo Bizarre Adventure": "Shonen", "Fairy Tail": "Shonen"
}

BASE_DIR = os.path.join("assets", "mangas")
NB_IMAGES = 100  # nombre souhaité par manga

# Résolutions 9:16 dans l’ordre de priorité (4K d’abord)
RESOLUTIONS = [
    "2160x3840",  # 4K
    "1440x2560",  # 2K+
    "1080x1920"   # Full HD (dernier recours)
]

def telecharger_images(manga_name, nb_images=100):
    dossier = os.path.join(BASE_DIR, manga_name)
    os.makedirs(dossier, exist_ok=True)

    # Compter les jpg déjà présents
    existants = len([f for f in os.listdir(dossier) if f.lower().endswith('.jpg')])
    if existants >= nb_images:
        print(f"[OK] {manga_name} déjà complet ({existants} images). On passe.")
        return

    print(f"-> {manga_name} : besoin de {nb_images - existants} images supplémentaires.")

    restant = nb_images - existants
    for resolution in RESOLUTIONS:
        if restant <= 0:
            break
        print(f"   Essai avec résolution >= {resolution}...")
        restant = _telecharger_depuis_wallhaven(manga_name, dossier, resolution, restant, existants)
        time.sleep(2)  # petite pause entre les changements de résolution

    total_final = len([f for f in os.listdir(dossier) if f.lower().endswith('.jpg')])
    print(f"   Terminé pour {manga_name} : {total_final}/{nb_images} images.\n")

def _telecharger_depuis_wallhaven(query, dossier, atleast, max_nouvelles, existants):
    """Télécharge depuis Wallhaven jusqu'à max_nouvelles images.
    Retourne le nombre d'images encore manquantes après cette étape."""
    api_url = "https://wallhaven.cc/api/v1/search"
    params = {
        "q": query,
        "categories": "010",        # Anime seulement
        "ratios": "portrait",       # 9:16
        "atleast": atleast,
        "sorting": "toplist",
        "purity": "100"
    }

    compteur = 0
    page = 1
    while compteur < max_nouvelles and page <= 10:  # max 10 pages pour ne pas spammer
        params["page"] = page
        try:
            reponse = requests.get(api_url, params=params, timeout=15)
            if reponse.status_code != 200:
                print(f"   API status {reponse.status_code}, on arrête.")
                break
            data = reponse.json()
            images = data.get("data", [])
            if not images:
                print(f"   Plus d'images trouvées à cette résolution (page {page}).")
                break
        except Exception as e:
            print(f"   Erreur requête API : {e}")
            break

        for img in images:
            if compteur >= max_nouvelles:
                break
            url = img.get("path")
            if not url:
                continue
            # Nom de fichier unique
            nom_fichier = f"{query.replace(' ', '_')}_{existants + compteur}.jpg"
            chemin = os.path.join(dossier, nom_fichier)
            try:
                with requests.get(url, timeout=15) as r_img:
                    if r_img.status_code == 200:
                        with open(chemin, 'wb') as f:
                            f.write(r_img.content)
                        compteur += 1
                        print(f"   [{compteur}/{max_nouvelles}] téléchargé : {os.path.basename(chemin)}")
                    else:
                        print(f"   Échec téléchargement image (status {r_img.status_code})")
            except Exception as e:
                print(f"   Erreur lors du téléchargement de l'image : {e}")
            time.sleep(1.2)  # politesse serveur

        page += 1

    return max_nouvelles - compteur  # ce qui reste à faire

def generer_json():
    print("\n--- Création du catalogue ---")
    catalog = []
    for nom, cat in BIBLIOTHEQUE.items():
        dossier = os.path.join(BASE_DIR, nom)
        if os.path.isdir(dossier):
            images = [f"assets/mangas/{nom}/{img}" for img in os.listdir(dossier) if img.lower().endswith('.jpg')]
            if images:
                catalog.append({
                    "title": nom,
                    "category": cat,
                    "cover": images[0],
                    "images": images
                })
    with open("catalogues.json", "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=4, ensure_ascii=False)
    print("catalogues.json généré avec succès.")

if __name__ == "__main__":
    for manga in BIBLIOTHEQUE:
        telecharger_images(manga, NB_IMAGES)
    generer_json()
    print("\n🎉 Terminé ! Ta bibliothèque manga 4K est prête.")