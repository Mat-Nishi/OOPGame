import pygame
import pygame.gfxdraw
import os
import random
import time

class Window:
    def __init__(self,w,h,bgColor=(0,0,0)) -> None:
        self._height = h
        self._width = w
        self.bgColor = bgColor
        self._window = pygame.display.set_mode((w,h))
    
    def update(self):
        pygame.display.update()
    
    def setBG(self, color):
        self.bgColor = color
        self._window.fill(color)
        pygame.display.update()
    
    def clear(self):
        self._window.fill(self.bgColor)
    
    def drawImage(self, image, x, y):
        self._window.blit(image, (x,y))
    
    def drawPolygon(self, texture, points):
        pygame.gfxdraw.textured_polygon(self._window, points, texture,0,0)
        # pygame.draw.polygon(self._window, 'lightblue', points)
        
class Player:
    def __init__(self, w, h, speed, sprite, gravity=0.4) -> None:
        self._height = h
        self._width = w
        self.speed = 0
        self._maxSpeed = speed
        self._gravity = gravity
        img = pygame.image.load(os.path.join("Assets",sprite))
        self._body = pygame.transform.scale(img, (self._width, self._height))
        self.posX = 0
        self.posY = 0

    def move(self, dir):
        if dir == 'up':
            if self.speed > -self._maxSpeed:
                self.speed -= self._gravity
            self.posY += self.speed
        elif dir == 'down':
            if self.speed < self._maxSpeed:
                self.speed += self._gravity
            self.posY += self.speed
        elif dir == 'left':
            self.posX -= self.speed
        else:
            self.posX += self.speed
    
    def setPos(self, x,y):
        self.posX = x
        self.posY = y

class Obstacle:
    def __init__(self, w, yTop, yBot, speed, texture) -> None:
        self._width = w
        self._top = yTop
        self._bottom = yBot
        self.speed = speed
        self._texture = pygame.image.load(os.path.join("Assets",texture))

    def move(self):
        self._top = (self._top[0]-self.speed, self._top[1])
        self._bottom = (self._bottom[0]-self.speed, self._bottom[1])

class Engine:
    def __init__(self, window, player, fps=60) -> None:
        self.window = window
        self._fps = fps
        self._clock = pygame.time.Clock()
        self._state = "game"
        self._player = player
        self._obstacles = []

    def drawPlayer(self):
        self.window.drawImage(self._player._body, self._player.posX, self._player.posY)
    
    def makeObstacle(self):
        xTop = random.randint(self.window._width, self.window._width + 200)
        yTop = random.randint(0, self.window._height)
        xBot = random.randint(self.window._width, self.window._width + 200)
        yBot = random.randint(0, self.window._height)

        if abs(yTop-yBot) <= 50:
             yTop,yBot = min(yTop,yBot)-25, max(yTop, yBot)+25
        if yTop <= self._player._height + 5 and yBot >= self.window._height - 5 - self._player._height:
            yTop = self._player._height + 5
        if random.randint(0,1):
            xTop = self.window._width -1
        else:
            xBot = self.window._width -1
            
        self._obstacles.append(Obstacle(15, (xTop, yTop), (xBot,yBot), 5, "laserTexture.png"))
    
    def destroyObstacle(self, obs):
        self._obstacles.remove(obs)
    
    def drawObstacle(self, obs):
        # obs = self.makeObstacle()
        coords = [obs._top, (obs._top[0]+obs._width, obs._top[1]), (obs._bottom[0]+obs._width, obs._bottom[1]), obs._bottom]
        try:
            self.window.drawPolygon(obs._texture, coords)
        except pygame.error:
            self.destroyObstacle(obs)
    
    def checkCollision(self):
        def ccw(A,B,C):
            return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
        def intersect(A,B,C,D):
            return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

        if self._player.posY + self._player._height >= self.window._height:
            self._player.speed = 0
            self._player.posY = self.window._height - self._player._height
        elif self._player.posY <= 0:
            self._player.speed = 0
            self._player.posY = 0
        
        playerCorners = [(self._player.posX, self._player.posY),
                         (self._player.posX+self._player._width, self._player.posY),
                         (self._player.posX, self._player.posY+self._player._height),
                         (self._player.posX+self._player._width, self._player.posY+self._player._height)]
        
        for obstacle in self._obstacles:
            for i in range(4):
                for j in range(i,4):
                    if intersect(playerCorners[i], playerCorners[j], obstacle._top, obstacle._bottom):
                        pygame.quit()
                        return
    
    def playerMovement(self):
        pressed_keys = pygame.key.get_pressed()
        
        if pressed_keys[pygame.K_w] and self._player.posY > 0: #Up
            self._player.move('up')
        else:
            self._player.move('down')
            
        # if pressed_keys[pygame.K_a] and self._player.posX > 0: #Left
        #     self._player.move('left')
        # if pressed_keys[pygame.K_s] and self._player.posY < self.window._height - self._player._height: #Down
        #     self._player.move('down')
        # if pressed_keys[pygame.K_d] and self._player.posX < self.window._width - self._player._width: #Right
        #     self._player.move('right')

    def runGame(self):
        timer = time.time()
        obsCd = timer
        nextObs = 3
        self._player.setPos(0, self.window._height-self._player._height)
        while self._state == "game":
            self._clock.tick(self._fps)
            timer = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._state = "menu"
                
            # self.window.setBG((255,0,0))
            self.window.clear()
            self.playerMovement()
            self.checkCollision()

            if timer-obsCd >= nextObs:
                obsCd = timer
                nextObs = 1 + random.random()*2
                self.makeObstacle()

            for obstacle in self._obstacles:
                obstacle.move()
                self.drawObstacle(obstacle)

            self.drawPlayer()
            self.window.update()

        pygame.quit()


# Driver code

def main():
    window = Window(1000,500)
    player = Player(140,60,20,"crab.png")
    game = Engine(window, player)
    game.runGame()

if __name__ == "__main__":
    main()