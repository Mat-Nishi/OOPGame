import pygame
import pygame.gfxdraw
import os
import random
import time


class Window:
    def __init__(self, w, h, bgColor=(0, 0, 0),bgImage = None) -> None:
        self._height = h
        self._width = w
        self.bgColor = bgColor
        self.bgImage = bgImage
        self._window = pygame.display.set_mode((w, h))
        if bgImage is not None:
            img = pygame.image.load(os.path.join("Assets", bgImage)).convert_alpha()
            self.bgImage = pygame.transform.scale(img, (self._width, self._height))

        pygame.display.set_caption("Endless Scroll") #flag

    def update(self):
        pygame.display.update()





    def setBG(self, color):
        self.bgColor = pygame.image.load("bg.png").convert()
        pygame.display.update()

    def clear(self):
        if self.bgImage is None:
            self._window.fill(self.bgColor)
        else:
            self._window.blit(self.bgImage, (0, 0))

    def drawImage(self, image, x, y):
        self._window.blit(image, (x, y))

    def drawPolygon(self, texture, points):
        pygame.gfxdraw.textured_polygon(self._window, points, texture, 0, 0)
        # pygame.draw.polygon(self._window, 'lightblue', points)

    def drawText(self, txt, x=None, y=None, offsetX=0, offsetY=0, center=True):
        if x is None:
            x = self._width // 2
        if y is None:
            y = self._height // 2

        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render(txt, True, 'white', 'black')
        textRect = text.get_rect()
        if center:
            textRect.center = (x + offsetX, y + offsetY)
        else:
            textRect.x = x + offsetX
            textRect.y = y + offsetY
        # self._window.fill('black')
        self._window.blit(text, textRect)


class Player:
    def __init__(self, w, h, speed, sprite, gravity=0.4) -> None:
        self._height = h
        self._width = w
        self.speed = 0
        self._maxSpeed = speed
        self._gravity = gravity
        img = pygame.image.load(os.path.join("Assets", sprite)).convert_alpha()
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

    def setPos(self, x, y):
        self.posX = x
        self.posY = y


class Obstacle:
    def __init__(self, w, yTop, yBot, texture) -> None:
        self._width = w
        self._top = yTop
        self._bottom = yBot
        self._texture = pygame.image.load(os.path.join("Assets", texture)).convert_alpha()

    def move(self, speed):
        self._top = (self._top[0] - speed, self._top[1])
        self._bottom = (self._bottom[0] - speed, self._bottom[1])

class Missile:
    def __init__(self,w,h,speed,x,y,imagem):
        self.w = w
        self.h = h
        self.speed = speed
        self.y = y
        self.spawnTime = time.time()
        self.x = x
        img = pygame.image.load(os.path.join("Assets", imagem)).convert_alpha()
        self.imagem = pygame.transform.scale(img, (self.w, self.h))

    def move(self,player):

        initTime = time.time()
        if time.time() - self.spawnTime < 3:
            pos = player.posY

            if self.y < pos:
                self.y += self.speed
            else:
                self.y -= self.speed
        else:
             self.x -= 30

        if time.time() - self.spawnTime >= 15:
            return 1

