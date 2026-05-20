import os
import json
import asyncio
import re
from telethon import TelegramClient, events

# ==========================================
# CONFIGURATION MULTI-CANAUX ULTIME (9 CANAUX) 🎯
# ==========================================
API_ID = 33732454
API_HASH = '919426e61f0598cc823b10b3e9ca5787'

# La liste complète de toutes tes sources
LISTE_CANAUX = [
    'One_Piece_Family_Wallpapers',
    'anime_wallpapers_ocean',
    'AnimeWallpapers',
    'Anime_WallpapersHD',
    'zvanimewallpapers',
    'hd_ultra_wallpapers',
    'phone_4k_mobile_wallpaper_hd',
    'mobowalls',
    'animewallzx'
]
# ==========================================

IMAGE_DIR = 'image'
JSON_FILE = 'wallpapers.json'

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

print("🚀 Initialisation du robot Multi-Source Mangateka...")
client = TelegramClient('session_abou', API_ID, API_HASH)

def charger_fonds_existants():
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def sauvegarder_dans_json(liste_wallpapers):
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(liste_wallpapers, f, indent=2, ensure_ascii=False)

def extraire_details_message(texte_message, id_fallback, nom_canal):
    if not texte_message:
        return f"Anime Wall #{id_fallback}", nom_canal
        
    lignes = [l.strip() for l in texte_message.split('\n') if l.strip()]
    titre = lignes[0][:25] if lignes else f"Anime Wall #{id_fallback}"
    
    categorie = nom_canal.replace('_', ' ')
    hashtags = re.findall(r'#(\w+)', texte_message)
    if hashtags:
        categorie = hashtags[0].replace('_', ' ')
        
    return titre, categorie

async def ajouter_wallpaper_au_json(message, max_id, nom_canal):
    wallpapers = charger_fonds_existants()
    
    nouveau_id = max_id + 1
    nom_image = f"wallpaper_{nouveau_id}.jpg"
    chemin_complet = os.path.join(IMAGE_DIR, nom_image)
    
    print(f"   📥 Téléchargement de l'image #{nouveau_id}...")
    await message.download_media(file=chemin_complet)
    
    titre, categorie = extraire_details_message(message.message, nouveau_id, nom_canal)
    
    nouveau_wallpaper = {
        "id": nouveau_id,
        "t": titre,
        "a": categorie,
        "img": f"image/{nom_image}"
    }
    
    if not any(w['id'] == nouveau_id for w in wallpapers):
        wallpapers.insert(0, nouveau_wallpaper)
        sauvegarder_dans_json(wallpapers)
        return nouveau_id
    return max_id

async def scanner_tous_les_canaux():
    wallpapers = charger_fonds_existants()
    max_id = max([w['id'] for w in wallpapers], default=0)
    
    for canal in LISTE_CANAUX:
        print(f"\n🔎 Scan du canal : @{canal}...")
        compteur_canal = 0
        
        try:
            async for msg in client.iter_messages(canal, limit=15):
                if msg.photo:
                    max_id = await ajouter_wallpaper_au_json(msg, max_id, canal)
                    compteur_canal += 1
                    await asyncio.sleep(1.5) # Sécurité anti-blocage Telegram
            print(f"✅ Terminé pour @{canal} ! {compteur_canal} images récupérées.")
        except Exception as e:
            print(f"⚠️ Impossible d'accéder au canal @{canal} : {e}")
            
    print("\n🎉 Parfait ! Tournée générale des 9 canaux terminée.")

async def main():
    print("📢 Connexion aux serveurs Telegram...")
    await client.start()
    print("🛰️ Robot connecté avec succès !")
    
    await scanner_tous_les_canaux()
    
    print(f"\n🚀 Mode surveillance activé sur les 9 canaux en même temps...")
    @client.on(events.NewMessage(chats=LISTE_CANAUX))
    async def gestionnaire_en_direct(event):
        if event.photo:
            chat = await event.get_chat()
            nom_canal = chat.username if chat.username else "Nouveau"
            print(f"📸 Nouveau wallpaper détecté en direct sur @{nom_canal} !")
            
            w_list = charger_fonds_existants()
            current_max = max([w['id'] for w in w_list], default=0)
            await ajouter_wallpaper_au_json(event.message, current_max, nom_canal)

    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
