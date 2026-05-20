import requests
import json
import os
import time
import xml.etree.ElementTree as ET
from tqdm import tqdm

# Dictionnaire de secours avec les vrais tags d'API pour tes 20 mangas
MANGAS_SECOURS = {
    "Demon Slayer": "kimetsu_no_yaiba",
    "Attack on Titan": "shingeki_no_kyojin",
    "My Hero Academia": "boku_no_hero_academia",
    "Kaiju No 8": "kaijuu_8-gou",
    "Wind Breaker": "wind_breaker_(nii_satoru)",
    "Shangri La Frontier": "shangri-la_frontier",
    "Hells Paradise": "jigokuraku",
    "Sun Ken Rock": "sun-ken_rock",
    "Origin": "origin_(boichi)",
    "Kingdom": "kingdom_(hara_yasuhisa)",
    "Tomodachi Game": "tomodachi_game",
    "Blue Period": "blue_period",
    "Jojos Bizarre Adventure": "joojo_no_kimyou_na_bouken",
    "Bungo Stray Dogs": "bungou_stray_dogs",
    "One Punch Man": "one-punch_man",
    "Boruto": "boruto_-naruto_next_generations-",
    "Fire Force": "en'en_no_shouboutai",
    "Dr Stone": "dr._stone",
    "Haikyuu": "haikyuu!!",
    "Assassination Classroom": "ansatsu_kyoushitsu"
}

def telecharger_secours(manga_nom, tag_api, total_images=1500):
    print(f"\n⚡ Récupération forcée pour : {manga_nom.upper()} (Tag: {tag_api})")
    
    # On commence par interroger l'API Safebooru avec le bon tag
    url = "https://safebooru.org/index.php"
    wallpapers_list = []
    id_counter = 1
    page = 0
    
    pbar = tqdm(total=total_images, desc=" Progression", unit="img", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]")

    while len(wallpapers_list) < total_images and page < 15:
        params = {
            'page': 'dapi', 's': 'post', 'q': 'index',
            'tags': tag_api, 'pid': page, 'limit': 50
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200: break
            
            root = ET.fromstring(response.content)
            posts = root.findall('post')
            if not posts: break
                
            for post in posts:
                if len(wallpapers_list) >= total_images: break
                file_url = post.get('file_url')
                if not file_url: continue
                if file_url.startswith('//'): file_url = 'https:' + file_url
                
                width = post.get('width', '0')
                height = post.get('height', '0')
                ratio = "Portrait" if int(height) > int(width) else "Paysage"
                
                wallpapers_list.append({
                    "id": id_counter,
                    "t": manga_nom.capitalize(),
                    "g": f"HQ {ratio} {width}x{height}",
                    "img": file_url,
                    "thumb": 'https:' + post.get('sample_url') if post.get('sample_url').startswith('//') else file_url
                })
                id_counter += 1
                pbar.update(1)
            page += 1
            time.sleep(0.8)
        except:
            break

    # 🔄 MODE DE SECOURS DOUBLE : Si Safebooru n'a rien donné, on passe sur Danbooru
    if len(wallpapers_list) < 20:
        print(f"🔄 Passage sur l'API Danbooru pour compléter {manga_nom}...")
        danbooru_url = "https://danbooru.donmai.us/posts.json"
        page_dan = 1
        while len(wallpapers_list) < total_images and page_dan <= 5:
            dan_params = {
                'tags': tag_api, 'page': page_dan, 'limit': 100, 'rating': 'g'
            }
            try:
                res = requests.get(danbooru_url, params=dan_params, timeout=10).json()
                if not res or not isinstance(res, list): break
                for post in res:
                    if len(wallpapers_list) >= total_images: break
                    file_url = post.get('file_url')
                    if not file_url: continue
                    
                    width = post.get('image_width', 0)
                    height = post.get('image_height', 0)
                    ratio = "Portrait" if height > width else "Paysage"
                    
                    wallpapers_list.append({
                        "id": id_counter,
                        "t": manga_nom.capitalize(),
                        "g": f"UHD {ratio} {width}x{height}",
                        "img": file_url,
                        "thumb": post.get('large_file_url', file_url)
                    })
                    id_counter += 1
                    pbar.update(1)
                page_dan += 1
                time.sleep(1)
            except:
                break

    pbar.close()

    # Sauvegarde finale en écrasant l'ancien petit fichier foireux
    if len(wallpapers_list) > 0:
        nom_fichier = f"catalogues/{manga_nom.lower().replace(' ', '_').replace('.', '_')}.json"
        with open(nom_fichier, "w", encoding="utf-8") as f:
            json.dump(wallpapers_list, f, indent=2, ensure_ascii=False)
        print(f"[✅] Récupération réussie ! {len(wallpapers_list)} images enregistrées dans {nom_fichier}")
    else:
        print(f"[❌] Échec définitif pour {manga_nom}")

if __name__ == "__main__":
    print("🚀 DÉMARRAGE DU SCRIPT DE SECOURS POUR LES 20 MANGAS BLOCUÉ...")
    for nom, tag in MANGAS_SECOURS.items():
        telecharger_secours(nom, tag, total_images=1500)
    print("\n🏆 Fin du traitement de secours ! Relance ton script de vérification pour valider.")
