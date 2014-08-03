__author__ = 'Steven'

import pygame
from pygame.locals import *
import math
import sys

PI = math.pi

ROOMS = {}

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
roomTitleXOffset = 10
roomTitleYOffset = 130

playerYOffset = 10 #40
playerXOffset = 10
playerXSpacer = 20
playerYSpacer = -5
playerHeight = 40
playerWidth = 25

PLUM_OFFSET=(playerXOffset, playerYOffset)
PEACOCK_OFFSET=(PLUM_OFFSET[0]+playerWidth+playerXSpacer,PLUM_OFFSET[1])
MUSTARD_OFFSET=(PEACOCK_OFFSET[0]+playerWidth+playerXSpacer, PLUM_OFFSET[1])
GREEN_OFFSET=(playerXOffset, playerYOffset+playerHeight+playerYSpacer)
SCARLETT_OFFSET=(GREEN_OFFSET[0]+playerWidth+playerXSpacer, GREEN_OFFSET[1])
WHITE_OFFSET=(SCARLETT_OFFSET[0]+playerWidth+playerXSpacer, GREEN_OFFSET[1])

cursorHeight = 10
cursorWidth = 10

roomBorder = 2



DISPLAYSURF = pygame.display.set_mode(screen_size)


pygame.init()

DISPLAYFONT = pygame.font.Font(None, 24)

def drawText(surface, text, color, rect, font, aa=False, bkg=None):
    rect = Rect(rect)
    y = rect.top + 100
    lineSpacing = -2

    # get the height of the font
    fontHeight = font.size("Tg")[1]

    while text:
        i = 1

        # determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break

        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # if we've wrapped the text, then adjust the wrap to the last word
        if i < len(text):
            i = text.rfind(" ", 0, i) + 1

        # render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing

        # remove the text we just blitted
        text = text[i:]

    return text

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
        # self.layer = 99

        self.rect = self.image.get_rect()

    def update(self):
        pos = pygame.mouse.get_pos()

        self.rect.x, self.rect.y = pos

    def printPosition(self):
        print "cursor is at position: " + str(self.rect.x) + ", " + str(self.rect.y)


class Button(pygame.sprite.Sprite):
    def __init__(self, color, width, height):

        pass

class SuspectToken(pygame.sprite.Sprite):
    def __init__(self, color, playerOffset=(0,0), roomRect=None):
        super(SuspectToken, self).__init__()
        self.color = color
        self.image = pygame.Surface([playerHeight, playerWidth])
        # self.image.fill(color)
        self.image.set_colorkey(BLACK)
        pygame.draw.ellipse(self.image, color, [0, 0, playerHeight, playerWidth], 0)
        self.image = self.image.convert_alpha()
        self.playerOffset = playerOffset
        self.rect = self.image.get_rect()
        self.updateRoom(roomRect)
        print "Initial layout of color: " + str( color) + " at: " + str(self.rect)
        # self.layer=3

    def updateRoom(self, rect):
        print "Placing token color: " + str(self.color) + " at offset: " + str(self.playerOffset) + \
              " from rect: " + str(rect)
        self.rect.left = self.playerOffset[0] + rect.x
        self.rect.top = self.playerOffset[1] + rect.y

    # def update(self, xOffset, yOffset):
    #     self.rect.x = xOffset
    #     self.rect.y = yOffset
    #     pass


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
        # self.layer=1
        self.hilight = False

        # self.setName(name)

        # print "Room " + self.name + " configured with: " + str(self.xOffset) + ", "+ str(self.yOffset) + \
        #       ", "+ str(self.length) + ", "+ str(self.width)

    def update(self):
        # self.setName(self.text)
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
        # self.layer=1
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

class TextSurface(pygame.sprite.Sprite):
    def __init__(self, text, fontSize=20, refRect = None, xOffset = 1000, yOffset = 400):
        super(TextSurface, self).__init__()
        self.text = text
        self.font = pygame.font.Font(None, fontSize)
        self.image = self.font.render(text, 1, (0,0,0))
        self.rect = self.image.get_rect()
        if refRect:
            self.rect.x = refRect.x + xOffset
            self.rect.y = refRect.y + yOffset
        else:
            self.rect.x = xOffset
            self.rect.y = yOffset

    def updateText(self, text):
        self.image = self.font.render(text, 1, (0,0,0))

