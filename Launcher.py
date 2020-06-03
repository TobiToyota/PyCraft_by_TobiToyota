import pygame
import pygame as pg
import sys
#from GENERATE import *
#import test_3
from random import randint
#from tkinter import *

breite = 900
höhe = 550
pygame.init()
screen = pygame.display.set_mode((breite,höhe))
font = pygame.font.SysFont('Comic Sans MS', 20)


def textObjekt(text, font):
    textFlaeche = font.render(text, True, (0,0,0))
    return textFlaeche,textFlaeche.get_rect()
 
def spiel_start(text):
    #from main import main
    if text == "":
        text = randint(0, 999999)
    TEXT_END = int(text)
    return TEXT_END
 
aktiv = False
    

 
def button(bx,by,nachricht,laenge,hoehe,farbe_normal,farbe_aktiv,randDicke, text=None):
    global aktiv
    if maus[0] > bx and maus[0] < bx+laenge and maus[1] > by and maus[1] < by+hoehe:
        pygame.draw.rect(screen, farbe_aktiv, (bx,by,laenge,hoehe))
        if klick[0] == 1 and aktiv == False:
            aktiv = True
            if nachricht == "START":
                #pygame.quit()
                seed = spiel_start(text)
                return seed

            if nachricht == "SEED":
                input_box = pg.Rect(breite // 4 + breite // 8 + breite // 100 + 4, höhe // 3 + höhe // 3, 140, 32)
                return input_box
            
            if nachricht == "QUIT":
                pygame.quit()
        if klick[0] == 0:
            aktiv = False
    else:
        pygame.draw.rect(screen, farbe_normal, (bx,by,laenge,hoehe))
    pygame.draw.rect(screen, (0,0,0), (bx,by,laenge,hoehe),randDicke)
    textGrund,textKasten = textObjekt(nachricht,font)
    textKasten.center = ((bx+(laenge/2)),(by+(hoehe/2)))
    screen.blit(textGrund, textKasten)

pygame.display.set_caption("Pycraft Launcher")

go = True

clock = pg.time.Clock()


input_box = pg.Rect(-100, -100, 140, 32)
color_inactive = pg.Color(100,0,0)
color_active = pg.Color(200,0,0)
color = pg.Color(155,0,0)
active = False
text = ''
lengh = 0
num_keys = [pg.K_0, pg.K_1, pg.K_2, pg.K_3, pg.K_4, pg.K_5, pg.K_6, pg.K_7, pg.K_8, pg.K_9]

while go:
    seed = None
    screen.fill((0,155,0))
    maus = pygame.mouse.get_pos()
    klick = pygame.mouse.get_pressed()
    seed = button(150,220,"START",600,60,(150,0,0),(255,0,0),2,text=text)
    input = button(150,290,"SEED",600,60,(150,0,0),(255,0,0),2)
    button(550,440,"QUIT",300,60,(150,0,0),(255,0,0),2)
    textsurface_1 = pygame.font.SysFont('impact', 40).render(f'PyCraft', False, (255, 255, 255))     
    textsurface_2 = pygame.font.SysFont('impact', 40).render(f'PyCraft', True, (0, 0, 0))
    screen.blit(textsurface_2, ((breite // 2 - textsurface_2.get_width() // 2) + 5, (höhe * 3.25 // 4 - textsurface_2.get_height()) - 295))
    screen.blit(textsurface_1, (breite // 2 - textsurface_1.get_width() // 2, (höhe * 3.25 // 4 - textsurface_1.get_height()) - 300))

    if input != None:
        input_box = input


    if seed != None:
        GENERATE = seed
        pygame.quit()
        break
    
    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if input_box.collidepoint(event.pos):
                    # Toggle the active variable.
                active = not active
            else:
                active = False
                # Change the current color of the input box.
            color = color_active if active else color_inactive
        if event.type == pg.KEYDOWN:
            if active:
                if event.key == pg.K_BACKSPACE:
                    text = text[:-1]
                    lengh = 0
                elif len(text) < 16 and event.key in num_keys:
                    text += event.unicode
                elif len(text) == 16:
                    lengh = 1
                    textsurface_3 = pygame.font.SysFont('impact', 20).render(f'Maximum character amount of 16 reached!', True, (255, 0, 0))
                    screen.blit(textsurface_3, ((breite // 2 - textsurface_3.get_width() // 2), (höhe * 3.25 // 4 - textsurface_3.get_height()) - 20))


    # Render the current text.
    txt_surface = font.render(text, True, color)

    if lengh == 1:
        textsurface_3 = pygame.font.SysFont('impact', 20).render(f'Maximum character amount of 16 reached!', True, (255, 0, 0))
        screen.blit(textsurface_3, ((breite // 2 - textsurface_3.get_width() // 2), (höhe * 3.25 // 4 - textsurface_3.get_height()) - 20))

    width = max(196, txt_surface.get_width()+10)
    input_box.w = width
        # Blit the text.
    screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        # Blit the input_box rect.
    pg.draw.rect(screen, color, input_box, 2)
    

    pygame.display.flip()
