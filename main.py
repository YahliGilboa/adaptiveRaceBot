import os.path
from Entity import Entity
from Player import Player
from CollisionBox import CollisionBox
from Car import Car
from Rocket import Rocket
from Explosion import Explosion
import pygame
import math
import random
import neat
import pickle

screenWidth,screenHeight = 1352,855 #defining window height according to background image size
WIN = pygame.display.set_mode((screenWidth,screenHeight)) #defining the window through pygame - so we can use it to open a window on screen in the resulotion of the background

drawColCar = 0
drawColRaceCar = 0

raceCar = pygame.image.load(os.path.join('images','raceCarPNG.png')).convert_alpha()
background = pygame.image.load(os.path.join('images','backgroundPNG.png')).convert_alpha()
blueCar = pygame.image.load(os.path.join('images','blueCar.png')).convert_alpha()
greenCar = pygame.image.load(os.path.join('images','greenCar.png')).convert_alpha()
rocketIMG = pygame.image.load(os.path.join("images","rocketEnemy.png")).convert_alpha()
explosionIMG = pygame.image.load(os.path.join("images","explosionIMG.png")).convert_alpha()
heart = pygame.image.load(os.path.join("images","healthPNG.png")).convert_alpha()

FPS = 1
startingPos = [screenWidth//2 - raceCar.get_width()//2, screenHeight*0.6]

Lborder,Rborder,Tborder,Bborder = 409, 942,-1,855 #borders

racerHealth = 1

immunityTime = 120 #120 frames of immunty, while game runs at 60 frames per second, meaning 2 seconds of immunity
rocketMinTime = 120
rocketMaxTime = 360
rocketTimer = 0
rocketTargetTime = 0
explosionMaxTime = 45

carCollider = [CollisionBox(13, 0, 48, 7), CollisionBox(4, 7, 65, 108), CollisionBox(9, 115, 55, 14)] #the car collision box
raceCarCollider  = [CollisionBox(5, 70, 45, 85), CollisionBox(9, 6, 37, 64)] #list of "collision boxes" - offsetX from start pos, offsetY from start pos, width and height.
rocketCollider = [CollisionBox(40, 6, 22, 52), CollisionBox(62, 14, 44, 35), CollisionBox(106, 18, 11, 28)]
explosionCollider = [CollisionBox(17,24,17,76),CollisionBox(34,17,74,87), CollisionBox(108,26,8,73), CollisionBox(116,34,7,63), CollisionBox(123,46,10,39) ]

racerMaxVelocity = 6
carLimit = 6


def checkCollisions(racer,Cars,rocket):
    global drawColCar,drawColRaceCar
    for car in Cars:
        if racer.isCollided(car) and racer.immunity == 0:
            drawColCar = car
            drawColRaceCar = 1
            racer.decHealth()
            racer.immunity = immunityTime
            #racer- rocket collision:
    if rocket[0] != None and racer.immunity == 0:
        if racer.isCollided(rocket[0]):
            spawnExplosion(rocket)
            rocket[0] = None
            racer.decHealth()
            racer.immunity = immunityTime
        else:
            for car in Cars:
                if rocket[0].isCollided(car):
                    spawnExplosion(rocket)
                    rocket[0] = None
                    Cars.remove(car)
                    break
    if rocket[1] != 0 and racer.immunity == 0:
        if racer.isCollided(rocket[1]):
            racer.decHealth()
            racer.immunity = immunityTime

def spawnExplosion(rocket):
    if rocket[0].side == 0:
        rocket[1] = Explosion([rocket[0].position[0]+50,rocket[0].position[1]-33],explosionCollider,[0,0],explosionMaxTime,explosionIMG)
        rocket[0] = None
    else:
        rocket[1] = Explosion([rocket[0].position[0] + rocket[0].texture.get_width()- 50 - explosionIMG.get_width(), rocket[0].position[1] - 33], explosionCollider, [0, 0],explosionMaxTime, explosionIMG)
        rocket[0] = None
def spawnCar(lane,color,velocity,Cars):
    #if 4 lanes are occupied, and this cars lane is the one left do not spawn unless the velocity is greater or smaller to the one of the average of all cars velocity (preventing line of cars technique)

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
            if occupiedLanes[element] > 0:
                amountOccupied += 1

        if amountOccupied  >= 4:
            if velocity == avgVel:
                canSpawn = False
    #==========================================================



    #if there is car in current lane while trying to spawn this car, and this car's velocity is greater dont spawn it. if it is smaller equal to the smallest car velocity in that lane and distance from that car to top is greater than 150, spawn the car

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

    if len(Cars) < carLimit and canSpawn:
        grassLength = 409
        roadOffsetleft = 14
        laneDiff = 108
        spawnPos = [grassLength + roadOffsetleft + laneDiff * lane, -blueCar.get_height()]  # at x axis added the crass length size, added the distance needed from left of the road and added multiplication of road thickness, according to lane number
        texture = blueCar
        if color == 1:
            texture = greenCar
        Cars.append(Car(spawnPos, carCollider, [0, 1 * velocity], lane, texture))

def randomiserCar(Cars):#will handle return a car object, if no car spawns return -1

    #implent next: add if lane is occupied and car is not within set length of the top of the lane, spawn car in next lane. but if over set length and lane is occupied then spawn car that has same or less speed (or more by 1)
    #also change car generate system, cap will be more than 4 but cars cannot live or spawn within certain distabce of eachother (can be implemented with previous funcs)

    if random.randint(1,10000) > 9500: #needs to be changes to timer (pygame.time.set_timer())
        lane = random.randint(0, 4)
        color = random.randint(0, 1)
        velocity =  (random.randint(3, 8))
        spawnCar(lane,color,velocity,Cars)

def handleRocket(rocket,racer):
    global rocketMinTime, rocketMaxTime, rocketTimer, rocketTargetTime
    #print(rocketTimer)
    if rocket[0] == None:
        if rocketTargetTime == 0:
            rocketTargetTime = random.randint(rocketMinTime,rocketMaxTime)
        if rocketTimer == rocketTargetTime:
            side = random.randint(0,1) #side of rocket spawn, 0 is left 1 is right
            rndmAddRocket = (random.randint(0,200)*(racer.velocity[1]/6))
            if side == 0:
                rocket[0] = Rocket([-rocketIMG.get_width(),racer.position[1]+83+rndmAddRocket], rocketCollider, [5, 0], side, rocketIMG) #spawns rocket "around" middle of player (83 from plyer position) the player y location and depending ton which way he is going, spawns at speed that wil seem like screen is moving forward, "screen speed" is 2


            else:
                rocket[0] = Rocket([rocketIMG.get_width()+screenWidth, racer.position[1] + 83+rndmAddRocket], rocketCollider[::-1], [-5, 0], side, pygame.transform.rotate(rocketIMG, 180))#rotate image,flip collision box by slicing

            rocketTimer = 0
            rocketTargetTime = 0

        else:
            rocketTimer += 1
    elif rocket[0].velocity[0] < 0:
        if rocket[0].velocity[0] > -15:
            rocket[0].velocity[0] -= 0.2
    else:
        if rocket[0].velocity[0] < 15:
            rocket[0].velocity[0] += 0.2

def handleDespawn(Cars,rocket): #will handle despawn of all objects (cars, rockets, etc)
    for car in Cars:
        if car.position[1] >= screenHeight:
            Cars.remove(car)
    if rocket[0] != None:
        # if rocket[0].position[1] == screenHeight:
        #     rocket[0] = None
        if rocket[0].side == 0:
            if rocket[0].position[0] >= screenWidth:
                rocket[0] = None
        else:
            if rocket[0].position[0] <= 0 - rocket[0].texture.get_width():
                rocket[0] = None
    if rocket[1] != 0:
        if rocket[1].deSpawnTimer == 0:
            rocket[1] = 0
        else:
            rocket[1].deSpawnTimer -= 1

def draw_collider(entity):
    for collisionBox in entity.collider:
        pygame.draw.rect(WIN, (255, 255, 255), pygame.Rect(entity.position[0]+collisionBox.offsetX,entity.position[1]+collisionBox.offsetY,collisionBox.width,collisionBox.height))

def handleDrawnHealth(racer):
    startOffset = [50,50]
    for i in range(racer.health):
        WIN.blit(heart,tuple(startOffset))
        startOffset[0] += 60

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


def draw_win(background,racers,Cars,rocket):
    global drawColCar,drawColRaceCar
    #print(drawColCar,drawColRaceCar)
    WIN.blit(background,(0,0))
    #if drawColCar != 0:
        #draw_collider(drawColCar)
       # drawColCar = 0
    #if drawColRaceCar != 0:
        #draw_collider(racer)
       # drawColRaceCar = 0
    # draw_collider(racer)
    # for car in Cars:
    #     draw_collider(car)
    for racer in racers:
        WIN.blit(raceCar, tuple(racer.position))
    for car in Cars:
        WIN.blit(car.texture,tuple(car.position))
        #handleDrawnHealth(racer)
        if rocket[0] != None:
            WIN.blit(rocket[0].texture, tuple(rocket[0].position))
        if rocket[1] != 0:
            WIN.blit(rocket[1].texture,tuple(rocket[1].position))
    pygame.display.update() #actually updates all changes made to screen


def retInputs(Cars, racer, rocket):
        normliser = 100000 #this value is used so that the tanh function will not just give aproximations of -1 and 1 to values (good for games like flappy bird and internet dinosaur, not for my game)
        racerLatitude = racer.position[1] + 75  # latitude line, around the middle of the car
        racerXpos = racer.position[0] + 31 #gives the x coordinate of middle of racer
        # classify cars for individual lanes
        lanes = [[], [], [], [], []]
        for car in Cars:
            lanes[car.lane].append(car)
        output = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,racerXpos/normliser]
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

        if rocket[0] != None:
            output[10] = ((racer.position[0] + 28) - rocket[0].position[0])/normliser
            output[11] = (racerLatitude - rocket[0].position[1])/normliser
        return output