class Engine:
    def __init__(self, window, player, fps=60) -> None:
        self.window = window
        self._fps = fps
        self._clock = pygame.time.Clock()
        self._state = "game"
        self._player = player
        self._obstacles = []
        self.score = 0
        self._startSpeed = 3
        self.speed = 3
        self._startTime = time.time()


    def drawMissile(self,miss):
        self.window.drawImage(miss.imagem,miss.x,miss.y)
    def drawPlayer(self):
        self.window.drawImage(self._player._body, self._player.posX, self._player.posY)

    def updateScore(self):
        self.score = int((time.time() - self._startTime) * 10 * (self.speed / 5))
        self.window.drawText(str(self.score), 0, 0, 10, 10, False)

    def updateSpeed(self):
        self.speed = self._startSpeed + (time.time() - self._startTime) / 5

    def makeObstacle(self):
        xTop = random.randint(self.window._width, self.window._width + 200)
        yTop = random.randint(0, self.window._height)
        xBot = random.randint(self.window._width, self.window._width + 200)
        yBot = random.randint(0, self.window._height)
        yTop, yBot = min(yTop, yBot), max(yTop, yBot)

        if abs(yTop - yBot) <= 50:
            yTop, yBot = min(yTop, yBot) - 25, max(yTop, yBot) + 25
        if yTop <= self._player._height + 5 and yBot >= self.window._height - 5 - self._player._height:
            yTop = self._player._height + 5
        if random.randint(0, 1):
            xTop = self.window._width - 1
        else:
            xBot = self.window._width - 1

        self._obstacles.append(Obstacle(15, (xTop, yTop), (xBot, yBot), "laserTexture.png"))

    def makeMissile(self):
        self._obstacles.append(Missile(50, 50, 14, self.window._width - 15, 0,"laserTexture.png"))



    def destroyObstacle(self, obs):
        self._obstacles.remove(obs)

    def drawObstacle(self, obs):
        # obs = self.makeObstacle()
        coords = [obs._top, (obs._top[0] + obs._width, obs._top[1]), (obs._bottom[0] + obs._width, obs._bottom[1]),
                  obs._bottom]
        try:
            self.window.drawPolygon(obs._texture, coords)
        except pygame.error:
            self.destroyObstacle(obs)

    def checkCollision(self):
        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

        def intersect(A, B, C, D):
            return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

        if self._player.posY + self._player._height >= self.window._height:
            self._player.speed = 0
            self._player.posY = self.window._height - self._player._height
        elif self._player.posY <= 0:
            self._player.speed = 0
            self._player.posY = 0

        playerCorners = [(self._player.posX, self._player.posY),
                         (self._player.posX + self._player._width, self._player.posY),
                         (self._player.posX, self._player.posY + self._player._height),
                         (self._player.posX + self._player._width, self._player.posY + self._player._height)]

        for obstacle in self._obstacles:
            if type(obstacle) == Obstacle:
                for i in range(4):
                    for j in range(i, 4):
                        if intersect(playerCorners[i], playerCorners[j], obstacle._top, obstacle._bottom):
                            self._state = 'endScreen'
                            return
            elif type(obstacle) == Missile:
                if self._player.posX + self._player._width >= obstacle.x and self._player.posX <= obstacle.x + obstacle.w and  self._player.posY + self._player._height >= obstacle.y and self._player.posY <= obstacle.y + obstacle.h:
                            self._state = 'endScreen'
                            return

    def playerMovement(self):
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[pygame.K_w] and self._player.posY > 0:  # Up
            self._player.move('up')
        else:
            self._player.move('down')

        # if pressed_keys[pygame.K_a] and self._player.posX > 0: #Left
        #     self._player.move('left')
        # if pressed_keys[pygame.K_s] and self._player.posY < self.window._height - self._player._height: #Down
        #     self._player.move('down')
        # if pressed_keys[pygame.K_d] and self._player.posX < self.window._width - self._player._width: #Right
        #     self._player.move('right')

    def close(self):
        self._state = ''
        pygame.quit()

    def endScreen(self):
        self._obstacles = []
        self._player.setPos(0, self.window._height)
        self.speed = 3
        self._startTime = time.time()

        while self._state == 'endScreen':
            self.window.clear()
            self.window.drawText("Click anywhere to restart", offsetY=-20)
            self.window.drawText(f"Score: {self.score}", offsetY=20)
            self.window.update()

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    self._state = 'game'
                    self.score = 0
                if event.type == pygame.QUIT:
                    self.close()

    def runGame(self):
        timer = time.time()
        obsCd = timer
        nextObs = 3
        missCd = timer
        nextMiss = 6
        self._player.setPos(0, self.window._height - self._player._height)
        while self._state == "game":
            self._clock.tick(self._fps)
            timer = time.time()

            # self.window.setBG((255,0,0))
            self.window.clear()
            self.updateScore()
            self.updateSpeed()
            self.playerMovement()
            self.checkCollision()

            if timer - obsCd >= nextObs:
                obsCd = timer
                nextObs = 1 + random.random() * 2
                self.makeObstacle()
                
            if timer - missCd >= nextMiss:
                missCd = timer
                nextObs = 1 + random.random() * 2
                self.makeMissile()

            for obstacle in self._obstacles:

                if type(obstacle) == (Obstacle):
                    obstacle.move(self.speed)
                    self.drawObstacle(obstacle)
                else:
                    if obstacle.move(self._player):
                        self.destroyObstacle(obstacle)
                    self.drawMissile(obstacle)

            if self._state == 'endScreen':
                self.endScreen()

            self.drawPlayer()
            self.window.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()




# Driver code

def main():
    pygame.init()
    window = Window(1280, 720,bgImage= "bg.png")
    player = Player(140, 60, 20, "crab.png")
    game = Engine(window, player)
    game.runGame()



if __name__ == "__main__":
    main()