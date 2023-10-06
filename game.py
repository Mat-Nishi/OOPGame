import pygame

class Window:
    def __init__(self,h,w) -> None:
        self._height = h
        self._width = w
        self._window = pygame.display.set_mode((h,w))
    
    def setBG(self, color):
        self._window.fill(color)
        pygame.display.update()
        
class Player():
    def __init__(self, sprite) -> None:
        self._body = sprite
        self.posX = 0
        self.posY = 0
    
    def move(self, dir, speed):
        if dir == 'up':
            self.posY -= speed
        elif dir == 'down':
            self.posY += speed
        elif dir == 'left':
            self.posX -= speed
        else:
            self.posX += speed
    
    def setPos(self, x,y):
        self.posX = x
        self.posY = y


class Engine:
    def __init__(self, window, fps=60) -> None:
        self.window = window
        self._fps = fps
        self._clock = pygame.time.Clock()
        self._state = "game"
        

    def runGame(self):
        while self._state == "game":
            self._clock.tick(self._fps)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._state = "menu"
            # self.window.setBG((255,0,0))

        pygame.quit()



def main():
    window = Window(500,500)
    game = Engine(window)
    game.runGame()

if __name__ == "__main__":
    main()