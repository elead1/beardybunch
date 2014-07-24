__author__ = 'Steven'

import pygame
import math

PI = math.pi

#Define colors
BLACK = (0, 0, 0)
RED =  (255, 0, 0)
BROWN = (139, 115, 85)
TAN = (219, 147, 112)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
SCARLET = (255, 36, 0)
MUSTARD = (255, 165, 79)
PLUM = (71, 60, 139)
PEACOCK_BLUE = (0, 0, 156)

#Greys
GREY = (84, 84, 84)
SILVER_GREY = (192, 192, 192)
GREY58 = (148, 148, 148)

screen_size = (1440, 900)

roomLength = 150
roomWidth = 150
roomBaseXOffset = 20
roomBaseYOffset = 20

playerHeight = 40
playerWidth = 25

cursorHeight = 10
cursorWidth = 10

roomBorder = 2

class Cursor(pygame.sprite.Sprite):
    """This class represents the Cursor"""

    def __init__(self):
        super(Cursor, self).__init__()
        cursorWidth=2
        cursorHeight=2
        self.image = pygame.Surface([cursorWidth, cursorHeight])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        # pygame.draw.ellipse(self.image, GREEN, [0, 0, cursorWidth, cursorHeight], 0)
        self.image = self.image.convert_alpha()
        self.layer = 99

        self.rect = self.image.get_rect()

    def update(self):
        pos = pygame.mouse.get_pos()

        self.rect.x, self.rect.y = pos

    def printPosition(self):
        print "cursor is at position: " + str(self.rect.x) + ", " + str(self.rect.y)


class Button(pygame.sprite.Sprite):
    def __init__(self, color, width, height, color):

        pass

class SuspectToken(pygame.sprite.Sprite):
    def __init__(self, color, xOffset=0, yOffset=0):
        super(SuspectToken, self).__init__()
        self.color = color
        self.image = pygame.Surface([playerHeight, playerWidth])
        # self.image.fill(color)
        self.image.set_colorkey(BLACK)
        pygame.draw.ellipse(self.image, color, [0, 0, playerHeight, playerWidth], 0)
        self.image = self.image.convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.x = xOffset
        self.rect.y = yOffset
        self.layer=2

    def update(self, xOffset, yOffset):
        self.rect.x = xOffset
        self.rect.y = yOffset
        pass


class Room(pygame.sprite.Sprite):
    def __init__(self, name, color, xOffset=0, yOffset=0, border=roomBorder):
        super(Room, self).__init__()
        self.name = name
        self.color = color
        self.border = border
        self.height = roomLength
        self.width = roomWidth
        self.image = pygame.Surface([self.height, self.width])
        # self.image.fill(BLACK)
        self.drawInside()
        self.rect = self.image.get_rect()
        self.rect.x = xOffset + roomBaseXOffset
        self.rect.y = yOffset + roomBaseYOffset
        self.layer=1
        self.hilight = False

        # print "Room " + self.name + " configured with: " + str(self.xOffset) + ", "+ str(self.yOffset) + \
        #       ", "+ str(self.length) + ", "+ str(self.width)

    def update(self):
        pass

    def toggleHilight(self):
        self.hilight = not self.hilight
        if self.hilight:
            self.image.fill(WHITE)
            print "Hilight on hallway."
        else:
            self.image.fill(BLACK)
            print 'Hilight off hallway."'

        self.drawInside()

    def drawInside(self):

        pygame.draw.rect(self.image, self.color, [self.border, self.border,
                                          self.height-(2*self.border),
                                          self.width-(2*self.border)])
        pass

class Hallway(pygame.sprite.Sprite):
    def __init__(self, color, vertical=False, xOffset=0, yOffset=0, border=roomBorder):
        super(Hallway, self).__init__()
        self.color = color
        size = [roomLength, roomWidth]
        xOff = xOffset
        yOff = yOffset
        self.border = border
        if vertical:
            self.vertical = 1
            self.height = roomLength / 3
            self.width = roomWidth
            xOff += self.height
        else:
            self.vertical = 0
            self.height= roomLength
            self.width = roomWidth / 3
            yOff += self.width

        self.image = pygame.Surface([self.height, self.width])
        # self.image.fill(BLACK)
        self.drawInside()
        self.rect = self.image.get_rect()
        print "Self height: "+ str(self.image.get_height()) + " width: " + str(self.image.get_width())
        self.rect.x = xOff + roomBaseXOffset
        self.rect.y = yOff + roomBaseYOffset
        self.layer=1
        self.hilight = False

    def update(self):
        pass

    def toggleHilight(self):
        self.hilight = not self.hilight
        if self.hilight:
            self.image.fill(WHITE)
            print "Hilight on hallway."
        else:
            self.image.fill(BLACK)
            print 'Hilight off hallway."'

        self.drawInside()

    def drawInside(self):

        pygame.draw.rect(self.image, self.color, [self.border, self.border,
                                          self.height-(2*self.border),
                                          self.width-(2*self.border)])
        pass

        # print "Room " + self.name + " configured with: " + str(self.xOffset) + ", "+ str(self.yOffset) + \
        #       ", "+ str(self.length) + ", "+ str(self.width)