def main(genomes,config):
    nets = []
    ge = []
    racers = []
    score = 0
    for _, g in genomes: #genomes contains lists tuples of genomes of each network, underscore for ignoring the id part in the tuple .
        net = neat.nn.FeedForwardNetwork.create(g,config)
        nets.append(net) #adds the net to list of nets
        racers.append(Player(startingPos, raceCarCollider, [0, 0], raceCar, racerHealth, 0)) #adds racer that correspinds with net
        g.fitness = 0 #players initial fitness is 0
        ge.append(g) #adds g to list of genomes
    #racer = Player(startingPos, raceCarCollider, [0, 0], raceCar, racerHealth, 0)
    # for racer in racers:
    #     print(racer)
    #     print(racer.position)
    #     print("\n")
    Cars =[]
    rocket = [None,0] #if rocket is 0 then there is no rocket on field. if it is a rocket type object than this object will act accordingly on field, second cell is for explosion. has to be list so i can pass by reference
    #clock = pygame.time.Clock()
    stop = False

    while (stop != True):#while the game isnt supposed to stop, it will run
        #clock.tick(FPS)#makes sure the while loop runs 60 FPS, not more.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop = True
                pygame.quit()
                quit()
      #keysPressed = pygame.key.get_pressed()
        #handlePlayerMovement(racer,keysPressed)
        for car in Cars:
            car.changePos()
        if rocket[0] != None:
            rocket[0].changePos()
        for racer in racers:
            checkCollisions(racer,Cars,rocket)
            handleRocket(rocket, racer)

        randomiserCar(Cars)

        handleDespawn(Cars, rocket)


        #kills all losing racers
        for x, racer in enumerate(racers):  # meaning, for index x corresponding with object "bird" in iterable "birds"
            if racer.health == 0:
                ge[x].fitness -= 100
                racers.pop(x)
                nets.pop(x)
                ge.pop(x)

        # for x, racer in enumerate(racers):
        #     if racer.position[0] <= Lborder or racer.position[0] + racer.texture.get_width() >= Rborder:
        #         ge[x].fitness -= 1
        #     if racer.position[1] <= Tborder:
        #         ge[x].fitness -= 10
        #     if racer.position[1] + racer.texture.get_height() >= Bborder:
        #         ge[x].fitness += 0.5



        for x, racer in enumerate(racers):
            # print(racer)
            # print(racer.position)
            ge[x].fitness += 1
            outputs = nets[x].activate(tuple(retInputs(Cars,racer,rocket)))

                # this decides what the player will do
                #find max output, meaning what car wants to go to:
                #
            # for output in outputs:
            #     print(output)

            max = outputs[0]
            index = 0
            for i,output in enumerate(outputs):
                if output > max:
                    index = i
            #print(index)
            indexToMove(index, racer)


        # print("\n")
        # print(len(racers))
        if len(racers) == 0:
            stop = True
            break

        for racer in racers:
            if racer.immunity != 0:
                racer.immunity -= 1

        draw_win(background,racers,Cars,rocket)
        score += 1
        if score > 1000:
            break







def run(config_path):
    config = neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,neat.DefaultSpeciesSet,neat.DefaultStagnation,config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main,10000)
    pickle_out = open("theBot","wb")
    pickle.dump(winner,pickle_out)
    pickle_out.close()
if __name__ == "__main__": #this line makes sure that if an external file that imports this code tries to run this it wont be able to
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "ConfigFile.txt")
    run(config_path)


#