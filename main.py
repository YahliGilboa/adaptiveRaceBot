import os.path #library that is used to access files to
from Entity import Entity
from Player import Player
from CollisionBox import CollisionBox
from Car import Car
import pygame
import math
import random
import neat

screenWidth,screenHeight = 1352,855 #defining window height according to background image size
WIN = pygame.display.set_mode((screenWidth,screenHeight)) #defining the window through pygame - so we can
#use it to open a window on screen in the resulotion of the background

#this list contains lists of: frames until spawn,lane,color,velocity
#this list contains a constant wave of cars to check validity of input layer.
listSpawnCars = [[100,0,0,5],[20,1,0,5],[20,2,0,5],[40,4,0,3],
                 [120,0,0,6],[40,2,0,8],[20,1,0,3],[20,3,0,8],[40,4,0,4]]

menuScreen = pygame.image.load(os.path.join('images', 'menuScreen.png')).convert_alpha()
raceCar = pygame.image.load(os.path.join('images','raceCarPNG.png')).convert_alpha()
background = pygame.image.load(os.path.join('images','backgroundPNG.png')).convert_alpha()
blueCar = pygame.image.load(os.path.join('images','blueCar.png')).convert_alpha()
greenCar = pygame.image.load(os.path.join('images','greenCar.png')).convert_alpha()
explosionIMG = pygame.image.load(os.path.join("images","explosionIMG.png")).convert_alpha()
heart = pygame.image.load(os.path.join("images","healthPNG.png")).convert_alpha()

