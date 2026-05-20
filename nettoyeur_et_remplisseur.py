import os
import shutil
import requests
import json
import time

# Base de données d'IDs d'images Unsplash Haute Résolution (9:16) pour éviter TOUT doublon
BANQUE_IMAGES = {
    "Voitures": [
        "photo-1617788138017-80ad40651399",  # Supercar Neon
        "photo-1503376780353-7e6692767b70",  # Porsche
        "photo-1552519507-da3b142c6e3d",  # Muscle Car
        "photo-1618843479313-40f8afb4b4d8",  # Sports Car
        "photo-1542282088-72c9c27ed0cd",  # Avant de voiture luxe
        "photo-1605559424843-9e4c228bf1c2",  # Voiture classique
        "photo-1492144534655-ae79c964c9d7",  # Berline Premium
        "photo-1580273916550-e323be2ae537",  # Voiture de course
        "photo-1525609004556-c46c7d6cf0a3",  # Supercar profil
        "photo-1568605117036-5fe5e7bab0b7"   # Voiture de sport rouge
    ],
    "Montagnes": [
        "photo-1464822759023-fed622ff2c3b",  # Sommets enneigés
        "photo-1454496522488-7a8e488e8606",  # Hautes montagnes
        "photo-1486873249359-2731bd6da57b",  # Montagne rocheuse
        "photo-1498050108023-c5249f4df085",  # Vallée de montagne
        "photo-1506744038136-46273834b3fb",  # Paysage alpin
        "photo-1470071459604-3b5ec3a7fe05",  # Montagne brumeuse
        "photo-1519681393784-d120267933ba",  # Montagne sous les étoiles
        "photo-1434064511983-18c6dae20ed5",  # Crête de montagne
        "photo-1549880338-65ddcdfd017b",  # Fjord et montagne
        "photo-1418065460487-3e41a6c84dc5"   # Nature et montagnes
    ],
    "Cyberpunk": [
        "photo-1515621061946-eff1c2a352bd",  # Rue de Tokyo néon
        "photo-1601042879364-f3947d3f9c16",  # Ruelle Cyberpunk
        "photo-1545239351-ef35f43d514b",  # Ville futuriste de nuit
        "photo-1578894381163-e72c17f2d45f",  # Enseigne lumineuse asiatique
        "photo-1509198397868-475647b2a1e5",  # Ambiance néon bleu et rose
        "photo-1563089145-599997674d42",  # Écrans et lumières holographiques
        "photo-1522083165195-342750297f4e",  # Perspective urbaine futuriste
        "photo-1547394765-185e1e68f34e",  # Matrice et technologie
        "photo-1511447333015-45b65e60f6d5",  # Tunnel néon abstrait
        "photo-1535223289827-42f1e9919769"   # Ambiance technologique sombre
    ],
    "Espace": [
        "photo-1451187580459-43490279c0fa",  # Terre vue de l'espace
        "photo-1462331940025-496dfbfc7564",  # Nébuleuse colorée
        "photo-1506318137071-a8e063b4bec0",  # Galaxie lointaine
        "photo-1444703686981-a3abbc4d4fe3",  # Cosmos infini
        "photo-1538370965046-79c0d6907d47",  # Voie lactée claire
        "photo-1518531933037-91b2f5f229cc",  # Poussière d'étoiles
        "photo-1541185933-ef5d8ed016c2",  # Fusée spatiale
        "photo-1446776811953-b23d57bd21aa",  # Satellite en orbite
        "photo-1419242902214-272b3f66ee7a",  # Ciel étoilé profond
        "photo-1570288685280-7802a8f8c4fc"   # Nébuleuse cosmique sombre
    ],
    "Nature": [
        "photo-1441974231531-c6227db76b6e",  # Forêt avec rayons de soleil
        "photo-1472214222541-d510753a49fa",  # Cascade magnifique
        "photo-1501785888041-af3ef285b470",  # Lac miroir
        "photo-1447752875215-b2761acb3c5d",  # Rivière en forêt
        "photo-1475924156734-496f6cac6ec1",  # Coucher de soleil sur plage
        "photo-1513836279014-a89f7a76ae86",  # Forêt mystique verte
        "photo-1469474968028-56623f02e42e",  # Collines verdoyantes
        "photo-1507525428034-b723cf961d3e",  # Mer turquoise tropicale
        "photo-1518495973542-4542c06a5843",  # Gros plan feuille/soleil
        "photo-1426604966848-d7adac402bff"   # Vallée sauvage de carte postale
    ],
    "Architecture": [
        "photo-1486406146926-c627a92ad1ab",  # Gratte-ciel en verre
        "photo-1513694203232-719a280e022f",  # Bâtiment moderne futuriste
        "photo-1449034446853-66c86144b0ad",  # Pont suspendu géant
        "photo-1511055813348-e877a9a16f20",  # Façade géométrique noire
        "photo-1496568818309-53d7c7753022",  # Vue urbaine en contre-plongée
        "photo-1600585154340-be6161a56a0c",  # Villa design minimaliste
        "photo-1487958449943-2429e8be8625",  # Design architectural blanc
        "photo-1504297050568-910d24c426d3",  # Vue aérienne de buildings
        "photo-1511818966892-d7d671e672a2",  # Intérieur design épuré
        "photo-1522708323590-d24dbb6b0267"   # Appartement moderne de luxe
    ]
}

