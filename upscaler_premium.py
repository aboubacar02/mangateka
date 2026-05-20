import os
from PIL import Image, ImageFilter, ImageEnhance

# Localisation automatique dans le dossier Mangateka de ton PC
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# On cible le dossier 'catalogues' que l'on voit sur tes captures d'écran
TARGET_DIR = os.path.join(BASE_DIR, "catalogues")

def upscale_manga_flux():
    print("✨ [MangaFlux] Initialisation de l'Upscaler HD/4K...")
    
    if not os.path.exists(TARGET_DIR):
        print(f"❌ Erreur : Le dossier '{TARGET_DIR}' n'existe pas.")
        print("Vérifie que le script est bien placé dans 'Mangateka' à côté du dossier 'catalogues'.")
        return

    images_traitees = 0

    # On scanne tous les sous-dossiers (Shonen, Seinen, et les dossiers de mangas)
    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                file_path = os.path.join(root, file)
                print(f"🔄 Traitement et défloutage de : {file}")

                try:
                    with Image.open(file_path) as img:
                        # Évite les crashs si l'image utilise un espace couleur bizarre
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                        
                        # 1. UPSCALING multiplier par 3 la taille d'origine avec l'algo Lanczos (très propre pour l'anime)
                        width, height = img.size
                        img_resized = img.resize((width * 3, height * 3), Image.Resampling.LANCZOS)
                        
                        # 2. DÉFLOUTAGE AUTOMATIQUE (Accentuation forte des tracés et contours manga)
                        img_sharp = img_resized.filter(ImageFilter.SHARPEN)
                        img_sharp = img_sharp.filter(ImageFilter.DETAIL)
                        
                        # 3. AJUSTEMENT PREMIUM (Léger boost du contraste pour détacher les noirs)
                        contrast_enhancer = ImageEnhance.Contrast(img_sharp)
                        img_final = contrast_enhancer.enhance(1.12) # +12% de contraste
                        
                        # 4. Remplacement direct de l'image d'origine
                        img_final.save(file_path, "JPEG", quality=95)
                        images_traitees += 1
                        
                except Exception as e:
                    print(f"⚠️ Impossible de traiter le fichier {file} : {e}")

    print("\n--- ✅ PROCESSUS TERMINÉ ---")
    print(f"🚀 {images_traitees} images ont été nettoyées, défloutées et converties en Haute Définition !")

if __name__ == "__main__":
    upscale_manga_flux()
