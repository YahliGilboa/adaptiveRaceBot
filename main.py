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
#this list contains a constant wave for the raceCar to learn from in the bot portion of the game
listSpawnCars = [[100,0,0,5],[20,1,1,5],[20,2,0,5],[40,4,1,3],
                 [120,0,1,6],[40,2,0,8],[20,1,1,3],[20,3,0,8],[40,4,1,4]]

#these variables hold the image files to use to draw the objects on screen
menuScreen = pygame.image.load(os.path.join('images', 'menuScreen.png')).convert_alpha()
raceCar = pygame.image.load(os.path.join('images','raceCarPNG.png')).convert_alpha()
background = pygame.image.load(os.path.join('images','BGWithEnvironment.png')).convert_alpha()
blueCar = pygame.image.load(os.path.join('images','blueCar.png')).convert_alpha()
greenCar = pygame.image.load(os.path.join('images','greenCar.png')).convert_alpha()
explosionIMG = pygame.image.load(os.path.join("images","explosionIMG.png")).convert_alpha()
heart = pygame.image.load(os.path.join("images","healthPNG.png")).convert_alpha()

#environment variables
FPS = 60 #frames per second for player
startingPos = [screenWidth//2 - raceCar.get_width()//2, screenHeight*0.6] #the starting position of racers
Lborder,Rborder,Tborder,Bborder = 409, 942,-1,855 #borders that racers cant go past

#racer health varibles
racerHealth = 1
immunityTime = 120 #120 frames of immunty, while game runs at 60 frames per second, meaning 2 seconds of immunity

#list of "collision boxes" - offsetX from start pos, offsetY from start pos, width and height.
raceCarCollider  = [CollisionBox(5, 70, 45, 85),
CollisionBox(9, 6, 37, 64)]
carCollider = [CollisionBox(13, 0, 48, 7), CollisionBox(4, 7, 65, 108), CollisionBox(9, 115, 55, 14)]

#enemy car variables
racerMaxVelocity = 6
carLimit = 5

#this is the moving backround list
BG = [Entity([0,0],[0],[0,2],background),Entity([0,-855],[0],[0,2],background)]
#checks for collisions between racer and cars.
#goes through each car, and uses internal function of class entity "isCollided" in order
#to figure out if the 2 entities have collided. if so, decrase racer's health
def checkCollisions(racer,Cars):
    for car in Cars:
        if racer.isCollided(car) and racer.immunity == 0:
            racer.decHealth()
            racer.immunity = immunityTime


#spawns cars according to limitations documented in the function
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
def randomiserCar(Cars):
    if random.randint(1,20) > 19: #spawns random car in the probability of 1/20
        lane = random.randint(0, 4)
        color = random.randint(0, 1)
        velocity =  (random.randint(3, 8))
        spawnCar(lane,color,velocity,Cars)


#handels the despawn of cars
def handleDespawn(Cars):
    for car in Cars:
        if car.position[1] >= screenHeight:
            Cars.remove(car)


#draws player current health
def handleDrawnHealth(racer):
    startOffset = [50,50]
    #for each health racer has, draw it in offsets of 60 pixels
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

def drawBackground():
    global BG
    for element in BG:
        element.changePos()
        WIN.blit(element.texture, tuple(element.position))
        if element.position[1] > 855:
            element.position[1] = -854 #because speed is 2, it moves from 855 to -855 in 1 step and second is 854

#draws all entities on the screen, if racer is not list than it is single racer.
def draw_win(background,racers,Cars):
    #draws background
    drawBackground()

    #if racer is list then draw the first racer in the list (game mode 0) if it isnt
    # then move it like one racer (game mode 1)
    if type(racers) is list:
        for racer in racers:
            WIN.blit(racer.texture, tuple(racer.position))
            handleDrawnHealth(racer)
    else:
        WIN.blit(racers.texture, tuple(racers.position))
        handleDrawnHealth(racers)

    #draws cars
    for car in Cars:
        WIN.blit(car.texture,tuple(car.position))

    #updates display on screen
    pygame.display.update()

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
#returns the closest car in every lane, in front and back of the racer, and the x distance from left of lanes.
def retInputs(Cars, racer):
        normliser = 10000 #this value is used so that the tanh function will not just give aproximations of
        # -1 and 1 to values (good for games like flappy bird and internet dinosaur, not for my game)
        racerLatitude = racer.position[1] + 75  # latitude line, around the middle of the car
        racerXpos = racer.position[0] + 31 #gives the x coordinate of middle of racer

        # classify cars for individual lanes
        #================================================================================================
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

            index += 2 #goes on to finalize the 2 next outputs (front and back)
            # ==========================================================================================
        return output

def main(genomes,config):
    nets = []
    ge = []
    racers = []
    score = 0
    gameTick = 0
    Cars = []
    spawncarIndex = 0 #variable used for the known set of cars, in order to check validation of a learning curve.

    for _, g in genomes: #genomes contains lists tuples of ID's and genomes of each network,
        # underscore for ignoring the id part in the tuple.
        net = neat.nn.FeedForwardNetwork.create(g,config)
        nets.append(net) #adds the net to list of nets
        racers.append(Player(startingPos, raceCarCollider, [0, 0], raceCar, racerHealth, 0)) #adds racer
        # that corresponds with net
        g.fitness = 0 #players initial fitness is 0
        ge.append(g) #adds g to list of genomes

    stop = False #stop condition for the while loop of game
    while (stop != True):#while the game isnt supposed to stop, it will run
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop = True
                pygame.quit()
                quit()

        #changes position for every car
        for car in Cars:
            car.changePos()

        #changes position for every racer
        for racer in racers:
            checkCollisions(racer,Cars)

        #handles despawn of cars
        handleDespawn(Cars)

        #"kills" all losing racers (pops them out of their lists)
        for x, racer in enumerate(racers):  #meaning, for index x corresponding with object "racer" in iterable "racers"
            if racer.health == 0:
                ge[x].fitness -= 240
                racers.pop(x)
                nets.pop(x)
                ge.pop(x)


        #makes a move for each racer according to inputs
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

        #if all racers have "died" break out of this loop, crossover and mutate genomes and then return
        if len(racers) == 0:
            stop = True
            break

        #increments score and number current frame between car spawn frames
        score += 1
        gameTick += 1

        #this code is for testing the model sets known course and tries to run the
        #networks until it goes over a certain threshold
        #gameTick represents the current time tick between car spawns spawcarIndex is the current car to be
        #summoned from listSpawnCars
        if listSpawnCars[spawncarIndex][0] == gameTick:
            gameTick = 0
            spawnCar(listSpawnCars[spawncarIndex][1],listSpawnCars[spawncarIndex][2],
            listSpawnCars[spawncarIndex][3],Cars)
            spawncarIndex += 1
        if spawncarIndex == 8:
            spawncarIndex = 0

        #this is for stopping game when esc is pressed. we make the outer function p.run() think there is a fitting
        #genome that passes fitness threshold, then the function stops because there is a fitting genome.
        keysPressed = pygame.key.get_pressed()
        if keysPressed[pygame.K_ESCAPE]:
            ge[0].fitness = 2000 # so we could stop p.run from continuing to run
            score = 2000
        #stops the game due to previous condition and if the bot has cracked the pattern, so it wont go over to a
        #never ending loop (loop will only stop if broken manually)
        if score > 1800:
            break
        draw_win(background,racers,Cars)

def runGame():
    racer = Player(startingPos, raceCarCollider, [0, 0], raceCar, racerHealth, 0)
    Cars = []
    clock = pygame.time.Clock() #sets the clock of the game so we can make sure the screen
    # doesnt refresh more than 60 fps
    stop = False

    while (stop != True):  # while the game isnt supposed to stop, it will run
        clock.tick(FPS) #OPTIONAL: makes sure the while loop runs 60 FPS, not more.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop = True
                pygame.quit()
                quit()

        #checks if a key has been pressed
        keysPressed = pygame.key.get_pressed()

        #if key is escape, break
        if keysPressed[pygame.K_ESCAPE]:
            break

        #changes posiotion for every car
        for car in Cars:
            car.changePos()

        #handles game
        #========================================
        handlePlayerMovement(racer,keysPressed)

        checkCollisions(racer, Cars)

        randomiserCar(Cars)

        handleDespawn(Cars)
        #=======================================

        #checks if racer is not immune, reduce his immunity
        if racer.immunity != 0:
            racer.immunity -= 1

        #if racer loses, break out of the loop
        if racer.health == 0:
            break

        #updates screen
        draw_win(background, racer, Cars)


#function used for initializing the population according to config file. also is in charge of creating a reporter object
#that views the generation and population status
def run(config_path):
    #converts config file to neat format
    config = neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,config_path)

    #creates population of racers
    p = neat.Population(config)

    #creates a reporter to show learning stats
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    #runs the learning procces
    p.run(main,1000)

#this is the first function to be run. it reperesents the starting screen, and the player can navagite from it to the 2
#game modes: teleop control and machine controlled.
def startScreen():
    global racerHealth #so it could updare racer health according to the game mode
    stop = False
    while (stop != True):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop = True
                pygame.quit()
                quit()

        #draws menu screen
        WIN.blit(menuScreen, (0, 0))
        #checks for key presses
        keysPressed = pygame.key.get_pressed()
        #updates display on screen
        pygame.display.update()

        #if 0 pressed, go to machine controlled
        if keysPressed[pygame.K_0]:
            racerHealth = 1
            local_dir = os.path.dirname(__file__) #reference the current directory
            config_path = os.path.join(local_dir, "ConfigFile.txt")#join the directory of config file to this directory
            #so we can acces it
            run(config_path)

        #if pressed 1, run the teleop game mode
        if keysPressed[pygame.K_1]:
            racerHealth = 3
            runGame()


if __name__ == "__main__": #this line makes sure that if an external file that imports this
    # code tries to run this it wont be able to
    startScreen()