class Card(pygame.sprite.Sprite):
    def __init__(self, name, color, image=None):
        self(Card, self).__init__()
        if image:
            pass

    def update(self):
        pass

    def toggleHilight(self):
        pass

class Notes(object):
    def __init__(self):
        pass

class Game(object):
    def __init__(self):

        self.all_sprites_list = pygame.sprite.LayeredUpdates()
        self.all_rooms_list = pygame.sprite.Group()
        self.all_suspectTokens_list = pygame.sprite.Group()
        self.all_weapons_list = pygame.sprite.Group()

        self.rooms = [(Room("Study", BROWN), Hallway(GREY, xOffset=roomWidth),
          Room("Hall", GREY, xOffset=2*roomWidth),
          Hallway(GREY, xOffset=3*roomWidth),
          Room("Lounge", TAN, xOffset=4*roomWidth)),
        (Hallway(GREY, vertical = True, yOffset=roomLength*1),
         Hallway(GREY, vertical = True, yOffset=roomLength*1, xOffset=roomWidth*2),
         Hallway(GREY, vertical = True, yOffset=roomLength*1, xOffset = (roomWidth*4))),
        (Room("Library", SCARLET, yOffset=roomLength*2),
         Hallway(GREY, yOffset=roomLength*2, xOffset=roomWidth),
         Room("Billiard Room", PEACOCK_BLUE, yOffset=roomLength*2, xOffset = roomWidth*2),
         Hallway(GREY, yOffset=roomLength*2, xOffset = roomWidth*3),
         Room("Dining Room", TAN, yOffset=roomLength*2, xOffset = roomWidth*4)),
        (Hallway(GREY, vertical = True, yOffset=roomLength*3),
         Hallway(GREY, vertical = True, yOffset=roomLength*3, xOffset=roomWidth*2),
         Hallway(GREY, vertical = True, yOffset=roomLength*3, xOffset = roomWidth*4)),
        (Room("Conservatory", BROWN, yOffset=roomLength*4),
         Hallway(GREY, yOffset=roomLength*4, xOffset=roomWidth),
         Room("Ball Room", MUSTARD, yOffset=roomLength*4, xOffset=roomWidth*2),
         Hallway(GREY, yOffset=roomLength*4, xOffset=roomWidth*3),
         Room("Kitchen", GREEN, yOffset=roomLength*4, xOffset=roomWidth*4))]

        self.suspects = [SuspectToken(GREEN), SuspectToken(MUSTARD, 100, 100)]

        self.weapons = []

        for roomRow in self.rooms:
            for room in roomRow:
                self.all_sprites_list.add(room)
                self.all_rooms_list.add(room)

        for suspect in self.suspects:
            self.all_suspectTokens_list.add(suspect)
            self.all_sprites_list.add(suspect)

        self.cursor = Cursor()
        self.all_sprites_list.add(self.cursor)

        self.selectedRoom = None
        self.selectedSuspect = None
        self.selectedWeapon = None

    def processEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.cursor.printPosition()
                hit_list = pygame.sprite.spritecollide(self.cursor, self.all_rooms_list, False)
                if hit_list:
                    self.selectedRoom = hit_list[0]
                print str(hit_list)

            return False

    def runLogic(self):
        self.cursor.update()
        if self.selectedRoom:
            self.selectedRoom.toggleHilight()
            self.selectedRoom = None


    def displayFrame(self, screen):
        screen.fill(GREY58)

        self.all_sprites_list.draw(screen)

        pygame.display.flip()

def main():

    pygame.init()

    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("The Beardy Bunch - Clue-less")

    # all_sprites_list = pygame.sprite.Group()

    done = False

    clock = pygame.time.Clock()
    # print "Room dimensions are: " + str(roomLength) + ", " + str(roomWidth)

    game = Game()


    while not done:
        #Process events
        done = game.processEvents()
        #Game logic to pudate positions, check collisions
        game.runLogic()
        #Draw the frame
        game.displayFrame(screen)
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()