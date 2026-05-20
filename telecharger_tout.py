import os
import json
import time
import requests
from PIL import Image, ImageDraw

# =========================================================
# 🎌 TÉLÉCHARGEUR PRO API WALLHAVEN - MANGAFLUX HD
# =========================================================

DOWNLOAD_DIR = "catalogues"
NOM_SITE_WEB = "MANGAFLUX.COM"
TARGET_COUNT = 15  # Nombre d'images HD par personnage

# Configuration des recherches exactes (Wallhaven gère mieux les noms complets en anglais)
MANGAS_CONFIG = {
    "One_Piece": "roronoa zoro",
    "Naruto": "uzumaki naruto",
    "Shanks": "shanks",
    "Demon_Slayer": "kamado tanjiro",
    "Jujutsu_Kaisen": "gojo satoru"
}

def download_hd_pack(query, limit, anime_dir):
    full_dir = os.path.join(anime_dir, "full")
    thumb_dir = os.path.join(anime_dir, "thumbs")
    
    # Appel API ultra-léger filtré : Anime uniquement (010) + Format Vertical (9x16, 10x16)
    url = f"https://wallhaven.cc/api/v1/search?q={requests.utils.quote(query)}&categories=010&purity=100&ratios=9x16,10x16"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"   ⚠️ Erreur API Wallhaven (Code {r.status_code})")
            return []
            
        data = r.json().get("data", [])
        if not data:
            print(f"   ⚠️ Aucune image HD trouvée pour '{query}'")
            return []
            
        metadata_list = []
        count = 0
        
        for img_data in data:
            if count >= limit:
                break
                
            # C'est ici qu'on récupère la vraie image HD grâce au champ "path" du JSON !
            image_url = img_data.get("path")
            ext = image_url.split(".")[-1]
            filename = f"{query.replace(' ', '_')}_{count+1:03d}.{ext}"
            
            full_path = os.path.join(full_dir, filename)
            thumb_path = os.path.join(thumb_dir, filename)
            
            print(f"   📥 Téléchargement de l'image HD {count+1}/{limit}...")
            
            img_r = requests.get(image_url, headers=headers, timeout=20)
            if img_r.status_code == 200:
                with open(full_path, "wb") as f:
                    f.write(img_r.content)
                
                # Traitement de l'image (Recadrage parfait + Filigrane MangaFlux)
                finalize_wallpaper(full_path)
                
                # Création instantanée de la miniature d'aperçu pour ton catalogue
                try:
                    with Image.open(full_path) as img:
                        thumb = img.resize((300, 500))
                        thumb.save(thumb_path, quality=80)
                except:
                    pass
                
                # On enregistre les chemins exacts pour ton app
                metadata_list.append({
                    "title": f"{query.title()} HD Wallpaper {count+1}",
                    "image": full_path.replace("\\", "/"),
                    "thumbnail": thumb_path.replace("\\", "/")
                })
                count += 1
                time.sleep(0.5)  # Pause de sécurité pour ne pas se faire bloquer
                
        return metadata_list
    except Exception as e:
        print(f" ❌ Erreur réseau ou API : {e}")
        return []

def finalize_wallpaper(img_path, target_width=1080, target_height=1920):
    """Adapte l'image en 1080x1920 et écrit MANGAFLUX.COM en bas"""
    try:
        with Image.open(img_path) as img:
            img = img.convert("RGB")
            
            img_w, img_h = img.width, img.height
            scale_factor = target_width / img_w
            new_h = int(img_h * scale_factor)
            
            img_resized = img.resize((target_width, new_h), Image.Resampling.LANCZOS)
            top = (new_h - target_height) // 2
            final_img = img_resized.crop((0, max(0, top), target_width, max(0, top) + target_height))
            
            # Application du filigrane textuel propre
            draw = ImageDraw.Draw(final_img)
            text_pos = (target_width // 2, target_height - 70)
            # Effet d'ombre pour que le texte soit lisible sur fond blanc ou noir
            draw.text((text_pos[0] + 2, text_pos[1] + 2), NOM_SITE_WEB, fill="black", anchor="mm")
            draw.text(text_pos, NOM_SITE_WEB, fill="white", anchor="mm")
            
            final_img.save(img_path, format="JPEG", quality=85, optimize=True)
    except Exception:
        pass

def start():
    print("\n🚀 INITIALISATION DU TÉLÉCHARGEUR API MANGAFLUX...")
    
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    for manga_name, search_query in MANGAS_CONFIG.items():
        print(f"\n🎌 Génération du pack : {manga_name.upper()}")
        
        anime_dir = os.path.join(DOWNLOAD_DIR, manga_name)
        os.makedirs(os.path.join(anime_dir, "full"), exist_ok=True)
        os.makedirs(os.path.join(anime_dir, "thumbs"), exist_ok=True)
        
        # Lancement de l'aspiration API pour ce personnage
        metadata = download_hd_pack(search_query, TARGET_COUNT, anime_dir)
        
        # Écriture automatique du fichier de données JSON
        with open(os.path.join(anime_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)
            
        print(f"🏁 PACK {manga_name.upper()} TERMINÉ ET CONFIGURÉ.")

    print("\n🏆 PROCESSUS ENTIÈREMENT TERMINÉ ! TON CATALOGUE MANGAFLUX EST PRÊT TOUT EN HD !")

if __name__ == "__main__":
    start()
