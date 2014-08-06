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
SALMON = (255,169,122)
# BROWN = ()
WRENCH_ALPHA = (254, 255, 255)

#Greys
GREY = (84, 84, 84)
SILVER_GREY = (192, 192, 192)
GREY58 = (148, 148, 148)

screen_size = (1440, 900)

roomHeight = 150
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



playerSuspectListXOffset=800
playerSuspectListYOffset=200
playerSuspectListSpacer=10
playerCardBoxWidth = 7*playerSuspectListSpacer+6*90
playerCardBoxHeight = 2*playerSuspectListSpacer+90

weaponCardListXOffset = playerSuspectListXOffset
weaponCardListYOffset = playerSuspectListYOffset + playerSuspectListSpacer + playerCardBoxHeight

weaponCardBoxWidth = playerCardBoxWidth
weaponCardBoxHeight = playerCardBoxHeight

playLogX = weaponCardListXOffset
playLogY = weaponCardListYOffset + weaponCardBoxHeight + playerSuspectListSpacer

logXOffset = 800
logYOffset = 600

PLUM_OFFSET=(playerXOffset, playerYOffset)
PEACOCK_OFFSET=(PLUM_OFFSET[0]+playerWidth+playerXSpacer,PLUM_OFFSET[1])
MUSTARD_OFFSET=(PEACOCK_OFFSET[0]+playerWidth+playerXSpacer, PLUM_OFFSET[1])
GREEN_OFFSET=(playerXOffset, playerYOffset+playerHeight+playerYSpacer)
SCARLETT_OFFSET=(GREEN_OFFSET[0]+playerWidth+playerXSpacer, GREEN_OFFSET[1])
WHITE_OFFSET=(SCARLETT_OFFSET[0]+playerWidth+playerXSpacer, GREEN_OFFSET[1])

cursorHeight = 10
cursorWidth = 10

roomBorder = 2


notesBoxXOffset = 600
notesBoxYOffset = 200

DISPLAYSURF = pygame.display.set_mode(screen_size)


pygame.init()

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

class Button(object):
    def __init__(self, color, x, y, length, height, text, width=0, text_color = (0,0,0), font_size=22):
        super(Button, self).__init__()
        self.color = color
        self.x = x
        self.y = y
        self.length = length
        self.height = height
        self.width = width
        self.text = text
        self.text_color = text_color
        self.font_size = font_size

    def draw(self, surface):
        surface = self.draw_button(surface, self.color, self.length, self.height, self.x, self.y, self.width)
        surface = self.write_text(surface, self.text, self.text_color, self.length, self.height, self.x, self.y)
        self.rect = pygame.Rect(self.x, self.y, self.length, self.height)
        return surface

    # def create_button(self, surface, color, x, y, length, height, width, text, text_color):
    #     surface = self.draw_button(surface, color, length, height, x, y, width)
    #     surface = self.write_text(surface, text, text_color, length, height, x, y)
    #     self.rect = pygame.Rect(x,y, length, height)
    #     return surface

    def write_text(self, surface, text, text_color, length, height, x, y):
        # font_size = int(length//len(text))
        myFont = pygame.font.SysFont("Calibri", self.font_size)
        myText = myFont.render(text, 1, text_color)
        surface.blit(myText, ((x+length/2) - myText.get_width()/2, (y+height/2) - myText.get_height()/2))
        return surface

    def draw_button(self, surface, color, length, height, x, y, width):
        for i in range(1,10):
            s = pygame.Surface((length+(i*2),height+(i*2)))
            s.fill(color)
            alpha = (255/(i+2))
            if alpha <= 0:
                alpha = 1
            s.set_alpha(alpha)
            pygame.draw.rect(s, color, (x-i,y-i,length+i,height+i), width)
            surface.blit(s, (x-i,y-i))
        pygame.draw.rect(surface, color, (x,y,length,height), 0)
        pygame.draw.rect(surface, (190,190,190), (x,y,length,height), 1)
        return surface

    def pressed(self, mouse):
        if mouse[0] > self.rect.topleft[0]:
            if mouse[1] > self.rect.topleft[1]:
                if mouse[0] < self.rect.bottomright[0]:
                    if mouse[1] < self.rect.bottomright[1]:
                        print "Some button was pressed!"
                        return True
                    else: return False
                else: return False
            else: return False
        else: return False