FPS = 60
startingPos = [screenWidth//2 - raceCar.get_width()//2, screenHeight*0.6]

Lborder,Rborder,Tborder,Bborder = 409, 942,-1,855 #borders

racerHealth = 1

#120 frames of immunty, while game runs at 60 frames per second, meaning 2 seconds of immunity
immunityTime = 120
explosionMaxTime = 45

# the car collision box
carCollider = [CollisionBox(13, 0, 48, 7), CollisionBox(4, 7, 65, 108), CollisionBox(9, 115, 55, 14)]

#list of "collision boxes" - offsetX from start pos, offsetY from start pos, width and height.
raceCarCollider  = [CollisionBox(5, 70, 45, 85),
CollisionBox(9, 6, 37, 64)]

explosionCollider = [CollisionBox(17,24,17,76),CollisionBox(34,17,74,87),
CollisionBox(108,26,8,73), CollisionBox(116,34,7,63), CollisionBox(123,46,10,39) ]

racerMaxVelocity = 6
carLimit = 5

breakFromMain = False

#checks for collisions between racer and cars.
#goes through each car, and uses internal function of class entity "isCollided" in order
#to figure out if the 2 entities have collided. if so, decrase racer's health
def checkCollisions(racer,Cars):
    for car in Cars:
        if racer.isCollided(car) and racer.immunity == 0:
            racer.decHealth()
            racer.immunity = immunityTime
            #racer- rocket collision:



def spawnCar(lane,color,velocity,Cars):
    #if 4 lanes are occupied, and this cars lane is the one left do not spawn unless the
    # velocity is greater or smaller to the one of the average of all cars velocity (preventing line of cars technique)

    #===================================================================================================
    occupiedLanes = [0,0,0,0,0]
    avgVel = 0
    canSpawn = True

    #checks how many cars are in each lane
    if len(Cars) != 0: #makes sure there wont be division by 0
        for car in Cars:
            occupiedLanes[car.lane] =+ 1
            avgVel += car.velocity[1]
        avgVel = avgVel//len(Cars)
        amountOccupied = 0

        #checks how many lanes are occupied
        for element in occupiedLanes:
            if element > 0:
                amountOccupied += 1

        if amountOccupied  >= 4:
            if velocity == avgVel:
                canSpawn = False
    #==========================================================

    #if there is car in current lane while trying to spawn this car, and this car's velocity is greater dont spawn it.
    # if it is smaller equal to the smallest car velocity in that lane and distance from that car to top is
    # greater than 150, spawn the car
    #==============================================================
    minCarVel = 0  #will contain every car in same lane as this car.
    closestToTop = 0
    for car in Cars:
        if car.lane == lane:
            minCarVel = car.velocity[1] #getting a value from the sample
            closestToTop = car.position[1]

    for car in Cars:
        if car.lane == lane:
            minCarVel = min(minCarVel,car.velocity[1])
            closestToTop = min(closestToTop,car.position[1])

    if occupiedLanes[lane] > 0:
        if minCarVel < velocity:
            canSpawn = False
        elif closestToTop <= 180:
            canSpawn = False
    #======================================================================

    #if there are less cars than the car limit and the car can spawn, spawn it
    if len(Cars) < carLimit and canSpawn:
        grassLength = 409
        roadOffsetleft = 14
        laneDiff = 108
        spawnPos = [grassLength + roadOffsetleft + laneDiff * lane, -blueCar.get_height()]  # at x axis added the grass
        # length size, added the distance needed from left of the road and added
        # multiplication of road thickness, according to lane number
        texture = blueCar
        if color == 1:
            texture = greenCar
        Cars.append(Car(spawnPos, carCollider, [0, 1 * velocity], lane, texture))

#spawns random values for car
def randomiserCar(Cars):#will handle return a car object, if no car spawns return -1

    if random.randint(1,20) > 19: #spawns random car in the probability of 1/20
        lane = random.randint(0, 4)
        color = random.randint(0, 1)
        velocity =  (random.randint(3, 8))
        spawnCar(lane,color,velocity,Cars)


#handels the despawn of cars
def handleDespawn(Cars): #will handle despawn of all objects (cars, rockets, etc)
    for car in Cars:
        if car.position[1] >= screenHeight:
            Cars.remove(car)

#draws player current health
def handleDrawnHealth(racer):
    startOffset = [50,50]
    for i in range(racer.health):
        WIN.blit(heart,tuple(startOffset))
        startOffset[0] += 60

#converts between output of neural network to direction of movement
def indexToMove(index,racer):
    if index == 0:
        racer.velocity[0] = 0
        racer.velocity[1] = -racerMaxVelocity

    if index == 1:
        racer.velocity[0] = racerMaxVelocity
        racer.velocity[1] = -racerMaxVelocity

    if index == 2:
        racer.velocity[0] = racerMaxVelocity
        racer.velocity[1] = 0

    if index == 3:
        racer.velocity[0] = racerMaxVelocity
        racer.velocity[1] = racerMaxVelocity

    if index == 4:
        racer.velocity[0] = 0
        racer.velocity[1] = racerMaxVelocity

    if index == 5:
        racer.velocity[0] = -racerMaxVelocity
        racer.velocity[1] = racerMaxVelocity

    if index == 6:
        racer.velocity[0] = -racerMaxVelocity
        racer.velocity[1] = 0

    if index == 7:
        racer.velocity[0] = -racerMaxVelocity
        racer.velocity[1] = -racerMaxVelocity

#this code makes sure  car stays within bounds
    moveAfterChangeX = racer.position[0] + racer.velocity[0]
    moveAfterChangeY = racer.position[1] + racer.velocity[1]

    if moveAfterChangeX + racer.texture.get_width() > Rborder:
        racer.velocity[0] = 0
        racer.position[0] = Rborder - racer.texture.get_width()

    if moveAfterChangeX <= Lborder:
        racer.velocity[0] = 0
        racer.position[0] = Lborder

    if moveAfterChangeY <= Tborder:
        racer.velocity[1] = 0
        racer.position[1] = Tborder

    if moveAfterChangeY + racer.texture.get_height() >= Bborder:
        racer.velocity[1] = 0
        racer.position[1] = Bborder - racer.texture.get_height()

    racer.changePos()

#draws all entities on the screen, if racer is not list than it is single racer.
def draw_win(background,racers,Cars):
    WIN.blit(background,(0,0))
    if type(racers) is list:
        WIN.blit(racers[0].texture, tuple(racers[0].position))
        handleDrawnHealth(racers[0])
    else:
        WIN.blit(racers.texture, tuple(racers.position))
        handleDrawnHealth(racers)
    for car in Cars:
        WIN.blit(car.texture,tuple(car.position))


    pygame.display.update() #actually updates all changes made to screen

#converts key press to player velocity
def handlePlayerMovement(racer,keysPressed):
    if keysPressed[pygame.K_a]:
            racer.velocity[0] = -racerMaxVelocity
    if keysPressed[pygame.K_d]:
            racer.velocity[0] = racerMaxVelocity
    if not keysPressed[pygame.K_d] and not keysPressed[pygame.K_a]: #when nothing pressed: dont move.
        racer.velocity[0] = 0
    if keysPressed[pygame.K_w]:
        racer.velocity[1] = -racerMaxVelocity
    if keysPressed[pygame.K_s]:
        racer.velocity[1] = racerMaxVelocity
    if not keysPressed[pygame.K_w] and not keysPressed[pygame.K_s]:#when nothing pressed: dont move.
        racer.velocity[1] = 0

#this code limits the racer to move over from the border
    moveAfterChangeX = racer.position[0] + racer.velocity[0]
    moveAfterChangeY = racer.position[1] + racer.velocity[1]

    if moveAfterChangeX + racer.texture.get_width() > Rborder:
        racer.velocity[0] = 0
        racer.position[0] = Rborder - racer.texture.get_width()

    if moveAfterChangeX <= Lborder:
        racer.velocity[0] = 0
        racer.position[0] = Lborder

    if moveAfterChangeY <= Tborder:
        racer.velocity[1] = 0
        racer.position[1] = Tborder

    if moveAfterChangeY + racer.texture.get_height() >= Bborder:
        racer.velocity[1] = 0
        racer.position[1] = Bborder - racer.texture.get_height()

    racer.changePos()

#gets inputs from environment and converts them to a list the network could understand
def retInputs(Cars, racer):
        normliser = 10000 #this value is used so that the tanh function will not just give aproximations of
        # -1 and 1 to values (good for games like flappy bird and internet dinosaur, not for my game)
        racerLatitude = racer.position[1] + 75  # latitude line, around the middle of the car
        racerXpos = racer.position[0] + 31 #gives the x coordinate of middle of racer
        # classify cars for individual lanes
        lanes = [[], [], [], [], []]
        for car in Cars:
            lanes[car.lane].append(car)
        output = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1,racerXpos/normliser]
        index = 0
        for lane in lanes:
            for car in lane:
                dist = (racerLatitude - car.position[1])/normliser  # this is distance over latitude line
                if dist > 0:
                    if output[index] == -1:
                        output[index] = dist
                    else:
                        output[index] = min(output[index], dist)

                if dist <= 0:
                    if output[index + 1] == -1:
                        output[index + 1] = abs(dist)
                    else:
                        output[index + 1] = min(output[index], abs(dist))

            index += 2
        return output