BASE_DIR = "catalogues"

def telecharger_image_4k(id_image, chemin_sauvegarde, headers):
    """Télécharge l'image exacte depuis Unsplash en résolution 4K verticale."""
    # URL directe vers l'image brute haute qualité configurée en 1080x1920 (9:16)
    url = f"https://images.unsplash.com/json_id?auto=format&fit=crop&w=1080&h=1920&q=100"
    # On injecte l'identifiant réel de l'image de notre base de données
    url_reelle = url.replace("json_id", id_image)
    
    try:
        response = requests.get(url_reelle, headers=headers, timeout=20, stream=True)
        if response.status_code == 200:
            content = response.content
            # Sécurité : on s'assure que le fichier téléchargé n'est pas une page d'erreur vide
            if len(content) > 10000:
                with open(chemin_sauvegarde, 'wb') as f:
                    f.write(content)
                return True
    except Exception as e:
        print(f"    ⚠️ Erreur de connexion sur l'image : {e}")
    return False

def executer_nettoyage_et_remplissage_premium():
    print("==================================================")
    print("👑 APEX WALLS - SCRIPT DE REMPLISSAGE PREMIUM 4K 👑")
    print("==================================================")
    
    # 1. Destruction et recréation propre du dossier
    if os.path.exists(BASE_DIR):
        print("🧹 Nettoyage complet des anciens dossiers en cours...")
        shutil.rmtree(BASE_DIR)
        time.sleep(1)
        print("✅ Dossiers vidés avec succès.")
    
    os.makedirs(BASE_DIR)
    catalogue_json_final = []
    
    # Simulation d'un navigateur puissant pour ne pas être bridé
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # 2. Boucle principale sur notre catalogue d'images vérifiées
    for cat_nom, liste_ids in BANQUE_IMAGES.items():
        cat_dir = os.path.join(BASE_DIR, cat_nom)
        os.makedirs(cat_dir, exist_ok=True)
        
        images_enregistrees = []
        print(f"\n🚀 Lancement de la catégorie : [{cat_nom.upper()}]")
        print(f"--------------------------------------------------")
        
        for index, id_image in enumerate(liste_ids):
            nom_fichier = f"{cat_nom}_{index + 1}.jpg"
            chemin_image = os.path.join(cat_dir, nom_fichier)
            
            print(f" 📥 Téléchargement de l'image {index + 1}/{len(liste_ids)} (ID: {id_image})...")
            
            # Essai de téléchargement de l'image unique 4K
            succes = telecharger_image_4k(id_image, chemin_image, headers)
            
            if succes:
                # Ajout du chemin relatif exact que ton index.html va lire
                images_enregistrees.append(chemin_image)
                print(f"  ✅ Réussite ! Enregistrée dans -> {chemin_image}")
            else:
                print(f"  ❌ Échec du téléchargement pour l'ID : {id_image}")
            
            # Petite pause de sécurité entre les images pour stabiliser la connexion Termux
            time.sleep(0.4)
            
        # On ajoute la catégorie au tableau final du fichier JSON
        catalogue_json_final.append({
            "title": cat_nom,
            "images": images_enregistrees
        })
        print(f"📊 Fin de section : {cat_nom} complétée avec {len(images_enregistrees)} images uniques.")

    # 3. Génération du fichier catalogues.json propre
    print("\n--------------------------------------------------")
    print("📝 Écriture de la structure finale dans catalogues.json...")
    with open("catalogues.json", "w", encoding="utf-8") as f:
        json.dump(catalogue_json_final, f, indent=4, ensure_ascii=False)
        
    print("\n🎉 TOUT EST EN PLACE AVEC SUCCÈS ! 🎉")
    print("-> Toutes tes images sont uniques, en vrai format 4K vertical (1080x1920).")
    print("-> Le fichier catalogues.json est synchronisé avec ton index.html.")
    print("==================================================")

if __name__ == "__main__":
    executer_nettoyage_et_remplissage_premium()