class SuspectToken(pygame.sprite.Sprite):
    def __init__(self, color, playerOffset=(0,0), roomRect=None):
        super(SuspectToken, self).__init__()
        self.color = color
        self.image = pygame.Surface([playerHeight, playerWidth])
        self.image.fill(SALMON)
        self.image.set_colorkey(SALMON)
        pygame.draw.ellipse(self.image, BLACK, [0, 0, playerHeight, playerWidth], 0)
        pygame.draw.ellipse(self.image, color, [0+roomBorder, 0+roomBorder, playerHeight-2*roomBorder, playerWidth-2*roomBorder], 0)
        self.image = self.image.convert_alpha()
        self.playerOffset = playerOffset
        self.rect = self.image.get_rect()
        if roomRect:
            self.updateRoom(roomRect)
        print "Initial layout of color: " + str( color) + " at: " + str(self.rect)
        # self.layer=3

    def updateRoom(self, rect, hallway=False):
        # print "Placing token color: " + str(self.color) + " at offset: " + str(self.playerOffset) + \
        #       " from rect: " + str(rect)
        self.rect.left = self.playerOffset[0] + rect.x
        self.rect.top = self.playerOffset[1] + rect.y

class Checkbox():
    def __init__(self, x, y, text, checked = False):
        self.screen = pygame.display.get_surface()
        self.checked = checked
        self.text = text

        self.checkboxRect = pygame.Rect(x, y, 15, 15)
        self.crossRect = pygame.Rect(x + 2, y + 2, 11, 11)

        if pygame.font:
            font = pygame.font.Font(None, 22)
            self.textDisp = font.render(self.text, 1, (75, 75, 75))

        self.textRect = self.textDisp.get_rect(x = x + 25, centery = y + 9)

    def update(self):
        pygame.draw.rect(self.screen, (150, 150, 150), self.checkboxRect)

        if self.checked:
            pygame.draw.rect(self.screen, (75, 75, 75), self.crossRect)

        self.screen.blit(self.textDisp, self.textRect)

    def onCheckbox(self, (x, y)):
        if x >= self.getX() and x <= (self.getX() + 25 + self.textRect.w) and y >= self.getY() and y <= (self.getY() + 15):
            return True
        else:
            return False

    def changeState(self):
        if self.checked:
            self.checked = False
        else:
            self.checked = True

    def isChecked(self):
        return self.checked

    def getX(self):
        return self.checkboxRect.x

    def getY(self):
        return self.checkboxRect.y

class LabeledBox(object):
    def __init__(self, fillColor, x, y, width, height, image=None, alphaColor = None, imageXOffset=None, imageYOffset=None,
                 border=0, text="", textXOffset=0, textYOffset=0, textColor=BLACK, fontSize=22, hilightColor=WHITE):
        self.fillColor = fillColor
        self.x = x
        self.y = y
        self.width=width
        self.height=height
        self.border=border
        self.text=text
        self.textXOffset = textXOffset
        self.textYOffset = textYOffset
        self.textColor=textColor
        self.fontSize = fontSize
        self.hilightColor=hilightColor
        self.hilight = False
        self.alphaColor = alphaColor
        self.imageXOffset = imageXOffset
        self.imageYOffset = imageYOffset

        if image:
            print "Opening image: " + str(image)
            self.image = pygame.image.load(image) #.convert()
            if not self.image:
                print "Problem loading image."
            else:
                if self.alphaColor:
                    self.image.set_colorkey(alphaColor)
                self.image = self.image.convert_alpha()
                if not self.imageXOffset or not self.imageYOffset:
                    rect = self.image.get_rect()
                    self.imageXOffset = (self.width - rect.width)/2
                    self.imageYOffset = 20 #(self.height - rect.height)/2
        else:
            self.image=image

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def toggleHilight(self):
        self.hilight = not self.hilight

    def drawMain(self, surface):
        s = pygame.Surface((self.width, self.height))
        if self.hilight:
            s.fill(WHITE)
        else:
            s.fill(BLACK)

        pygame.draw.rect(s, self.fillColor, [self.border, self.border,
                                          self.width-(2*self.border),
                                          self.height-(2*self.border)])
        surface.blit(s, (self.x, self.y))

    def drawImage(self, surface):
        if self.image:
            surface.blit(self.image, (self.x+self.imageXOffset, self.y+self.imageYOffset))

    def writeText(self, surface):
        if self.text:
            myFont = pygame.font.SysFont("", self.fontSize)
            myText = myFont.render(self.text, 1, self.textColor)
            surface.blit(myText, (self.x+self.textXOffset, self.y+self.textYOffset))
            return surface

    def draw(self, surface):
        self.drawMain(surface)
        self.drawImage(surface)
        self.writeText(surface)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def pressed(self, mouse):
        if mouse[0] > self.rect.topleft[0]:
            if mouse[1] > self.rect.topleft[1]:
                if mouse[0] < self.rect.bottomright[0]:
                    if mouse[1] < self.rect.bottomright[1]:
                        print "Some button was pressed!"
                        return True
                    else: return False
                else: return False
            else: return False
        else: return False