def main(genomes,config):
    global breakFromMain
    nets = []
    ge = []
    racers = []
    score = 0
    gameTick = 0
    Cars = []
    spawncarIndex = 0 #variable used for the known set of cars, in order to check validation of a learning curve.

    for _, g in genomes: #genomes contains lists tuples of genomes of each network,
        # underscore for ignoring the id part in the tuple .
        net = neat.nn.FeedForwardNetwork.create(g,config)
        nets.append(net) #adds the net to list of nets
        racers.append(Player(startingPos, raceCarCollider, [0, 0], raceCar, racerHealth, 0)) #adds racer
        # that correspinds with net
        g.fitness = 0 #players initial fitness is 0
        ge.append(g) #adds g to list of genomes

    #clock = pygame.time.Clock() #OPTIONAL: this is if we want the game to run in frames, for ex 60 frames per second
    stop = False

    while (stop != True):#while the game isnt supposed to stop, it will run
        #clock.tick(FPS) #OPTIONAL: makes sure the while loop runs 60 FPS, not more.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop = True
                pygame.quit()
                quit()


     #lines below are when player wants to play. screen to switch will be implemented in future:
      #keysPressed = pygame.key.get_pressed()
        #handlePlayerMovement(racer,keysPressed)

        for car in Cars:
            car.changePos()

        for racer in racers:
            checkCollisions(racer,Cars)

        handleDespawn(Cars)

        #kills all losing racers
        for x, racer in enumerate(racers):  #meaning, for index x corresponding with object "racer" in iterable "racers"
            if racer.health == 0:
                ge[x].fitness -= 240
                racers.pop(x)
                nets.pop(x)
                ge.pop(x)


        #makes a move
        for x, racer in enumerate(racers):
            ge[x].fitness += 1
            outputs = nets[x].activate(tuple(retInputs(Cars,racer)))

            # this decides what the player will do
            #find max output, meaning what car wants to go to:

            max = outputs[0]
            index = 0
            for i,output in enumerate(outputs):
                if output > max:
                    index = i
            indexToMove(index, racer)


        if len(racers) == 0:
            stop = True
            break

        for racer in racers:
            if racer.immunity != 0:
                racer.immunity -= 1
        score += 1
        gameTick += 1

        #Optional: this code is for testing if the model can even learn. sets known course and tries to run the
        #networks untill it goes over a certain threshold
        if listSpawnCars[spawncarIndex][0] == gameTick:
            gameTick = 0
            spawnCar(listSpawnCars[spawncarIndex][1],listSpawnCars[spawncarIndex][2],
            listSpawnCars[spawncarIndex][3],Cars)
            spawncarIndex += 1
        if spawncarIndex == 8:
            spawncarIndex = 0

        #this iis for stopping game
        keysPressed = pygame.key.get_pressed()
        if keysPressed[pygame.K_ESCAPE]:
            ge[0].fitness = 2000 # so we could stop p.run from continuing to run
            score = 2000
        if score > 1800:
            break
        draw_win(background,racers,Cars)

