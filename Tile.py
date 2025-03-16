import pygame
pygame.init()
dico_image = {}
class Tile:
    """
    classe représentant un élément de la map
    utilisation en jeu:
        - Tile.get_id() et Tile.set_id() pour avoir et définir l'id de la tile
          l'id par défaut de la tile est l'id défini dans le mapmaker
        - Tile.set_visible() et get_visible() pour activer, désactiver ou obtenir le fait que la tile soit affichée lors de Map.render()
          si la tile est invisible, elle ne sera pas dans Map.get_tiles_on_screen, mais elle sera dans get_all_tiles() et get_invisible_tiles()
          attention : dans la classe Map, self.visible n'est pas sauvegardé, lors du lancement de la map, toutes les tiles seront visibles (sauf les spawn points et les event points)
        - get_tile_rect() qui permet d'avoir le rect de la tile, si elle est animée, le rect est celle de la frame actuelle
          se met à jour avec set_frame(), next_frame(), previous_frame() et Map.render()
        - Tile.get_co() et Tile.get_co_base(), je ne conseille pas vraiment de les utiliser parce que c'est compliqué, mais en gros:
          get_co_base() fait référence aux coordonnées de la tile sur la map si on ne prend pas en compte la caméra
          get_co() fait référence aux coordonnées d'affichage de la tile sur l'écran (en prenant en compte la caméra), cette méthode se met à jour avec Map.render()
    dans le cas d'une tile animée :
        - Tile.get_animated pour savoir si la tile est animée ou pas
        - Tile.get_actual_frame() qui retourne l'indice de la frame actuelle (0 pour la première frame)
        - Tile.next_frame() pour passer à la frame suivante lors de Map.render(), le rect sera mis à jour
        - Tile.previous_frame() pour passer à la frame précédente lors de Map.render(), le rect sera mis à jour
        - Tile.set_frame() pour passer à la frame d'indice passé en paramètre lors de Map.render(), le rect sera mis à jour
    le reste des méthodes nécessaires pour la classe Map, mais ne doivent pas être utilisées
    """
    def __init__(self, co_de_base=(0,0)):
        self.id = ""
        # x et y de départ, à sauvegarder
        self.x_base = co_de_base[0]
        self.y_base = co_de_base[1]

        self.animated = False   # détermine si la tile a une animation
        self.actual_frame = 0   # frame de l'animation, 0 est la première image
        self.liste_frames = []  # ensemble des images de l'animation

        self.chemin_image = None    # liste de str ou str (animations ou pas)
        self.image = None   # image actuelle si animation

        self.proportion = 100   # en %

        self.rect = None

        # x et y variables (selon la caméra)
        self.x = co_de_base[0]
        self.y = co_de_base[1]
        self.visible = True  # détermine si la tile doit s'afficher (son rect ne sera pas dans Map.rects_on_screen)

    # getters
    def get_id(self):
        return self.id
    def get_co(self) -> tuple:
        """
        retourne la position du tile sur l'écran (selon la caméra)
        se met à jour après render()
        """
        return (self.x, self.y)

    def get_co_base(self) -> tuple:
        """
        retourne la véritable position du tile
        """
        return (self.x_base, self.y_base)
    def get_animated(self) -> bool:
        return self.animated
    def get_actual_frame(self) -> int:
        if self.animated:
            return self.actual_frame
    def get_tile_rect(self):
        return self.rect
    def get_visible(self) -> bool:
        return self.visible

    # setters
    def set_id(self, new_id:str):
        self.id = new_id

    # important
    def set_visible(self, visible:bool):
        assert type(visible) == bool, "visible doit être un booléen"
        self.visible = visible

    def next_frame(self):
        """
        change l'image vers la frame suivante
        return True si c'était la dernière frame, False sinon
        fait une boucle si c'était la dernière frame à afficher
        """
        assert self.get_animated(), "cette tile n'est pas animée"
        self.actual_frame = self.actual_frame + 1
        if self.actual_frame >= len(self.liste_frames):
            self.actual_frame = 0
        self.image = self.liste_frames[self.actual_frame]
        self.maj_rect()
        if self.actual_frame == len(self.liste_frames) - 1:
            return True
        return False

    def previous_frame(self):
        """
        change l'image vers la frame précédente
        return True si c'était la dernière frame, False sinon
        fait une boucle si c'était la dernière frame à afficher
        """
        assert self.get_animated(), "cette tile n'est pas animée"
        self.actual_frame = self.actual_frame - 1
        if self.actual_frame <= -1:
            self.actual_frame = len(self.liste_frames) - 1
        self.image = self.liste_frames[self.actual_frame]
        self.maj_rect()
        if self.actual_frame == 0:
            return True
        return False

    def set_frame(self, index_frame:int):
        """
        change l'image vers la frame d'index passée en paramètre
        """
        assert self.get_animated(), "cette tile n'est pas animée"
        assert type(index_frame) == int, "index_frame doit être un entier"
        assert index_frame >= 0 and index_frame < len(self.liste_frames)
        self.actual_frame = index_frame
        self.image = self.liste_frames[self.actual_frame]
        self.maj_rect()

    def maj_rect(self):
        """
        met à jour la taille et la position du rect du tile par rapport à self.image, self.x et self.y
        si tile animée, le rect est de la taille de la frame actuelle
        """
        assert type(self.image) == pygame.Surface, "l'image n'est pas valide ou pas encore chargée"
        self.rect = self.image.get_rect()   # même chose que ce soit animé ou pas
        self.rect.x = self.x
        self.rect.y = self.y

    def load_dico(self, chemin_image:str):
        """
        Permet d'économiser de la place en mémoire
        """
        if not chemin_image in dico_image:
            dico_image[chemin_image] = pygame.image.load(chemin_image).convert_alpha()
        return dico_image[chemin_image]

    def charger_image(self, largeur=None, hauteur=None):    # largeur et hauteur personnalisée
        """
        charge/met à jour l'image grâce à self.chemin_image, puis le met à la bonne proportion grâce à self.proportion
        si une largeur ou une hauteur est passée en paramètre, elles seront utilisées à la place de la proportion
        si animée, l'image mise est la première frame
        """
        self.image = None
        self.liste_frames = []

        if type(self.chemin_image) == list:
            # animé
            self.animated = True
            self.chemin_image.sort()    # triage des animations
            for chemin in self.chemin_image:
                image = self.load_dico(chemin)
                if largeur == None:
                    largeur = int(image.get_size()[0]*(self.proportion/100))
                if hauteur == None:
                    hauteur = int(image.get_size()[1]*(self.proportion/100))

                if hauteur == 0 or largeur == 0:
                    print("trop petit")
                else:
                    image = pygame.transform.scale(image, (largeur, hauteur))
                self.liste_frames.append(image)
            self.image = self.liste_frames[0]   # image de base
            self.maj_rect()     # génération du rect
        else:
            # pas animé
            self.animated = False
            self.image = self.load_dico(self.chemin_image)
            # ATTENTION : si largeur ou hauteur = 0, le truc pour le quadrillage va faire une boucle infinie
            if largeur == None:
                largeur = int(self.image.get_size()[0]*(self.proportion/100))
            if hauteur == None:
                hauteur = int(self.image.get_size()[1]*(self.proportion/100))

            if hauteur == 0 or largeur == 0:
                print("trop petit")
            else:
                self.image = pygame.transform.scale(self.image, (largeur, hauteur))
                # TypeError: size must be two numbers = nombre trop grand
            self.maj_rect()     # génération du rect

    def affiche_tile(self):
        print(self.id, self.x_base, self.y_base, self.animated, self.proportion, self.chemin_image)
        print(type(self.id), type(self.x_base), type(self.y_base), type(self.animated), type(self.proportion), type(self.chemin_image))
        print(self.get_tile_rect().width, self.get_tile_rect().height)

    def cloner(self):
        """
        retourne un nouveau tile avec les mêmes attributs
        """
        tile = Tile()
        tile.id = self.id
        tile.x_base = self.x_base
        tile.y_base = self.y_base

        tile.animated = self.animated
        tile.actual_frame = self.actual_frame
        tile.liste_frames = self.liste_frames

        tile.chemin_image = self.chemin_image
        tile.image = self.image

        tile.proportion = self.proportion

        tile.rect = self.rect

        tile.x = self.x
        tile.y = self.y
        tile.visible = self.visible
        return tile