class Room(LabeledBox):
    def __init__(self, name, color, x, y, width=roomWidth, height=roomHeight, border=roomBorder):
        super(Room, self).__init__(fillColor=color, x=x+roomBaseXOffset, y=y+roomBaseYOffset,
                                   text=name, width=width, height=height, border=border)
        self.textXOffset=10
        self.textYOffset = self.height-20

class Hallway(LabeledBox):
    def __init__(self, color, x, y, vertical = False, width=roomWidth, height=roomHeight, border=roomBorder):
        if vertical:
            width = roomWidth / 3
            height = roomHeight
            x += width
        else:
            width= roomWidth
            height = roomHeight / 3
            y += height
        super(Hallway, self).__init__(fillColor=color, x=x+roomBaseXOffset, y=y+roomBaseYOffset, width=width, height=height, border=border)

class SuspectCard(LabeledBox):
    def __init__(self, name, suspectColor, x, y, xOffset=0, yOffset=0, fillColor=SALMON, width=90, height=90, border=roomBorder):
        super(SuspectCard, self).__init__(fillColor=fillColor, x=x+xOffset, y=y+yOffset, text=name, width=width, height=height, border=border)
        self.textXOffset = 10
        self.textYOffset = 5
        self.xOffset = xOffset
        self.yOffset = yOffset
        self.suspectColor = suspectColor
        self.suspectHeadHeight = self.height*0.5
        self.suspectHeadWidth = self.width*0.35
        self.suspectXOffset = (self.width - self.suspectHeadWidth)/2
        self.suspectYOffset = (self.height - self.suspectHeadHeight)/2
        self.suspectShouldersWidth = self.width*0.65
        self.suspectShouldersHeight = self.height*0.35
        self.suspectShouldersXOffset = (self.width-self.suspectShouldersWidth)/2
        self.suspectShouldersYOffset = self.height*0.6

    def drawMain(self, surface):
        s = pygame.Surface((self.width, self.height))
        if self.hilight:
            s.fill(WHITE)
        else:
            s.fill(BLACK)

        pygame.draw.rect(s, self.fillColor, [self.border, self.border,
                                          self.width-(2*self.border),
                                          self.height-(2*self.border)])

        pygame.draw.ellipse(s, BLACK, [self.suspectShouldersXOffset, self.suspectShouldersYOffset,
                                       self.suspectShouldersWidth, self.suspectShouldersHeight])
        pygame.draw.ellipse(s, self.suspectColor, [self.suspectShouldersXOffset+roomBorder,
                                                   self.suspectShouldersYOffset+roomBorder,
                                                   self.suspectShouldersWidth-2*roomBorder,
                                                   self.suspectShouldersHeight-2*roomBorder])

        pygame.draw.ellipse(s, BLACK, [self.suspectXOffset, self.suspectYOffset,
                                       self.suspectHeadWidth, self.suspectHeadHeight])
        pygame.draw.ellipse(s, self.suspectColor, [self.suspectXOffset+roomBorder, self.suspectYOffset+roomBorder,
                                                   self.suspectHeadWidth-2*roomBorder, self.suspectHeadHeight-2*roomBorder])
        surface.blit(s, (self.x, self.y))

    def updateXYRef(self, newX, newY):
        self.x=newX + self.xOffset
        self.y=newY + self.yOffset

