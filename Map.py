import pygame
import os
from Tile import Tile
import sys
class Map:
    """
    inclus un logiciel de création de map, et des commandes utiles pour l'utilisation de la map dans un jeu
    utilisation lors de la création de jeu :
        - map.charger_map() pour charger le fichier de sauvegarde de la map (le dossier de tiles utilisé doit être présent avec le même chemin)
        - map.set_dimensions() pour définir les dimensions d'affichage de la map (pour l'optimisation)
          les dimensions ne modifient en aucun cas les dimensions des tiles, elles sont seulement utilisées pour éviter d'afficher l'intégralité des tiles de la map à chaque fois (optimisation)
          la largeur et la hauteur partent du (0,0), c'est à dire que le rectangle créé grâce aux dimensions se situera en haut à gauche de l'écran
        - map.get_dimensions()
        - map.set_camera_pos() pour définir l'emplacement de la caméra (agit comme un sprite, c'est-à-dire qu'il va vers la droite quand x augmente, et vers le bas quand y augmente)
        - map.get_camera_pos()
        - map.render() pour blit la map selon l'emplacement de la caméra
        - map.maj_map_image() à exécuter si une tile non animée a changé d'emplacement ou de visibilité
          si cette méthode n'est pas exécutée, le visuel ne changera pas (pas d'incidence sur les rects)
        - tous les get_truc_on_screen pour obtenir les tiles qu'on voit sur l'écran (se met à jour lors de l'utilisation de map.render())
        - tous les get_all_truc pour obtenir toutes les tiles
        - tous les get précédemment cités renvoient des listes de Tile (voir le fichier concerné pour voir ce qu'il est possible de faire)
        - map.is_on_screen(), qui permet de savoir si la tile est dans le champs de la caméra
        - map.update_rect_pos(), qui permet de décaler la position du rect passé en paramètre après un render() pour donner l'illusion que celui-ci n'a pas bougé
          ATTENTION : cette méthode ne doit être utilisé qu'une seule fois par sprite par render (si utilisé plusieurs fois, le décalage se fera plusieurs fois)
        les autres méthodes ne sont pas à utiliser
    """
    def __init__(self, dimensions=None):
        self.__camera_x = 0
        self.__camera_y = 0
        self.__previous_camera_x = 0    # camera_x de l'ancien render(), permet de calculer la distance pour update_rect_pos()
        self.__previous_camera_y = 0
        pygame.font.init()
        self.police = pygame.font.SysFont("arial", 50, True)    # police du mapmaker
        self.tiles_on_screen = []  # ensemble des rects dans le champs (se met à jour avec render()) sans les spawn et events
        self.spawn_points_on_screen = [] # pareil mais pour les spawn_points
        self.event_points_on_screen = [] # pareil mais pour les event_points
        self.invisible_tiles = []    # ensemble des tiles invisibles (sans les spawn et events)
        self.is_map_maker = False # définit si les spawn et events doivent être affichés
        self.surface_map = None   # contient la surface qui est blitée sur le screen lors du render
        self.decalage_negatif = (0, 0)  # décalage qui permet de prendre en compte des tiles avec des coordonnées négatives pour surface_map

        if type(dimensions) == tuple:
            self.largeur = dimensions[0]
            self.hauteur = dimensions[1]
        else:
            self.largeur = None  # largeur de l'affichage, utilisé pour l'optimisation
            self.hauteur = None  # pareil, mais pour la hauteur

        # à sauvegarder
        self.chemin_dossier = ""    # dossier qui mène aux png des tiles
        self.background = "black"
        self.map = []   # ensemble des éléments dans la map, contenant des tiles (les tiles sont chargées selon l'ordre de la liste)
        self.spawn_points = []  # ensemble des spawn_points de la map
        self.event_points = [] # ensemble des event_points de la map

    def set_camera_pos(self, pos:tuple):
        assert type(pos) == tuple, "pos doit être un tuple"
        assert type(pos[0]) == int and type(pos[1]) == int, "les éléments de pos doivent être des entiers"
        self.__camera_x = pos[0]
        self.__camera_y = pos[1]

    def get_camera_pos(self):
        return (self.__camera_x, self.__camera_y)

    def set_dimensions(self, dimensions):
        assert type(dimensions) == tuple, "dimensions doit être un tuple"
        self.largeur = dimensions[0]
        self.hauteur = dimensions[1]
    def get_dimensions(self):
        return (self.largeur, self.hauteur)

    def get_tiles_on_screen(self):
        """
        retourne une liste contenant toutes les tiles (sauf spawn et event) affichés à l'écran (ce qui signifie qu'ils sont dans le champs)
        la liste retournée est celle de la dernière fois où la méthode render() a été appelée
        (en gros ça veut dire que pour mettre à jour la liste retournée, il faut appeller render())
        """
        return list(self.tiles_on_screen)

    def get_all_tiles(self):
        """
        retourne une liste contenant toutes les tiles (sauf spawn et event) de la map (même ceux hors champs)
        """
        return list(self.map)

    def get_spawn_points_on_screen(self):
        """
        retourne une liste contenant toutes les tiles spawn_points affichés à l'écran (ce qui signifie qu'ils sont dans le champs)
        la liste retournée est celle de la dernière fois où la méthode render() a été appelée
        (en gros ça veut dire que pour mettre à jour la liste retournée, il faut appeller render())
        """
        return list(self.spawn_points_on_screen)

    def get_all_spawn_points(self):
        """
        retourne une liste contenant toutes les tiles spawn_points de la map (même ceux hors champs)
        """
        return list(self.spawn_points)

    def get_event_points_on_screen(self):
        """
        retourne une liste contenant toutes les tiles event_points affichés à l'écran (ce qui signifie qu'ils sont dans le champs)
        la liste retournée est celle de la dernière fois où la méthode render() a été appelée
        (en gros ça veut dire que pour mettre à jour la liste retournée, il faut appeller render())
        """
        return list(self.event_points_on_screen)

    def get_all_event_points(self):
        """
        retourne une liste contenant toutes les tiles event_points de la map (même ceux hors champs)
        """
        return list(self.event_points)

    def get_invisible_tiles(self):
        """
        retourne toutes les tiles qui ne sont pas affichées (qui ont leur attribut self.visible à False)
        ne prend pas en compte les event_points et les spawn_points
        la liste retournée est celle de la dernière fois où la méthode render() a été appelée
        (en gros ça veut dire que pour mettre à jour la liste retournée, il faut appeller render())
        """
        return list(self.invisible_tiles)

    def __add_tile(self, tile:Tile, type_tile:str, fin=True):
        """
        ajoute un tile à la fin de self.map (premier plan)
        si fin = False, la tile sera mise au début (dernier plan)
        le type est soit basique, soit spawn, soit event : il permet de savoir dans quelle liste il faut mettre la tile
        """
        assert type(tile) == Tile, "tile doit être un objet Tile"
        assert type_tile == "basique" or type_tile == "spawn" or type_tile == "event", "type_tile invalide"
        liste_a_modifier = None # mini effet de bord
        if type_tile == "basique":
            liste_a_modifier = self.map
        elif type_tile == "spawn":
            liste_a_modifier = self.spawn_points
        elif type_tile == "event":
            liste_a_modifier = self.event_points
        else:
            print("problème avec le type")
        if fin:
            liste_a_modifier.append(tile)
        else:
            liste_a_modifier.insert(0, tile)

    def __remove_tile(self, tile:Tile, type_tile:str):
        """
        enlève la tile passé en paramètre
        il ne doit pas y avoir deux fois la même instance dans les listes (2 tiles pareilles = 2 instances différentes)
        le type est soit basique, soit spawn, soit event : il permet de savoir dans quelle liste il faut chercher la tile
        """
        assert type(tile) == Tile, "tile doit être un objet Tile"
        assert type_tile == "basique" or type_tile == "spawn" or type_tile == "event", "type_tile invalide"
        liste_a_modifier = None  # mini effet de bord
        if type_tile == "basique":
            liste_a_modifier = self.map
        elif type_tile == "spawn":
            liste_a_modifier = self.spawn_points
        elif type_tile == "event":
            liste_a_modifier = self.event_points
        else:
            print("problème avec le type")
        if tile in liste_a_modifier:
            liste_a_modifier.remove(tile)

    def __charge_tile(self, dossier):
        """
        crée une tile par image dans le dossier self.chemin_dossier
        ATTENTION : les tiles ne sont pas triées (sauf tiles animées)
        ordre des listes dossiers = ordre des noms de dossier
        les dossiers ne doivent pas avoir de . dans leur nom
        les images sont en png ou jpg
        """
        assert dossier[len(dossier)-1] == "/", "la destination doit se terminer par un /"
        tiles_charge = []
        for tile in os.listdir(dossier):
            if tile[len(tile)-4:] == ".png" or tile[len(tile)-4:] == ".jpg":
                # image de base
                instance_tile = Tile()
                instance_tile.chemin_image = dossier + tile
                instance_tile.charger_image()
                tiles_charge.append(instance_tile)

            elif not "." in tile:
                # dossier
                instance_tile = Tile()
                instance_tile.chemin_image = []
                for element in os.listdir(dossier + tile + "/"):
                    instance_tile.chemin_image.append(dossier + tile + "/" + element)
                instance_tile.charger_image()
                tiles_charge.append(instance_tile)

            else:
                print(str(tile) + " inconnu")
        return tiles_charge

    def __create_button(self, screen, text, co:tuple):
        """
        crée un bouton, le blit, et renvoie le rect du bouton
        """
        text_button = self.police.render(text, True, "white")
        text_button_rect = text_button.get_rect()
        text_button_rect.update(co[0], co[1], text_button_rect.width + 20, text_button_rect.height + 20)
        pygame.draw.rect(screen, "grey", text_button_rect)
        screen.blit(text_button, (text_button_rect.x + 10, text_button_rect.y + 10))
        return text_button_rect

    def __get_quadrillage_rect(self, espacement_x, espacement_y) -> pygame.Rect:
        """
        crée des carrés selon l'espacement, puis retourne le carré où se trouve la souris
        ATTENTION : si l'espacement est très bas, cette fonction va prendre beaucoup de temps
        """
        # calcul du décalage par rapport au (0,0)
        depart_x = self.__camera_x *-1    # si la camera est à x = 3 et y = 4, alors le vrai (0,0) se trouve en (-3, -4)
        depart_y = self.__camera_y *-1
            # gauche vers droite
        while not depart_x + espacement_x >= 0:
            depart_x = depart_x + espacement_x
        while not depart_y + espacement_y >= 0:
            depart_y = depart_y + espacement_y

            # droite vers gauche
        while depart_x + espacement_x >= 0:
            depart_x = depart_x - espacement_x
        while depart_y + espacement_y >= 0:
            depart_y = depart_y - espacement_y

        # calcul du rect dans lequel la souris est positionnée
        x = depart_x
        y = depart_y
        resultat = None
        while x <= 1920 and y <= 1080:
            rect = pygame.rect.Rect((x,y), (espacement_x, espacement_y))
            if rect.collidepoint(pygame.mouse.get_pos()):
                return rect
            else:
                x = x + espacement_x
                if x > 1920:
                    x = depart_x
                    y = y + espacement_y

    def __get_colors_allowed(self):
        """
        retourne la liste des couleurs str que pygame comprend
        """
        colors = []
        for couleur in pygame.colordict.THECOLORS.keys():
            colors.append(couleur)
        return colors

    # fonctions position tile
    def is_on_screen(self, tile:Tile):
        """
        détermine si la tile est dans le champs de la caméra
        """
        temp_rect = tile.cloner()
        position_x = tile.x_base - self.__camera_x  # en supposant que la caméra agit comme un sprite (positif quand on va vers la droite ou le bas)
        position_y = tile.y_base - self.__camera_y
        temp_rect.x = position_x
        temp_rect.y = position_y
        temp_rect.maj_rect()
        return temp_rect.get_tile_rect().colliderect(pygame.rect.Rect((0, 0), (self.largeur, self.hauteur)))    # coordonnées de base : (0,0)

    def __move_selon_camera(self,tile:Tile):
        """
        déplace la tile en paramètre selon la position de la caméra
        met à jour x, y (autrement get_co()) et le rect (autrement dit get_tile_rect()) du tile
        """
        tile.x = tile.x_base - self.__camera_x
        tile.y = tile.y_base - self.__camera_y
        tile.maj_rect()
    # fin fonctions position tile

    def __save(self, nom_fichier):
        """
        sauvegarde la map dans un fichier txt
        la sauvegarde est organisée de la manière suivante : chemin_dossier, background, [tiles], [spawn_points], [event_points]
        les différents éléments ne doivent pas contenir :
            - &slinfos&
            - &sltile&
            - &slanimation&
            - &slnewtile&
            - &sltype&
        """
        # première partie de la save : les infos de la map
        text_save = str(self.chemin_dossier) + "&slinfos&" + str(self.background) + "&sltype&"
        # deuxième partie de la save : les différentes tiles
        # tiles basiques
        have_tiles = False
        for tile in self.get_all_tiles():   # attention, les tiles peuvent être animées
            pygame.event.get()      # anti ne répond pas
            have_tiles = True
            # gestion des chemins des images
            chemin_image_tile = ""
            if type(tile.chemin_image) == list:
                for chemin in tile.chemin_image:
                    chemin_image_tile = chemin_image_tile + chemin + "&slanimation&"
                chemin_image_tile = chemin_image_tile[:len(chemin_image_tile)-13]    # enlever le &slanimation& de fin
            else:
                chemin_image_tile = tile.chemin_image

            # création du texte
            # texte de la forme id,x_base,y_base,animated,proportion,chemin_image : séparé par &sltile&
            text_infos_tile_basique = str(tile.id) + "&sltile&" + str(tile.x_base) + "&sltile&" + str(tile.y_base) + "&sltile&" + str(tile.animated) + "&sltile&" + str(tile.proportion) + "&sltile&" + chemin_image_tile + "&slnewtile&"
            text_save = text_save + text_infos_tile_basique
        if have_tiles:
            text_save = text_save[:len(text_save)-11]
        text_save = text_save + "&sltype&"

        # spawn points
        have_spawn_points = False
        for tile in self.get_all_spawn_points():
            pygame.event.get()  # anti ne répond pas
            have_spawn_points = True
            # texte de la forme id,x_base,y_base,largeur,hauteur : séparé par &sltile&
            text_save = text_save + str(tile.id) + "&sltile&" + str(tile.x_base) + "&sltile&" + str(tile.y_base) + "&sltile&" + str(tile.get_tile_rect().width) + "&sltile&" + str(tile.get_tile_rect().height) + "&slnewtile&"
        if have_spawn_points:
            text_save = text_save[:len(text_save)-11]
        text_save = text_save + "&sltype&"

        # event points
        have_event_points = False
        for tile in self.get_all_event_points():
            pygame.event.get()  # anti ne répond pas
            have_event_points = True
            text_save = text_save + str(tile.id) + "&sltile&" + str(tile.x_base) + "&sltile&" + str(tile.y_base) + "&sltile&" + str(tile.get_tile_rect().width) + "&sltile&" + str(tile.get_tile_rect().height) + "&slnewtile&"
        if have_event_points:
            text_save = text_save[:len(text_save) - 11] # enlever le &slnewtile& en trop

        # écriture dans le fichier
        fichier_save = open(nom_fichier, "w")
        fichier_save.write(text_save)
        fichier_save.close()

    def __str_to_bool(self, texte:str) -> bool:
        if texte == "True":
            return True
        else:
            return False

    def maj_map_image(self):
        """
        les tiles qui ne sont pas animées sont blitées sur une grande surface, qui sera tout le temps blitée sur le screen
        si la position ou la visibilité d'une tile est modifiée, cette méthode doit être appellée, sinon le visuel ne changera pas
        """
        # calcul des dimensions de la map
        largeur_max = float("inf") * -1
        hauteur_max = float("inf") * -1
        if len(self.map) == 0:
            largeur_max = 1
            hauteur_max = 1
        for tile in self.map:
            #print(not tile.get_animated,  tile.get_visible())
            if not tile.get_animated() and tile.get_visible():
                if tile.get_co_base()[0] + tile.image.get_size()[0] > largeur_max:
                    largeur_max = tile.get_co_base()[0] + tile.image.get_size()[0]

                if tile.get_co_base()[1] + tile.image.get_size()[1] > hauteur_max:
                    hauteur_max = tile.get_co_base()[1] + tile.image.get_size()[1]

        largeur_min = float("inf")
        hauteur_min = float("inf")
        for tile in self.map:
            if not tile.get_animated() and tile.get_visible():
                #print("tile", tile.get_co_base(), tile.get_co_base()[0] < largeur_min)
                if tile.get_co_base()[0]< largeur_min:
                    largeur_min = tile.get_co_base()[0]

                if tile.get_co_base()[1] < hauteur_min:
                    hauteur_min = tile.get_co_base()[1]


        #print("a", largeur_min, hauteur_min)
        if largeur_min < 0:
            largeur_max = largeur_max + abs(largeur_min)
            self.decalage_negatif = (abs(largeur_min), 0)
            largeur_min = 0

        if hauteur_min < 0:
            hauteur_max = hauteur_max + abs(hauteur_min)
            self.decalage_negatif = (self.decalage_negatif[0], abs(hauteur_min))
            hauteur_min = 0

        #print((largeur_max, hauteur_max))

        self.surface_map = pygame.surface.Surface((largeur_max, hauteur_max), pygame.SRCALPHA) # SRCALPHA pour la transparence

        # blit des éléments sur la surface
        for tile in self.map:
            if not tile.get_animated() and tile.get_visible():
                #print("cos", (tile.get_co_base()[0] + self.decalage_negatif[0], tile.get_co_base()[1] + self.decalage_negatif[1]))
                self.surface_map.blit(tile.image, (tile.get_co_base()[0] + self.decalage_negatif[0], tile.get_co_base()[1] + self.decalage_negatif[1]))


    def charger_map(self, nom_fichier):
        """
        lit le fichier, et charge les attributs pour que la map soit prête à l'emploi
        met également la caméra à (0,0)
        """
        self.map = []
        self.spawn_points = []
        self.event_points = []
        self.__camera_x = 0
        self.__camera_y = 0
        self.__previous_camera_x = 0
        self.__previous_camera_y = 0
        fichier_save = open(nom_fichier, "r")
        text_save = fichier_save.read()
        fichier_save.close()
        # découpage du txt_save

        liste_save = text_save.split("&sltype&")
        # infos
        infos = liste_save[0].split("&slinfos&")
        self.chemin_dossier = infos[0]
        self.background = infos[1]

        # tiles basiques
        tiles_basiques = liste_save[1]
        # texte de la forme id,x_base,y_base,animated,proportion,chemin_image : séparé par &sltile&
        if not tiles_basiques.split("&slnewtile&")[0] == "":  # au cas où il n'y a pas de tile
            for tile_str in tiles_basiques.split("&slnewtile&"):
                pygame.event.get()  # anti ne répond pas
                attributs_tile = tile_str.split("&sltile&")
                new_tile = Tile()
                new_tile.id = attributs_tile[0]
                new_tile.x_base = int(attributs_tile[1])
                new_tile.y_base = int(attributs_tile[2])
                new_tile.animated = self.__str_to_bool(attributs_tile[3])
                new_tile.proportion = int(attributs_tile[4])
                # chemin_image (peut être animée)
                liste_chemins = attributs_tile[5].split("&slanimation&")
                if len(liste_chemins) == 1:
                    new_tile.chemin_image = liste_chemins[0]
                else:
                    new_tile.chemin_image = []
                    for chemin in liste_chemins:
                        new_tile.chemin_image.append(chemin)
                new_tile.charger_image()
                new_tile.maj_rect()
                self.map.append(new_tile)
        self.maj_map_image()
        #print("truc image", self.surface_map)

        # spawn points
        tiles_spawn_points = liste_save[2]
        # texte de la forme id,x_base,y_base,largeur,hauteur : séparé par &sltile&
        if not tiles_spawn_points.split("&slnewtile&")[0] == "":    # au cas où il n'y a pas de tile
            for spawn_point_str in tiles_spawn_points.split("&slnewtile&"):
                pygame.event.get()  # anti ne répond pas
                attributs_spawn_point = spawn_point_str.split("&sltile&")
                new_spawn_point = Tile()
                new_spawn_point.id = attributs_spawn_point[0]
                new_spawn_point.x_base = int(attributs_spawn_point[1])
                new_spawn_point.y_base = int(attributs_spawn_point[2])
                new_spawn_point.chemin_image = "mapmaker_assets/spawn_point.png"
                new_spawn_point.charger_image(int(attributs_spawn_point[3]), int(attributs_spawn_point[4]))
                new_spawn_point.maj_rect()
                self.spawn_points.append(new_spawn_point)

        # event points
        tiles_event_points = liste_save[3]
        # texte de la forme id,x_base,y_base,largeur,hauteur : séparé par &sltile&
        if not tiles_event_points.split("&slnewtile&")[0] == "":  # au cas où il n'y a pas de tile
            for event_point_str in tiles_event_points.split("&slnewtile&"):
                pygame.event.get()  # anti ne répond pas
                attributs_event_point = event_point_str.split("&sltile&")
                new_event_point = Tile()
                new_event_point.id = attributs_event_point[0]
                new_event_point.x_base = int(attributs_event_point[1])
                new_event_point.y_base = int(attributs_event_point[2])
                new_event_point.chemin_image = "mapmaker_assets/event_point.png"
                new_event_point.charger_image(int(attributs_event_point[3]), int(attributs_event_point[4]))
                new_event_point.maj_rect()
                self.event_points.append(new_event_point)


    def render(self, screen):
        """
        blit la map de manière optimisée
        met à jour les méthodes get_tiles_on_screen(), get_event_points_on_screen() et get_spawn_points_on_screen(), ainsi que Tile.get_tile_rect() et Tile.get_co()
        pour fonctionner, cette méthode a besoin des trois listes avec des tiles avec ses cos de base, et avec l'image de chargée
        """
        self.__previous_camera_x = self.__camera_x
        self.__previous_camera_y = self.__camera_y

        self.tiles_on_screen = []
        self.event_points_on_screen = []
        self.spawn_points_on_screen = []
        self.invisible_tiles = []
        dimensions = self.get_dimensions()
        assert dimensions[0] != None and dimensions[1] != None, "les dimensions d'affichage de la map ne sont pas définies, définissez les avec set_dimensions()"
        if not self.background == "none":
            screen.fill(self.background)

        # tiles dans self.map
        # blit de surface_map
        assert self.surface_map != None, "la map n'est pas chargée"

        x_blit = self.__camera_x*-1 - self.decalage_negatif[0]
        y_blit = self.__camera_y*-1 - self.decalage_negatif[1]
        rect = pygame.rect.Rect(self.decalage_negatif[0]+self.__camera_x, self.decalage_negatif[1]+self.__camera_y, self.largeur, self.hauteur)
        screen.blit(self.surface_map, (0, 0), area=rect)
        for tile in self.map:
            # calcul de est-ce que la tile est dans le champs
            if tile.get_visible():
                if self.is_on_screen(tile):
                    # la tile est dans le champs, il faut donc la mettre dans tiles_on_screen
                    self.__move_selon_camera(tile)
                    self.tiles_on_screen.append(tile)

                    # on affiche la tile seulement si elle est animée
                    if tile.get_animated():
                        screen.blit(tile.image, (tile.get_co()))
            else:
                self.invisible_tiles.append(tile)

        # tiles dans spawn_points
        for tile in self.spawn_points:
            if self.is_on_screen(tile):
                self.__move_selon_camera(tile)
                self.spawn_points_on_screen.append(tile)
                if self.is_map_maker:
                    screen.blit(tile.image, (tile.get_co()))

        # tiles dans event_points
        for tile in self.event_points:
            if self.is_on_screen(tile):
                self.__move_selon_camera(tile)
                self.event_points_on_screen.append(tile)
                if self.is_map_maker:
                    screen.blit(tile.image, (tile.get_co()))

    def update_rect_pos(self, rect:pygame.rect.Rect):
        """
        décale la position du rect passé en paramètre après un render pour donner l'illusion que celui-ci n'a pas bougé
        cette méthode ne doit être utilisé qu'une seule fois par sprite par render (si utilisé plusieurs fois, le décalage se fera plusieurs fois)
        comme cette méthode utilise la caméra et le previous_camera, la valeur du décalage sera mis à jour avec render()
        """
        difference_x = self.__camera_x - self.__previous_camera_x
        difference_y = self.__camera_y - self.__previous_camera_y
        # si positif, la caméra s'est déplacée vers la droite/bas, c'est-à-dire que le sprite doit se décaler vers la gauche/haut
        if difference_x > 0:
            rect.x = rect.x - difference_x
        else:
            rect.x = rect.x + difference_x

        if difference_y > 0:
            rect.y = rect.y - difference_y
        else:
            rect.y = rect.y + difference_y
    def mapmaker(self):
        """
        les sous-dossiers dans lesquels il y a une tile animée ne doit pas contenir de .
        à ne pas utiliser dans le jeu, uniquement en ligne de commande
        permet de créer une map simplement
        tant que l'utilisateur n'aura pas utilisé le bouton espace pour changer l'espacement, l'espacement sera de 100*100 pixel, peu importe la proportion
        si l'utilisateur a utilisé le bouton espace et qu'il change la proportion, l'espacement sera modifié en conséquence
        les dimensions du spawn_point et de l'event_point sont toujours l'espacement (la proportion n'a aucun effet)
        au niveau de la proportion :
            1) si on essaye de charger une image avec une proportion de grande, ça va soit laguer, soit crash
            2) si on met un espacement très petit et qu'on charge une image, __get_quadrillage_rect va faire laguer
        """
        assert "mapmaker_assets" in os.listdir("."), "dossier mapmaker_assets introuvable"
        pygame.init()
        screen = pygame.display.set_mode((1920,1080))
        pygame.display.set_caption("map maker par JB")
        pygame.display.set_icon(pygame.transform.smoothscale(pygame.image.load("mapmaker_assets/logo.jpg"), (32, 32)))
        self.is_map_maker = True
        self.set_dimensions((1920-600, 1080))

        boucle_global = True
        fps = 60
        clock_global = pygame.time.Clock()
        y_offset_tile = 0
        quadrillage = True
        espacement_x = 100    # espacement au pif
        espacement_y = 100
        tile_espacement = None  # tile responsable de l'espacement
        changement_espacement = False
        proportion = 100    # en %
        id_text = ""
        tile_selectionee = None
        is_point = False    # détermine si la tile sélectionnée est un spawn_point ou un event_point
        type_point = ""     # détermine si la tile_selectionnée un spawn_point ou un event_point
        rects_tiles_collection = []
        tiles_affiche = []
        etoile = pygame.image.load("mapmaker_assets/etoile.png")
        pixel_rouge = pygame.image.load("mapmaker_assets/pixel rouge.png").convert_alpha()
        etoile = pygame.transform.scale(etoile, (20,20))
        shift_pressed = False
        tab_pressed = False
        right_click = False
        position_souris = None
        assistant_id = False

        # demande de où chercher les images
        clock_dossier = pygame.time.Clock()
        boucle_dossier = True
        chemin_dossier = ""
        while boucle_dossier:
            screen.fill((0,0,0))
            choix_utilisateur_btn = self.__create_button(screen, "choix : " + chemin_dossier, (10, 1080//2))
            chemin_dossier_btn = self.__create_button(screen, "entrez le chemin du dossier de tiles ou le chemin d'une save", (choix_utilisateur_btn.x, choix_utilisateur_btn.y - 10 - choix_utilisateur_btn.height))
            valider_dossier_btn = self.__create_button(screen, "charger dossier", (choix_utilisateur_btn.x, choix_utilisateur_btn.bottom + 10))
            charger_sauvegarde_btn = self.__create_button(screen, "charger sauvegarde", (valider_dossier_btn.right + 20, valider_dossier_btn.y))
            slash_btn = self.__create_button(screen, "/", (charger_sauvegarde_btn.right + 20, charger_sauvegarde_btn.y))
            point_btn = self.__create_button(screen, ".", (slash_btn.right + 20, slash_btn.y))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    boucle_dossier = False
                    boucle_global = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    touche = pygame.key.name(event.key)
                    if touche == "backspace" and len(chemin_dossier) > 0:
                        chemin_dossier = chemin_dossier[:len(chemin_dossier) - 1]
                    elif touche == "space":
                        chemin_dossier = chemin_dossier + " "
                    elif touche != "backspace" and len(touche) == 1 and len(chemin_dossier) < 60:
                        chemin_dossier = chemin_dossier + touche
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        if slash_btn.collidepoint(event.pos):
                            if len(chemin_dossier) < 60:
                                chemin_dossier = chemin_dossier + "/"
                        elif point_btn.collidepoint(event.pos):
                            if len(chemin_dossier) < 60:
                                chemin_dossier = chemin_dossier + "."
                        elif valider_dossier_btn.collidepoint(event.pos):
                            self.chemin_dossier = chemin_dossier
                            if self.chemin_dossier[len(self.chemin_dossier) - 1] != "/":
                                self.chemin_dossier = self.chemin_dossier + "/"
                            boucle_dossier = False
                        elif charger_sauvegarde_btn.collidepoint(event.pos):
                            if not chemin_dossier[len(chemin_dossier)-4:] == ".txt":  # chemin_dossier est un fichier txt
                                chemin_dossier = chemin_dossier + ".txt"
                            self.charger_map(chemin_dossier)
                            boucle_dossier = False
            clock_dossier.tick(fps)

        # chargement d'une surface vide
        self.maj_map_image()

        # chargement des tiles présents dans le dossier
        tiles = self.__charge_tile(self.chemin_dossier)

        # mise dans images_tiles du visuel des tiles (leur image en gros)
        images_tiles = []   # même ordre que tiles
        for tile in tiles:
            if type(tile.chemin_image) == list:
                images_tiles.append(tile.liste_frames[0])
            else:
                images_tiles.append(tile.image)

        charge_tile_selectionee = True
        while boucle_global:
            # fill fond noir si fond transparent
            screen.fill((0, 0, 0))

            # blit de la map
            self.render(screen)
            # ce qui suit n'est pas forcément optimisé (on pourrait le mettre directement dans render, mais dans tous les cas vu que c'est optimisé, normalement c'est pas la mort)
            # assistant id du mapmaker
            all_tiles_on_screen = self.get_tiles_on_screen() + self.get_spawn_points_on_screen() + self.get_event_points_on_screen()
            if assistant_id:
                for tile in all_tiles_on_screen:
                    if tile.get_id() == id_text:
                        carre_rouge = pygame.transform.scale(pixel_rouge, tile.get_tile_rect().size)
                        carre_rouge.set_alpha(128)
                        screen.blit(carre_rouge, (tile.get_tile_rect().x, tile.get_tile_rect().y))

            # affichage tile selectionnée au niveau de la souris
            if tile_selectionee != None:
                # mise à l'échelle de l'image, amélioration : faire en sorte que ça fasse cela quand c'est nécessaire, et pas tout le temps
                if charge_tile_selectionee:
                    tile_selectionee.proportion = proportion
                    if is_point:    # dimensions du spawn_point égales à l'espacement
                        tile_selectionee.charger_image(espacement_x, espacement_y)
                    else:
                        tile_selectionee.charger_image()
                    charge_tile_selectionee = False

                tile_image = tile_selectionee.image
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[0] < 1920 - 600:
                    if quadrillage:
                        quadrillage_rect = self.__get_quadrillage_rect(espacement_x, espacement_y)
                        x_affichage = quadrillage_rect.x
                        y_affichage = quadrillage_rect.y
                    else:
                        x_affichage = mouse_pos[0]-(tile_image.get_size()[0]/2)
                        y_affichage = mouse_pos[1]-(tile_image.get_size()[1]/2)

                    tile_image.set_alpha(128)
                    screen.blit(tile_image, (x_affichage, y_affichage)) # x et y de l'affichage

            # affichage de l'id si tab est appuyé
            if tab_pressed:
                mouse_pos = pygame.mouse.get_pos()
                for tile in all_tiles_on_screen:
                    # génération d'un texte
                    if tile.get_tile_rect().collidepoint(mouse_pos):
                        text_affiche_id = self.police.render("id : " + str(tile.get_id()), True, "white")
                        text_affiche_id_rect = text_affiche_id.get_rect()
                        text_affiche_id_rect.update(0,0, text_affiche_id_rect.width + 20, text_affiche_id_rect.height + 20)
                        text_affiche_id_rect.x = mouse_pos[0]
                        text_affiche_id_rect.bottom = mouse_pos[1]
                        pygame.draw.rect(screen, "grey", text_affiche_id_rect)
                        screen.blit(text_affiche_id, (text_affiche_id_rect.x + 10, text_affiche_id_rect.y + 10))

            # affichage des tiles que l'on peut placer
            # fond partie tiles
            color_fond = "grey"
            if changement_espacement:
                color_fond = "green"
            pygame.draw.rect(screen, color_fond, pygame.rect.Rect((1920 - 600, 0), (600, 1080)))
            x_tile = 1920 - 600 + 20
            y_tile = 300

            rects_tiles_collection = []
            tiles_affiche = []
            avancement = -1
            for visuel in images_tiles:
                avancement = avancement + 1
                if y_tile + y_offset_tile + 100 > 0 and y_tile + y_offset_tile < 1080:
                    image = pygame.transform.scale(visuel, (100,100))

                    screen.blit(image, (x_tile, y_tile + y_offset_tile))
                    rect = image.get_rect()
                    rect.x = x_tile
                    rect.y = y_tile + y_offset_tile
                    rects_tiles_collection.append(rect)
                    tiles_affiche.append(tiles[avancement])

                    # ajouter une étoile si animé
                    if tiles_affiche[len(tiles_affiche)-1].get_animated():
                        screen.blit(etoile, (x_tile, y_tile + y_offset_tile))

                x_tile = x_tile + 110
                if x_tile > 1920 - 100 - 10:
                    x_tile = 1920 - 600 + 20
                    y_tile = y_tile + 110

            # affichage du fond de texte et le texte
            pygame.draw.rect(screen, "grey44", pygame.rect.Rect((1920 - 600, 0), (600, 280)))
            screen.blit(self.police.render("tiles dans le dossier", True, "white"),(1920 - 600 + 50, 20))  # dimensions au pif

            # affichage des boutons au-dessus des tiles
            spawn_point_btn = self.__create_button(screen, "spawn point", (1920-600+145, 100))
            event_point_btn = self.__create_button(screen, "event point", (1920-600+157, 190))

            # affichage boutons
            co_btn = self.__create_button(screen, "caméra : " + str(self.__camera_x) + "," + str(self.__camera_y), (10, 1080-90))
            fichier_btn = self.__create_button(screen, "fichier", (20,20))
            fps_btn = self.__create_button(screen, "fps : " + str(int(clock_global.get_fps())), (fichier_btn.x, fichier_btn.bottom + 10))
            if quadrillage:
                quadrillage_btn = self.__create_button(screen, "quadrillé", (1920-600-240, 20))
                espace_btn = self.__create_button(screen, "espace", (1920-600-240, quadrillage_btn.bottom + 10))
            else:
                quadrillage_btn = self.__create_button(screen, "libre", (1920-600-240, 20))
            proportion_btn = self.__create_button(screen, "proportion : " + str(proportion) + "%", (fichier_btn.right + 10, 20))
            id_btn = self.__create_button(screen, "id : " + id_text, (proportion_btn.x + 150, proportion_btn.bottom + 10))
            background_btn = self.__create_button(screen, "fond", (1920-600-140, 1080-90))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    boucle_global = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEWHEEL:
                    for i in range(abs(event.y)):
                        if pygame.mouse.get_pos()[0] > 1920 - 600:
                            if event.y > 0 and y_offset_tile < 0:
                                y_offset_tile = y_offset_tile + 80
                            elif event.y < 0 and y_tile + y_offset_tile > 1080 - 100:
                                y_offset_tile = y_offset_tile - 80

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LSHIFT:
                        shift_pressed = True
                    elif event.key == pygame.K_TAB:
                        tab_pressed = True
                    else:
                        touche = pygame.key.name(event.key)
                        if touche == "backspace" and len(id_text) > 0:
                            id_text = id_text[:len(id_text)-1]
                        elif touche == "space":
                            id_text = id_text + " "
                        elif touche != "backspace" and len(touche) == 1 and len(id_text) < 20:
                            id_text = id_text + touche

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LSHIFT:
                        shift_pressed = False
                    elif event.key == pygame.K_TAB:
                        tab_pressed = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:
                        right_click = True
                        position_souris = event.pos

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 3:
                        # suppression de la tile au niveau de la souris sur la map
                        right_click = False
                        if not shift_pressed:
                            for tile in self.get_tiles_on_screen():
                                if tile.get_tile_rect().collidepoint(event.pos):
                                    self.__remove_tile(tile, "basique")
                            for tile in self.get_spawn_points_on_screen():
                                if tile.get_tile_rect().collidepoint(event.pos):
                                    self.__remove_tile(tile, "spawn")
                            for tile in self.get_event_points_on_screen():
                                if tile.get_tile_rect().collidepoint(event.pos):
                                    self.__remove_tile(tile, "event")

                            self.maj_map_image()
                    elif event.button == 2:
                        # suppression de la sélection
                        tile_selectionee = None
                        is_point = False

                    elif event.button == 1:
                        if spawn_point_btn.collidepoint(event.pos):
                            # création du tile spawn point
                            tile_selectionee = Tile()
                            tile_selectionee.chemin_image = "mapmaker_assets/spawn_point.png"
                            is_point = True
                            type_point = "spawn"
                            charge_tile_selectionee = True
                        elif event_point_btn.collidepoint(event.pos):
                            # création du tile event point
                            tile_selectionee = Tile()
                            tile_selectionee.chemin_image = "mapmaker_assets/event_point.png"
                            is_point = True
                            type_point = "event"
                            charge_tile_selectionee = True

                        else:
                            for rect in rects_tiles_collection:
                                if rect.collidepoint(event.pos):
                                    if changement_espacement:   # changement espacement entre les tiles
                                        # redimensionnement tile pour dimensions appropriées
                                        tile = tiles_affiche[rects_tiles_collection.index(rect)]
                                        tile.proportion = proportion
                                        tile.charger_image()
                                        tile.maj_rect()
                                        tile_espacement = tile
                                        espacement_x = tile.rect.width
                                        espacement_y = tile.rect.height
                                        changement_espacement = False
                                        charge_tile_selectionee = True
                                    else:
                                        # sélection de la tile à placer
                                        tile_selectionee = tiles_affiche[rects_tiles_collection.index(rect)]
                                        is_point = False
                                        charge_tile_selectionee = True

                        if background_btn.collidepoint(event.pos):
                            boucle_background = True
                            clock_background = pygame.time.Clock()
                            background_color = ""
                            while boucle_background:
                                retour_btn = self.__create_button(screen, "retour", (background_btn.x-40, background_btn.y))
                                valider_color_btn = self.__create_button(screen, "valider", (retour_btn.x-15, retour_btn.top - retour_btn.height - 10))

                                # création d'un affichage car mauvais côté
                                affichage_background_color = self.police.render("couleur : " + background_color, True, (255,255,255))
                                affichage_background_color_rect = affichage_background_color.get_rect()
                                affichage_background_color_rect.update(affichage_background_color_rect.x, retour_btn.top, affichage_background_color_rect.width + 20, affichage_background_color_rect.height + 20)
                                affichage_background_color_rect.right = retour_btn.left - 10
                                pygame.draw.rect(screen, "grey", pygame.rect.Rect(0, retour_btn.top, retour_btn.x-10, retour_btn.height))
                                screen.blit(affichage_background_color, (affichage_background_color_rect.x + 10, affichage_background_color_rect.y + 10))
                                pygame.display.flip()


                                for event_background in pygame.event.get():
                                    if event_background.type == pygame.QUIT:
                                        boucle_background = False
                                        boucle_global = False
                                        pygame.quit()
                                        sys.exit()

                                    elif event_background.type == pygame.MOUSEBUTTONUP:
                                        if event_background.button == 1:
                                            if retour_btn.collidepoint(event_background.pos):
                                                boucle_background = False
                                            elif valider_color_btn.collidepoint(event_background.pos):
                                                if background_color == "none":
                                                    # fond transparent
                                                    self.background = "none"
                                                    boucle_background = False
                                                elif background_color in self.__get_colors_allowed():
                                                    self.background = background_color
                                                    boucle_background = False

                                    elif event_background.type == pygame.KEYDOWN:
                                        touche = pygame.key.name(event_background.key)
                                        if touche == "backspace" and len(background_color) > 0:
                                            background_color = background_color[:len(background_color) - 1]
                                        elif touche == "space":
                                            background_color = background_color + " "
                                        elif touche != "backspace" and len(touche) == 1 and len(background_color) < 30:
                                            background_color = background_color + touche
                                clock_background.tick(fps)

                        elif quadrillage and espace_btn.collidepoint(event.pos):
                            if changement_espacement:
                                changement_espacement = False
                            else:
                                changement_espacement = True

                        elif quadrillage_btn.collidepoint(event.pos):
                            if quadrillage:
                                quadrillage = False
                                changement_espacement = False
                            else:
                                quadrillage = True
                        elif proportion_btn.collidepoint(event.pos):
                            player_input = str(proportion)

                            boucle_proportion = True
                            clock_proportion = pygame.time.Clock()
                            while boucle_proportion:
                                if player_input != "":
                                    affichage_valeur = player_input + "%"
                                else:
                                    affichage_valeur = ""
                                pygame.draw.rect(screen, "grey", pygame.rect.Rect((10, proportion_btn.bottom + 110), (1920-600-10-10, 76)))
                                new_proportion = self.__create_button(screen, "nouvelle proportion : " + affichage_valeur,(10, proportion_btn.bottom + 110))
                                back_btn = self.__create_button(screen, "retour",(new_proportion.x, new_proportion.bottom + 10))
                                valider_btn = self.__create_button(screen, "valider", (back_btn.x + 355, new_proportion.bottom + 10))

                                pygame.display.flip()
                                for event_proportion in pygame.event.get():
                                    if event_proportion.type == pygame.QUIT:
                                        boucle_proportion = False
                                        boucle_global = False
                                        pygame.quit()
                                        sys.exit()

                                    elif event_proportion.type == pygame.MOUSEBUTTONUP:
                                        if event_proportion.button == 1:
                                            if back_btn.collidepoint(event_proportion.pos):
                                                boucle_proportion = False
                                            elif valider_btn.collidepoint(event_proportion.pos):
                                                if len(player_input) > 0:
                                                    if int(player_input) > 0:
                                                        proportion = int(player_input)
                                                        # mise à jour de l'espace du quadrillage (s'il a été initié)
                                                        if tile_espacement != None:
                                                            tile_espacement.proportion = proportion
                                                            tile_espacement.charger_image()
                                                            tile_espacement.maj_rect()
                                                            espacement_x = tile_espacement.rect.width
                                                            espacement_y = tile_espacement.rect.height
                                                        charge_tile_selectionee = True
                                                        boucle_proportion = False

                                    elif event_proportion.type == pygame.KEYDOWN:
                                        touche = pygame.key.name(event_proportion.key)
                                        if touche in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "backspace"]:
                                            if touche == "backspace" and len(player_input) > 0:
                                                player_input = player_input[:len(player_input)-1]
                                            else:
                                                if touche != "backspace" and len(player_input) < 18:
                                                    player_input = player_input + touche
                                clock_proportion.tick(fps)

                        elif fichier_btn.collidepoint(event.pos):
                            back_btn = self.__create_button(screen, "retour", (20,20))
                            save_btn = self.__create_button(screen, "sauvegarder", (20, back_btn.bottom + 10))
                            clear_btn = self.__create_button(screen, "clear", (20,save_btn.bottom + 10 + save_btn.height + 10))
                            quit_btn = self.__create_button(screen, "quitter", (20, clear_btn.bottom + 10))

                            boucle_fichier = True
                            clock_fichier = pygame.time.Clock()
                            while boucle_fichier:
                                text_assistant = "non"
                                if assistant_id:
                                    text_assistant = " oui" # espace au début car le "non" est plus grand
                                id_btn = self.__create_button(screen, "assistant id : " + text_assistant,(20, save_btn.bottom + 10))

                                pygame.display.flip()

                                for event_fichier in pygame.event.get():
                                    if event_fichier.type == pygame.QUIT:
                                        boucle_fichier = False
                                        boucle_global = False
                                        pygame.quit()
                                        sys.exit()

                                    elif event_fichier.type == pygame.MOUSEBUTTONUP:
                                        if event_fichier.button == 1:
                                            if quit_btn.collidepoint(event_fichier.pos):
                                                boucle_fichier = False
                                                boucle_global = False
                                                pygame.quit()
                                                sys.exit()
                                            elif clear_btn.collidepoint(event_fichier.pos):
                                                self.map = []
                                                self.spawn_points = []
                                                self.event_points = []
                                                self.maj_map_image()
                                                boucle_fichier = False
                                            elif back_btn.collidepoint(event_fichier.pos):
                                                boucle_fichier = False
                                            elif id_btn.collidepoint(event_fichier.pos):
                                                if assistant_id:
                                                    assistant_id = False
                                                else:
                                                    assistant_id = True
                                            elif save_btn.collidepoint(event_fichier.pos):

                                                boucle_save = True
                                                clock_save = pygame.time.Clock()
                                                nom_fichier_save = ""
                                                while boucle_save:
                                                    pygame.draw.rect(screen, "grey", pygame.rect.Rect(save_btn.x, save_btn.bottom + 10, 1920-600-20, 250))
                                                    fichier_save_btn = self.__create_button(screen, "nom du fichier : " + nom_fichier_save, (save_btn.x, save_btn.bottom + 10))
                                                    retour_save_btn = self.__create_button(screen, "retour", (20,20))
                                                    valider_save_btn = self.__create_button(screen, "valider", (fichier_save_btn.x, save_btn.bottom + 10 + 250 + 10))

                                                    pygame.display.flip()
                                                    for event_save in pygame.event.get():
                                                        if event_save.type == pygame.QUIT:
                                                            boucle_save = False
                                                            boucle_fichier = False
                                                            boucle_global = False
                                                            pygame.quit()
                                                            sys.exit()

                                                        elif event_save.type == pygame.KEYDOWN:
                                                            touche = pygame.key.name(event_save.key)
                                                            if touche == "backspace" and len(nom_fichier_save) > 0:
                                                                nom_fichier_save = nom_fichier_save[:len(nom_fichier_save) - 1]
                                                            elif touche == "space":
                                                                nom_fichier_save = nom_fichier_save + " "
                                                            elif touche != "backspace" and len(touche) == 1 and len(nom_fichier_save) < 30:
                                                                nom_fichier_save = nom_fichier_save + touche

                                                        elif event_save.type == pygame.MOUSEBUTTONUP:
                                                            if retour_save_btn.collidepoint(event_save.pos):
                                                                boucle_save = False
                                                                boucle_fichier = False
                                                            elif valider_save_btn.collidepoint(event_save.pos):
                                                                nom_fichier_save = nom_fichier_save + ".txt"
                                                                self.__save(nom_fichier_save)
                                                                boucle_save = False
                                                                boucle_fichier = False
                                                    clock_save.tick(fps)
                                clock_fichier.tick(fps)

                        elif event.pos[0] < 1920 - 600 and tile_selectionee != None:
                            # ajout du tile sélectionnée dans la map
                            new_tile = Tile()   # nouvelle instance pour faire la différence avec les autres tiles pareilles
                            new_tile.chemin_image = tile_selectionee.chemin_image
                            new_tile.proportion = tile_selectionee.proportion
                            new_tile.set_id(id_text)
                            new_tile.x = int(x_affichage)
                            new_tile.y = int(y_affichage)
                            # génération des cos de base :  x = x_base - camera_x donc x_base = x + camera_x
                            new_tile.x_base = int(new_tile.x + self.__camera_x)
                            new_tile.y_base = int(new_tile.y + self.__camera_y)
                            new_tile.charger_image()
                            new_tile.maj_rect()
                            # test si la touche shift est enfoncée
                            type_tile = "basique"
                            if is_point:
                                type_tile = type_point
                                # dimensions du spawn_point égales à l'espacement
                                new_tile.charger_image(espacement_x, espacement_y)
                            if shift_pressed:  # renvoie True ou False
                                self.__add_tile(new_tile, type_tile, False)  # mise au dernier plan
                            else:
                                self.__add_tile(new_tile, type_tile) # mise au premier plan

                            self.maj_map_image()
                        # calcul du changement de position de la souris si right click + shift pressé

            # calcul déplacement caméra
            if right_click and shift_pressed:
                # position_souris est forcément un tuple avec la position, car le logiciel se lance avec right_click à False, et la right_click est changée en même temps qu'elle
                new_position_souris = pygame.mouse.get_pos()
                difference_x = new_position_souris[0] - position_souris[0]
                difference_y = new_position_souris[1] - position_souris[1]
                # si c'est négatif, ça veut dire que la souris s'est déplacée vers la gauche
                # et gauche --> caméra +
                #    droite --> caméra -
                self.__camera_x = int(self.__camera_x - difference_x)
                self.__camera_y = int(self.__camera_y - difference_y)
                position_souris = new_position_souris
            clock_global.tick(fps)

if __name__ == '__main__':
    map = Map()
    map.mapmaker()