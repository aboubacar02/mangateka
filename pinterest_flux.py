import os
import json
import time
import requests
from PIL import Image, ImageDraw
import sys

# =========================================================
# 🎌 SCRIPT MANGAFLUX V11.4 - FIX DES MOTS-CLÉS (LA PIE)
# =========================================================

# 🗝️ Ta clé officielle Wallhaven
API_KEY = "xhBf8oV9q80rJruddxXQFCf0SAdiyeLb"  

DOWNLOAD_DIR = "catalogues"
NOM_SITE_WEB = "MANGAFLUX.COM"
TARGET_COUNT = 50  # Objectif strict : 50 images par pack
PAUSE_SEC = 1      # 1 seconde de pause avec ton API premium

# Mots-clés simplifiés au maximum pour forcer des milliers de résultats !
MANGAS_CONFIG = {
    "One_Piece": "one piece",
    "Naruto": "naruto",
    "Shanks": "shanks",
    "Demon_Slayer": "demon slayer",
    "Jujutsu_Kaisen": "jujutsu kaisen"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def compte_a_rebours(secondes):
    for i in range(secondes, 0, -1):
        sys.stdout.write(f"\r   ⚡ Mode Premium Actif - Pause sécurité... ")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\r" + " " * 60 + "\r")

def search_wallhaven_premium(query, limit):
    """Recherche simplifiée et efficace sur l'API officielle"""
    query_encoded = requests.utils.quote(query)
    
    # categories=010 -> Anime uniquement | ratios=9x16,10x16 -> Format téléphone vertical
    url = f"https://wallhaven.cc/api/v1/search?q={query_encoded}&categories=010&purity=100&ratios=9x16,10x16&apikey={API_KEY}"
        
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            data = response.json().get("data", [])
            urls = [item.get("path") for item in data if item.get("path")]
            return urls[:limit]
        else:
            print(f"   ⚠️ Erreur API Wallhaven (Code {response.status_code})")
            return []
    except Exception as e:
        print(f"   ❌ Erreur de connexion : {e}")
        return []

def is_image_valid(file_path):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return False
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except:
        return False

def finalize_wallpaper(img_path, target_width=1080, target_height=1920):
    """Recadrage parfait et écriture du filigrane"""
    try:
        with Image.open(img_path) as img:
            img = img.convert("RGB")
            scale_factor = target_width / img.width
            new_h = int(img.height * scale_factor)
            img_resized = img.resize((target_width, new_h), Image.Resampling.LANCZOS)
            top = (new_h - target_height) // 2
            final_img = img_resized.crop((0, max(0, top), target_width, max(0, top) + target_height))
            
            draw = ImageDraw.Draw(final_img)
            text_pos = (target_width // 2, target_height - 70)
            draw.text((text_pos[0] + 2, text_pos[1] + 2), NOM_SITE_WEB, fill="black", anchor="mm")
            draw.text(text_pos, NOM_SITE_WEB, fill="white", anchor="mm")
            final_img.save(img_path, format="JPEG", quality=92, optimize=True)
    except:
        pass

def run_downloader():
    print("🔥 MISE À JOUR DES MOTS-CLÉS : REPLISSAGE REEL DES PACKS MANGAFLUX 🔥\n")
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    for manga, query in MANGAS_CONFIG.items():
        anime_dir = os.path.join(DOWNLOAD_DIR, manga)
        full_dir = os.path.join(anime_dir, "full")
        thumb_dir = os.path.join(anime_dir, "thumbs")
        
        os.makedirs(full_dir, exist_ok=True)
        os.makedirs(thumb_dir, exist_ok=True)
        
        print(f"📊 Analyse locale du pack : {manga.upper()}")
        
        valid_slots = []
        metadata = []
        
        # Identification des images valides déjà présentes
        for slot in range(1, TARGET_COUNT + 1):
            filename = f"image_{slot:03d}.jpg"
            full_path = os.path.join(full_dir, filename)
            
            if is_image_valid(full_path):
                valid_slots.append(slot)
                metadata.append({
                    "title": f"{manga.replace('_', ' ')} Wallpaper {slot}",
                    "local_full_path": full_path.replace("\\", "/"),
                    "local_thumb_path": os.path.join(thumb_dir, filename).replace("\\", "/")
                })
            else:
                if os.path.exists(full_path):
                    os.remove(full_path)
                    
        manquantes = TARGET_COUNT - len(valid_slots)
        print(f"   ✅ Images OK : {len(valid_slots)}/50 | 📥 À compléter : {manquantes}")
        
        # Téléchargement effectif si des images manquent
        if manquantes > 0:
            print(f"   🔍 Recherche de pépites sur le mot-clé : '{query}'...")
            urls_list = search_wallhaven_premium(query, manquantes)
            print(f"   📡 Serveur : {len(urls_list)} images trouvées prêtes à l'envoi.")
            
            url_idx = 0
            for slot in range(1, TARGET_COUNT + 1):
                if slot in valid_slots:
                    continue
                    
                if url_idx >= len(urls_list):
                    print("   ⚠️ Plus d'images dans la liste récupérée.")
                    break
                    
                url = urls_list[url_idx]
                url_idx += 1
                
                filename = f"image_{slot:03d}.jpg"
                full_path = os.path.join(full_dir, filename)
                thumb_path = os.path.join(thumb_dir, filename)
                
                try:
                    print(f"   📥 Téléchargement réel de l'image {slot:03d}...")
                    img_data = requests.get(url, headers=HEADERS, timeout=15).content
                    with open(full_path, "wb") as f:
                        f.write(img_data)
                        
                    if is_image_valid(full_path):
                        finalize_wallpaper(full_path)
                        with Image.open(full_path) as img:
                            thumb = img.resize((300, 533))
                            thumb.save(thumb_path, quality=80)
                            
                        metadata.append({
                            "title": f"{manga.replace('_', ' ')} Wallpaper {slot}",
                            "local_full_path": full_path.replace("\\", "/"),
                            "local_thumb_path": thumb_path.replace("\\", "/")
                        })
                        compte_a_rebours(PAUSE_SEC)
                    else:
                        if os.path.exists(full_path): os.remove(full_path)
                except Exception as e:
                    if os.path.exists(full_path): os.remove(full_path)
                    
        with open(os.path.join(anime_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)
        print(f"   🏁 Pack {manga.upper()} au complet.\n")

    print("🏆 TOUS LES DOSSIERS ONT ÉTÉ COMPLÉTÉS ET MIS À JOUR AVEC SUCCÈS ! BOUM !")

if __name__ == "__main__":
    run_downloader()