class TextBox(object):
    def __init__(self, x, y, height, width, text="", textColor=BLACK, font=None, fontSize=20, aa=False, bkg=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.x=x
        self.y=y
        self.height=height
        self.width=width
        self.text = text
        self.textColor=textColor
        self.fontSize = fontSize
        self.font=font
        self.aa=aa
        self.bkg=bkg

    def draw(self, surface):
        y = self.rect.top + 100
        lineSpacing = -2
        if self.font:
            font = pygame.font.SysFont(self.font, self.fontSize)
        else:
            font = pygame.font.SysFont("", self.fontSize)
        # get the height of the font
        fontHeight = font.size("Tg")[1]
        text = self.text
        while text:
            i = 1

            # determine if the row of text will be outside our area
            if y + fontHeight > self.rect.bottom:
                break

            # determine maximum width of line
            while font.size(text[:i])[0] < self.rect.width and i < len(text):
                i += 1

            # if we've wrapped the text, then adjust the wrap to the last word
            if i < len(text):
                i = text.rfind(" ", 0, i) + 1

            # render the line and blit it to the surface
            if self.bkg:
                image = font.render(text[:i], 1, self.textColor, self.bkg)
                image.set_colorkey(self.bkg)
            else:
                image = font.render(text[:i], self.aa, self.textColor)

            surface.blit(image, (self.rect.left, y))
            y += fontHeight + lineSpacing

            # remove the text we just blitted
            text = text[i:]

        return text

    def updateRect(self, x=None, y=None, width=None, height=None):
        if x:
            self.rect.x = x
        if y:
            self.rect.y = y
        if width:
            self.rect.width = width
        if height:
            self.rect.height = height

    def setText(self, text):
        if text:
            self.text = text
        else:
            self.text=""

# class TextSurface(pygame.sprite.Sprite):
#     def __init__(self, text, fontSize=14, refRect = None, xOffset = 1000, yOffset = 400):
#         super(TextSurface, self).__init__()
#         self.text = text
#         self.font = pygame.font.Font(None, fontSize)
#         self.image = self.font.render(text, 1, (0,0,0))
#         self.rect = self.image.get_rect()
#         if refRect:
#             self.rect.x = refRect.x + xOffset
#             self.rect.y = refRect.y + yOffset
#         else:
#             self.rect.x = xOffset
#             self.rect.y = yOffset
#
#     def updateText(self, text):
#         self.image = self.font.render(text, 1, (0,0,0))

class Notes(object):

    def __init__(self,x, y):
        self.x = x
        self.y = y
        items = ['PLUM', 'SCARLETT', 'WHITE', 'GREEN', 'PEACOCK', 'MUSTARD', 'ROPE', 'PIPE', 'WRENCH', 'PISTOL', 'CANDLESTICK',
         'KNIFE', 'STUDY', 'HALL', 'LOUNGE', 'LIBRARY', 'BILLIARD ROOM', 'DINING ROOM', 'CONSERVATORY', 'BALL ROOM', 'KITCHEN']

        self.notesDict ={}
        counter = 10
        for item in items:
            self.notesDict[item] = Checkbox(x = self.x+10, y = self.y+counter, text=item)
            counter += 25

        self.width = 175
        self.height = 550

    def draw(self, screen):

        pygame.draw.rect(screen, BLACK, [self.x, self.y, self.width, self.height])
        pygame.draw.rect(screen, WHITE, [self.x+roomBorder, self.y+roomBorder,
                                              self.width-2*roomBorder, self.height-2*roomBorder])
        for boxKey in self.notesDict.keys():
            self.notesDict[boxKey].update()

        myFont = pygame.font.SysFont("", 24)
        myText = myFont.render("Notes", 1, BLACK)
        screen.blit(myText, (self.x, self.y-50))

    def pressed(self, mouse):
        for item in self.notesDict.keys():
            if self.notesDict[item].onCheckbox(mouse):
                self.notesDict[item].changeState()

class Game(object):
    def __init__(self):

        # self.all_sprites_list = pygame.sprite.LayeredUpdates()
        # self.all_rooms_list = pygame.sprite.Group()
        self.all_suspectTokens_list = pygame.sprite.Group()
        # self.all_weapons_list = pygame.sprite.Group()
        # self.all_text_boxes_list = pygame.sprite.Group()
        # self.all_buttons_list = pygame.sprite.Group()

        self.gameData= {'rooms':{'STUDY':{'object':Room("Study", BROWN, x=0, y=0), 'name':'Study'},
                                 'HWAY1':{'object':Hallway(GREY, x=roomWidth, y=0), 'name':'Hallway'},
                                 'HALL':{'object':Room("Hall", GREY, x=2*roomWidth, y=0), 'name':'Hall'},
                                 'HWAY2':{'object':Hallway(GREY, x=3*roomWidth, y=0), 'name':'Hallway'},
                                 'LOUNGE':{'object':Room("Lounge", TAN, x=4*roomWidth, y=0), 'name':'Lounge'},
                                 'HWAY3':{'object':Hallway(GREY, vertical = True, x=0, y=roomHeight*1), 'name':'Hallway'},
                                 'HWAY4':{'object':Hallway(GREY, vertical = True, y=roomHeight*1, x=roomWidth*2), 'name':'Hallway'},
                                 'HWAY5':{'object': Hallway(GREY, vertical = True, y=roomHeight*1, x = (roomWidth*4)), 'name':'Hallway'},
                                 'LIBRARY':{'object':Room("Library", SCARLET, x=0, y=roomHeight*2), 'name':'Library'},
                                 'HWAY6':{'object':Hallway(GREY, y=roomHeight*2, x=roomWidth), 'name':'Hallway'},
                                 'BILLIARD':{'object':Room("Billiard Room", PEACOCK_BLUE, y=roomHeight*2, x = roomWidth*2), 'name':'Billiard Room'},
                                 'HWAY7':{'object':Hallway(GREY, y=roomHeight*2, x = roomWidth*3), 'name':'Hallway'},
                                 'DINING':{'object':Room("Dining Room", TAN, y=roomHeight*2, x = roomWidth*4), 'name':'Dining Room'},
                                 'HWAY8':{'object':Hallway(GREY, vertical = True, x=0, y=roomHeight*3), 'name':'Hallway'},
                                 'HWAY9':{'object':Hallway(GREY, vertical = True, y=roomHeight*3, x=roomWidth*2), 'name':'Hallway'},
                                 'HWAY10':{'object':Hallway(GREY, vertical = True, y=roomHeight*3, x = roomWidth*4), 'name':'Hallway'},
                                 'CONSERV':{'object':Room("Conservatory", BROWN, x=0, y=roomHeight*4), 'name':'Conservatory'},
                                 'HWAY11':{'object':Hallway(GREY, y=roomHeight*4, x=roomWidth), 'name':'Hallway'},
                                 'BALL':{'object':Room("Ball Room", MUSTARD, y=roomHeight*4, x=roomWidth*2), 'name':'Ball Room'},
                                 'HWAY12':{'object':Hallway(GREY, y=roomHeight*4, x=roomWidth*3), 'name':'Hallway'},
                                 'KITCHEN':{'object':Room("Kitchen", GREEN, y=roomHeight*4, x=roomWidth*4),'name':'Kitchen'},},}
        self.gameData['suspects'] = {'PLUM':{'object':SuspectToken(PLUM, PLUM_OFFSET), 'name':'Mr. Plum', 'room':'STUDY',
                                             'card':SuspectCard(name="Plum", suspectColor=PLUM, x=playerSuspectListXOffset, y=playerSuspectListYOffset, xOffset=0*90+1*playerSuspectListSpacer,
                                                                yOffset=0*90+1*playerSuspectListSpacer)},
                                    'SCARLETT':{'object':SuspectToken(SCARLET, SCARLETT_OFFSET), 'name':'Ms. Scarlett', 'room':'STUDY',
                                             'card':SuspectCard(name='Scarlett', suspectColor=SCARLET, x=playerSuspectListXOffset, y=playerSuspectListYOffset, xOffset=1*90+2*playerSuspectListSpacer,
                                                                yOffset=0*90+1*playerSuspectListSpacer)},
                                    'GREEN':{'object':SuspectToken(GREEN, GREEN_OFFSET), 'name':'Mr. Green', 'room':'STUDY',
                                             'card':SuspectCard(name='Green', suspectColor=GREEN,x=playerSuspectListXOffset, y=playerSuspectListYOffset, xOffset=2*90+3*playerSuspectListSpacer,
                                                               yOffset=0*90+1*playerSuspectListSpacer)},
                                    'WHITE':{'object':SuspectToken(WHITE, WHITE_OFFSET), 'name':'Mrs. White', 'room':'STUDY',
                                             'card':SuspectCard(name='White', suspectColor=WHITE, x=playerSuspectListXOffset, y=playerSuspectListYOffset, xOffset=3*90+4*playerSuspectListSpacer,
                                                                yOffset=0*90+1*playerSuspectListSpacer)},
                                    'MUSTARD':{'object':SuspectToken(MUSTARD, MUSTARD_OFFSET), 'name':'Colonel Mustard', 'room':'STUDY',
                                             'card':SuspectCard(name='Mustard', suspectColor=MUSTARD, x=playerSuspectListXOffset, y=playerSuspectListYOffset, xOffset=4*90+5*playerSuspectListSpacer,
                                                                yOffset=0*90+1*playerSuspectListSpacer)},
                                    'PEACOCK':{'object':SuspectToken(PEACOCK_BLUE, PEACOCK_OFFSET), 'name':'Mrs. Peacock', 'room':'STUDY',
                                             'card':SuspectCard(name='Peacock', suspectColor=PEACOCK_BLUE, x=playerSuspectListXOffset, y=playerSuspectListYOffset, xOffset=5*90+6*playerSuspectListSpacer,
                                                                yOffset=0*90+1*playerSuspectListSpacer)}}
        self.gameData['weapons'] = {'ROPE':{'card':LabeledBox(fillColor=RED, text="Rope", height=90, width=90, textXOffset = 10, textYOffset = 5,
                                                              x=weaponCardListXOffset+playerSuspectListSpacer,
                                                              y=weaponCardListYOffset+playerSuspectListSpacer, image="noose.png", alphaColor=WHITE, border=roomBorder), 'name':'Rope'},
                                    'PIPE':{'card':LabeledBox(fillColor=RED, text="Lead Pipe", height=90, width=90,textXOffset = 10, textYOffset = 5,
                                                              x=weaponCardListXOffset+1*90+2*playerSuspectListSpacer,
                                                              y=weaponCardListYOffset+playerSuspectListSpacer, image="pipe.png", border=roomBorder), 'name':'Lead Pipe'},
                                    'WRENCH':{'card':LabeledBox(fillColor=RED, text="Wrench", height=90, width=90,textXOffset = 10, textYOffset = 5,
                                                              x=weaponCardListXOffset+2*90+3*playerSuspectListSpacer,
                                                              y=weaponCardListYOffset+playerSuspectListSpacer, image="wrench.png", alphaColor=WRENCH_ALPHA, border=roomBorder), 'name':'Wrench'},
                                    'PISTOL':{'card':LabeledBox(fillColor=RED, text="Pistol", height=90, width=90,textXOffset = 10, textYOffset = 5,
                                                              x=weaponCardListXOffset+3*90+4*playerSuspectListSpacer,
                                                              y=weaponCardListYOffset+playerSuspectListSpacer, image="pistol.png", border=roomBorder), 'name':'Pistol'},
                                    'STICK':{'card':LabeledBox(fillColor=RED, text="C. stick", height=90, width=90, textXOffset = 10, textYOffset = 5,
                                                              x=weaponCardListXOffset+4*90+5*playerSuspectListSpacer,
                                                              y=weaponCardListYOffset+playerSuspectListSpacer, image="candlestick.png", border=roomBorder), 'name':'Candlestick'},
                                    'KNIFE':{'card':LabeledBox(fillColor=RED, text="Knife", height=90, width=90,textXOffset = 10, textYOffset = 5,
                                                              x=weaponCardListXOffset+5*90+6*playerSuspectListSpacer,
                                                              y=weaponCardListYOffset+playerSuspectListSpacer, image="knife.png", alphaColor=WHITE, border=roomBorder), 'name':'Knife'}}

        self.gameData['currentTurn'] = None
        self.gameData['player'] = None
        self.gameData['mode'] = "CHOOSECHAR" # Other modes are PLAY and END
        self.gameData['lastMode'] = "PLAY"
        self.gameData['textBox'] = TextBox(text="Player Log", x=playLogX, y=playLogY,
                                           width=playerCardBoxWidth, height=playerCardBoxHeight*2)

        # for roomKey in self.gameData['rooms'].keys():
        #     if not 'HWAY' in roomKey:
        #         self.gameData['rooms'][roomKey]['titleBox'] = TextSurface(self.gameData['rooms'][roomKey]['name'],
        #                                                               refRect = self.gameData['rooms'][roomKey]['object'].rect,
        #                                                               xOffset=roomTitleXOffset, yOffset=roomTitleYOffset)
        #         self.all_text_boxes_list.add(self.gameData['rooms'][roomKey]['titleBox'])
        #     else:
        #         self.gameData['rooms'][roomKey]['titleBox'] = None
        #     print "Adding room: " + str(roomKey) + " to list."
        #     # self.all_sprites_list.add(self.gameData['rooms'][roomKey]['object'])
        #     self.all_rooms_list.add(self.gameData['rooms'][roomKey]['object'])

        # self.all_text_boxes_list.add(self.gameData['textBox'])

        for suspKey in self.gameData['suspects'].keys():
            self.all_suspectTokens_list.add(self.gameData['suspects'][suspKey]['object'])
            # self.all_sprites_list.add(self.gameData['suspects'][suspKey]['object'])

        self.doneButton = Button(color=(255,255,255), width=0, height=50, length=100,  text='Done', x=1240, y=840)
        self.notesButton = Button(color=(255,255,255), width=0, height=50, length=100,  text='Notes', x=1000, y=840)
        self.suggestButton = Button(color=(255,255,255), width=0, height=50, length=100,  text='Suggest', x=1000, y=770)
        self.accuseButton = Button(color=(255,255,255), width=0, height=50, length=100,  text='Accuse', x=1240, y=770)
        self.cancelButton = Button(color=(255,255,255), width=0, height=50, length=100,  text='Cancel', x=1120, y=840)
        # self.all_buttons_list.add(self.testButton)

        self.cursor = Cursor()
        # self.all_sprites_list.add(self.cursor)
        self.cursorGroup = pygame.sprite.GroupSingle()
        self.cursorGroup.add(self.cursor)
        self.selectedRoom = None
        self.selectedSuspect = None
        self.selectedWeapon = None

        self.notes = Notes(x=notesBoxXOffset, y=notesBoxYOffset)

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
                if self.gameData['mode'] is "CHOOSECHAR":
                    if self.doneButton.pressed(pygame.mouse.get_pos()):
                        print "Done Clicked! Moving to Game mode!"
                        self.gameData['mode'] = "PLAY"

                elif self.gameData['mode'] is "NOTES":
                    if self.doneButton.pressed(pygame.mouse.get_pos()):
                        print "Done Clicked! Moving to Game mode!"
                        self.gameData['mode'] = "PLAY"

                    self.notes.pressed(pygame.mouse.get_pos())

                elif self.gameData['mode'] is "PLAY":
                    for roomKey in self.gameData['rooms'].keys():
                        if self.gameData['rooms'][roomKey]['object'].pressed(pygame.mouse.get_pos()):
                            self.selectedRoom = roomKey
                            break
                    # room_hit_list = pygame.sprite.spritecollide(self.cursor, self.all_rooms_list, False)
                    # if room_hit_list:
                    #     self.selectedRoom = room_hit_list[0]
                    #     print str(room_hit_list)
                    if self.doneButton.pressed(pygame.mouse.get_pos()):
                            print "Done Clicked!"
                    if self.suggestButton.pressed(pygame.mouse.get_pos()):
                            print "Suggest Clicked!"
                    if self.notesButton.pressed(pygame.mouse.get_pos()):
                        print "Notes Clicked!"
                        self.gameData['lastMode'] = self.gameData['mode']
                        self.gameData['mode'] = "NOTES"
                    if self.accuseButton.pressed(pygame.mouse.get_pos()):
                            print "Accuse Clicked!"
                    if self.cancelButton.pressed(pygame.mouse.get_pos()):
                            print "Cancel Clicked!"
                # button_hit_list = pygame.sprite.spritecollide(self.cursor, self.all_buttons_list, False)
                # if button_hit_list:
                #     print "Button clicked!"

            return False

    def runLogic(self):
        self.cursor.update()
        if self.selectedRoom:
            self.gameData['rooms'][self.selectedRoom]['object'].toggleHilight()
            # self.gameData['suspects']['PLUM']['object'].updateRoom(self.selectedRoom.rect)
            # if self.selectedRoom.hilight:
            #
            #     self.testTextBox.updateText("Quite Highlighted.")
            # else:
            #     drawText(self.selectedRoom.image, "", (0,0,0), self.selectedRoom.rect, DISPLAYFONT)
            #     self.testTextBox.updateText("Not Quite Highlighted.")
            self.selectedRoom = None

        #Update sprites here
        if self.gameData['mode'] is "PLAY":
            if self.gameData['lastMode'] is "CHOOSECHAR":
                for suspectKey in self.gameData['suspects'].keys():
                    self.gameData['suspects'][suspectKey]['card'].updateXYRef(newX=playerSuspectListXOffset,
                                                                              newY=playerSuspectListYOffset)

                pass
            for playerKey in self.gameData['suspects'].keys():
                self.gameData['suspects'][playerKey]['object'].updateRoom(
                    self.gameData['rooms'][self.gameData['suspects'][playerKey]['room']]['object'].rect)
        elif self.gameData['mode'] is "CHOOSECHAR":
            if self.gameData['lastMode'] is "PLAY":
                for suspectKey in self.gameData['suspects'].keys():
                    self.gameData['suspects'][suspectKey]['card'].updateXYRef(newX=(1440-playerCardBoxWidth)/2,
                                                                              newY=(900-playerCardBoxHeight)/2)

        self.gameData['lastMode'] = self.gameData['mode']

    def displayFrame(self, screen):
        screen.fill(GREY58)
        if self.gameData['mode'] is "CHOOSECHAR":
            pygame.draw.rect(screen, BLACK, [(1440-playerCardBoxWidth)/2, (900-playerCardBoxHeight)/2,
                                             playerCardBoxWidth, playerCardBoxHeight])
            pygame.draw.rect(screen, BROWN, [(1440-playerCardBoxWidth)/2+roomBorder, (900-playerCardBoxHeight)/2+roomBorder,
                                             playerCardBoxWidth-2*roomBorder, playerCardBoxHeight-2*roomBorder])
            for suspectKey in self.gameData['suspects'].keys():
                self.gameData['suspects'][suspectKey]['card'].draw(screen)
            self.doneButton.draw(screen)
        elif self.gameData['mode'] is "PLAY":
            for roomKey in self.gameData['rooms'].keys():
                self.gameData['rooms'][roomKey]['object'].draw(screen)

            # Draw background rect for player boxes
            pygame.draw.rect(screen, BLACK, [playerSuspectListXOffset, playerSuspectListYOffset,
                                             playerCardBoxWidth, playerCardBoxHeight])
            pygame.draw.rect(screen, BROWN, [playerSuspectListXOffset+roomBorder, playerSuspectListYOffset+roomBorder,
                                             playerCardBoxWidth-2*roomBorder, playerCardBoxHeight-2*roomBorder])

            # Draw background rect for weapon boxes
            pygame.draw.rect(screen, BLACK, [weaponCardListXOffset, weaponCardListYOffset,
                                             weaponCardBoxWidth, weaponCardBoxHeight])
            pygame.draw.rect(screen, BROWN, [weaponCardListXOffset+roomBorder, weaponCardListYOffset+roomBorder,
                                             weaponCardBoxWidth-2*roomBorder, weaponCardBoxHeight-2*roomBorder])
            self.doneButton.draw(screen)
            self.notesButton.draw(screen)
            self.suggestButton.draw(screen)
            self.cancelButton.draw(screen)
            self.accuseButton.draw(screen)
            for suspectKey in self.gameData['suspects'].keys():
                self.gameData['suspects'][suspectKey]['card'].draw(screen)
            for weaponKey in self.gameData['weapons'].keys():
                self.gameData['weapons'][weaponKey]['card'].draw(screen)
            self.gameData['textBox'].draw(screen)
            self.all_suspectTokens_list.draw(screen)

        elif self.gameData['mode'] == "NOTES":
            self.notes.draw(screen)
            self.doneButton.draw(screen)

        self.cursorGroup.draw(screen)
        pygame.display.flip()

def main():

    # pygame.font.init()
    pygame.display.set_caption("The Beardy Bunch - Clue-less")

    # all_sprites_list = pygame.sprite.Group()

    done = False

    clock = pygame.time.Clock()
    # print "Room dimensions are: " + str(roomHeight) + ", " + str(roomWidth)

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