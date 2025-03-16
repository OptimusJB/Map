import pygame
pygame.init()

class Screen:
    """
    système permettant de simplement changer la résolution du jeu en temps réel (en supposant que le tag pygame.RESIZABLE soit mis)
    permet également de sauvegarder des surfaces pour les recharger plus tard (utilisé lors de l'animation des cartes qui arrivent dans le combat)
    """
    def __init__(self, dimensions_calcul):
        """
        mise en place de la surface pour le calcul
        """
        assert type(dimensions_calcul) == tuple, "les dimensions doivent être un tuple"
        self.screen_calcul = pygame.surface.Surface(dimensions_calcul)
        self.dimensions_screen_calcul = dimensions_calcul
        self.screen = None
        self.saves = {}

    def set_mode(self, dimensions, flag=None):
        """
        mise en place du screen d'affichage
        l'affichage va commencer à pixeliser s'il est plus grand que le screen de calcul
        """
        assert type(dimensions) == tuple, "les dimensions doivent être un tuple"
        if flag != None:
            self.screen = pygame.display.set_mode(dimensions, flag)
        else:
            self.screen = pygame.display.set_mode(dimensions)
        self.dimensions_screen = dimensions

    def blit(self, surface, cos):
        self.screen_calcul.blit(surface, cos)

    def draw_rect(self, color, rect):
        pygame.draw.rect(self.screen_calcul, color, rect)

    def fill(self, color):
        self.screen_calcul.fill(color)

    def flip(self):
        """
        équivalent de pygame.display.flip()
        """
        infos = pygame.display.Info()
        self.screen.blit(pygame.transform.smoothscale(self.screen_calcul, (infos.current_w, infos.current_h)), (0,0))
        pygame.display.flip()

    def get_calcul_mouse_cos(self, mouse_cos):
        """
        IMPORTANT : permet d'obtenir les coordonnées de la souris par rapport au screen de calcul
        prend en paramètre les coordonnées de la souris sur le screen d'affichage
        """
        infos = pygame.display.Info()
        mouse_x = int(mouse_cos[0] / infos.current_w * self.dimensions_screen_calcul[0])
        mouse_y = int(mouse_cos[1] / infos.current_h * self.dimensions_screen_calcul[1])
        return (mouse_x, mouse_y)

    def save_screen(self, id):
        """
        sauvegarde le screen de calcul actuel
        """
        self.saves[id] = self.screen_calcul.copy()

    def del_save(self, id):
        self.saves.pop(id)

    def load_screen(self, id):
        """
        attention : une nouvelle instance est crée lors du chargement (le fait de blit des trucs sur l'image ne changera pas la save)
        """
        self.screen_calcul = self.saves[id].copy()

resize_screen = Screen((1920, 1080))
# pour blit un truc : resize_screen.blit(element, coordonnées)
# pour fill : resize_screen.fill()