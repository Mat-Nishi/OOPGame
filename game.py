import pygame
import os

class Window:
    def __init__(self,h,w,bgColor=(0,0,0)) -> None:
        self._height = h
        self._width = w
        self.bgColor = bgColor
        self._window = pygame.display.set_mode((h,w))
    
    def setBG(self, color):
        self.bgColor = color
        self._window.fill(color)
        pygame.display.update()
    
    def clear(self):
        self._window.fill(self.bgColor)
    
    def drawImage(self, image, x, y):
        self._window.blit(image, (x,y))
        pygame.display.update()
        
class Player():
    def __init__(self, h, w, speed, sprite) -> None:
        self._height = h
        self._width = w
        self.speed = speed
        img = pygame.image.load(os.path.join("Assets",sprite))
        self._body = pygame.transform.scale(img, (self._height, self._width))
        self.posX = 0
        self.posY = 0
    
    def move(self, dir):
        if dir == 'up':
            self.posY -= self.speed
        elif dir == 'down':
            self.posY += self.speed
        elif dir == 'left':
            self.posX -= self.speed
        else:
            self.posX += self.speed
    
    def setPos(self, x,y):
        self.posX = x
        self.posY = y


class Engine:
    def __init__(self, window, player, fps=60) -> None:
        self.window = window
        self._fps = fps
        self._clock = pygame.time.Clock()
        self._state = "game"
        self._player = player

    def drawPlayer(self):
        self.window.drawImage(self._player._body, self._player.posX, self._player.posY)
    
    def playerMovement(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_w]: #Up
            self._player.move('up')
        if pressed_keys[pygame.K_a]: #Left
            self._player.move('left')
        if pressed_keys[pygame.K_s]: #Down
            self._player.move('down')
        if pressed_keys[pygame.K_d]: #Right
            self._player.move('right')

    def runGame(self):
        while self._state == "game":
            self._clock.tick(self._fps)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._state = "menu"
            # self.window.setBG((255,0,0))
            self.window.clear()
            self.playerMovement()
            self.drawPlayer()

        pygame.quit()



def main():
    window = Window(500,500)
    player = Player(140,60,5,"crab.png")
    game = Engine(window, player)
    game.runGame()

if __name__ == "__main__":
    main()