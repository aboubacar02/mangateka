import os
from PIL import Image, ImageFilter, ImageEnhance

# Configuration des chemins d'accès automatiques sur ton PC
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Si ton dossier d'images s'appelle 'catalogues' ou 'images', ajuste le nom ici :
IMAGES_DIR = os.path.join(BASE_DIR, "catalogues") 

def debloat_and_upscale():
    print("🚀 Démarrage du traitement d'amélioration des images...")
    
    if not os.path.exists(IMAGES_DIR):
        print(f"❌ Dossier introuvable. Vérifie le chemin : {IMAGES_DIR}")
        return

    compteur = 0

    # Parcours complet de tes sous-dossiers (One_Piece, Naruto, Shanks...)
    for root, dirs, files in os.walk(IMAGES_DIR):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                chemin_image = os.path.join(root, file)
                print(f"🔄 Amélioration de : {file}...")

                try:
                    # 1. Ouverture de l'image originale
                    with Image.open(chemin_image) as img:
                        # Convertir en RGB si c'est un format spécial pour éviter les bugs
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                        
                        # 2. Upscale : On multiplie la taille actuelle par 3 (Idéal pour la HD sur PC)
                        largeur, hauteur = img.size
                        nouvelle_image = img.resize((largeur * 3, hauteur * 3), Image.Resampling.LANCZOS)
                        
                        # 3. Supprimer le flou : On applique un filtre d'accentuation des contours
                        nouvelle_image = nouvelle_image.filter(ImageFilter.SHARPEN)
                        nouvelle_image = nouvelle_image.filter(ImageFilter.DETAIL)
                        
                        # 4. Booster les détails : Augmenter légèrement le contraste pour rendre le dessin manga plus "vif"
                        contraste = ImageEnhance.Contrast(nouvelle_image)
                        nouvelle_image = contraste.enhance(1.15) # +15% de contraste
                        
                        # Nettoyer les couleurs (saturation) pour un effet Premium
                        couleur = ImageEnhance.Color(nouvelle_image)
                        nouvelle_image = couleur.enhance(1.05)

                        # 5. Sauvegarde et remplacement de l'image floue
                        nouvelle_image.save(chemin_image, "JPEG", quality=95)
                        compteur += 1

                except Exception as e:
                    print(f"⚠️ Erreur sur le fichier {file} : {e}")

    print("\n✨ --- TRAITEMENT TERMINÉ --- ✨")
    print(f"✅ {compteur} images floues ont été agrandies et nettoyées avec succès !")
    print("🚀 Ton catalogue MangaFlux est prêt et totalement optimisé !")

if __name__ == "__main__":
    debloat_and_upscale()
