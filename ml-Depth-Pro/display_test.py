import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Charger l'image PNG
img = mpimg.imread('/Users/eleonore/MLDepthLayers/ml-Depth-Pro/input/images/Le Syrphe Origine.png')  # Remplace par le chemin de ton fichier

# Afficher l'image
plt.imshow(img)       # imshow gère les couleurs automatiquement
plt.axis('off')       # Optionnel : pour ne pas afficher les axes
plt.show()