def runGame():
    racer = Player(startingPos, raceCarCollider, [0, 0], raceCar, racerHealth, 0)
    score = 0
    gameTick = 0
    Cars = []
    clock = pygame.time.Clock() #OPTIONAL: this is if we want the game to run in frames, for ex 60 frames per second
    stop = False

    while (stop != True):  # while the game isnt supposed to stop, it will run
        clock.tick(FPS) #OPTIONAL: makes sure the while loop runs 60 FPS, not more.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop = True
                pygame.quit()
                quit()

        keysPressed = pygame.key.get_pressed()
        if keysPressed[pygame.K_ESCAPE]:
            break

        handlePlayerMovement(racer,keysPressed)
        for car in Cars:
            car.changePos()

        checkCollisions(racer, Cars)

        randomiserCar(Cars)

        handleDespawn(Cars)

        if racer.immunity != 0:
            racer.immunity -= 1


        draw_win(background, racer, Cars)



def run(config_path):
    global breakFromMain
    config = neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main,1000)
    breakFromMain = False #resets so it can run again after the break from main

def startScreen():
    global racerHealth
    stop = False
    while (stop != True):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop = True
                pygame.quit()
                quit()

        WIN.blit(menuScreen, (0, 0))
        keysPressed = pygame.key.get_pressed()
        pygame.display.update()  # actually updates all changes made to screen
        if keysPressed[pygame.K_0]:
            racerHealth = 1
            local_dir = os.path.dirname(__file__)
            config_path = os.path.join(local_dir, "ConfigFile.txt")
            run(config_path)
        if keysPressed[pygame.K_1]:
            racerHealth = 3
            runGame()

if __name__ == "__main__": #this line makes sure that if an external file that imports this
    # code tries to run this it wont be able to
    startScreen()





