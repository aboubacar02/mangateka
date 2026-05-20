import os
import json

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

def verifier():
    print("\n🔍 [MANGATEKA] Analyse approfondie des catalogues (Vides ou Incomplets)...\n")
    incomplets = []
    
    for manga in MANGAS_ATTENDUS:
        nom_fichier = f"catalogues/{manga.lower().replace(' ', '_').replace('.', '_')}.json"
        
        # 1. Si le fichier n'existe pas du tout
        if not os.path.exists(nom_fichier):
            incomplets.append((manga, 0, "Fichier manquant"))
            continue
            
        # 2. Si le fichier existe, on regarde ce qu'il a dans le ventre
        try:
            with open(nom_fichier, "r", encoding="utf-8") as f:
                data = json.load(f)
                nb_images = len(data)
                
                # Si le catalogue a moins de 150 images, on considère qu'il est incomplet
                if nb_images < 150:
                    incomplets.append((manga, nb_images, f"Seulement {nb_images} images"))
        except Exception:
            incomplets.append((manga, 0, "Fichier corrompu/vide"))

    if incomplets:
        print(f"⚠️ {len(incomplets)} MANGAS À COMPLÉTER AVEC UNE AUTRE API :")
        print("=" * 60)
        print(f"{'Nom du Manga':<30} | {'Images récupérées':<25}")
        print("-" * 60)
        for i, (m, nb, statut) in enumerate(incomplets, 1):
            print(f"[{i:02d}] {m:<25} | {statut}")
        print("=" * 60)
        print("\n📸 Fais une capture d'écran de cette liste et envoie-la moi !")
    else:
        print("🏆 Parfait ! Tous tes catalogues sont blindés d'images !")

if __name__ == "__main__":
    verifier()
