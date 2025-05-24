# Map

## Présentation
fichier Map : contient de multiples méthodes permettant la gestion d'une map en 2d avec pygame.  
si le fichier Map est lancé directement, lance un logiciel de création de map

## Dépendances

voir requirements.txt

## Comment utiliser

### Map :  
les différentes méthodes utilisables sont :  
- map.charger_map() pour charger le fichier de sauvegarde de la map (le dossier de tiles utilisé lors de la création de la map avec le logiciel intégré doit être présent avec le même chemin).
- map.set_dimensions() pour définir les dimensions d'affichage de la map (pour l'optimisation) les dimensions ne modifient en aucun cas les dimensions des tiles, elles sont seulement utilisées pour éviter d'afficher l'intégralité des tiles de la map à chaque fois (optimisation) la largeur et la hauteur partent du (0,0), c'est à dire que le rectangle créé grâce aux dimensions se situera en haut à gauche de l'écran.
- map.get_dimensions()
- map.set_camera_pos() pour définir l'emplacement de la caméra (agit comme un sprite, c'est-à-dire qu'il va vers la droite quand x augmente, et vers le bas quand y augmente).
- map.get_camera_pos()
- map.render() pour blit la map selon l'emplacement de la caméra.
- map.maj_map_image() à exécuter si une tile non animée a changé d'emplacement ou de visibilité. Si cette méthode n'est pas exécutée, le visuel ne changera pas (pas d'incidence sur les rects).
- tous les get_truc_on_screen pour obtenir les tiles qu'on voit sur l'écran (se met à jour lors de l'utilisation de map.render())
- tous les get_all_truc pour obtenir toutes les tiles.
- tous les get précédemment cités renvoient des listes de Tile (voir le fichier concerné pour voir ce qu'il est possible de faire).
- map.is_on_screen(), qui permet de savoir si la tile est dans le champs de la caméra.
- map.update_rect_pos(), qui permet de décaler la position du rect passé en paramètre après un render() pour donner l'illusion que celui-ci n'a pas bougé.  
          ATTENTION : cette méthode ne doit être utilisé qu'une seule fois par sprite par render (si utilisé plusieurs fois, le décalage se fera plusieurs fois)

Les autres méthodes ne sont pas à utiliser.
  
### Tile :  
Les tiles sont les éléments qui composent la map (les méthodes get_all_truc et get_truc_on_screen de Map retournent des listes de Tile).  
les différentes méthodes utilisables sont :  
- Tile.get_id() et Tile.set_id() pour avoir et définir l'id de la tile.  
  l'id par défaut de la tile est l'id défini dans le mapmaker.
- Tile.set_visible() et get_visible() pour activer, désactiver ou obtenir le fait que la tile soit affichée lors de Map.render().  
Si la tile est invisible, elle ne sera pas dans Map.get_tiles_on_screen, mais elle sera dans get_all_tiles() et get_invisible_tiles().  
Attention : dans la classe Map, self.visible n'est pas sauvegardé, lors du lancement de la map, toutes les tiles seront visibles (sauf les spawn points et les event points).
- get_tile_rect() qui permet d'avoir le rect de la tile, si elle est animée, le rect est celle de la frame actuelle.
Se met à jour avec set_frame(), next_frame(), previous_frame() et Map.render().  
- Tile.get_co() et Tile.get_co_base(), je ne conseille pas vraiment de les utiliser parce que c'est compliqué, mais en gros:  
get_co_base() fait référence aux coordonnées de la tile sur la map si on ne prend pas en compte la caméra.  
get_co() fait référence aux coordonnées d'affichage de la tile sur l'écran (en prenant en compte la caméra), cette méthode se met à jour avec Map.render().  
  
dans le cas d'une tile animée :
- Tile.get_animated pour savoir si la tile est animée ou pas.
- Tile.get_actual_frame() qui retourne l'indice de la frame actuelle (0 pour la première frame).
- Tile.next_frame() pour passer à la frame suivante lors de Map.render(), le rect sera mis à jour.
- Tile.previous_frame() pour passer à la frame précédente lors de Map.render(), le rect sera mis à jour.
- Tile.set_frame() pour passer à la frame d'indice passé en paramètre lors de Map.render(), le rect sera mis à jour.

le reste des méthodes de Tile nécessaires pour la classe Map, et ne doivent pas être utilisées.