class Game(object):
    def __init__(self):

        # self.all_sprites_list = pygame.sprite.LayeredUpdates()
        self.all_rooms_list = pygame.sprite.Group()
        self.all_suspectTokens_list = pygame.sprite.Group()
        self.all_weapons_list = pygame.sprite.Group()
        self.all_text_boxes_list = pygame.sprite.Group()

        self.gameData= {'rooms':{'STUDY':{'object':Room("Study", BROWN), 'name':'Study'},
                                 'HWAY1':{'object':Hallway(GREY, xOffset=roomWidth), 'name':'Hallway'},
                                 'HALL':{'object':Room("Hall", GREY, xOffset=2*roomWidth), 'name':'Hall'},
                                 'HWAY2':{'object':Hallway(GREY, xOffset=3*roomWidth), 'name':'Hallway'},
                                 'LOUNGE':{'object':Room("Lounge", TAN, xOffset=4*roomWidth), 'name':'Lounge'},
                                 'HWAY3':{'object':Hallway(GREY, vertical = True, yOffset=roomLength*1), 'name':'Hallway'},
                                 'HWAY4':{'object':Hallway(GREY, vertical = True, yOffset=roomLength*1, xOffset=roomWidth*2), 'name':'Hallway'},
                                 'HWAY5':{'object': Hallway(GREY, vertical = True, yOffset=roomLength*1, xOffset = (roomWidth*4)), 'name':'Hallway'},
                                 'LIBRARY':{'object':Room("Library", SCARLET, yOffset=roomLength*2), 'name':'Library'},
                                 'HWAY6':{'object':Hallway(GREY, yOffset=roomLength*2, xOffset=roomWidth), 'name':'Hallway'},
                                 'BILLIARD':{'object':Room("Billiard Room", PEACOCK_BLUE, yOffset=roomLength*2, xOffset = roomWidth*2), 'name':'Billiard Room'},
                                 'HWAY7':{'object':Hallway(GREY, yOffset=roomLength*2, xOffset = roomWidth*3), 'name':'Hallway'},
                                 'DINING':{'object':Room("Dining Room", TAN, yOffset=roomLength*2, xOffset = roomWidth*4), 'name':'Dining Room'},
                                 'HWAY8':{'object':Hallway(GREY, vertical = True, yOffset=roomLength*3), 'name':'Hallway'},
                                 'HWAY9':{'object':Hallway(GREY, vertical = True, yOffset=roomLength*3, xOffset=roomWidth*2), 'name':'Hallway'},
                                 'HWAY10':{'object':Hallway(GREY, vertical = True, yOffset=roomLength*3, xOffset = roomWidth*4), 'name':'Hallway'},
                                 'CONSERV':{'object':Room("Conservatory", BROWN, yOffset=roomLength*4), 'name':'Conservatory'},
                                 'HWAY11':{'object':Hallway(GREY, yOffset=roomLength*4, xOffset=roomWidth), 'name':'Hallway'},
                                 'BALL':{'object':Room("Ball Room", MUSTARD, yOffset=roomLength*4, xOffset=roomWidth*2), 'name':'Ball Room'},
                                 'HWAY12':{'object':Hallway(GREY, yOffset=roomLength*4, xOffset=roomWidth*3), 'name':'Hallway'},
                                 'KITCHEN':{'object':Room("Kitchen", GREEN, yOffset=roomLength*4, xOffset=roomWidth*4),'name':'Kitchen'},},}
        self.gameData['suspects'] = {'PLUM':{'object':SuspectToken(PLUM, PLUM_OFFSET, self.gameData['rooms']['STUDY']['object'].rect), 'name':'Mr. Plum', 'room':None,},
                                    'SCARLETT':{'object':SuspectToken(SCARLET, SCARLETT_OFFSET, self.gameData['rooms']['STUDY']['object'].rect), 'name':'Ms. Scarlett', 'room':None,},
                                    'GREEN':{'object':SuspectToken(GREEN, GREEN_OFFSET, self.gameData['rooms']['STUDY']['object'].rect), 'name':'Mr. Green', 'room':None,},
                                    'WHITE':{'object':SuspectToken(WHITE, WHITE_OFFSET, self.gameData['rooms']['STUDY']['object'].rect), 'name':'Mrs. White', 'room':None,},
                                    'MUSTARD':{'object':SuspectToken(MUSTARD, MUSTARD_OFFSET, self.gameData['rooms']['STUDY']['object'].rect), 'name':'Colonel Mustard', 'room':None,},
                                    'PEACOCK':{'object':SuspectToken(PEACOCK_BLUE, PEACOCK_OFFSET, self.gameData['rooms']['STUDY']['object'].rect), 'name':'Mrs. Peacock', 'room':None,}}
        self.gameData['currentTurn'] = None
        self.gameData['player'] = None
        self.gameData['textBox'] = ''



        for roomKey in self.gameData['rooms'].keys():
            if not 'HWAY' in roomKey:
                self.gameData['rooms'][roomKey]['titleBox'] = TextSurface(self.gameData['rooms'][roomKey]['name'],
                                                                      refRect = self.gameData['rooms'][roomKey]['object'].rect,
                                                                      xOffset=roomTitleXOffset, yOffset=roomTitleYOffset)
                self.all_text_boxes_list.add(self.gameData['rooms'][roomKey]['titleBox'])
            else:
                self.gameData['rooms'][roomKey]['titleBox'] = None
            print "Adding room: " + str(roomKey) + " to list."
            # self.all_sprites_list.add(self.gameData['rooms'][roomKey]['object'])
            self.all_rooms_list.add(self.gameData['rooms'][roomKey]['object'])


        for suspKey in self.gameData['suspects'].keys():
            self.all_suspectTokens_list.add(self.gameData['suspects'][suspKey]['object'])
            # self.all_sprites_list.add(self.gameData['suspects'][suspKey]['object'])

        # self.testTextBox = TextSurface(self.gameData['rooms']['STUDY']['name'], refRect = self.gameData['rooms']['STUDY']['object'].rect, xOffset=roomTitleXOffset, yOffset=roomTitleYOffset)
        # self.testTextBox2 = TextSurface(self.gameData['rooms']['HALL']['name'], refRect = self.gameData['rooms']['HALL']['object'].rect, xOffset=roomTitleXOffset, yOffset=roomTitleYOffset)
        # self.all_text_boxes_list.add(self.testTextBox)
        # self.all_text_boxes_list.add(self.testTextBox2)

        self.cursor = Cursor()
        # self.all_sprites_list.add(self.cursor)
        self.cursorGroup = pygame.sprite.GroupSingle()
        self.cursorGroup.add(self.cursor)
        self.selectedRoom = None
        self.selectedSuspect = None
        self.selectedWeapon = None



    def updateState(self, stateDict):
        '''This function takes a state dictionary object as an argument and updates the class's internal
        data model.'''
        pass


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
            print "Rectangle is: " + str(self.selectedRoom.rect)
            self.gameData['suspects']['PLUM']['object'].updateRoom(self.selectedRoom.rect)
            # if self.selectedRoom.hilight:
            #
            #     self.testTextBox.updateText("Quite Highlighted.")
            # else:
            #     drawText(self.selectedRoom.image, "", (0,0,0), self.selectedRoom.rect, DISPLAYFONT)
            #     self.testTextBox.updateText("Not Quite Highlighted.")
            self.selectedRoom = None

        #Update sprites here
            # self.updateFromState()


    def displayFrame(self, screen):
        screen.fill(GREY58)
        for roomKey in self.gameData['rooms'].keys():
            self.gameData['rooms'][roomKey]['object'].update()
        # self.all_sprites_list.draw(screen)
        self.all_rooms_list.draw(screen)
        self.all_suspectTokens_list.draw(screen)
        self.all_weapons_list.draw(screen)
        self.all_text_boxes_list.draw(screen)
        self.cursorGroup.draw(screen)
        pygame.display.flip()

def main():

    # pygame.font.init()
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
        game.displayFrame(DISPLAYSURF)
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()