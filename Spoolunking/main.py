#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Spoolunking
Nathan Janit
2021/06/18

RPG yarn based roguelite.

Created 06/18/21
All Rights Reserved
Made with Pygame
English
"""


# Pygame Imports
import pygame

pygame.init()


# Game Modules and needed imports
import Assets_Dict.Images as Image
from Saves.Saved_Area import Loaded
from Globals import *
from Spritesheet import SpriteSheet
import math
import random
from Saves.Saved_Status import *
from Saves.Saved_Area import *
from Saves.Saved_Items import *

# Loads Save Files From Previous Play Throughs
if Loaded:
    from Saves.Saved_Area import *

saved_loaded = False # Checks if there is a save file loaded


# Generic Class for In-Game Objects
class Entities(pygame.sprite.Sprite):
    # Initiates entity instances
    def __init__(self, x, y, file):
        super(Entities, self).__init__()
        if file != "none":
            self.surf = pygame.image.load(file).convert()
            self.file = file
            transcolour = self.surf.get_at((0, 0))
            self.surf.set_colorkey(transcolour)
        self.rect = self.surf.get_rect(
            topleft=(
                x,
                y
            )
        )
        self.size = self.surf.get_size()


class Healthbars():
    # creates a class for health bars and energy bars
    healthbar1 = pygame.image.load(Image.Healthbar[0]).convert()
    healthbar2 = pygame.image.load(Image.Healthbar[1]).convert()
    energybar1 = pygame.image.load(Image.Energybar[0]).convert()
    energybar2 = pygame.image.load(Image.Energybar[1]).convert()
    monsterhealth1 = pygame.transform.scale(pygame.image.load(Image.Monsterhealth[0]).convert(), (32, 5))
    monsterhealth2 = pygame.transform.scale(pygame.image.load(Image.Monsterhealth[1]).convert(), (32, 5)) 


# Creates health bars based on percent full
def health_bar(monster, total, amount):
    """

    :param monster: Bool
    :param total: Float
    :param amount: Float
    :return: pygame.Surface
    """
    if total == amount:
        amount -= 0.0000001
    if monster:
        real_bar = Healthbars.monsterhealth2.copy()
        rect = pygame.Rect(0, 0, round(32 * amount / total), 5)
        real_bar.blit(Healthbars.monsterhealth1, (0,0), rect)
    else:
        real_bar = Healthbars.healthbar1.copy()
        rect = pygame.Rect(0, 0, 18 + round(78*amount/total), 15)
        real_bar.blit(Healthbars.healthbar2, (0, 0), rect)

    return real_bar


# Creates energy bars based on percent full
def energy_bar(total, amount):
    """

    :param total: Float
    :param amount: Float 
    :return: pygame.Surface
    """
    
    if total == amount:
        amount -= 0.0000001
    real_bar = Healthbars.energybar1.copy()
    rect = pygame.Rect(0, 0, 18 + round(78 * amount / total), 15)
    real_bar.blit(Healthbars.energybar2, (0, 0), rect)

    return real_bar


# Stationary Entities
class Blocks(Entities):
    # Initialise Blocks instance
    def __init__(self, x, y, file, density):
        super(Blocks, self).__init__(x, y, file)
        self.density = density


# Light Emitting Blocks
class Lights(Blocks):
    # Initialise Light instance
    def __init__(self, x, y, file, brightness, density):
        super(Lights, self).__init__(x, y, file, density)
        self.lightlv = brightness


# Adds Solid Block
def add_solid_block(x, y):
    """

    :param x: Int 
    :param y: Int
    """
    new_block = Blocks(x, y, Image.brick, 2)
    all_blocks.add(new_block)


# Adds String Block
def add_string_block(x, y):
    """

    :rtype: pygame.Sprite
    :param x: Int
    :param y: Int
    """
    new_block = Blocks(x, y, Image.block, 1)
    all_blocks.add(new_block)


# Adds Torch
def add_torch(x, y, z):
    """

    :param x: Int
    :param y: Int
    :param z: pygame.Sprite
    """
    if z == 0:
        new_torch = Lights(x, y, Image.torchL, 1, 0)

    if z == 1:
        new_torch = Lights(x, y, Image.torchR, 1, 0)

    if z == 2:
        new_torch = Lights(x, y, Image.torchU, 1, 0)

    if z == 3:
        new_torch = Lights(x, y, Image.torchD, 1, 0)
    all_lights.add(new_torch)


# Collectible/Usable Entities
class Items(pygame.sprite.Sprite):
    # Initialise Item Entity
    def __init__(self, x, y, file1, file2, type):
        super(Items, self).__init__()
        self.surf = pygame.image.load(file1).convert()
        transcolour = self.surf.get_at((0, 0))
        self.surf.set_colorkey(transcolour)
        self.size = self.surf.get_size()
        self.type = type
        self.file2 = file2
        self.file1 = file1
        self.vectorlength = 0

    # Causes Item To Appear On Screen
    def spawn(self, x, y):
        self.rect = self.surf.get_rect()
        self.rect.center = (x, y)
        all_items.add(self)

    # Distinguishes item in players range
    def light_up(self):
        self.surf = pygame.image.load(self.file2).convert()
        transcolour = self.surf.get_at((0, 0))
        self.surf.set_colorkey(transcolour)

    def darken(self):
        self.surf = pygame.image.load(self.file1).convert()
        transcolour = self.surf.get_at((0, 0))
        self.surf.set_colorkey(transcolour)

    # Deletes item
    def remove(self):
        self.kill()


# Background Images and Assets
class Background(pygame.sprite.Sprite):
    # Initialise Background instance
    def __init__(self, x, y, file):
        super(Background, self).__init__()
        self.surf = pygame.image.load(file).convert()
        transcolour = self.surf.get_at((0, 0))
        self.surf.set_colorkey(transcolour)
        self.rect = self.surf.get_rect(
            topleft=(
                x,
                y
            )
        )
        self.size = self.surf.get_size()


# Class For Creating Visual Layers (Used as a storage class)
class Layers:
    Dimensions = [SCREEN_WIDTH, SCREEN_HEIGHT]
    map = [[0 for i in range(65)] for j in range(35)]
    Map = pygame.surface.Surface((65*32, 35*32))
    Map.set_colorkey((100,90,50))
    Light_Layer = pygame.surface.Surface((65*32, 35*32))
    light = pygame.image.load(Image.light).convert_alpha()
    light = pygame.transform.smoothscale(light, (200, 200))
    floor = pygame.image.load(Image.floor).convert()
    floor_layer = pygame.surface.Surface((screen.get_width(), screen.get_height()))
    zoom = 3
    walls = [5, 6]
    solid = [5]


# Updates Light Layer in game
# Adds Light Filters to Light Layer
def light_up():
    Layers.Light_Layer.fill((150, 150, 150))
    for light in all_lights:
        if all((((thred.rect.center[0]-screen.get_width()/4)<light.rect.left<(thred.rect.center[0]+screen.get_width()/4)), ((thred.rect.center[1]-screen.get_height()/4)<light.rect.top<(thred.rect.center[1]+screen.get_height()/4)))):
            Layers.Light_Layer.blit(pygame.transform.scale(Layers.light, (round(light.lightlv*200), round(light.lightlv*200))), tuple(map(lambda r: round(r-200*light.lightlv/2), light.rect.center)))
    Layers.Light_Layer.blit(pygame.transform.scale(Layers.light, (round(thred.sight*200), round(thred.sight*200))), tuple(map(lambda r: round(r-200*thred.sight/2), thred.rect.center)))


# Updates Map Layer
# This includes all game sprites
def update_map():
    Layers.Map.fill((100,90,50))
    for entity in all_attacksa:
        entity.update()
    for entity in all_attacksb:
        entity.update()
    for enemy in all_enemies:
        enemy.update()
    for entity in all_backgrounds:
        Layers.Map.blit(entity.surf, entity.rect)
    for entity in all_blocks:
        Layers.Map.blit(entity.surf, entity.rect)
    for entity in all_lights:
        Layers.Map.blit(entity.surf, entity.rect)
    for entity in all_text:
        Layers.Map.blit(entity.surf, entity.rect)
    for entity in all_visuals:
        Layers.Map.blit(entity.surf, entity.rect)
    for entity in all_enemies:
        Layers.Map.blit(entity.surf, entity.rect)
    for entity in all_items:
        Layers.Map.blit(entity.surf, entity.rect)
    for entity in all_enemies:
        Layers.Map.blit(entity.bar, (entity.rect.left+(entity.rect.width-32)/2, entity.rect.top-6))
    for entity in all_cursors:
        Layers.Map.blit(entity.surf, entity.rect)
    for entity in all_mains:
        Layers.Map.blit(entity.surf, entity.rect)
    for entity in all_attacksa:
        Layers.Map.blit(entity.surf, entity.rect)
    for entity in all_attacksb:
        Layers.Map.blit(entity.surf, entity.rect)


# Interactive/Clickable Sprites
class Buttons(pygame.sprite.Sprite):
    # Initialises Button Instances
    def __init__(self, x, y, un_pressed, pressed):
        self.X_Value = x
        self.Y_Value = y
        self.frame_1 = pygame.image.load(un_pressed).convert()
        self.frame_2 = pygame.image.load(pressed).convert()
        super(Buttons, self).__init__()
        self.surf = self.frame_1.convert()
        transcolour = self.surf.get_at((0, 0))
        self.surf.set_colorkey(transcolour)
        self.rect = self.surf.get_rect\
            (topleft=(x,
                      y)
             )
        self.size = self.surf.get_size()
        self.file = 1

    # Switch If Touched By Mouse
    def switch(self):
        self.file = 2
        self.surf = self.frame_2.convert()
        transcolour = self.surf.get_at((0, 0))
        self.surf.set_colorkey(transcolour)
        self.rect = self.surf.get_rect(
            topleft=(
                self.X_Value,
                self.Y_Value)
        )
        self.size = self.surf.get_size()

    def switch_back(self):
        self.file = 1
        self.surf = self.frame_1.convert()
        transcolour = self.surf.get_at((0, 0))
        self.surf.set_colorkey(transcolour)
        self.rect = self.surf.get_rect(
            topleft=(
                self.X_Value,
                self.Y_Value
            )
        )
        self.size = self.surf.get_size()


# Visual Numeric Representation (Numbers)
class Numbers(pygame.sprite.Sprite):
    # initialises Number instances
    def __init__(self, value, x, y):
        super(Numbers, self).__init__()
        if value == 1:
            self.file = Image.one
        elif value == 2:
            self.file = Image.two
        elif value == 3:
            self.file = Image.three
        elif value == 4:
            self.file = Image.four
        elif value == 5:
            self.file = Image.five
        elif value == 6:
            self.file = Image.six
        elif value == 7:
            self.file = Image.seven
        elif value == 8:
            self.file = Image.eight
        elif value == 9:
            self.file = Image.nine
        else:
            self.file = Image.zero

        self.surf = pygame.image.load(self.file).convert()
        transcolour = self.surf.get_at((0, 0))
        self.surf.set_colorkey(transcolour)
        self.rect = self.surf.get_rect(
            center=(
                x,
                y
            )
        )
        self.size = self.surf.get_size()


# Stores values, Contains display methods
class Values:

    # initialises value instances
    def __init__(self,n,x,y):
        self.X_Value = x
        self.Y_Value = y
        self.number = n
        super(Values, self).__init__()

    def display_num(self, digits):
        num = round(float(self.number))
        for i in range(digits):
            val_1 = num % 10 ** (i + 1)
            val_2 = val_1 // 10 ** (i)
            new_digit = Numbers(val_2, (self.X_Value + (12 * (digits - (i + 1)))), self.Y_Value)
            all_numbers.add(new_digit)


# Adds Sprites to Screen (During the Game)
# Organises blits and layers based on input
def update_screen_game(playing, title):
    """
    :type playing: Bool
    :type title: Bool
    """
    camera = pygame.surface.Surface((SCREEN_WIDTH // Layers.zoom, SCREEN_HEIGHT // Layers.zoom))
    camera.fill((250, 250, 250))
    if playing:
        update_map()
        button = thred.inv_button
        button.rect.height = thred.inv_button.rect.height * (screen.get_height()/(SCREEN_HEIGHT/Layers.zoom))
        button.rect.width = thred.inv_button.rect.width * (screen.get_width()/(SCREEN_WIDTH/Layers.zoom))
        button.rect.top = thred.inv_button.rect.top*(screen.get_height()/(SCREEN_HEIGHT/Layers.zoom))
        button.rect.left = thred.inv_button.rect.left*(screen.get_width()/(SCREEN_WIDTH/Layers.zoom))
        light_up()
        if button.rect.collidepoint(pygame.mouse.get_pos()):
            thred.inv_button.switch()
        else:
            thred.inv_button.switch_back()

    if not title:
        if thred.rect.left < camera.get_width()/2:
            cam_x = camera.get_width()/2
        elif thred.rect.left > Layers.Map.get_width()-camera.get_width()/2:
            cam_x = Layers.Map.get_width()-camera.get_width()/2
        else:
            cam_x = thred.rect.left

        if thred.rect.top < camera.get_height()/2:
            cam_y = camera.get_height()/2
        elif thred.rect.top > Layers.Map.get_height()-camera.get_height()/2:
            cam_y = Layers.Map.get_height()-camera.get_height()/2
        else:
            cam_y = thred.rect.top

        x_rel = (800-cam_x) % 800
        x_part2 = x_rel - 800 if x_rel > 0 else x_rel + 800
        y_rel = (800-cam_y) % 750
        y_part2 = y_rel - 750 if y_rel > 0 else y_rel + 750

        Layers.floor_layer.blit(Layers.floor, (x_rel, y_rel))
        Layers.floor_layer.blit(Layers.floor, (x_rel, y_part2))
        Layers.floor_layer.blit(Layers.floor, (x_part2, y_part2))
        Layers.floor_layer.blit(Layers.floor, (x_part2, y_rel))
        camera.blit(Layers.floor_layer, (0,0))
        camera.blit(Layers.Map, (camera.get_width()/2-cam_x, camera.get_height()/2-cam_y))
        if playing:
            camera.blit(Layers.Light_Layer, (camera.get_width() / 2 - cam_x, camera.get_height() / 2 - cam_y),
                        special_flags=pygame.BLEND_RGBA_SUB)
            camera.blit(thred.hbar, ((camera.get_width()-96), (camera.get_height()-28)))
            camera.blit(thred.ebar, ((camera.get_width()-96), (camera.get_height()-16)))
            camera.blit(thred.ebar, ((camera.get_width() - 96), (camera.get_height() - 16)))
            camera.blit(thred.inv_button.surf, thred.inv_button.rect)
            # Thread & level HUD
            try:
                _tf = pygame.font.Font(None, 16)
                _ts = _tf.render("Thread:" + str(int(thred.thread)), True, (220, 200, 100))
                camera.blit(_ts, (2, camera.get_height()-28))
                _ls = _tf.render("Lvl " + str(current_level) + "/3", True, (180, 160, 80))
                camera.blit(_ls, (2, camera.get_height()-16))
            except Exception:
                pass
        if not playing:
            filter_off = pygame.surface.Surface((camera.get_width(), camera.get_height()))
            filter_off.fill((200, 200, 200))
            filter_on = pygame.surface.Surface((camera.get_width()*3/4, camera.get_height()*3/4))
            filter_on.fill((200, 200, 200))
            camera.blit(filter_off, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
            camera.blit(filter_on, (camera.get_width() / 8, camera.get_height() / 8))
            for things in all_temps:
                button = things
                button.rect.height = things.rect.height * (screen.get_height() / (SCREEN_HEIGHT / Layers.zoom))
                button.rect.width = things.rect.width * (screen.get_width() / (SCREEN_WIDTH / Layers.zoom))
                button.rect.top = things.rect.top * (screen.get_height() / (SCREEN_HEIGHT / Layers.zoom))
                button.rect.left = things.rect.left * (screen.get_width() / (SCREEN_WIDTH / Layers.zoom))
                if button.rect.collidepoint(pygame.mouse.get_pos()):
                    things.switch()
                else:
                    things.switch_back()
                camera.blit(things.surf, things.rect)
    if title:
            for things in all_tempsback:
                camera.blit(things.surf, things.rect)

            for things in all_temps:
                button = things
                button.rect.height = things.rect.height * (screen.get_height() / (SCREEN_HEIGHT / Layers.zoom))
                button.rect.width = things.rect.width * (screen.get_width() / (SCREEN_WIDTH / Layers.zoom))
                button.rect.top = things.rect.top * (screen.get_height() / (SCREEN_HEIGHT / Layers.zoom))
                button.rect.left = things.rect.left * (screen.get_width() / (SCREEN_WIDTH / Layers.zoom))
                if button.rect.collidepoint(pygame.mouse.get_pos()):
                    things.switch()
                else:
                    things.switch_back()
                camera.blit(things.surf, things.rect)
            for numbers in all_numbers:
                numbers.surf = pygame.transform.scale(numbers.surf, (12, 12))
                camera.blit(numbers.surf, numbers.rect)

    camera = pygame.transform.scale(camera, (screen.get_width(), screen.get_height()))
    screen.blit(camera, (0, 0))


# Lists of "weapon" and "armor" items for Player Class
weapons = ["Claw", "Ball", "Straw", "none"]
armor = ["Red", "Green", "naked"]


# Player Entity, The Players Charecter
class Player(pygame.sprite.Sprite):

    # Initialise Player instance
    def __init__(self, x, y, file, energy, health, attack, state, speed, sight):
        super(Player, self).__init__()
        a_0 = SpriteSheet('Images/Sprites/Thred/Hero_a_0.png')
        b_0 = SpriteSheet('Images/Sprites/Thred/Hero_b_0.png')
        c_0 = SpriteSheet('Images/Sprites/Thred/Hero_c_0.png')
        a_1 = SpriteSheet('Images/Sprites/Thred/Hero_a_1.png')
        b_1 = SpriteSheet('Images/Sprites/Thred/Hero_b_1.png')
        c_1 = SpriteSheet('Images/Sprites/Thred/Hero_c_1.png')
        a_2 = SpriteSheet('Images/Sprites/Thred/Hero_a_2.png')
        b_2 = SpriteSheet('Images/Sprites/Thred/Hero_b_2.png')
        c_2 = SpriteSheet('Images/Sprites/Thred/Hero_c_2.png')
        a_3 = SpriteSheet('Images/Sprites/Thred/Hero_a_3.png')
        b_3 = SpriteSheet('Images/Sprites/Thred/Hero_b_3.png')
        c_3 = SpriteSheet('Images/Sprites/Thred/Hero_c_3.png')
        a_B = SpriteSheet('Images/Sprites/Thred/Hero_a_B.png')
        b_B = SpriteSheet('Images/Sprites/Thred/Hero_b_B.png')
        c_B = SpriteSheet('Images/Sprites/Thred/Hero_c_B.png')

        self.A_0 = []
        for row in range(9):
            self.A_0.append([])
            for column in range(4):
                self.A_0[row].append(a_0.image_at(((column*32)+5, row*32, 22, 32), colorkey=(141, 47, 173)))
        self.A_1 = []
        for row in range(9):
            self.A_1.append([])
            for column in range(4):
                self.A_1[row].append(a_1.image_at(((column*32)+5, row*32, 22, 32), colorkey=(141, 47, 173)))
        self.A_2 = []
        for row in range(9):
            self.A_2.append([])
            for column in range(4):
                self.A_2[row].append(a_2.image_at(((column*32)+5, row*32, 22, 32), colorkey=(141, 47, 173)))
        self.A_3 = []
        for row in range(9):
            self.A_3.append([])
            for column in range(4):
                self.A_3[row].append(a_3.image_at(((column*32)+5, row*32, 22, 32), colorkey=(141, 47, 173)))
        self.B_0 = []
        for row in range(9):
            self.B_0.append([])
            for column in range(4):
                self.B_0[row].append(b_0.image_at(((column*32)+5, row*32, 22, 32), colorkey=(141, 47, 173)))
        self.B_1 = []
        for row in range(9):
            self.B_1.append([])
            for column in range(4):
                self.B_1[row].append(b_1.image_at(((column*32)+5, row*32, 22, 32), colorkey=(141, 47, 173)))
        self.B_2 = []
        for row in range(9):
            self.B_2.append([])
            for column in range(4):
                self.B_2[row].append(b_2.image_at(((column*32)+5, row*32, 22, 32), colorkey=(141, 47, 173)))
        self.B_3 = []
        for row in range(9):
            self.B_3.append([])
            for column in range(4):
                self.B_3[row].append(b_3.image_at(((column*32)+5, row*32, 22, 32), colorkey=(141, 47, 173)))
        self.C_0 = []
        for row in range(9):
            self.C_0.append([])
            for column in range(4):
                self.C_0[row].append(c_0.image_at(((column*32)+5, row*32, 22, 32), colorkey=(141, 47, 173)))
        self.C_1 = []
        for row in range(9):
            self.C_1.append([])
            for column in range(4):
                self.C_1[row].append(c_1.image_at(((column*32)+5, row*32, 22, 32), colorkey=(141, 47, 173)))
        self.C_2 = []
        for row in range(9):
            self.C_2.append([])
            for column in range(4):
                self.C_2[row].append(c_2.image_at(((column*32)+5, row*32, 22, 32), colorkey=(141, 47, 173)))
        self.C_3 = []
        for row in range(9):
            self.C_3.append([])
            for column in range(4):
                self.C_3[row].append(c_3.image_at(((column*32)+5, row*32, 22, 32), colorkey=(141, 47, 173)))
        self.A_B = []
        for row in range(9):
            self.A_B.append([])
            for column in range(4):
                self.A_B[row].append(a_B.image_at(((column*32)+5, row*32, 22, 32), colorkey=(141, 47, 173)))
        self.B_B = []
        for row in range(9):
            self.B_B.append([])
            for column in range(4):
                self.B_B[row].append(b_B.image_at(((column*32)+5, row*32, 22, 32), colorkey=(141, 47, 173)))
        self.C_B = []
        for row in range(9):
            self.C_B.append([])
            for column in range(4):
                self.C_B[row].append(c_B.image_at(((column*32)+5, row*32, 22, 32), colorkey=(141, 47, 173)))
        self.Puddle_Form = pygame.image.load("Images/Sprites/Thred/puddle.png").convert()
        transcolour = self.Puddle_Form.get_at((0, 0))
        self.Puddle_Form.set_colorkey(transcolour)

        self.surf = self.A_0[0][0]
        self.file = file
        transcolour = self.surf.get_at((0, 0))
        self.surf.set_colorkey(transcolour)
        self.rect = self.surf.get_rect(
            topleft=(
                x,
                y
            )
        )
        self.size = self.surf.get_size()
        self.energy = energy
        self.health = health
        self.max_health = health
        self.max_energy = energy
        self.attack = attack
        self.hand = "none"
        self.armor = "naked"
        self.state = state
        self.speed = speed
        self.sight = sight
        self.last_tl = [self.rect.top // 32, self.rect.left // 32]
        self.last_row = 1
        self.step = 0
        self.reload = 1
        self.hbar = health_bar(False, health, health)
        self.ebar = energy_bar(energy, energy)
        self.inv_button = ""
        self.form = "Solid"
        self.inv = ["Green", "Ball", "Cat_Claw"]
        # Expansion: thread currency, skills, stat multipliers
        self.thread = 0
        self.skills = set()
        self.dmg_mult = 1.0
        self.defense_mult = 1.0
        self.thread_mult = 1.0
        self.crit_chance = 0.0

    # The player equivilant of update
    # based on input and item and armor moves the player entity
    # sets the player entities surface for animations
    # starts player attacks based on cooldpws
    # creates health and energy bars in the bottom right
    def control(self, pressed_keys):  # Controls Player Entity With Keys
        if self.health > 0:
             # Regeneration

            if self.health < self.max_health:
                self.health += self.max_health/600
            if self.health > self.max_health:
                self.health = self.max_health
            if self.state != 1:
                if self.energy < self.max_energy:
                    self.energy += self.max_energy/400
                if self.energy > self.max_energy:
                    self.energy = self.max_energy

            down = False
            up = False
            right = False
            left = False

            # Inputs
            if pressed_keys[K_w]:
                self.rect.move_ip(0, -self.speed)
                up = True
            if pressed_keys[K_s]:
                self.rect.move_ip(0, self.speed)
                down = True
            if pressed_keys[K_a]:
                self.rect.move_ip(-self.speed, 0)
                left = True
            if pressed_keys[K_d]:
                self.rect.move_ip(self.speed, 0)
                right = True
            if pressed_keys[K_q]:
                self.puddle()
            else:
                if self.state == 1:
                    if any((((Layers.map[(self.rect.top//32)][(self.rect.left//32)]) in Layers.walls), ((Layers.map[(self.rect.top//32)][(self.rect.right//32)]) in Layers.walls), ((Layers.map[(self.rect.bottom//32)][(self.rect.left//32)]) in Layers.walls), ((Layers.map[(self.rect.bottom//32)][(self.rect.right//32)]) in Layers.walls))):
                        self.die()
                    self.form = "Solid"
                    self.state = 0

            # Collision Detection
            cur_tl = [self.rect.top // 16, self.rect.left // 16]
            if self.state != 1:
                if (Layers.map[(self.rect.top//32)][(self.rect.left//32)]) in Layers.walls:
                    if (Layers.map[(self.rect.top//32)][(self.rect.right//32)]) in Layers.walls:
                        if (Layers.map[(self.rect.bottom//32)][(self.rect.left//32)]) in Layers.walls:
                            self.rect.move_ip(((self.last_tl[1] - cur_tl[1]) * self.speed), ((self.last_tl[0] - cur_tl[0]) * self.speed))

                        elif (Layers.map[(self.rect.bottom//32)][(self.rect.right//32)]) in Layers.walls:
                            self.rect.move_ip((self.last_tl[1] - cur_tl[1])*self.speed, ((self.last_tl[0] - cur_tl[0])*self.speed))
                        else:
                            self.rect.move_ip(0, ((self.last_tl[0] - cur_tl[0]) * self.speed))
                    elif (Layers.map[(self.rect.bottom//32)][(self.rect.left//32)]) in Layers.walls:
                        if (Layers.map[(self.rect.bottom//32)][(self.rect.right//32)]) in Layers.walls:
                            self.rect.move_ip(((self.last_tl[1] - cur_tl[1]) * self.speed), ((self.last_tl[0] - cur_tl[0]) * self.speed))
                        else:
                            self.rect.move_ip(((self.last_tl[1] - cur_tl[1]) * self.speed), 0)
                    else:
                        self.rect.move_ip((abs(self.last_tl[1] - cur_tl[1]) * self.speed), (abs(self.last_tl[0] - cur_tl[0])*self.speed))
                elif (Layers.map[(self.rect.top//32)][(self.rect.right//32)]) in Layers.walls:
                    if (Layers.map[(self.rect.bottom//32)][(self.rect.left//32)]) in Layers.walls:
                        self.rect.move_ip(((self.last_tl[1] - cur_tl[1]) * self.speed), ((self.last_tl[0] - cur_tl[0])*self.speed))
                    elif (Layers.map[(self.rect.bottom//32)][(self.rect.right//32)]) in Layers.walls:
                        self.rect.move_ip((-abs(self.last_tl[1] - cur_tl[1]) * self.speed), 0)
                    else:
                        self.rect.move_ip((-abs(self.last_tl[1] - cur_tl[1]) * self.speed), (abs(self.last_tl[0] - cur_tl[0]) * self.speed))
                elif (Layers.map[(self.rect.bottom//32)][(self.rect.right//32)]) in Layers.walls:
                    if (Layers.map[(self.rect.bottom//32)][(self.rect.left//32)]) in Layers.walls:
                        self.rect.move_ip(0, ((self.last_tl[0] - cur_tl[0]) * self.speed))
                    else:
                        self.rect.move_ip((-abs(self.last_tl[1] - cur_tl[1]) * self.speed), (-abs(self.last_tl[0] - cur_tl[0])*self.speed))
                elif (Layers.map[(self.rect.bottom//32)][(self.rect.left//32)]) in Layers.walls:
                    self.rect.move_ip((abs(self.last_tl[1] - cur_tl[1]) * self.speed), (-abs(self.last_tl[0] - cur_tl[0]) * self.speed))
                lengths = []

                for items in all_items:
                    itemvector = pygame.math.Vector2(items.rect.centerx - self.rect.centerx,
                                                     items.rect.centery - self.rect.centery)
                    items.vectorlength = itemvector.length()
                    lengths.append(items.vectorlength)
                for items in all_items:
                    if items.vectorlength == min(lengths):
                        if min(lengths) < 40:
                            if pressed_keys[K_e]:
                                if self.reload > 15:
                                    self.reload = 0
                                    self.inv.append(items.type)
                                    items.remove()
                                else:
                                    items.light_up()
                            else:
                                items.light_up()
                        else:
                            items.darken()
                    else:
                        items.darken()

            elif self.state == 1:
                if (Layers.map[(self.rect.top // 32)][(self.rect.left // 32)]) in Layers.solid:
                    if (Layers.map[(self.rect.top // 32)][(self.rect.right // 32)]) in Layers.solid:
                        if (Layers.map[(self.rect.bottom // 32)][(self.rect.left // 32)]) in Layers.solid:
                            self.rect.move_ip(((self.last_tl[1] - cur_tl[1]) * self.speed),
                                              ((self.last_tl[0] - cur_tl[0]) * self.speed))
                        elif (Layers.map[(self.rect.bottom // 32)][(self.rect.right // 32)]) in Layers.solid:
                            self.rect.move_ip((self.last_tl[1] - cur_tl[1]) * self.speed,
                                              ((self.last_tl[0] - cur_tl[0]) * self.speed))
                        else:
                            self.rect.move_ip(0, ((self.last_tl[0] - cur_tl[0]) * self.speed))
                    elif (Layers.map[(self.rect.bottom // 32)][(self.rect.left // 32)]) in Layers.solid:
                        if (Layers.map[(self.rect.bottom // 32)][(self.rect.right // 32)]) in Layers.solid:
                            self.rect.move_ip(((self.last_tl[1] - cur_tl[1]) * self.speed),
                                              ((self.last_tl[0] - cur_tl[0]) * self.speed))
                        else:
                            self.rect.move_ip(((self.last_tl[1] - cur_tl[1]) * self.speed), 0)
                    else:
                        self.rect.move_ip((abs(self.last_tl[1] - cur_tl[1]) * self.speed),
                                          (abs(self.last_tl[0] - cur_tl[0]) * self.speed))
                elif (Layers.map[(self.rect.top // 32)][(self.rect.right // 32)]) in Layers.solid:
                    if (Layers.map[(self.rect.bottom // 32)][(self.rect.left // 32)]) in Layers.solid:
                        self.rect.move_ip(((self.last_tl[1] - cur_tl[1]) * self.speed),
                                          ((self.last_tl[0] - cur_tl[0]) * self.speed))
                    elif (Layers.map[(self.rect.bottom // 32)][(self.rect.right // 32)]) in Layers.solid:
                        self.rect.move_ip((-abs(self.last_tl[1] - cur_tl[1]) * self.speed), 0)
                    else:
                        self.rect.move_ip((-abs(self.last_tl[1] - cur_tl[1]) * self.speed),
                                          (abs(self.last_tl[0] - cur_tl[0]) * self.speed))
                elif (Layers.map[(self.rect.bottom // 32)][(self.rect.right // 32)]) in Layers.solid:
                    if (Layers.map[(self.rect.bottom // 32)][(self.rect.left // 32)]) in Layers.solid:
                        self.rect.move_ip(0, ((self.last_tl[0] - cur_tl[0]) * self.speed))
                    else:
                        self.rect.move_ip((-abs(self.last_tl[1] - cur_tl[1]) * self.speed),
                                          (-abs(self.last_tl[0] - cur_tl[0]) * self.speed))
                elif (Layers.map[(self.rect.bottom // 32)][(self.rect.left // 32)]) in Layers.solid:
                    self.rect.move_ip((abs(self.last_tl[1] - cur_tl[1]) * self.speed),
                                      (-abs(self.last_tl[0] - cur_tl[0]) * self.speed))

            self.last_tl = [self.rect.top // 16, self.rect.left // 16]

            # Animations/Actions

            if self.state == 1:
                self.step += 1
                self.surf = self.Puddle_Form

            elif self.state == 2:
                self.reload = 0
                if down:
                    if left:
                        row = 7
                        self.step += 1
                    elif right:
                        row = 1
                        self.step += 1
                    else:
                        row = 0
                        self.step += 1
                elif up:
                    if left:
                        row = 5
                        self.step += 1
                    elif right:
                        row = 3
                        self.step += 1
                    else:
                        row = 4
                        self.step += 1
                elif left:
                    row = 6
                    self.step += 1
                elif right:
                    row = 2
                    self.step += 1
                else:
                    row = self.last_row
                    self.step += 1

                self.last_row = row
                if (self.step // round(4.2/self.speed)) > 4:
                    self.state = 0
                    self.step = 0
                if self.step == round(5/self.speed):
                    self.throw_ball(row)
                if self.file == "A_2":
                    self.surf = self.A_B[row][(self.step//round(4.2/self.speed))%4]
                if self.file == "B_2":
                    self.surf = self.B_B[row][(self.step//round(4.2/self.speed))%4]
                if self.file == "C_2":
                    self.surf = self.C_B[row][(self.step//round(4.2/self.speed))%4]

            elif self.state == 3:
                self.reload = 0
                if down:
                    if left:
                        row = 7
                        self.step += 1
                    elif right:
                        row = 1
                        self.step += 1
                    else:
                        row = 0
                        self.step += 1
                elif up:
                    if left:
                        row = 5
                        self.step += 1
                    elif right:
                        row = 3
                        self.step += 1
                    else:
                        row = 4
                        self.step += 1
                elif left:
                    row = 6
                    self.step += 1
                elif right:
                    row = 2
                    self.step += 1
                else:
                    row = self.last_row
                    self.step+=1

                self.last_row = row
                if (self.step // round(4.2 / self.speed)) > 4:
                    self.state = 0
                    self.step = 0
                if self.step == round(5/self.speed):
                    self.blow_straw(row)
                if self.file == "A_1":
                    self.surf = self.A_1[row][(self.step // round(4.2 / self.speed)) % 4]
                if self.file == "B_1":
                    self.surf = self.B_1[row][(self.step // round(4.2 / self.speed)) % 4]
                if self.file == "C_1":
                    self.surf = self.C_1[row][(self.step // round(4.2 / self.speed)) % 4]

            elif self.state == 4:
                self.reload = 0
                if down:
                    if left:
                        row = 7
                        self.step += 1
                    elif right:
                        row = 1
                        self.step += 1
                    else:
                        row = 0
                        self.step += 1
                elif up:
                    if left:
                        row = 5
                        self.step += 1
                    elif right:
                        row = 3
                        self.step += 1
                    else:
                        row = 4
                        self.step += 1
                elif left:
                    row = 6
                    self.step += 1
                elif right:
                    row = 2
                    self.step += 1
                else:
                    row = self.last_row
                    self.step += 1

                self.last_row = row
                if (self.step // round(4.2 / self.speed)) > 4:
                    self.state = 0
                    self.step = 0
                if self.step == round(5/self.speed):
                    self.claw_strike(row)
                if self.file == "A_3":
                    self.surf = self.A_3[row][(self.step // round(4.2 / self.speed)) % 4]
                if self.file == "B_3":
                    self.surf = self.B_3[row][(self.step // round(4.2 / self.speed)) % 4]
                if self.file == "C_3":
                    self.surf = self.C_3[row][(self.step // round(4.2 / self.speed)) % 4]

            elif self.state == 5:
                self.reload = 0
                if down:
                    if left:
                        row = 7
                        self.step += 1
                    elif right:
                        row = 1
                        self.step += 1
                    else:
                        row = 0
                        self.step += 1
                elif up:
                    if left:
                        row = 5
                        self.step += 1
                    elif right:
                        row = 3
                        self.step += 1
                    else:
                        row = 4
                        self.step += 1
                elif left:
                    row = 6
                    self.step += 1
                elif right:
                    row = 2
                    self.step += 1
                else:
                    row = self.last_row
                    self.step += 1

                self.last_row = row
                if (self.step // round(4.2 / self.speed)) > 4:
                    self.state = 0
                    self.step = 0
                if self.step == round(3/self.speed):
                    self.punch(row)
                if self.file == "A_0":
                    self.surf = self.A_0[row][(self.step // round(4.2 / self.speed)) % 4]
                if self.file == "B_0":
                    self.surf = self.B_0[row][(self.step // round(4.2 / self.speed)) % 4]
                if self.file == "C_0":
                    self.surf = self.C_0[row][(self.step // round(4.2 / self.speed)) % 4]

            else:
                if down:
                    if left:
                        row = 7
                        self.step += 1
                    elif right:
                        row = 1
                        self.step += 1
                    else:
                        row = 0
                        self.step += 1
                elif up:
                    if left:
                        row = 5
                        self.step += 1
                    elif right:
                        row = 3
                        self.step += 1
                    else:
                        row = 4
                        self.step += 1
                elif left:
                    row = 6
                    self.step += 1
                elif right:
                    row = 2
                    self.step += 1
                else:
                    row = self.last_row
                    self.step = 0

                self.last_row = row

                if self.file == "A_0":
                    self.surf = self.A_0[row][(self.step // round(6.2 / self.speed)) % 4]
                if self.file == "A_1":
                    self.surf = self.A_1[row][(self.step // round(6.2 / self.speed)) % 4]
                if self.file == "A_2":
                    self.surf = self.A_2[row][(self.step // round(6.2 / self.speed)) % 4]
                if self.file == "A_3":
                    self.surf = self.A_3[row][(self.step // round(6.2 / self.speed)) % 4]
                if self.file == "B_0":
                    self.surf = self.B_0[row][(self.step // round(6.2 / self.speed)) % 4]
                if self.file == "B_1":
                    self.surf = self.B_1[row][(self.step // round(6.2 / self.speed)) % 4]
                if self.file == "B_2":
                    self.surf = self.B_2[row][(self.step // round(6.2 / self.speed)) % 4]
                if self.file == "B_3":
                    self.surf = self.B_3[row][(self.step // round(6.2 / self.speed)) % 4]
                if self.file == "C_0":
                    self.surf = self.C_0[row][(self.step // round(6.2 / self.speed)) % 4]
                if self.file == "C_1":
                    self.surf = self.C_1[row][(self.step // round(6.2 / self.speed)) % 4]
                if self.file == "C_2":
                    self.surf = self.C_2[row][(self.step // round(6.2 / self.speed)) % 4]
                if self.file == "C_3":
                    self.surf = self.C_3[row][(self.step // round(6.2 / self.speed)) % 4]

            self.reload += 1
        else:
            self.die()
        self.hbar = health_bar(False, self.max_health, self.health)
        self.ebar = energy_bar(self.max_energy, self.energy)

    # Ball Attack
    def throw_ball(self, row):
        if row == 0:
            new_ball = Ball(self.rect.left+3, self.rect.bottom-5, "Down", self.attack)
        if row == 1:
            new_ball = Ball(self.rect.left + 14, self.rect.bottom - 10, "Down Right", self.attack)
        if row == 2:
            new_ball = Ball(self.rect.left + 20, self.rect.bottom - 26, "Right", self.attack)
        if row == 3:
            new_ball = Ball(self.rect.left + 10, self.rect.bottom - 32, "Up Right", self.attack)
        if row == 4:
            new_ball = Ball(self.rect.left + 3, self.rect.bottom - 36, "Up ", self.attack)
        if row == 5:
            new_ball = Ball(self.rect.left -10, self.rect.bottom - 32, "Up Left", self.attack)
        if row == 6:
            new_ball = Ball(self.rect.left -18, self.rect.bottom - 26, "Left", self.attack)
        if row == 7:
            new_ball = Ball(self.rect.left -16, self.rect.bottom - 10, "Down Left", self.attack)

    # Claw Attack
    def claw_strike(self, row):
        if row == 0:
            new_ball = Claw(self.rect.left, self.rect.bottom-12, "Down", self.attack)
        if row == 1:
            new_ball = Claw(self.rect.right-9, self.rect.bottom-5, "Down Right", self.attack)
        if row == 2:
            new_ball = Claw(self.rect.right-10, self.rect.top+8, "Right", self.attack)
        if row == 3:
            new_ball = Claw(self.rect.right - 3, self.rect.top - 4, "Up Right", self.attack)
        if row == 4:
            new_ball = Claw(self.rect.left, self.rect.top-10, "Up ", self.attack)
        if row == 5:
            new_ball = Claw(self.rect.left - 12, self.rect.top - 8, "Up Left", self.attack)
        if row == 6:
            new_ball = Claw(self.rect.left - 10, self.rect.top+8, "Left", self.attack)
        if row == 7:
            new_ball = Claw(self.rect.left - 7, self.rect.bottom - 3, "Down Left", self.attack)

    # Straw Attack
    def blow_straw(self, row):
        if row == 0:
            new_ball = Straw(self.rect.left + 6, self.rect.top + 5, "Down", self.attack)
        if row == 1:
            new_ball = Straw(self.rect.right - 10, self.rect.top + 2, "Down Right", self.attack)
        if row == 2:
            new_ball = Straw(self.rect.right-10, self.rect.top + 6, "Right", self.attack)
        if row == 3:
            new_ball = Straw(self.rect.right - 12, self.rect.top + 5, "Up Right", self.attack)
        if row == 4:
            new_ball = Straw(self.rect.left + 6, self.rect.top-10, "Up ", self.attack)
        if row == 5:
            new_ball = Straw(self.rect.left + 3, self.rect.top + 5, "Up Left", self.attack)
        if row == 6:
            new_ball = Straw(self.rect.left+5, self.rect.top + 6, "Left", self.attack)
        if row == 7:
            new_ball = Straw(self.rect.left + 3, self.rect.top + 3, "Down Left", self.attack)

    # Magic Hackeysack attack
    def punch(self, row):
        if row == 0:
            new_ball = Punch(self.rect.left, self.rect.bottom - 5, "Down", self.attack)
        if row == 1:
            new_ball = Punch(self.rect.right - 9, self.rect.bottom - 5, "Down Right", self.attack)
        if row == 2:
            new_ball = Punch(self.rect.right - 10, self.rect.top + 8, "Right", self.attack)
        if row == 3:
            new_ball = Punch(self.rect.right - 3, self.rect.top - 4, "Up Right", self.attack)
        if row == 4:
            new_ball = Punch(self.rect.left, self.rect.top - 10, "Up ", self.attack)
        if row == 5:
            new_ball = Punch(self.rect.left - 12, self.rect.top - 8, "Up Left", self.attack)
        if row == 6:
            new_ball = Punch(self.rect.left - 10, self.rect.top + 8, "Left", self.attack)
        if row == 7:
            new_ball = Punch(self.rect.left - 7, self.rect.bottom - 3, "Down Left", self.attack)

    # Equips armor or weapon to player
    def equip(self, item):
        global weapons
        global armor

        if item in weapons:
            self.hand = item
        if item in armor:
            self.armor = item

        if self.armor == "Red":
            self.max_health = 20
            self.sight = 1.8
            self.speed = 1.5
            if self.hand == "Claw":
                self.attack = 5
                self.speed -= 0.5
                self.file = "C_3"
            if self.hand == "Ball":
                self.attack = 2.5
                self.file = "C_2"
            if self.hand == "none":
                self.attack = 1
                self.file = "C_0"
            if self.hand == "Straw":
                self.attack = 1.5
                self.file = "C_1"
        if self.armor == "Green":
            self.max_health = 6
            self.sight = 1
            self.speed = 3.5
            if self.hand == "Claw":
                self.attack = 5
                self.speed -= 0.5
                self.file = "B_3"
            if self.hand == "Ball":
                self.attack = 2.5
                self.file = "B_2"
            if self.hand == "none":
                self.attack = 1
                self.file = "B_0"
            if self.hand == "Straw":
                self.attack = 1.5
                self.file = "B_1"
        if self.armor == "naked":
            self.max_health = 10
            self.sight = 1.3
            self.speed = 2
            if self.hand == "Claw":
                self.attack = 5
                self.speed -= 0.5
                self.file = "A_3"
            if self.hand == "Ball":
                self.attack = 2.5
                self.file = "A_2"
            if self.hand == "none":
                self.attack = 1
                self.file = "A_0"
            if self.hand == "Straw":
                self.attack = 1.5
                self.file = "A_1"

    # Causes player to become a puddle
    def puddle(self):
        if self.energy > 0:
            self.state = 1
            self.energy = self.energy - 0.05
        elif self.energy <= 0:
            self.health = self.health - 40
        self.form = "None"

    # Pick up in range items
    def pick_up(self, item):
        self.inv.append(item)

    # Sorts inventory
    def sort_inv(self):
        Ball = 0
        Cat_Claw = 0
        Claw = 0
        Green = 0
        Red = 0
        Slime = 0
        Straw = 0
        Sword = 0
        Wine_Drop = 0
        if "Ball" in self.inv:
            for x in range(len(self.inv)):
                if self.inv[x] == "Ball":
                    Ball += 1
        if "Cat_Claw" in self.inv:
            for x in range(len(self.inv)):
                if self.inv[x] == "Cat_Claw":
                    Cat_Claw += 1
        if "Claw" in self.inv:
            for x in range(len(self.inv)):
                if self.inv[x] == "Claw":
                    Claw += 1
        if "Green" in self.inv:
            for x in range(len(self.inv)):
                if self.inv[x] == "Green":
                    Green += 1
        if "Red" in self.inv:
            for x in range(len(self.inv)):
                if self.inv[x] == "Red":
                    Red += 1
        if "Slime" in self.inv:
            for x in range(len(self.inv)):
                if self.inv[x] == "Slime":
                    Slime += 1
        if "Straw" in self.inv:
            for x in range(len(self.inv)):
                if self.inv[x] == "Straw":
                    Straw += 1
        if "Sword" in self.inv:
            for x in range(len(self.inv)):
                if self.inv[x] == "Sword":
                    Sword += 1
        if "Wine_Drop" in self.inv:
            for x in range(len(self.inv)):
                if self.inv[x] == "Wine_Drop":
                    Wine_Drop += 1

        return[Ball, Cat_Claw, Claw, Green, Red, Slime, Straw, Sword, Wine_Drop]

    # If player charecters health reaches 0
    # Death process
    def die(self):
        global player_dead
        player_dead = True
        self.health = 1  # Prevent repeated die() calls


# Attacks from Player Charecter
class PlayerAttacks(Entities):
    # Initialises Player Attacks instances
    def __init__(self, x, y, file, damage, speed, direction):
        super(PlayerAttacks, self).__init__(x, y, file)
        self.damage = damage
        self.speed = speed
        self.direction = direction
        self.frame = 0
        all_attacksa.add(self)

    # if attack hits an enemy
    def hit(self, entity):
        entity.health -= self.damage


# Create class for ball attack sprites
class Ball(PlayerAttacks):
    def __init__(self, x, y, direction, damage):
        super(Ball, self).__init__(x, y, "Images/Sprites/Thred/SlimeBall.png", damage, 3, direction)

    def update(self):
        self.frame += 1
        if "Up" in self.direction:
            if "Left" in self.direction:
                self.rect.move_ip(-0.7*self.speed, -0.7* self.speed)
            elif "Right" in self.direction:
                self.rect.move_ip(0.7*self.speed, -0.7*self.speed)
            else:
                self.rect.move_ip(0, -self.speed)
        elif "Down" in self.direction:
            if "Left" in self.direction:
                self.rect.move_ip(-0.7*self.speed, 0.7*self.speed)
            elif "Right" in self.direction:
                self.rect.move_ip(0.7*self.speed, 0.7*self.speed)
            else:
                self.rect.move_ip(0, self.speed)
        elif "Left" in self.direction:
            self.rect.move_ip(-self.speed, 0)
        elif "Right" in self.direction:
            self.rect.move_ip(self.speed, 0)

        if self.frame == 20:
            self.kill()
        if (Layers.map[(self.rect.centery//32)][(self.rect.centerx//32)]) in Layers.walls:
            self.kill()
        for enemy in all_enemies:
            if self.rect.colliderect(enemy.rect):
                self.hit(enemy)
                self.kill()
                break


# Create class for claw attack sprites
class Claw(PlayerAttacks):
    claw0 = pygame.image.load("Images/Sprites/Thred/Claw0.png").convert()
    transcolour = claw0.get_at((0, 0))
    claw0.set_colorkey(transcolour)
    claw1 = pygame.image.load("Images/Sprites/Thred/Claw1.png").convert()
    transcolour = claw1.get_at((0, 0))
    claw1.set_colorkey(transcolour)
    claw2 = pygame.image.load("Images/Sprites/Thred/Claw2.png").convert()
    transcolour = claw2.get_at((0, 0))
    claw2.set_colorkey(transcolour)
    claw3 = pygame.image.load("Images/Sprites/Thred/Claw3.png").convert()
    transcolour = claw3.get_at((0, 0))
    claw3.set_colorkey(transcolour)
    claw4 = pygame.image.load("Images/Sprites/Thred/Claw4.png").convert()
    transcolour = claw4.get_at((0, 0))
    claw4.set_colorkey(transcolour)
    claw5 = pygame.image.load("Images/Sprites/Thred/Claw5.png").convert()
    transcolour = claw5.get_at((0, 0))
    claw5.set_colorkey(transcolour)
    claw6 = pygame.image.load("Images/Sprites/Thred/Claw6.png").convert()
    transcolour = claw6.get_at((0, 0))
    claw6.set_colorkey(transcolour)
    claw7 = pygame.image.load("Images/Sprites/Thred/Claw7.png").convert()
    transcolour = claw7.get_at((0, 0))
    claw7.set_colorkey(transcolour)
    clawU = [claw2, claw3, claw0]
    clawD = [claw0, claw1, claw2]
    clawR = [claw4, claw5, claw7]
    clawL = [claw3, claw0, claw1]
    clawUL = [claw2, claw3, claw0]
    clawUR = [claw6, claw4, claw5]
    clawDL = [claw3, claw0, claw1]
    clawDR = [claw4, claw5, claw7]

    def __init__(self, x, y, direction, damage):
        self.direction = direction
        if "Up" in self.direction:
            if "Left" in self.direction:
                self.file = self.clawUL
            elif "Right" in self.direction:
                self.file = self.clawUR
            else:
                self.file = self.clawU
        elif "Down" in self.direction:
            if "Left" in self.direction:
                self.file = self.clawDL
            elif "Right" in self.direction:
                self.file = self.clawDR
            else:
                self.file = self.clawD
        elif "Left" in self.direction:
            self.file = self.clawL
        elif "Right" in self.direction:
            self.file = self.clawR
        self.surf = self.file[0]
        super(Claw, self).__init__(x, y, "none", damage, 2, direction)

    def update(self):
        if 1 <= self.frame < 3:
            self.surf = self.file[1]
        if 3 <= self.frame < 4:
            self.surf = self.file[2]
        self.frame += 1
        if self.frame == 4:
            self.kill()
        for enemy in all_enemies:
            if self.rect.colliderect(enemy.rect):
                self.hit(enemy)
                self.kill()
                break


# Create class for straw attacks
class Straw(PlayerAttacks):
    def __init__(self, x, y, direction, damage):
        super(Straw, self).__init__(x, y, "Images/Sprites/Thred/Drip.png", damage, 6, direction)

    def update(self):
        self.frame += 1
        if "Up" in self.direction:
            if "Left" in self.direction:
                self.rect.move_ip(-0.7 * self.speed, -0.7 * self.speed)
            elif "Right" in self.direction:
                self.rect.move_ip(0.7 * self.speed, -0.7 * self.speed)
            else:
                self.rect.move_ip(0, -self.speed)
        elif "Down" in self.direction:
            if "Left" in self.direction:
                self.rect.move_ip(-0.7 * self.speed, 0.7 * self.speed)
            elif "Right" in self.direction:
                self.rect.move_ip(0.7 * self.speed, 0.7 * self.speed)
            else:
                self.rect.move_ip(0, self.speed)
        elif "Left" in self.direction:
            self.rect.move_ip(-self.speed, 0)
        elif "Right" in self.direction:
            self.rect.move_ip(self.speed, 0)

        if self.frame == 35:
            self.kill()
        if (Layers.map[(self.rect.centery // 32)][(self.rect.centerx // 32)]) in Layers.walls:
            self.kill()
        for enemy in all_enemies:
            if self.rect.colliderect(enemy.rect):
                self.hit(enemy)
                self.kill()
                break


# Create class for punch attacks
class Punch(PlayerAttacks):
    punch0 = pygame.image.load("Images/Sprites/Thred/YarnFist0.png").convert()
    transcolour = punch0.get_at((0, 0))
    punch0.set_colorkey(transcolour)
    punch1 = pygame.image.load("Images/Sprites/Thred/YarnFist1.png").convert()
    transcolour = punch1.get_at((0, 0))
    punch1.set_colorkey(transcolour)
    punch2 = pygame.image.load("Images/Sprites/Thred/YarnFist2.png").convert()
    transcolour = punch2.get_at((0, 0))
    punch2.set_colorkey(transcolour)
    punch3 = pygame.image.load("Images/Sprites/Thred/YarnFist3.png").convert()
    transcolour = punch3.get_at((0, 0))
    punch3.set_colorkey(transcolour)
    punch4 = pygame.image.load("Images/Sprites/Thred/YarnFist4.png").convert()
    transcolour = punch4.get_at((0, 0))
    punch4.set_colorkey(transcolour)
    punch5 = pygame.image.load("Images/Sprites/Thred/YarnFist5.png").convert()
    transcolour = punch5.get_at((0, 0))
    punch5.set_colorkey(transcolour)
    punch6 = pygame.image.load("Images/Sprites/Thred/YarnFist6.png").convert()
    transcolour = punch6.get_at((0, 0))
    punch6.set_colorkey(transcolour)
    punch7 = pygame.image.load("Images/Sprites/Thred/YarnFist7.png").convert()
    transcolour = punch7.get_at((0, 0))
    punch7.set_colorkey(transcolour)
    punchU = [punch2, punch3, punch0]
    punchD = [punch0, punch1, punch2]
    punchR = [punch4, punch5, punch7]
    punchL = [punch3, punch0, punch1]
    punchUL = [punch2, punch3, punch0]
    punchUR = [punch6, punch4, punch5]
    punchDL = [punch3, punch0, punch1]
    punchDR = [punch4, punch5, punch7]

    def __init__(self, x, y, direction, damage):
        self.direction = direction
        if "Up" in self.direction:
            if "Left" in self.direction:
                self.file = self.punchUL
            elif "Right" in self.direction:
                self.file = self.punchUR
            else:
                self.file = self.punchU
        elif "Down" in self.direction:
            if "Left" in self.direction:
                self.file = self.punchDL
            elif "Right" in self.direction:
                self.file = self.punchDR
            else:
                self.file = self.punchD
        elif "Left" in self.direction:
            self.file = self.punchL
        elif "Right" in self.direction:
            self.file = self.punchR
        self.surf = self.file[0]
        super(Punch, self).__init__(x, y, "none", damage, 2, direction)

    def update(self):
        if 4 <= self.frame < 8:
            self.surf = self.file[1]
        if 8 <= self.frame < 12:
            self.surf = self.file[2]
        self.frame += 1
        if self.frame == 12:
            self.kill()
        for enemy in all_enemies:
            if self.rect.colliderect(enemy.rect):
                self.hit(enemy)
                self.kill()
                break


# Enemeis, anything that attacks the player
class Enemies(pygame.sprite.Sprite):
    # Initialise Enemy instance
    def __init__(self, x, y, file, health, attack, state, sight, speed, enemy):
        super(Enemies, self).__init__()
        if file != "none":
            self.surf = pygame.image.load(file).convert()
            self.file = file
            transcolour = self.surf.get_at((0, 0))
            self.surf.set_colorkey(transcolour)
        self.rect = self.surf.get_rect(
            topleft=(
                x,
                y
            )
        )
        self.size = self.surf.get_size()
        self.health = health
        self.max_health = health
        self.attack = attack
        self.state = state
        self.sight = sight
        self.speed = speed
        self.enemy = enemy
        # Patrol wander state (used when player not in sight)
        self.patrol_timer = random.randint(0, 60)
        self.patrol_dx = 0
        self.patrol_dy = 0

    def patrol_wander(self):
        self.patrol_timer += 1
        if self.patrol_timer >= 90:
            self.patrol_timer = 0
            angle = random.uniform(0, 6.2832)
            spd = self.speed * 0.4
            self.patrol_dx = math.cos(angle) * spd
            self.patrol_dy = math.sin(angle) * spd
        dx = int(self.patrol_dx)
        dy = int(self.patrol_dy)
        if dx != 0 or dy != 0:
            self.rect.move_ip(dx, dy)
            r, c = self.rect.centery // 32, self.rect.centerx // 32
            r = max(0, min(r, len(Layers.map)-1))
            c = max(0, min(c, len(Layers.map[0])-1))
            if Layers.map[r][c] in Layers.walls:
                self.rect.move_ip(-dx*2, -dy*2)
                self.patrol_dx = -self.patrol_dx
                self.patrol_dy = -self.patrol_dy


# Attacks from Enemy entities
class EnemyAttacks(Entities):
    # Initialises enemy attacks
    def __init__(self, x, y, file, damage, speed, direction):
        super(EnemyAttacks, self).__init__(x, y, file)
        self.damage = damage
        self.speed = speed
        self.direction = direction
        self.frame = 0
        all_attacksb.add(self)

    # if enemy attack hits player
    def hit(self, entity):
        if entity.form == "Solid":
            defense = getattr(entity, 'defense_mult', 1.0)
            entity.health -= self.damage * defense


# Wine Enemy Class
class wine_boi(Enemies):
    # Initialise Wine enemy instances
    def __init__(self, x, y, health, attack, speed, sight, enemy):
        wine = SpriteSheet('Images/Sprites/Wine/Wine.png')
        wine_al = SpriteSheet('Images/Sprites/Wine/Wine_Attack_Left.png')
        wine_ar = SpriteSheet('Images/Sprites/Wine/Wine_Attack_Right.png')
        wine_mr = SpriteSheet('Images/Sprites/Wine/Wine_Missing_Right.png')
        wine_ml = SpriteSheet('Images/Sprites/Wine/Wine_Missing_Left.png')
        wine_mb = SpriteSheet('Images/Sprites/Wine/Wine_Missing_Both.png')
        wine_aml = SpriteSheet('Images/Sprites/Wine/Wine_Attack_Missing_Left.png')
        wine_amr = SpriteSheet('Images/Sprites/Wine/Wine_Attack_Missing_Right.png')
        self.Wine_0 = []
        for row in range(9):
            self.Wine_0.append([])
            for column in range(4):
                self.Wine_0[row].append(wine.image_at(((column * 32), row * 32, 32, 32), colorkey=(141, 47, 173)))
        self.A_L = []
        for row in range(9):
            self.A_L.append([])
            for column in range(4):
                self.A_L[row].append(wine_al.image_at(((96 - (column * 32)), row * 32, 32, 32), colorkey=(141, 47, 173)))
        self.A_R = []
        for row in range(9):
            self.A_R.append([])
            for column in range(4):
                self.A_R[row].append(wine_ar.image_at(((column * 32), row * 32, 32, 32), colorkey=(141, 47, 173)))
        self.M_L = []
        for row in range(9):
            self.M_L.append([])
            for column in range(4):
                self.M_L[row].append(wine_ml.image_at(((96 - (column * 32)), row * 32, 32, 32), colorkey=(141, 47, 173)))
        self.M_R = []
        for row in range(9):
            self.M_R.append([])
            for column in range(4):
                self.M_R[row].append(wine_mr.image_at(((column*32), row*32, 32, 32), colorkey=(141, 47, 173)))
        self.M_B = []
        for row in range(9):
            self.M_B.append([])
            for column in range(4):
                self.M_B[row].append(wine_mb.image_at(((column * 32), row * 32, 32, 32), colorkey=(141, 47, 173)))
        self.Wine_A_M_R = []
        for row in range(9):
            self.Wine_A_M_R .append([])
            for column in range(4):
                self.Wine_A_M_R[row].append(wine_amr.image_at((96-(column * 32), row * 32, 32, 32), colorkey=(141, 47, 173)))
        self.Wine_A_M_L = []
        for row in range(9):
            self.Wine_A_M_L.append([])
            for column in range(4):
                self.Wine_A_M_L[row].append(wine_aml.image_at(((column * 32), row * 32, 32, 32), colorkey=(141, 47, 173)))
        self.surf = self.Wine_0[0][0]
        super(wine_boi, self).__init__(x, y, "none", health, attack, 0, sight, speed, enemy)
        self.last_tl = [self.rect.top // 32, self.rect.left // 32]
        self.last_row = 0
        self.step = 0
        self.reload = 1
        self.reloadL = 0
        self.reloadR = 0
        self.hand = [1, 1]
        self.trajectory = 0
        self.bar = health_bar(True, health, health)
        self.item = Items(0, 0, Image.winedrop[1], Image.winedrop[0], "Wine")

    # Updates wine enemy based on player position and frame number
    def update(self):
        if self.health > 0:
            # Renders if on screen
            if all((((self.enemy.rect.center[0]-screen.get_width()/2)<self.rect.left<(self.enemy.rect.center[0]+screen.get_width()/2)), ((self.enemy.rect.center[1]-screen.get_height()/2)<self.rect.top<(self.enemy.rect.center[1]+screen.get_height()/2)))):

                down = False
                up = False
                right = False
                left = False

                # get x and y displacements from enemy to objects
                # See if player is in sight or behind walls
                if self.enemy.form == "Solid":
                    playerVect = pygame.math.Vector2(self.enemy.rect.centerx - self.rect.centerx, self.enemy.rect.centery - self.rect.top)
                else:
                    playerVect = pygame.math.Vector2(10000, 10000)
                if playerVect.length() <= self.sight:
                    sight1 = True
                    sight2 = True
                    sight3 = True
                    sight4 = True
                    for wall in all_blocks:
                        wallVect = pygame.math.Vector2(wall.rect.centerx - self.rect.centerx, wall.rect.centery - self.rect.top)
                        if wallVect.length() <= self.sight:
                            if abs(wallVect.length()) <= abs(playerVect.length()):
                                if all(((wall.rect.centery < self.rect.top), (self.enemy.rect.centery < self.rect.top))):
                                    if (math.atan2(wallVect[0]-16, wallVect[1]+16) < math.atan2(self.enemy.rect.left - self.rect.centerx, self.enemy.rect.bottom - self.rect.top) < math.atan2(wallVect[0]+16, wallVect[1]+16)):
                                        sight1 = False
                                        sight3 = False
                                    if (math.atan2(wallVect[0]-16, wallVect[1]+16) < math.atan2(self.enemy.rect.right - self.rect.centerx, self.enemy.rect.bottom - self.rect.top) < math.atan2(wallVect[0]+16, wallVect[1]+16)):
                                        sight2 = False
                                        sight4 = False
                                elif all(((wall.rect.centery > self.rect.top), (self.enemy.rect.centery > self.rect.top))):
                                    if (math.atan2(wallVect[0] + 16, wallVect[1] - 16) < math.atan2(
                                            self.enemy.rect.left - self.rect.centerx, self.enemy.rect.top - self.rect.top) < math.atan2(wallVect[0] - 16,
                                                                                             wallVect[1] - 16)):
                                        sight1 = False
                                        sight3 = False
                                    if (math.atan2(wallVect[0] + 16, wallVect[1] + 16) < math.atan2(
                                            self.enemy.rect.right - self.rect.centerx, self.enemy.rect.top - self.rect.top) < math.atan2(wallVect[0] - 16,
                                                                                              wallVect[1] + 16)):
                                        sight2 = False
                                        sight4 = False
                                if all(((wall.rect.centerx < self.rect.centerx), (self.enemy.rect.centerx < self.rect.centerx))):
                                    if (math.atan2(wallVect[0] + 16, wallVect[1] - 16) < math.atan2(
                                            self.enemy.rect.right - self.rect.centerx, self.enemy.rect.top - self.rect.top) < math.atan2(wallVect[0] + 16,
                                                                                             wallVect[1] + 16)):
                                        sight2 = False
                                        sight3 = False
                                    if (math.atan2(wallVect[0] + 16, wallVect[1] - 16) < math.atan2(
                                            self.enemy.rect.right - self.rect.centerx, self.enemy.rect.bottom - self.rect.top) < math.atan2(wallVect[0] + 16,
                                                                                              wallVect[1] + 16)):
                                        sight1 = False
                                        sight4 = False
                                elif all(((wall.rect.centerx > self.rect.centerx), (self.enemy.rect.centerx > self.rect.centerx))):
                                    if (math.atan2(wallVect[0] + 16, wallVect[1] + 16) < math.atan2(
                                            self.enemy.rect.left - self.rect.centerx, self.enemy.rect.top - self.rect.top) < math.atan2(wallVect[0] + 16,
                                                                                             wallVect[1] - 16)):
                                        sight2 = False
                                        sight3 = False
                                    if (math.atan2(wallVect[0] + 16, wallVect[1] + 16) < math.atan2(
                                            self.enemy.rect.left - self.rect.centerx, self.enemy.rect.bottom - self.rect.top) < math.atan2(wallVect[0] + 16,
                                                                                              wallVect[1] - 16)):
                                        sight1 = False
                                        sight4 = False

                    if any((sight1, sight2, sight3, sight4)):
                        if playerVect[0] == 0:
                            playerVect[0] = 0.0000000001
                        if playerVect[1] == 0:
                            playerVect[1] = 0.0000000001
                        self.trajectory = playerVect.normalize()
                        if abs(playerVect.length()) < 45:
                            self.rect.move_ip(
                                -round(self.trajectory[0] * self.speed + math.copysign(0.5, self.trajectory[0])),
                                -round(self.trajectory[1] * self.speed + math.copysign(0.5, self.trajectory[1])))
                        elif abs(playerVect.length()) > 55:
                            self.rect.move_ip(
                                round(self.trajectory[0] * self.speed + math.copysign(0.5, self.trajectory[0])),
                                round(self.trajectory[1] * self.speed + math.copysign(0.5, self.trajectory[1])))

                        if self.trajectory[0]*self.speed <= -0.5:
                            left = True
                        if self.trajectory[0]*self.speed >= 0.5:
                            right = True
                        if self.trajectory[1]*self.speed <= -0.5:
                            up = True
                        if self.trajectory[1]*self.speed >= 0.5:
                            down = True

                        # Collision Detection
                        cur_tl = [self.rect.top // 16, self.rect.left // 16]

                        if (Layers.map[(self.rect.top//32)][(self.rect.left//32)]) in Layers.walls:
                            if (Layers.map[(self.rect.top//32)][(self.rect.right//32)]) in Layers.walls:
                                if (Layers.map[(self.rect.bottom//32)][(self.rect.left//32)]) in Layers.walls:
                                    self.rect.move_ip(((self.last_tl[1] - cur_tl[1]) * self.speed), ((self.last_tl[0] - cur_tl[0]) * self.speed))
                                elif (Layers.map[(self.rect.bottom//32)][(self.rect.right//32)]) in Layers.walls:
                                    self.rect.move_ip((self.last_tl[1] - cur_tl[1])*self.speed, ((self.last_tl[0] - cur_tl[0])*self.speed))
                                else:
                                    self.rect.move_ip(0, ((self.last_tl[0] - cur_tl[0]) * self.speed))
                            elif (Layers.map[(self.rect.bottom//32)][(self.rect.left//32)]) in Layers.walls:
                                if (Layers.map[(self.rect.bottom//32)][(self.rect.right//32)]) in Layers.walls:
                                    self.rect.move_ip(((self.last_tl[1] - cur_tl[1]) * self.speed), ((self.last_tl[0] - cur_tl[0]) * self.speed))
                                else:
                                    self.rect.move_ip(((self.last_tl[1] - cur_tl[1]) * self.speed), 0)
                            else:
                                self.rect.move_ip((abs(self.last_tl[1] - cur_tl[1]) * self.speed)+1, (abs(self.last_tl[0] - cur_tl[0])*self.speed)+1)
                        elif (Layers.map[(self.rect.top//32)][(self.rect.right//32)]) in Layers.walls:
                            if (Layers.map[(self.rect.bottom//32)][(self.rect.left//32)]) in Layers.walls:
                                self.rect.move_ip(((self.last_tl[1] - cur_tl[1]) * self.speed), ((self.last_tl[0] - cur_tl[0])*self.speed))
                            elif (Layers.map[(self.rect.bottom//32)][(self.rect.right//32)]) in Layers.walls:
                                self.rect.move_ip((-abs(self.last_tl[1] - cur_tl[1]) * self.speed), 0)
                            else:
                                self.rect.move_ip((-abs(self.last_tl[1] - cur_tl[1]) * self.speed)-1, (abs(self.last_tl[0] - cur_tl[0]) * self.speed)+1)
                        elif (Layers.map[(self.rect.bottom//32)][(self.rect.right//32)]) in Layers.walls:
                            if (Layers.map[(self.rect.bottom//32)][(self.rect.left//32)]) in Layers.walls:
                                self.rect.move_ip(0, ((self.last_tl[0] - cur_tl[0]) * self.speed))
                            else:
                                self.rect.move_ip((-abs(self.last_tl[1] - cur_tl[1]) * self.speed)-1, (-abs(self.last_tl[0] - cur_tl[0])*self.speed)-1)
                        elif (Layers.map[(self.rect.bottom//32)][(self.rect.left//32)]) in Layers.walls:
                            self.rect.move_ip((abs(self.last_tl[1] - cur_tl[1]) * self.speed)+1, (-abs(self.last_tl[0] - cur_tl[0]) * self.speed)-1)

                        self.last_tl = [self.rect.top // 16, self.rect.left // 16]

                        if any(((self.state == 0), (self.state == 4), (self.state == 3))):
                            if self.reload > 80:
                                if self.hand[0] == 1:
                                    self.state = 2
                                    self.step = 0
                                    self.reloadL = 0
                                    self.reload = 0
                                    self.hand[0] = 0
                                elif self.hand[1] == 1:
                                    self.state = 1
                                    self.step = 0
                                    self.reloadR = 0
                                    self.reload = 0
                                    self.hand[1] = 0

                # Patrol wander when player not in sight
                if playerVect.length() > self.sight:
                    self.patrol_wander()

                # If seen move enemy
                if all(((self.state != 1), (self.state != 2), (self.state != 6), (self.state != 7))):
                    if self.hand[0] == 0:
                        if self.reloadL > 120:
                            self.hand[0] = 1
                        else:
                            self.reloadL += 1

                    if self.hand[1] == 0:
                        if self.reloadR > 120:
                            self.hand[1] = 1
                        else:
                            self.reloadR += 1

                    if self.hand[0] == 1:
                        if self.hand[1] == 0:
                            self.state = 3
                        elif self.hand[1] == 1:
                            self.state = 0
                    elif self.hand[1] == 1:
                        self.state = 4
                    else:
                        self.state = 5
                if any(((self.state == 1), (self.state == 6))):
                    if self.hand[0] == 1:
                        self.state = 1
                    else:
                        self.state = 6
                if any(((self.state == 2), (self.state == 7))):
                    if self.hand[1] == 1:
                        self.state = 2
                    else:
                        self.state = 7

                # Enemy Animations and Actions
                if self.state == 1:  # Attack Right
                    if down:
                        if left:
                            row = 7
                            self.step += 1
                        elif right:
                            row = 1
                            self.step += 1
                        else:
                            row = 0
                            self.step += 1
                    elif up:
                        if left:
                            row = 5
                            self.step += 1
                        elif right:
                            row = 3
                            self.step += 1
                        else:
                            row = 4
                            self.step += 1
                    elif left:
                        row = 6
                        self.step += 1
                    elif right:
                        row = 2
                        self.step += 1
                    else:
                        row = self.last_row
                        self.step += 1

                    self.last_row = row
                    if (self.step // round(6.2/self.speed)) >= 3:
                        self.state = 0
                        self.step = 0
                        self.surf = self.A_R[row][3]
                    else:
                        self.surf = self.A_R[row][(self.step // round(6.2 / self.speed)) % 4]
                    if self.step == round(5/self.speed):
                        self.throw_wine(row, (not left))

                elif self.state == 2:  # Attack Left
                    if down:
                        if left:
                            row = 1
                            self.step += 1
                        elif right:
                            row = 7
                            self.step += 1
                        else:
                            row = 0
                            self.step += 1
                    elif up:
                        if left:
                            row = 3
                            self.step += 1
                        elif right:
                            row = 5
                            self.step += 1
                        else:
                            row = 4
                            self.step += 1
                    elif left:
                        row = 2
                        self.step += 1
                    elif right:
                        row = 6
                        self.step += 1
                    else:
                        row = self.last_row
                        self.step += 1

                    self.last_row = row
                    if (self.step // round(6.2 / self.speed)) >= 3:
                        self.state = 0
                        self.step = 0
                        self.surf = self.A_L[row][3]
                    else:
                        self.surf = self.A_L[row][(self.step // round(6.2 / self.speed)) % 4]
                    if self.step == round(5/self.speed):
                        self.throw_wine(row, (not left))
                    self.surf = self.A_L[row][(self.step // round(6.2 / self.speed)) % 4]

                elif self.state == 3:  # Missing Right
                    if down:
                        if left:
                            row = 7
                            self.step += 1
                        elif right:
                            row = 1
                            self.step += 1
                        else:
                            row = 0
                            self.step += 1
                    elif up:
                        if left:
                            row = 5
                            self.step += 1
                        elif right:
                            row = 3
                            self.step += 1
                        else:
                            row = 4
                            self.step += 1
                    elif left:
                        row = 6
                        self.step += 1
                    elif right:
                        row = 2
                        self.step += 1
                    else:
                        row = self.last_row
                        self.step += 1
                    self.last_row = row
                    self.surf = self.M_R[row][(self.step // round(6.2 / self.speed)) % 4]

                elif self.state == 4:  # Missing Left
                    if down:
                        if left:
                            row = 1
                            self.step += 1
                        elif right:
                            row = 7
                            self.step += 1
                        else:
                            row = 0
                            self.step += 1
                    elif up:
                        if left:
                            row = 3
                            self.step += 1
                        elif right:
                            row = 5
                            self.step += 1
                        else:
                            row = 4
                            self.step += 1
                    elif left:
                        row = 2
                        self.step += 1
                    elif right:
                        row = 6
                        self.step += 1
                    else:
                        row = self.last_row
                        self.step += 1

                    self.last_row = row
                    self.surf = self.M_L[row][(self.step // round(6.2 / self.speed)) % 4]

                elif self.state == 5:  # Missing Both
                    if down:
                        if left:
                            row = 7
                            self.step += 1
                        elif right:
                            row = 1
                            self.step += 1
                        else:
                            row = 0
                            self.step += 1
                    elif up:
                        if left:
                            row = 5
                            self.step += 1
                        elif right:
                            row = 3
                            self.step += 1
                        else:
                            row = 4
                            self.step += 1
                    elif left:
                        row = 6
                        self.step += 1
                    elif right:
                        row = 2
                        self.step += 1
                    else:
                        row = self.last_row
                        self.step += 1

                    self.last_row = row
                    self.surf = self.M_B[row][(self.step // round(6.2 / self.speed)) % 4]

                elif self.state == 6:  # Attack Right
                    if down:
                        if left:
                            row = 7
                            self.step += 1
                        elif right:
                            row = 1
                            self.step += 1
                        else:
                            row = 0
                            self.step += 1
                    elif up:
                        if left:
                            row = 5
                            self.step += 1
                        elif right:
                            row = 3
                            self.step += 1
                        else:
                            row = 4
                            self.step += 1
                    elif left:
                        row = 6
                        self.step += 1
                    elif right:
                        row = 2
                        self.step += 1
                    else:
                        row = self.last_row
                        self.step += 1

                    self.last_row = row
                    if (self.step // round(6.2/self.speed)) >= 3:
                        self.state = 0
                        self.step = 0
                        self.surf = self.Wine_A_M_L[row][3]
                    else:
                        self.surf = self.Wine_A_M_L[row][(self.step // round(6.2 / self.speed)) % 4]
                    if self.step == round(5/self.speed):
                        self.throw_wine(row, (not left))

                elif self.state == 7:  # Attack Left
                    if down:
                        if left:
                            row = 1
                            self.step += 1
                        elif right:
                            row = 7
                            self.step += 1
                        else:
                            row = 0
                            self.step += 1
                    elif up:
                        if left:
                            row = 3
                            self.step += 1
                        elif right:
                            row = 5
                            self.step += 1
                        else:
                            row = 4
                            self.step += 1
                    elif left:
                        row = 2
                        self.step += 1
                    elif right:
                        row = 6
                        self.step += 1
                    else:
                        row = self.last_row
                        self.step += 1

                    self.last_row = row
                    if (self.step // round(6.2 / self.speed)) >= 3:
                        self.state = 0
                        self.step = 0
                        self.surf = self.Wine_A_M_R[row][3]
                    else:
                        self.surf = self.Wine_A_M_R[row][(self.step // round(6.2 / self.speed)) % 4]
                    if self.step == round(5/self.speed):
                        self.throw_wine(row, (not left))

                else:
                    if down:
                        if left:
                            row = 7
                            self.step += 1
                        elif right:
                            row = 1
                            self.step += 1
                        else:
                            row = 0
                            self.step += 1
                    elif up:
                        if left:
                            row = 5
                            self.step += 1
                        elif right:
                            row = 3
                            self.step += 1
                        else:
                            row = 4
                            self.step += 1
                    elif left:
                        row = 6
                        self.step += 1
                    elif right:
                        row = 2
                        self.step += 1
                    else:
                        row = self.last_row
                        self.step += 1

                    self.last_row = row
                    self.surf = self.Wine_0[row][(self.step // round(6.2 / self.speed)) % 4]

                self.reload += 1

        else:
            self.surf = self.Wine_0[8][(self.step // round(9 / self.speed)) % 4]
            self.step += 1
            if (self.step // round(9 / self.speed)) > 3:
                self.die()

        self.bar = health_bar(True, self.max_health, self.health)

    # Enemy Attacks with wine ball
    def throw_wine(self, row, right):
        if not right:
            if row == 0:
                new_ball = wine(self.rect.left + 3, self.rect.bottom - 5, self.trajectory, self.attack)
            if row == 1:
                new_ball = wine(self.rect.left + 14, self.rect.bottom - 10, self.trajectory, self.attack)
            if row == 2:
                new_ball = wine(self.rect.left + 20, self.rect.bottom - 26, self.trajectory, self.attack)
            if row == 3:
                new_ball = wine(self.rect.left + 10, self.rect.bottom - 32, self.trajectory, self.attack)
            if row == 4:
                new_ball = wine(self.rect.left + 3, self.rect.bottom - 36, self.trajectory, self.attack)
            if row == 5:
                new_ball = wine(self.rect.left -10, self.rect.bottom - 32, self.trajectory, self.attack)
            if row == 6:
                new_ball = wine(self.rect.left -18, self.rect.bottom - 26, self.trajectory, self.attack)
            if row == 7:
                new_ball = wine(self.rect.left -16, self.rect.bottom - 10, self.trajectory, self.attack)
        if right:
            if row == 0:
                new_ball = wine(self.rect.left + 3, self.rect.bottom - 5, self.trajectory, self.attack)
            if row == 7:
                new_ball = wine(self.rect.left + 14, self.rect.bottom - 10, self.trajectory, self.attack)
            if row == 6:
                new_ball = wine(self.rect.left + 20, self.rect.bottom - 26, self.trajectory, self.attack)
            if row == 5:
                new_ball = wine(self.rect.left + 10, self.rect.bottom - 32, self.trajectory, self.attack)
            if row == 4:
                new_ball = wine(self.rect.left + 3, self.rect.bottom - 36, self.trajectory, self.attack)
            if row == 3:
                new_ball = wine(self.rect.left -10, self.rect.bottom - 32, self.trajectory, self.attack)
            if row == 2:
                new_ball = wine(self.rect.left -18, self.rect.bottom - 26, self.trajectory, self.attack)
            if row == 1:
                new_ball = wine(self.rect.left -16, self.rect.bottom - 10, self.trajectory, self.attack)

    # Enemy death process
    def die(self):
        global thred
        try:
            thred.thread += max(1, int(3 * getattr(thred, 'thread_mult', 1.0)))
        except Exception:
            pass
        self.item.spawn(self.rect.centerx, self.rect.centery)
        self.kill()


# Enemy attack wine sprites
class wine(EnemyAttacks):

    # Initiates instances of wine
    def __init__(self, x, y, direction, damage):
        super(wine, self).__init__(x, y, "Images/Sprites/Thred/Drip.png", damage, 6, direction)
        self.trajectory = direction

    def update(self):
        self.frame += 1
        self.rect.move_ip(self.trajectory[0]*self.speed, self.trajectory[1]*self.speed)

        if self.frame == 35:
            self.kill()
        if (Layers.map[(self.rect.centery // 32)][(self.rect.centerx // 32)]) in Layers.walls:
            self.kill()
        for player in all_mains:
            if self.rect.colliderect(player.rect):
                self.hit(player)
                self.kill()
                break


# Slime Enemy Class
class slime_boi(Enemies):

    # Initiates Slime Instances
    def __init__(self, x, y, health, attack, speed, sight, enemy, color, size):
        self.size = size
        self.slime_white = SpriteSheet('Images/Sprites/Slime/Slime_Small_White.png')
        self.slime_white2 = SpriteSheet('Images/Sprites/Slime/Slime_Medium_White.png')
        self.slime_red = SpriteSheet('Images/Sprites/Slime/Slime_Small_Red.png')
        self.slime_red2 = SpriteSheet('Images/Sprites/Slime/Slime_Medium_Red.png')
        self.slime_green = SpriteSheet('Images/Sprites/Slime/Slime_Small_Green.png')
        self.slime_green2 = SpriteSheet('Images/Sprites/Slime/Slime_Medium_Green.png')
        self.explosion = [pygame.transform.scale(pygame.image.load("Images/Sprites/Slime/Explosion/explosion anim1.png").convert(), (16, 16)),
                     pygame.transform.scale(pygame.image.load("Images/Sprites/Slime/Explosion/explosion anim2.png").convert(), (16, 16)),
                     pygame.transform.scale(pygame.image.load("Images/Sprites/Slime/Explosion/explosion anim3.png").convert(), (16, 16)),
                     pygame.transform.scale(pygame.image.load("Images/Sprites/Slime/Explosion/explosion anim4.png").convert(), (16, 16)),
                     pygame.transform.scale(pygame.image.load("Images/Sprites/Slime/Explosion/explosion anim5.png").convert(), (16, 16)),
                     pygame.transform.scale(pygame.image.load("Images/Sprites/Slime/Explosion/explosion anim6.png").convert(), (16, 16)),
                     pygame.transform.scale(pygame.image.load("Images/Sprites/Slime/Explosion/explosion anim7.png").convert(), (16, 16))]
        self.invisible = pygame.image.load("Images/Sprites/Slime/Invisible.png")
        self.invisible.set_colorkey((141, 47, 173))
        # Initialise Player Entity
        self.white1 = []
        for row in range(4):
            self.white1.append([])
            for column in range(2):
                self.white1[row].append(self.slime_white.image_at(((column * 32),(row * 32), 32, 32), colorkey=(141, 47, 173)))
        self.white2 = []
        for row in range(4):
            self.white2.append([])
            for column in range(4):
                self.white2[row].append(self.slime_white2.image_at(((column * 32), (row * 32), 32, 32), colorkey=(141, 47, 173)))
        self.red1 = []
        for row in range(4):
            self.red1.append([])
            for column in range(2):
                self.red1[row].append(self.slime_red.image_at(((column * 32), (row * 32), 32, 32), colorkey=(141, 47, 173)))
        self.red2 = []
        for row in range(4):
            self.red2.append([])
            for column in range(4):
                self.red2[row].append(self.slime_red2.image_at(((column * 32), (row * 32), 32, 32), colorkey=(141, 47, 173)))
        self.green1 = []
        for row in range(4):
            self.green1.append([])
            for column in range(2):
                self.green1[row].append(self.slime_green.image_at(((column * 32), (row * 32), 32, 32), colorkey=(141, 47, 173)))
        self.green2 = []
        for row in range(4):
            self.green2.append([])
            for column in range(4):
                self.green2[row].append(self.slime_green2.image_at(((column * 32), (row * 32), 32, 32), colorkey=(141, 47, 173)))
        if color == "Red":
            if self.size == 2:
                self.surf = self.red2[0][0]
            else:
                self.surf = self.red1[0][0]
        elif color == "Green":
            if self.size == 2:
                self.surf = self.white2[0][0]
            else:
                self.surf = self.white1[0][0]
        elif color == "White":
            if self.size == 2:
                self.surf = self.white2[0][0]
            else:
                self.surf = self.white1[0][0]

        super(slime_boi, self).__init__(x, y, "none", health, attack, 1, sight, speed, enemy)
        self.last_tl = [self.rect.top // 32, self.rect.left // 32]
        self.last_row = 1
        self.step = 1
        self.reload = 1
        self.color = color
        self.trajectory = [0.4, 0.5]
        self.bar = health_bar(True, health, health)
        self.item = Items(0, 0, Image.slime[1], Image.slime[0], "Slime")

    # Same General Update Process as Wine with some minor tweeks
    def update(self):
        if self.health > 0:
            if all((((self.enemy.rect.centerx-screen.get_width()/2)<self.rect.left<(self.enemy.rect.centerx+screen.get_width()/2)), ((self.enemy.rect.centery-screen.get_height()/2)<self.rect.top<(self.enemy.rect.centery+screen.get_height()/2)))):
                down = False
                up = False
                right = False
                left = False

                # get x and y displacements from enemy to objects
                if self.enemy.form == "Solid":
                    playerVect = pygame.math.Vector2(self.enemy.rect.centerx - self.rect.centerx, self.enemy.rect.centery - self.rect.top)
                else:
                    playerVect = pygame.math.Vector2(10000, 10000)
                if playerVect.length() <= self.sight:
                    sight1 = True
                    sight2 = True
                    sight3 = True
                    sight4 = True
                    for wall in all_blocks:
                        wallVect = pygame.math.Vector2(wall.rect.centerx - self.rect.centerx, wall.rect.centery - self.rect.top)
                        if wallVect.length() <= self.sight:
                            if abs(wallVect.length()) <= abs(playerVect.length()):
                                if all(((wall.rect.centery < self.rect.top), (self.enemy.rect.centery < self.rect.top))):
                                    if (math.atan2(wallVect[0]-16, wallVect[1]+16) < math.atan2(self.enemy.rect.left - self.rect.centerx, self.enemy.rect.bottom - self.rect.top) < math.atan2(wallVect[0]+16, wallVect[1]+16)):
                                        sight1 = False
                                        sight3 = False
                                    if (math.atan2(wallVect[0]-16, wallVect[1]+16) < math.atan2(self.enemy.rect.right - self.rect.centerx, self.enemy.rect.bottom - self.rect.top) < math.atan2(wallVect[0]+16, wallVect[1]+16)):
                                        sight2 = False
                                        sight4 = False
                                elif all(((wall.rect.centery > self.rect.top), (self.enemy.rect.centery > self.rect.top))):
                                    if (math.atan2(wallVect[0] + 16, wallVect[1] - 16) < math.atan2(
                                            self.enemy.rect.left - self.rect.centerx, self.enemy.rect.top - self.rect.top) < math.atan2(wallVect[0] - 16,
                                                                                             wallVect[1] - 16)):
                                        sight1 = False
                                        sight3 = False
                                    if (math.atan2(wallVect[0] + 16, wallVect[1] + 16) < math.atan2(
                                            self.enemy.rect.right - self.rect.centerx, self.enemy.rect.top - self.rect.top) < math.atan2(wallVect[0] - 16,
                                                                                              wallVect[1] + 16)):
                                        sight2 = False
                                        sight4 = False
                                if all(((wall.rect.centerx < self.rect.centerx), (self.enemy.rect.centerx < self.rect.centerx))):
                                    if (math.atan2(wallVect[0] + 16, wallVect[1] - 16) < math.atan2(
                                            self.enemy.rect.right - self.rect.centerx, self.enemy.rect.top - self.rect.top) < math.atan2(wallVect[0] + 16,
                                                                                             wallVect[1] + 16)):
                                        sight2 = False
                                        sight3 = False
                                    if (math.atan2(wallVect[0] + 16, wallVect[1] - 16) < math.atan2(
                                            self.enemy.rect.right - self.rect.centerx, self.enemy.rect.bottom - self.rect.top) < math.atan2(wallVect[0] + 16,
                                                                                              wallVect[1] + 16)):
                                        sight1 = False
                                        sight4 = False
                                elif all(((wall.rect.centerx > self.rect.centerx), (self.enemy.rect.centerx > self.rect.centerx))):
                                    if (math.atan2(wallVect[0] + 16, wallVect[1] + 16) < math.atan2(
                                            self.enemy.rect.left - self.rect.centerx, self.enemy.rect.top - self.rect.top) < math.atan2(wallVect[0] + 16,
                                                                                             wallVect[1] - 16)):
                                        sight2 = False
                                        sight3 = False
                                    if (math.atan2(wallVect[0] + 16, wallVect[1] + 16) < math.atan2(
                                            self.enemy.rect.left - self.rect.centerx, self.enemy.rect.bottom - self.rect.top) < math.atan2(wallVect[0] + 16,
                                                                                              wallVect[1] - 16)):
                                        sight1 = False
                                        sight4 = False

                    if any((sight1, sight2, sight3, sight4)):
                        if playerVect[0] == 0:
                            playerVect[0] = 0.0000000001
                        if playerVect[1] == 0:
                            playerVect[1] = 0.0000000001
                        self.trajectory = playerVect.normalize()
                        if self.color == "Green":
                            if abs(playerVect.length()) < 45:
                                self.rect.move_ip(
                                    -round(self.trajectory[0] * self.speed + math.copysign(0.5, self.trajectory[0])),
                                    -round(self.trajectory[1] * self.speed + math.copysign(0.5, self.trajectory[1])))
                            elif abs(playerVect.length()) > 60:
                                self.rect.move_ip(
                                    round(self.trajectory[0] * self.speed + math.copysign(0.5, self.trajectory[0])),
                                    round(self.trajectory[1] * self.speed + math.copysign(0.5, self.trajectory[1])))
                        elif self.color == "Red":
                            self.burn()
                            self.rect.move_ip(
                                round(self.trajectory[0] * self.speed + math.copysign(0.5, self.trajectory[0])),
                                round(self.trajectory[1] * self.speed + math.copysign(0.5, self.trajectory[1])))
                        elif self.color == "White":
                            if abs(playerVect.length()) < 75:
                                self.state = 1
                                self.burn()
                                self.rect.move_ip(
                                    round(self.trajectory[0] * self.speed + math.copysign(0.5, self.trajectory[0])),
                                    round(self.trajectory[1] * self.speed + math.copysign(0.5, self.trajectory[1])))

                        if self.trajectory[0]*self.speed <= -0.5:
                            left = True
                        if self.trajectory[0]*self.speed >= 0.5:
                            right = True
                        if self.trajectory[1]*self.speed <= -0.5:
                            up = True
                        if self.trajectory[1]*self.speed >= 0.5:
                            down = True

                        cur_tl = [self.rect.top // 16, self.rect.left // 16]

                        if (Layers.map[(self.rect.top//32)][(self.rect.left//32)]) in Layers.walls:
                            if (Layers.map[(self.rect.top//32)][(self.rect.right//32)]) in Layers.walls:
                                if (Layers.map[(self.rect.bottom//32)][(self.rect.left//32)]) in Layers.walls:
                                    self.rect.move_ip(((self.last_tl[1] - cur_tl[1]) * self.speed), ((self.last_tl[0] - cur_tl[0]) * self.speed))
                                elif (Layers.map[(self.rect.bottom//32)][(self.rect.right//32)]) in Layers.walls:
                                    self.rect.move_ip((self.last_tl[1] - cur_tl[1])*self.speed, ((self.last_tl[0] - cur_tl[0])*self.speed))
                                else:
                                    self.rect.move_ip(0, ((self.last_tl[0] - cur_tl[0]) * self.speed))
                            elif (Layers.map[(self.rect.bottom//32)][(self.rect.left//32)]) in Layers.walls:
                                if (Layers.map[(self.rect.bottom//32)][(self.rect.right//32)]) in Layers.walls:
                                    self.rect.move_ip(((self.last_tl[1] - cur_tl[1]) * self.speed), ((self.last_tl[0] - cur_tl[0]) * self.speed))
                                else:
                                    self.rect.move_ip(((self.last_tl[1] - cur_tl[1]) * self.speed), 0)
                            else:
                                self.rect.move_ip((abs(self.last_tl[1] - cur_tl[1]) * self.speed)+1, (abs(self.last_tl[0] - cur_tl[0])*self.speed)+1)
                        elif (Layers.map[(self.rect.top//32)][(self.rect.right//32)]) in Layers.walls:
                            if (Layers.map[(self.rect.bottom//32)][(self.rect.left//32)]) in Layers.walls:
                                self.rect.move_ip(((self.last_tl[1] - cur_tl[1]) * self.speed), ((self.last_tl[0] - cur_tl[0])*self.speed))
                            elif (Layers.map[(self.rect.bottom//32)][(self.rect.right//32)]) in Layers.walls:
                                self.rect.move_ip((-abs(self.last_tl[1] - cur_tl[1]) * self.speed), 0)
                            else:
                                self.rect.move_ip((-abs(self.last_tl[1] - cur_tl[1]) * self.speed)-1, (abs(self.last_tl[0] - cur_tl[0]) * self.speed)+1)
                        elif (Layers.map[(self.rect.bottom//32)][(self.rect.right//32)]) in Layers.walls:
                            if (Layers.map[(self.rect.bottom//32)][(self.rect.left//32)]) in Layers.walls:
                                self.rect.move_ip(0, ((self.last_tl[0] - cur_tl[0]) * self.speed))
                            else:
                                self.rect.move_ip((-abs(self.last_tl[1] - cur_tl[1]) * self.speed)-1, (-abs(self.last_tl[0] - cur_tl[0])*self.speed)-1)
                        elif (Layers.map[(self.rect.bottom//32)][(self.rect.left//32)]) in Layers.walls:
                            self.rect.move_ip((abs(self.last_tl[1] - cur_tl[1]) * self.speed)+1, (-abs(self.last_tl[0] - cur_tl[0]) * self.speed)-1)

                        self.last_tl = [self.rect.top // 16, self.rect.left // 16]

                if all(((playerVect.length() >= 105), (self.color == "White"))):
                    self.state = 0

                if self.state == 0:
                    self.surf = self.invisible
                    self.step = 0

                else:
                    if down:
                        if left:
                            row = 3
                            self.step += 1
                        elif right:
                            row = 1
                            self.step += 1
                        else:
                            row = 0
                            self.step += 1
                    elif up:
                        if left:
                            row = 3
                            self.step += 1
                        elif right:
                            row = 1
                            self.step += 1
                        else:
                            row = 2
                            self.step += 1
                    elif left:
                        row = 3
                        self.step += 1
                    elif right:
                        row = 1
                        self.step += 1
                    else:
                        row = self.last_row
                        self.step += 1

                    self.last_row = row

                    if self.size == 2:
                        if self.color == "Red":
                            self.surf = self.red2[row][(self.step // round(7 / self.speed)) % 4]
                        if self.color == "Green":
                                self.surf = self.green2[row][(self.step // round(7 / self.speed)) % 4]
                                if self.reload > 80:
                                    self.throw_slime()
                                    self.reload = 0
                        if self.color == "White":
                            self.surf = self.white2[row][(self.step // round(7 / self.speed)) % 4]

                    else:
                        if self.color == "Red":
                            self.surf = self.red1[row][(self.step // round(7 / self.speed)) % 2]
                        if self.color == "Green":
                                self.surf = self.green1[row][(self.step // round(7 / self.speed)) % 2]
                                if self.reload > 80:
                                    self.throw_slime()
                                    self.reload = 0
                        if self.color == "White":
                            self.surf = self.white1[row][(self.step // round(7 / self.speed)) % 2]

                self.reload += 1

        else:
            if self.state != 5:
                self.state = 5
                self.step = 0
                self.surf = self.explosion[(self.step // round(3 / self.speed)) % 7]
                self.surf.set_colorkey((251, 8, 255))
                self.step += 1
                self.rect.move_ip(16, 16)
            else:
                self.surf = self.explosion[(self.step // round(3 / self.speed)) % 7]
                self.surf.set_colorkey((251, 8, 255))
                self.step += 1
                if (self.step // round(3 / self.speed)) >= 7:
                    self.die()

        if self.state != 0:
            self.bar = health_bar(True, self.max_health, self.health)
        else:
            self.bar = self.invisible

    # Slime attacks, throws a slime ball
    def throw_slime(self):
            new_ball = slime(self.rect.left + 4, self.rect.top + 4, self.trajectory, self.attack)

    # Slime attacks burns player
    def burn(self):
        if self.rect.colliderect(thred.rect):
            thred.health -= 0.05

    # Slime death process
    def die(self):
        global thred
        try:
            thred.thread += max(1, int(1 * getattr(thred, 'thread_mult', 1.0)))
        except Exception:
            pass
        self.item.spawn(self.rect.centerx, self.rect.centery)
        self.kill()

# Enemy attack slime sprites
class slime(EnemyAttacks):

    def __init__(self, x, y, direction, damage):
        super(slime, self).__init__(x, y, "Images/Sprites/Thred/SlimeBall.png", damage, 4, direction)
        self.trajectory = direction

    def update(self):
        self.frame += 1
        self.rect.move_ip(self.trajectory[0]*self.speed, self.trajectory[1]*self.speed)

        if self.frame == 27:
            self.kill()
        if (Layers.map[(self.rect.centery // 32)][(self.rect.centerx // 32)]) in Layers.walls:
            self.kill()
        for player in all_mains:
            if self.rect.colliderect(player.rect):
                self.hit(player)
                self.kill()
                break

# Enemy. type cat.
class cat_boi(Enemies):
    # Initialises instance of cat
    def __init__(self, x, y, health, attack, speed, sight, enemy):
        self.kitty = SpriteSheet('Images/Sprites/Cat.png')
        # Initialise Player Entity
        self.cat = []
        for row in range(4):
            self.cat.append([])
            for column in range(4):
                self.cat[row].append(
                    self.kitty.image_at(((column * 32), (row * 32), 32, 32), colorkey=(141, 47, 173)))
        self.surf = self.cat[0][0]
        super(cat_boi, self).__init__(x, y, "none", health, attack, 1, sight, speed, enemy)
        self.last_tl = [self.rect.top // 32, self.rect.left // 32]
        self.last_row = 1
        self.step = 1
        self.reload = 1
        self.last_erow = 0
        self.trajectory = [0.4, 0.5]
        self.bar = health_bar(True, health, health)
        self.item = Items(0, 0, Image.claw[1], Image.claw[0], "Cat_Claw")

    # Same General Update Process as Wine and slime with some minor tweeks
    def update(self):
        if self.health > 0:
            if all((((self.enemy.rect.centerx-screen.get_width()/2)<self.rect.left<(self.enemy.rect.centerx+screen.get_width()/2)), ((self.enemy.rect.centery-screen.get_height()/2)<self.rect.top<(self.enemy.rect.centery+screen.get_height()/2)))):
                down = False
                up = False
                right = False
                left = False

                # get x and y displacements from enemy to objects
                if self.enemy.form == "Solid":
                    playerVect = pygame.math.Vector2(self.enemy.rect.centerx - self.rect.centerx, self.enemy.rect.centery - self.rect.top)
                else:
                    playerVect = pygame.math.Vector2(10000, 10000)
                if playerVect.length() <= self.sight:
                    sight1 = True
                    sight2 = True
                    sight3 = True
                    sight4 = True
                    for wall in all_blocks:
                        wallVect = pygame.math.Vector2(wall.rect.centerx - self.rect.centerx, wall.rect.centery - self.rect.top)
                        if wallVect.length() <= self.sight:
                            if abs(wallVect.length()) <= abs(playerVect.length()):
                                if all(((wall.rect.centery < self.rect.top), (self.enemy.rect.centery < self.rect.top))):
                                    if (math.atan2(wallVect[0]-16, wallVect[1]+16) < math.atan2(self.enemy.rect.left - self.rect.centerx, self.enemy.rect.bottom - self.rect.top) < math.atan2(wallVect[0]+16, wallVect[1]+16)):
                                        sight1 = False
                                        sight3 = False
                                    if (math.atan2(wallVect[0]-16, wallVect[1]+16) < math.atan2(self.enemy.rect.right - self.rect.centerx, self.enemy.rect.bottom - self.rect.top) < math.atan2(wallVect[0]+16, wallVect[1]+16)):
                                        sight2 = False
                                        sight4 = False
                                elif all(((wall.rect.centery > self.rect.top), (self.enemy.rect.centery > self.rect.top))):
                                    if (math.atan2(wallVect[0] + 16, wallVect[1] - 16) < math.atan2(
                                            self.enemy.rect.left - self.rect.centerx, self.enemy.rect.top - self.rect.top) < math.atan2(wallVect[0] - 16,
                                                                                             wallVect[1] - 16)):
                                        sight1 = False
                                        sight3 = False
                                    if (math.atan2(wallVect[0] + 16, wallVect[1] + 16) < math.atan2(
                                            self.enemy.rect.right - self.rect.centerx, self.enemy.rect.top - self.rect.top) < math.atan2(wallVect[0] - 16,
                                                                                              wallVect[1] + 16)):
                                        sight2 = False
                                        sight4 = False
                                if all(((wall.rect.centerx < self.rect.centerx), (self.enemy.rect.centerx < self.rect.centerx))):
                                    if (math.atan2(wallVect[0] + 16, wallVect[1] - 16) < math.atan2(
                                            self.enemy.rect.right - self.rect.centerx, self.enemy.rect.top - self.rect.top) < math.atan2(wallVect[0] + 16,
                                                                                             wallVect[1] + 16)):
                                        sight2 = False
                                        sight3 = False
                                    if (math.atan2(wallVect[0] + 16, wallVect[1] - 16) < math.atan2(
                                            self.enemy.rect.right - self.rect.centerx, self.enemy.rect.bottom - self.rect.top) < math.atan2(wallVect[0] + 16,
                                                                                              wallVect[1] + 16)):
                                        sight1 = False
                                        sight4 = False
                                elif all(((wall.rect.centerx > self.rect.centerx), (self.enemy.rect.centerx > self.rect.centerx))):
                                    if (math.atan2(wallVect[0] + 16, wallVect[1] + 16) < math.atan2(
                                            self.enemy.rect.left - self.rect.centerx, self.enemy.rect.top - self.rect.top) < math.atan2(wallVect[0] + 16,
                                                                                             wallVect[1] - 16)):
                                        sight2 = False
                                        sight3 = False
                                    if (math.atan2(wallVect[0] + 16, wallVect[1] + 16) < math.atan2(
                                            self.enemy.rect.left - self.rect.centerx, self.enemy.rect.bottom - self.rect.top) < math.atan2(wallVect[0] + 16,
                                                                                              wallVect[1] - 16)):
                                        sight1 = False
                                        sight4 = False

                    if any((sight1, sight2, sight3, sight4)):
                        if playerVect[0] == 0:
                            playerVect[0] = 0.0000000001
                        if playerVect[1] == 0:
                            playerVect[1] = 0.0000000001
                        self.trajectory = playerVect.normalize()
                        if abs(playerVect.length()) < 32:
                            self.rect.move_ip(
                                -round(self.trajectory[0] * self.speed + math.copysign(0.5, self.trajectory[0])),
                                -round(self.trajectory[1] * self.speed + math.copysign(0.5, self.trajectory[1])))
                        elif abs(playerVect.length()) >= 32:
                            self.rect.move_ip(
                                round(self.trajectory[0] * self.speed + math.copysign(0.5, self.trajectory[0])),
                                round(self.trajectory[1] * self.speed + math.copysign(0.5, self.trajectory[1])))

                        if self.trajectory[0]*self.speed <= -0.5:
                            left = True
                        if self.trajectory[0]*self.speed >= 0.5:
                            right = True
                        if self.trajectory[1]*self.speed <= -0.5:
                            up = True
                        if self.trajectory[1]*self.speed >= 0.5:
                            down = True

                        cur_tl = [self.rect.top // 16, self.rect.left // 16]

                        if (Layers.map[(self.rect.top//32)][(self.rect.left//32)]) in Layers.walls:
                            if (Layers.map[(self.rect.top//32)][(self.rect.right//32)]) in Layers.walls:
                                if (Layers.map[(self.rect.bottom//32)][(self.rect.left//32)]) in Layers.walls:
                                    self.rect.move_ip(((self.last_tl[1] - cur_tl[1]) * self.speed), ((self.last_tl[0] - cur_tl[0]) * self.speed))
                                elif (Layers.map[(self.rect.bottom//32)][(self.rect.right//32)]) in Layers.walls:
                                    self.rect.move_ip((self.last_tl[1] - cur_tl[1])*self.speed, ((self.last_tl[0] - cur_tl[0])*self.speed))
                                else:
                                    self.rect.move_ip(0, ((self.last_tl[0] - cur_tl[0]) * self.speed))
                            elif (Layers.map[(self.rect.bottom//32)][(self.rect.left//32)]) in Layers.walls:
                                if (Layers.map[(self.rect.bottom//32)][(self.rect.right//32)]) in Layers.walls:
                                    self.rect.move_ip(((self.last_tl[1] - cur_tl[1]) * self.speed), ((self.last_tl[0] - cur_tl[0]) * self.speed))
                                else:
                                    self.rect.move_ip(((self.last_tl[1] - cur_tl[1]) * self.speed), 0)
                            else:
                                self.rect.move_ip((abs(self.last_tl[1] - cur_tl[1]) * self.speed)+1, (abs(self.last_tl[0] - cur_tl[0])*self.speed)+1)
                        elif (Layers.map[(self.rect.top//32)][(self.rect.right//32)]) in Layers.walls:
                            if (Layers.map[(self.rect.bottom//32)][(self.rect.left//32)]) in Layers.walls:
                                self.rect.move_ip(((self.last_tl[1] - cur_tl[1]) * self.speed), ((self.last_tl[0] - cur_tl[0])*self.speed))
                            elif (Layers.map[(self.rect.bottom//32)][(self.rect.right//32)]) in Layers.walls:
                                self.rect.move_ip((-abs(self.last_tl[1] - cur_tl[1]) * self.speed), 0)
                            else:
                                self.rect.move_ip((-abs(self.last_tl[1] - cur_tl[1]) * self.speed)-1, (abs(self.last_tl[0] - cur_tl[0]) * self.speed)+1)
                        elif (Layers.map[(self.rect.bottom//32)][(self.rect.right//32)]) in Layers.walls:
                            if (Layers.map[(self.rect.bottom//32)][(self.rect.left//32)]) in Layers.walls:
                                self.rect.move_ip(0, ((self.last_tl[0] - cur_tl[0]) * self.speed))
                            else:
                                self.rect.move_ip((-abs(self.last_tl[1] - cur_tl[1]) * self.speed)-1, (-abs(self.last_tl[0] - cur_tl[0])*self.speed)-1)
                        elif (Layers.map[(self.rect.bottom//32)][(self.rect.left//32)]) in Layers.walls:
                            self.rect.move_ip((abs(self.last_tl[1] - cur_tl[1]) * self.speed)+1, (-abs(self.last_tl[0] - cur_tl[0]) * self.speed)-1)

                        self.last_tl = [self.rect.top // 16, self.rect.left // 16]

                        if down:
                            if left:
                                row = 1
                                erow = 7
                                self.step += 1
                            elif right:
                                row = 2
                                erow = 1
                                self.step += 1
                            else:
                                row = 0
                                erow = 0
                                self.step += 1
                        elif up:
                            if left:
                                row = 1
                                erow = 0
                                self.step += 1
                            elif right:
                                row = 2
                                erow = 3
                                self.step += 1
                            else:
                                row = 3
                                erow = 4
                                self.step += 1
                        elif left:
                            row = 1
                            erow = 6
                            self.step += 1
                        elif right:
                            row = 2
                            erow = 2
                            self.step += 1
                        else:
                            row = self.last_row
                            erow = self.last_erow
                            self.step += 1

                        self.last_row = row
                        if abs(playerVect.length()) < 30:
                            if self.reload > 15:
                                self.strike(erow)
                                self.reload = 0
                        self.surf = self.cat[row][(self.step // round(7 / self.speed)) % 4]
                else:
                    self.surf = self.cat[self.last_row][1]
                    self.patrol_wander()
                self.reload += 1
            self.bar = health_bar(True, self.max_health, self.health)
        else:
            self.die()

    # Cat claw attack
    def strike(self, row):
        if row == 0:
            new_ball = cat_claw(self.rect.left, self.rect.bottom - 12, "Down", self.attack)
        if row == 1:
            new_ball = cat_claw(self.rect.right - 9, self.rect.bottom - 5, "Down Right", self.attack)
        if row == 2:
            new_ball = cat_claw(self.rect.right - 10, self.rect.top + 8, "Right", self.attack)
        if row == 3:
            new_ball = cat_claw(self.rect.right - 3, self.rect.top - 4, "Up Right", self.attack)
        if row == 4:
            new_ball = cat_claw(self.rect.left, self.rect.top - 10, "Up ", self.attack)
        if row == 5:
            new_ball = cat_claw(self.rect.left - 12, self.rect.top - 8, "Up Left", self.attack)
        if row == 6:
            new_ball = cat_claw(self.rect.left - 10, self.rect.top + 8, "Left", self.attack)
        if row == 7:
            new_ball = cat_claw(self.rect.left - 7, self.rect.bottom - 3, "Down Left", self.attack)

    # Cat death process
    def die(self):
        global thred
        try:
            thred.thread += max(1, int(2 * getattr(thred, 'thread_mult', 1.0)))
        except Exception:
            pass
        self.item.spawn(self.rect.centerx, self.rect.centery)
        self.kill()

# Enemy attack claw sprite
class cat_claw(EnemyAttacks):
    claw0 = pygame.image.load("Images/Sprites/Thred/Claw0.png").convert()
    transcolour = claw0.get_at((0, 0))
    claw0.set_colorkey(transcolour)
    claw1 = pygame.image.load("Images/Sprites/Thred/Claw1.png").convert()
    transcolour = claw1.get_at((0, 0))
    claw1.set_colorkey(transcolour)
    claw2 = pygame.image.load("Images/Sprites/Thred/Claw2.png").convert()
    transcolour = claw2.get_at((0, 0))
    claw2.set_colorkey(transcolour)
    claw3 = pygame.image.load("Images/Sprites/Thred/Claw3.png").convert()
    transcolour = claw3.get_at((0, 0))
    claw3.set_colorkey(transcolour)
    claw4 = pygame.image.load("Images/Sprites/Thred/Claw4.png").convert()
    transcolour = claw4.get_at((0, 0))
    claw4.set_colorkey(transcolour)
    claw5 = pygame.image.load("Images/Sprites/Thred/Claw5.png").convert()
    transcolour = claw5.get_at((0, 0))
    claw5.set_colorkey(transcolour)
    claw6 = pygame.image.load("Images/Sprites/Thred/Claw6.png").convert()
    transcolour = claw6.get_at((0, 0))
    claw6.set_colorkey(transcolour)
    claw7 = pygame.image.load("Images/Sprites/Thred/Claw7.png").convert()
    transcolour = claw7.get_at((0, 0))
    claw7.set_colorkey(transcolour)
    clawU = [claw2, claw3, claw0]
    clawD = [claw0, claw1, claw2]
    clawR = [claw4, claw5, claw7]
    clawL = [claw3, claw0, claw1]
    clawUL = [claw2, claw3, claw0]
    clawUR = [claw6, claw4, claw5]
    clawDL = [claw3, claw0, claw1]
    clawDR = [claw4, claw5, claw7]

    def __init__(self, x, y, direction, damage):
        self.direction = direction
        if "Up" in self.direction:
            if "Left" in self.direction:
                self.file = self.clawUL
            elif "Right" in self.direction:
                self.file = self.clawUR
            else:
                self.file = self.clawU
        elif "Down" in self.direction:
            if "Left" in self.direction:
                self.file = self.clawDL
            elif "Right" in self.direction:
                self.file = self.clawDR
            else:
                self.file = self.clawD
        elif "Left" in self.direction:
            self.file = self.clawL
        elif "Right" in self.direction:
            self.file = self.clawR
        self.surf = self.file[0]
        super(cat_claw, self).__init__(x, y, "none", damage, 2, direction)

    def update(self):
        if 1 <= self.frame < 3:
            self.surf = self.file[1]
        if 3 <= self.frame < 4:
            self.surf = self.file[2]
        self.frame += 1
        if self.frame == 4:
            self.kill()
        for enemy in all_mains:
            if self.rect.colliderect(enemy.rect):
                self.hit(enemy)
                self.kill()
                break


# Creating Sprite Groups to store sprites and order blits
all_backgrounds = pygame.sprite.Group()
all_cursors = pygame.sprite.Group()
all_mains = pygame.sprite.Group()
all_enemies = pygame.sprite.Group()
all_items = pygame.sprite.Group()
all_attacksa = pygame.sprite.Group()
all_attacksb = pygame.sprite.Group()
all_visuals = pygame.sprite.Group()
all_buttons = pygame.sprite.Group()
all_text = pygame.sprite.Group()
all_lights = pygame.sprite.Group()
all_blocks = pygame.sprite.Group()
all_temps = pygame.sprite.Group()
all_tempsback = pygame.sprite.Group()
all_numbers = pygame.sprite.Group()


# Empties Sprite Groups
def empty_all():
    global thred
    thred.kill()
    del(thred)
    all_backgrounds.empty()
    all_buttons.empty()
    all_items.empty()
    all_enemies.empty()
    all_visuals.empty()
    all_cursors.empty()
    all_attacksa.empty()
    all_attacksb.empty()
    all_mains.empty()
    all_text.empty()
    all_lights.empty()
    all_blocks.empty()


    # Restart is handled externally (see player_dead flag / load_level())
    pass

# "Main Code"
if __name__ == "__main__":

    # Creates a Function to Save Player Progress

    # Saves Players Current Progress (All enemy and player states and map state)
    def save_game():
        global thred
        global saved_loaded
        saved_loaded = True
        # File I/O is unavailable in WebAssembly — wrap everything in try/except
        try:
            Layout = open("Saves/Saved_Area.py", "w")
            Collection = open("Saves/Saved_Items.py", "w")
            Stats = open("Saves/Saved_Status.py", "w")
            saved_emap = [[0 for i in range(len(Layers.map[1]))] for j in range(len(Layers.map))]
            saved_imap = [[0 for i in range(len(Layers.map[1]))] for j in range(len(Layers.map))]

            for enemy in all_enemies:
                if enemy.item.type == "Wine":
                    saved_emap[enemy.rect.centery // 32][enemy.rect.centerx // 32] = (
                        "W", enemy.max_health, enemy.health, enemy.attack, enemy.speed, enemy.sight)
                elif enemy.item.type == "Cat_Claw":
                    saved_emap[enemy.rect.centery // 32][enemy.rect.centerx // 32] = (
                        "C", enemy.max_health, enemy.health, enemy.attack, enemy.speed, enemy.sight)
                elif enemy.item.type == "Slime":
                    saved_emap[enemy.rect.centery // 32][enemy.rect.centerx // 32] = (
                        "S", enemy.max_health, enemy.health, enemy.attack, enemy.speed, enemy.sight, enemy.color, enemy.size)
            for item in all_items:
                if item.type == "Wine":
                    saved_imap[item.rect.centery // 32][item.rect.centerx // 32] += 10
                if item.type == "Cat_Claw":
                    saved_imap[item.rect.centery // 32][item.rect.centerx // 32] += 1000
                if item.type == "Slime":
                    saved_imap[item.rect.centery // 32][item.rect.centerx // 32] += 100000
            Layout.write("Loaded = True" + "\n" + "e_map = " + str(saved_emap) + "\n" + "i_map = " + str(
                saved_imap) + "\n" + "w_map = " + str(Layers.map))

            global e_map
            global i_map
            global w_map
            e_map = saved_emap
            i_map = saved_imap
            w_map = Layers.map

            Layout.close()

            items = []
            for item in thred.inv:
                items.append(item)
            Collection.write("item_list = " + str(items))
            Collection.close()

            global item_list
            item_list = items

            player_pos = (thred.rect.centerx // 32, thred.rect.centery // 32)
            Stats.write("Energy = " + str(thred.energy) + "\n" +
                        "Max_Energy = " + str(thred.max_energy) + "\n" +
                        "Health = " + str(thred.health) + "\n" +
                        "Max_Health = " + str(thred.max_health) + "\n" +
                        "Attack = " + str(thred.attack) + "\n" +
                        "Armor = " + "'" + thred.armor + "'" + "\n" +
                        "Weapon = " + "'" + thred.hand + "'" + "\n" +
                        "Speed = " + str(thred.speed) + "\n" +
                        "Sight = " + str(thred.sight) + "\n" +
                        "Position = " + str(player_pos) + "\n")
            Stats.close()

            global Energy
            global Max_Energy
            global Health
            global Max_Health
            global Armor
            global Attack
            global Weapon
            global Speed
            global Sight
            global Position
            Energy = thred.energy
            Max_Energy = thred.max_energy
            Health = thred.health
            Max_Health = thred.max_health
            Attack = thred.attack
            Armor = thred.armor
            Weapon = thred.hand
            Speed = thred.speed
            Sight = thred.sight
            Position = player_pos
        except Exception:
            pass  # File writes not available in WebAssembly — silently skip

    # Loads save file (Last point saved)
    def load_save():
        global thred
        global e_map
        global i_map
        global w_map
        global Energy
        global Max_Energy
        global Health
        global Max_Health
        global Armor
        global Attack
        global Weapon
        global Speed
        global Sight
        global Position
        global item_list
        thred = Player(0, 0, "A_0", 1, 1, 1, 1, 1, 1)
        inv_button = Buttons(390, -5, Image.backpack[0], Image.backpack[1])
        thred.inv_button = inv_button
        all_buttons.add(thred.inv_button)
        all_mains.add(thred)
        global saved_loaded
        saved_loaded = True

        for row in range(len(w_map)):
            for column in range(len(w_map[row])):
                tile = w_map[row][column]
                Layers.map[row][column] = tile
                if tile == 0:
                    pass

                elif any(((tile == 1), (tile == 2),
                          (tile == 3), (tile == 4))):
                    add_torch(column * 32, row * 32, (tile - 1))

                elif tile == 5:
                    add_solid_block(column * 32, row * 32)

                elif tile == 6:
                    add_string_block(column * 32, row * 32)

        for row in range(len(e_map)):
            for column in range(len(e_map[row])):
                tile = e_map[row][column]
                if type(tile) != int:
                    if tile[0] == "W":
                        new_enemy = wine_boi(column * 32, row * 32, tile[1], tile[3], tile[4], tile[5],
                                                     thred)
                        new_enemy.health = tile[2]
                        all_enemies.add(new_enemy)
                    elif tile[0] == "C":
                        new_enemy = cat_boi(column * 32, row * 32, tile[1], tile[3], tile[4], tile[5],
                                                    thred)
                        new_enemy.health = tile[2]
                        all_enemies.add(new_enemy)
                    elif tile[0] == "S":
                        new_enemy = slime_boi(column * 32, row * 32, tile[1], tile[3], tile[4], tile[5],
                                                      thred, tile[6], tile[7])
                        new_enemy.health = tile[2]
                        all_enemies.add(new_enemy)
        for row in range(len(i_map)):
            for column in range(len(i_map[row])):
                tile = i_map[row][column]
                for times in range(tile // 100000):
                    new_item = Items(column * 32, row * 32, Image.winedrop[0], Image.winedrop[1],
                                     "Wine")
                    all_items.add(new_item)
                for times in range((tile % 100000) // 1000):
                    new_item = Items(column * 32, row * 32, Image.claw[0], Image.claw[1], "Cat_Claw")
                    all_items.add(new_item)
                for times in range((tile % 1000) // 10):
                    new_item = Items(column * 32, row * 32, Image.slime[0], Image.slime[1], "Slime")
                    all_items.add(new_item)
        thred.rect.centerx = Position[0]*32
        thred.rect.centery = Position[1]*32
        thred.max_health = Max_Health
        thred.max_energy = Max_Energy
        thred.energy = Energy
        thred.health = Health
        thred.sight = Sight
        thred.speed = Speed
        thred.armor = Armor
        thred.hand = Weapon
        thred.attack = Attack
        thred.inv = item_list

    # Creates a new save file, overwriting old save file if one was present
    def new_file():
        global thred, current_level
        thred = Player(80, 80, "A_0", 5, 15, 2, 1, 2.1, 1.3)
        inv_button = Buttons(390, -5, Image.backpack[0], Image.backpack[1])
        thred.inv_button = inv_button
        all_buttons.add(thred.inv_button)
        all_mains.add(thred)

        try:
            if current_level == 2:
                import map_level2
                map_grid = map_level2.map
            elif current_level == 3:
                import map_level3
                map_grid = map_level3.map
            else:
                import map_level1
                map_grid = map_level1.map
        except Exception:
            from map import map as map_grid  # fallback to original map
        for row in range(len(map_grid)):
            for column in range(len(map_grid[row])):
                tile = map_grid[row][column]
                if any(((type(tile) == int), (type(tile) == float))):
                    if tile < 10:
                        Layers.map[row][column] = tile
                        if tile == 0:
                            pass

                        elif any(((tile == 1), (tile == 2),
                                  (tile == 3), (tile == 4))):
                            add_torch(column * 32, row * 32, (tile - 1))

                        elif tile == 5:
                            add_solid_block(column * 32, row * 32)

                        elif tile == 6:
                            add_string_block(column * 32, row * 32)

        for row in range(len(map_grid)):
            for column in range(len(map_grid[row])):
                tile = map_grid[row][column]
                if type(tile) == tuple:
                    if tile[0] == "W":
                        new_enemy1 = wine_boi(column * 32, row * 32, tile[1], tile[2], tile[3], tile[4], thred)
                        all_enemies.add(new_enemy1)
                    elif tile[0] == "C":
                        new_enemy2 = cat_boi(column * 32, row * 32, tile[1], tile[2], tile[3], tile[4], thred)
                        all_enemies.add(new_enemy2)
                    elif tile[0] == "S":
                        new_enemy3 = slime_boi(column * 32, row * 32, tile[1], tile[2], tile[3], tile[4], thred,
                                                      tile[5], tile[6])
                        all_enemies.add(new_enemy3)
                elif type(tile) == str:
                    if tile == "spawn":
                        thred.rect.centerx = column * 32
                        thred.rect.centery = row * 32

        # Track initial enemy count for level-complete detection
        global initial_enemy_count
        initial_enemy_count = len(all_enemies)

    # Creates Clock for game speed
    clock = pygame.time.Clock()

    # Creates the first screen layout
    def loadscreen():
        global Room
        global screen
        title = Background(90, 10, Image.title)
        all_tempsback.add(title)
        loads_button = Buttons(320, 130, Image.load_save[0], Image.load_save[1])
        all_temps.add(loads_button)
        news_button = Buttons(90, 130, Image.new_save[0], Image.new_save[1])
        all_temps.add(news_button)
        overwrite_button = Buttons(90, 70, Image.overwrite_save[0], Image.overwrite_save[1])
        exit_button = Buttons(205, 170, Image.exit[0], Image.exit[1])
        all_temps.add(exit_button)
        # Creates the Rooms Frame Loop
        while Room == -1:
            for event in pygame.event.get():

                # Checks for KEYDOWN event
                if event.type == KEYDOWN:

                    # If the Esc key is pressed, then exits the loop
                    if event.key == K_ESCAPE:
                        Room = 0
                        break

                elif event.type == QUIT:
                    # Check for QUIT event. If QUIT, stops then program
                    Room = 0
                    break

                # Checks if Mouse is Clicked
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if news_button.file == 2:
                        if Loaded:
                            all_temps.remove(news_button)
                            all_temps.add(overwrite_button)
                        else:
                            all_temps.empty()
                            Room = 1
                            new_file()
                            break

                    if loads_button.file == 2:
                        all_temps.empty()
                        Room = 1
                        if Loaded:
                            load_save()
                        else:
                            new_file()
                        break

                    if overwrite_button.file == 2:
                        new_file()
                        all_temps.empty()
                        Room = 1
                        break

                    if exit_button.file == 2:
                        all_temps.empty()
                        Room = 0
                        break

                elif event.type == pygame.VIDEORESIZE:
                    # Resizes Screen If User Tries To Change Screen Size
                    screen = pygame.display.set_mode((event.w, event.h), RESIZABLE)

            # Clears The Screen
            screen.fill((0, 0, 0))

            # Adds Sprites To Screen
            update_screen_game(False, True)

            # Updates Screen
            pygame.display.update()

            # Sets Frame Rate
            clock.tick(60)


    # Creates the tutorial screen layout
    def tutorial():
        global Room
        global screen
        tutorial_back = Background(0, 0, Image.tutorial)
        tutorial_back.surf = pygame.transform.scale(tutorial_back.surf, (round(SCREEN_WIDTH / Layers.zoom), round(SCREEN_HEIGHT / Layers.zoom)))
        all_tempsback.add(tutorial_back)
        start_button = Buttons(210, 185, Image.start[0], Image.start[1])
        start_button.frame_1 = pygame.transform.scale(start_button.frame_1, (70, 50))
        start_button.frame_2 = pygame.transform.scale(start_button.frame_2, (70, 50))
        all_temps.add(start_button)
        change = False
        # Creates the Rooms Frame Loop
        while Room == 1:
            for event in pygame.event.get():

                # Checks for KEYDOWN event
                if event.type == KEYDOWN:

                    # If the Esc key is pressed, then exits the loop
                    if event.key == K_ESCAPE:
                        all_temps.empty()
                        all_tempsback.empty()
                        Room = -1
                        break

                elif event.type == QUIT:
                    # Check for QUIT event. If QUIT, stops then program
                    Room = 0
                    break

                # Checks if Mouse is Clicked
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button.file == 2:
                        all_temps.empty()
                        all_tempsback.empty()
                        Room = 2
                        break

                elif event.type == pygame.VIDEORESIZE:
                    # Resizes Screen If User Tries To Change Screen Size
                    screen = pygame.display.set_mode((event.w, event.h), RESIZABLE)

            # Clears The Screen
            screen.fill((0, 0, 0))

            # Adds Sprites To Screen
            update_screen_game(False, True)

            # Updates Screen
            pygame.display.update()

            # Sets Frame Rate
            clock.tick(60)


    # Creates the game layout and update processes
    def game():
        global Room
        global screen
        global thred
        global player_dead
        global initial_enemy_count
        global current_level

        enemies_started = initial_enemy_count > 0

        # Creates the Rooms Frame Loop
        while Room == 2:
            for event in pygame.event.get():
                # Checks for KEYDOWN event
                if event.type == KEYDOWN:

                    # If the Esc key is pressed, then exits the loop
                    if event.key == K_ESCAPE:
                        pause()

                elif event.type == QUIT:
                    # Check for QUIT event. If QUIT, stops then program
                    Room = 0
                    break

                elif event.type == MOUSEBUTTONDOWN:

                    if event.button == 1:
                        if thred.inv_button.file == 2:
                            inventory()
                        else:
                            if ((thred.hand == "none") and (thred.reload >= 2) and (thred.state != 1)):
                                thred.state = 5
                                thred.step = 0
                            if ((thred.hand == "Ball") and (thred.reload >= 15) and (thred.state != 1)):
                                thred.state = 2
                                thred.step = 0
                            if ((thred.hand == "Straw") and (thred.reload >= 5) and (thred.state != 1)):
                                thred.state = 3
                                thred.step = 0
                            if ((thred.hand == "Claw") and (thred.reload >= 15) and (thred.state != 1)):
                                thred.state = 4
                                thred.step = 0

            pressed_keys = pygame.key.get_pressed()
            thred.control(pressed_keys)

            # Check player death
            if player_dead:
                player_dead = False
                game_over_screen()
                break

            # Check level complete (all enemies cleared)
            if enemies_started and len(all_enemies) == 0:
                level_complete_screen()
                enemies_started = False
                break

            # Clears The Screen
            screen.fill((0, 0, 0))

            # Adds Sprites To Screen
            update_screen_game(True, False)

            # Updates Screen
            pygame.display.update()

            # Sets Frame Rate
            clock.tick(20)


    # Creates the pause screen layout
    def pause():
        global Last_Room
        global Room
        global screen
        resume_button = Buttons(70, 130, Image.resume[0], Image.resume[1])
        exit_button = Buttons(340, 130, Image.exit[0], Image.exit[1])
        save_button = Buttons(205, 130, Image.save[0], Image.save[1])
        all_temps.add(resume_button)
        all_temps.add(exit_button)
        all_temps.add(save_button)
        # Creates the Rooms Frame Loop
        while True:
            for event in pygame.event.get():

                # Checks for KEYDOWN event
                if event.type == KEYDOWN:

                    # If the Esc key is pressed, then exits the loop
                    if event.key == K_ESCAPE:
                        all_temps.empty()
                        return

                elif event.type == QUIT:
                    # Check for QUIT event. If QUIT, stops then program
                    Room = 0
                    all_temps.empty()
                    return

                elif event.type == MOUSEBUTTONDOWN:
                    if resume_button.file == 2:
                        all_temps.empty()
                        return

                    if exit_button.file == 2:
                        Room = -1
                        all_temps.empty()
                        return

                    if save_button.file == 2:
                        save_game()

            # Clears The Screen
            screen.fill((0, 0, 0))

            update_screen_game(False, False)
            # Updates Screen
            pygame.display.update()

            # Sets Frame Rate
            clock.tick(60)


    # Creates the inventory layout
    def inventory():
        global Room
        global screen
        inv_back = Background(0, 0, Image.inventory)
        inv_back.surf = pygame.transform.scale(inv_back.surf, (round(SCREEN_WIDTH / Layers.zoom), round(SCREEN_HEIGHT / Layers.zoom)))
        all_tempsback.add(inv_back)
        resume_button = Buttons(70, 190, Image.resume[0], Image.resume[1])
        all_temps.add(resume_button)
        slime = Buttons(365, 153, Image.slime[1], Image.slime[2])
        all_temps.add(slime)
        wine = Buttons(407, 153, Image.winedrop[1], Image.winedrop[2])
        all_temps.add(wine)
        claw = Buttons(365, 195, Image.claw[1], Image.claw[2])
        all_temps.add(claw)
        Straw = Buttons(22, 130, Image.straw, Image.lock)
        Straw.frame_1 = pygame.transform.scale(Straw.frame_1, (40, 40))
        Straw.frame_2 = pygame.transform.scale(Straw.frame_2, (40, 40))
        all_temps.add(Straw)
        Ball = Buttons(171, 66, Image.ball, Image.lock)
        Ball.frame_1 = pygame.transform.scale(Ball.frame_1, (40, 40))
        Ball.frame_2 = pygame.transform.scale(Ball.frame_2, (40, 40))
        all_temps.add(Ball)
        Sword = Buttons(22, 66, Image.sword, Image.lock)
        Sword.frame_1 = pygame.transform.scale(Sword.frame_1, (40, 40))
        Sword.frame_2 = pygame.transform.scale(Sword.frame_2, (40, 40))
        all_temps.add(Sword)
        Green = Buttons(342, 66, Image.green, Image.lock)
        Green.frame_1 = pygame.transform.scale(Green.frame_1, (40, 40))
        Green.frame_2 = pygame.transform.scale(Green.frame_2, (40, 40))
        all_temps.add(Green)
        Red = Buttons(171, 130, Image.red, Image.lock)
        Red.frame_1 = pygame.transform.scale(Red.frame_1, (40, 40))
        Red.frame_2 = pygame.transform.scale(Red.frame_2, (40, 40))
        all_temps.add(Red)
        items = thred.sort_inv()
        ball = False
        red = False
        sword = False
        green = False
        straw = False
        if items[0] > 0:
            ball = True
            Ball.frame_2 = Ball.frame_1
        if items[4] > 0:
            red = True
            Red.frame_2 = Red.frame_1
        if items[3] > 0:
            green = True
            Green.frame_2 = Green.frame_1
        if items[7]+items[2] > 0:
            sword = True
            Sword.frame_2 = Sword.frame_1
        if items[6] > 0:
            straw = True
            Straw.frame_2 = Straw.frame_1
        s = items[5]
        w = items[8]
        c = items[1]
        slimes = Values(s, 385, 183)
        wines = Values(w, 427, 183)
        claws = Values(c, 385, 225)
        thred.inv = []
        # Creates the Rooms Frame Loop
        while True:
            all_numbers.empty()
            slime_number = Numbers(slimes.number, slimes.X_Value, slimes.Y_Value)
            wine_number = Numbers(wines.number, wines.X_Value, wines.Y_Value)
            claw_number = Numbers(claws.number, claws.X_Value, claws.Y_Value)
            all_numbers.add(claw_number)
            all_numbers.add(wine_number)
            all_numbers.add(slime_number)

            for event in pygame.event.get():

                # Checks for KEYDOWN event
                if event.type == KEYDOWN:

                    # If the Esc key is pressed, then exits the loop
                    if event.key == K_ESCAPE:
                        items[1] = claws.number
                        items[5] = slimes.number
                        items[8] = wines.number
                        del(wines)
                        del(slimes)
                        del(claws)
                        for x in range(items[0]):
                            thred.inv.append("Ball")
                        for x in range(items[1]):
                            thred.inv.append("Cat_Claw")
                        for x in range(items[2]):
                            thred.inv.append("Claw")
                        for x in range(items[3]):
                            thred.inv.append("Green")
                        for x in range(items[4]):
                            thred.inv.append("Red")
                        for x in range(items[5]):
                            thred.inv.append("Slime")
                        for x in range(items[6]):
                            thred.inv.append("Straw")
                        for x in range(items[7]):
                            thred.inv.append("Sword")
                        for x in range(items[8]):
                            thred.inv.append("Wine_Drop")
                        all_temps.empty()
                        all_tempsback.empty()
                        all_numbers.empty()
                        return

                elif event.type == QUIT:
                    # Check for QUIT event. If QUIT, stops then program
                    Room = 0
                    return

                # Checks if Mouse is Clicked
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if resume_button.file == 2:
                        items[1] = claws.number
                        items[5] = slimes.number
                        items[8] = wines.number
                        del(wines)
                        del(slimes)
                        del(claws)
                        for x in range(items[0]):
                            thred.inv.append("Ball")
                        for x in range(items[1]):
                            thred.inv.append("Cat_Claw")
                        for x in range(items[2]):
                            thred.inv.append("Claw")
                        for x in range(items[3]):
                            thred.inv.append("Green")
                        for x in range(items[4]):
                            thred.inv.append("Red")
                        for x in range(items[5]):
                            thred.inv.append("Slime")
                        for x in range(items[6]):
                            thred.inv.append("Straw")
                        for x in range(items[7]):
                            thred.inv.append("Sword")
                        for x in range(items[8]):
                            thred.inv.append("Wine_Drop")
                        all_temps.empty()
                        all_tempsback.empty()
                        all_numbers.empty()
                        return

                    if Red.file == 2:
                        if red:
                            thred.equip("Red")
                        else:
                            if all(((slimes.number >= 1), (claws.number >= 1), (wines.number >= 6))):
                                red = True
                                Red.frame_2 = Red.frame_1
                                items[4] = items[4] + 1
                                slimes.number -= 1
                                claws.number -= 1
                                wines.number -= 6
                            else:
                                pass
                    if Green.file == 2:
                        if green:
                            thred.equip("Green")
                        else:
                            if all(((slimes.number >= 5), (claws.number >= 0), (wines.number >= 3))):
                                green = True
                                Green.frame_2 = Green.frame_1
                                items[3] = items[3] + 1
                                slimes.number -= 5
                                claws.number -= 0
                                wines.number -= 3
                            else:
                                pass
                    if Straw.file == 2:
                        if straw:
                            thred.equip("Straw")
                        else:
                            if all(((slimes.number >= 1), (claws.number >= 1), (wines.number >= 4))):
                                straw = True
                                Straw.frame_2 = Straw.frame_1
                                items[6] = items[6] + 1
                                slimes.number -= 1
                                claws.number -= 1
                                wines.number -= 4
                            else:
                                pass
                    if Ball.file == 2:
                        if ball:
                            thred.equip("Ball")
                        else:
                            if all(((slimes.number >= 6), (claws.number >= 0), (wines.number >= 0))):
                                ball = True
                                Ball.frame_2 = Ball.frame_1
                                items[0] = items[0] + 1
                                slimes.number -= 6
                                claws.number -= 0
                                wines.number -= 0
                            else:
                                pass
                    if Sword.file == 2:
                        if sword:
                            thred.equip("Claw")
                        else:
                            if all(((slimes.number >= 1), (claws.number >= 4), (wines.number >= 1))):
                                sword = True
                                Sword.frame_2 = Sword.frame_1
                                items[7] = items[7] + 1
                                slimes.number -= 1
                                claws.number -= 4
                                wines.number -= 1
                            else:
                                pass

                elif event.type == pygame.VIDEORESIZE:
                    # Resizes Screen If User Tries To Change Screen Size
                    screen = pygame.display.set_mode((event.w, event.h), RESIZABLE)

            # Clears The Screen
            screen.fill((0, 0, 0))

            # Adds Sprites To Screen
            update_screen_game(False, True)

            # Updates Screen
            pygame.display.update()

            # Sets Frame Rate
            clock.tick(60)


    # ─────────────────────────────────────────────────────────────────
    # SKILL TREE data + helpers
    # ─────────────────────────────────────────────────────────────────
    SKILL_TREE = [
        {"id":"vitality_1",  "name":"Vitality I",    "desc":"+5 max HP",          "cost": 3, "needs":None,           "row":0,"col":0},
        {"id":"vitality_2",  "name":"Vitality II",   "desc":"+5 max HP",          "cost": 6, "needs":"vitality_1",   "row":0,"col":1},
        {"id":"iron_yarn",   "name":"Iron Yarn",     "desc":"-20% damage taken",  "cost":10, "needs":"vitality_2",   "row":0,"col":2},
        {"id":"energy_1",    "name":"Energy I",      "desc":"+2 max energy",      "cost": 3, "needs":None,           "row":1,"col":0},
        {"id":"energy_2",    "name":"Energy II",     "desc":"+3 max energy",      "cost": 6, "needs":"energy_1",     "row":1,"col":1},
        {"id":"puddle_surge","name":"Puddle Surge",  "desc":"Puddle costs 50% less","cost":10,"needs":"energy_2",    "row":1,"col":2},
        {"id":"speed_1",     "name":"Quick Feet I",  "desc":"+0.3 speed",         "cost": 4, "needs":None,           "row":2,"col":0},
        {"id":"speed_2",     "name":"Quick Feet II", "desc":"+0.5 speed",         "cost": 8, "needs":"speed_1",      "row":2,"col":1},
        {"id":"damage_1",    "name":"Sharpness I",   "desc":"+0.5 attack",        "cost": 4, "needs":None,           "row":3,"col":0},
        {"id":"damage_2",    "name":"Sharpness II",  "desc":"+0.8 attack",        "cost": 8, "needs":"damage_1",     "row":3,"col":1},
        {"id":"crit_strike", "name":"Crit Strike",   "desc":"20% crit chance",    "cost":12, "needs":"damage_2",     "row":3,"col":2},
        {"id":"sight_1",     "name":"Eagle Eye I",   "desc":"+0.3 sight radius",  "cost": 3, "needs":None,           "row":4,"col":0},
        {"id":"sight_2",     "name":"Eagle Eye II",  "desc":"+0.5 sight radius",  "cost": 6, "needs":"sight_1",      "row":4,"col":1},
        {"id":"thread_sense","name":"Thread Sense",  "desc":"+50% thread drops",  "cost": 5, "needs":None,           "row":4,"col":2},
    ]

    def apply_skill(skill_id):
        global thred
        if skill_id == "vitality_1" or skill_id == "vitality_2":
            thred.max_health += 5
            thred.health = min(thred.health + 5, thred.max_health)
        elif skill_id == "iron_yarn":
            thred.defense_mult = getattr(thred, 'defense_mult', 1.0) * 0.8
        elif skill_id == "energy_1":
            thred.max_energy += 2
        elif skill_id == "energy_2":
            thred.max_energy += 3
        elif skill_id == "speed_1":
            thred.speed += 0.3
        elif skill_id == "speed_2":
            thred.speed += 0.5
        elif skill_id == "damage_1":
            thred.attack += 0.5
        elif skill_id == "damage_2":
            thred.attack += 0.8
        elif skill_id == "crit_strike":
            thred.crit_chance = 0.2
        elif skill_id == "sight_1":
            thred.sight += 0.3
        elif skill_id == "sight_2":
            thred.sight += 0.5
        elif skill_id == "thread_sense":
            thred.thread_mult = getattr(thred, 'thread_mult', 1.0) + 0.5

    def skill_tree_screen():
        global Room, screen, thred
        pygame.font.init()
        font_title = pygame.font.Font(None, 14)
        font_sm    = pygame.font.Font(None, 10)
        font_xs    = pygame.font.Font(None, 9)
        # Camera is SCREEN_WIDTH/zoom × SCREEN_HEIGHT/zoom = 500×233
        # Fit 3 cols × 5 rows in that space
        CELL_W, CELL_H = 148, 30
        PAD_X, PAD_Y   = 8, 5
        START_X, START_Y = 10, 48

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    Room = 0
                    return
                elif event.type == KEYDOWN:
                    if event.key == K_RETURN or event.key == K_ESCAPE:
                        waiting = False
                elif event.type == MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    w, h = screen.get_width(), screen.get_height()
                    cam_w2 = round(SCREEN_WIDTH / Layers.zoom)
                    cam_h2 = round(SCREEN_HEIGHT / Layers.zoom)
                    # Map screen mouse → camera coords
                    scale_x = w / cam_w2
                    scale_y = h / cam_h2
                    gmx = mx / scale_x; gmy = my / scale_y
                    # Continue button area (in camera space)
                    btn_cx2 = cam_w2 - 45; btn_cy2 = cam_h2 - 12
                    if (btn_cx2-40) <= gmx <= (btn_cx2+42) and (btn_cy2-9) <= gmy <= (btn_cy2+9):
                        waiting = False
                        continue
                    for sk in SKILL_TREE:
                        cx = START_X + sk["col"] * (CELL_W + PAD_X)
                        cy = START_Y + sk["row"] * (CELL_H + PAD_Y)
                        if cx <= gmx <= cx + CELL_W and cy <= gmy <= cy + CELL_H:
                            purchased = getattr(thred, 'skills', set())
                            needs_met  = sk["needs"] is None or sk["needs"] in purchased
                            can_afford = thred.thread >= sk["cost"]
                            not_bought = sk["id"] not in purchased
                            if needs_met and can_afford and not_bought:
                                thred.thread -= sk["cost"]
                                thred.skills.add(sk["id"])
                                apply_skill(sk["id"])

            sw, sh = screen.get_width(), screen.get_height()
            # Draw onto a camera-sized surface, then scale up
            cam_w = round(SCREEN_WIDTH / Layers.zoom)
            cam_h = round(SCREEN_HEIGHT / Layers.zoom)
            cam = pygame.surface.Surface((cam_w, cam_h))
            cam.fill((15, 10, 25))

            # Title
            t = font_title.render("~~ SKILL TREE ~~  (click to buy, Enter to continue)", True, (220, 200, 100))
            cam.blit(t, (2, 2))
            thread_surf = font_sm.render("Thread: " + str(int(thred.thread)) + "   Skills: " + str(len(getattr(thred,'skills',set()))), True, (220,200,100))
            cam.blit(thread_surf, (2, 14))

            purchased = getattr(thred, 'skills', set())

            # Connection lines
            for sk in SKILL_TREE:
                if sk["needs"]:
                    parent = next((s for s in SKILL_TREE if s["id"] == sk["needs"]), None)
                    if parent:
                        px = START_X + parent["col"] * (CELL_W + PAD_X) + CELL_W
                        py = START_Y + parent["row"] * (CELL_H + PAD_Y) + CELL_H // 2
                        cx = START_X + sk["col"] * (CELL_W + PAD_X)
                        cy = START_Y + sk["row"] * (CELL_H + PAD_Y) + CELL_H // 2
                        col = (80, 170, 80) if sk["id"] in purchased else (60, 55, 40)
                        pygame.draw.line(cam, col, (px, py), (cx, cy), 2)

            # Skill nodes
            mx_raw, my_raw = pygame.mouse.get_pos()
            gmx = mx_raw * cam_w / sw if sw > 0 else 0
            gmy = my_raw * cam_h / sh if sh > 0 else 0
            for sk in SKILL_TREE:
                x = START_X + sk["col"] * (CELL_W + PAD_X)
                y = START_Y + sk["row"] * (CELL_H + PAD_Y)
                bought     = sk["id"] in purchased
                needs_met  = sk["needs"] is None or sk["needs"] in purchased
                can_afford = thred.thread >= sk["cost"]
                if bought:
                    bg, bd, tc = (30,70,30), (70,180,70), (130,255,130)
                elif needs_met and can_afford:
                    bg, bd, tc = (30,30,70), (80,80,200), (180,180,255)
                elif needs_met:
                    bg, bd, tc = (50,40,15), (90,70,25), (150,130,70)
                else:
                    bg, bd, tc = (25,20,30), (55,45,65), (90,80,100)
                hovering = x <= gmx <= x+CELL_W and y <= gmy <= y+CELL_H
                if hovering and not bought and needs_met:
                    bd = (255,220,60)
                pygame.draw.rect(cam, bg, (x, y, CELL_W, CELL_H), border_radius=3)
                pygame.draw.rect(cam, bd, (x, y, CELL_W, CELL_H), 1, border_radius=3)
                ns = font_sm.render(sk["name"], True, tc)
                cam.blit(ns, (x+3, y+2))
                ds = font_xs.render(sk["desc"], True, (160,150,160))
                cam.blit(ds, (x+3, y+12))
                if bought:
                    sts = font_xs.render("LEARNED", True, (70,200,70))
                elif not needs_met:
                    sts = font_xs.render("LOCKED", True, (110,95,125))
                else:
                    sts = font_xs.render(str(sk["cost"]) + " thread", True, (210,190,90))
                cam.blit(sts, (x+3, y+21))

            # Continue button (in camera space)
            btn_cx = cam_w - 45; btn_cy = cam_h - 12
            pygame.draw.rect(cam, (28,78,28), (btn_cx-40, btn_cy-9, 82, 18), border_radius=4)
            pygame.draw.rect(cam, (65,168,65), (btn_cx-40, btn_cy-9, 82, 18), 1, border_radius=4)
            bs = font_sm.render("CONTINUE >>", True, (120,248,120))
            cam.blit(bs, (btn_cx - bs.get_width()//2, btn_cy - bs.get_height()//2))
            # Hint text
            ht = font_xs.render("Click skill to buy | Enter/Esc to continue", True, (80,75,100))
            cam.blit(ht, (4, cam_h - 9))

            scaled = pygame.transform.scale(cam, (sw, sh))
            screen.blit(scaled, (0, 0))
            pygame.display.flip()
            clock.tick(30)

    def level_complete_screen():
        global Room, current_level, initial_enemy_count
        pygame.font.init()
        font_title = pygame.font.Font(None, 48)
        font_sub   = pygame.font.Font(None, 30)
        font_sm    = pygame.font.Font(None, 22)
        waiting = True
        level_names = {1: "The Tangled Cavern", 2: "The Wool Labyrinth", 3: "The Spool Chamber"}
        lname = level_names.get(current_level, "Level " + str(current_level))
        while waiting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    Room = 0
                    return
                elif event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
                    waiting = False
            sw, sh = screen.get_width(), screen.get_height()
            screen.fill((10, 30, 10))
            t = font_title.render("AREA CLEARED!", True, (100,230,100))
            screen.blit(t, (sw//2 - t.get_width()//2, sh//5))
            sub = font_sub.render(lname, True, (160,200,160))
            screen.blit(sub, (sw//2 - sub.get_width()//2, sh//5 + 55))
            ts = font_sm.render("Thread collected: " + str(int(thred.thread)), True, (220,200,100))
            screen.blit(ts, (sw//2 - ts.get_width()//2, sh//2 - 20))
            if current_level < MAX_LEVEL:
                ps = font_sm.render("Click or press any key to visit the Skill Tree", True, (150,200,150))
            else:
                ps = font_sm.render("Click or press any key to continue", True, (150,200,150))
            screen.blit(ps, (sw//2 - ps.get_width()//2, sh*3//4))
            pygame.display.flip()
            clock.tick(30)

        if current_level < MAX_LEVEL:
            skill_tree_screen()
            current_level += 1
            load_level()
        else:
            victory_screen()
            current_level = 1
            Room = -1
            all_backgrounds.empty(); all_buttons.empty(); all_items.empty()
            all_enemies.empty(); all_visuals.empty(); all_cursors.empty()
            all_attacksa.empty(); all_attacksb.empty(); all_mains.empty()
            all_text.empty(); all_lights.empty(); all_blocks.empty()
            all_temps.empty(); all_tempsback.empty(); all_numbers.empty()
            Layers.map = [[0 for i in range(65)] for j in range(35)]
            loadscreen()

    def game_over_screen():
        global Room, current_level, player_dead
        pygame.font.init()
        font_title = pygame.font.Font(None, 52)
        font_sub   = pygame.font.Font(None, 32)
        font_sm    = pygame.font.Font(None, 24)
        saved_thread = int(getattr(thred, 'thread', 0))
        saved_level  = current_level
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    Room = 0
                    return
                elif event.type == KEYDOWN:
                    if event.key == K_RETURN or event.key == K_SPACE or event.key == K_ESCAPE:
                        waiting = False
                elif event.type == MOUSEBUTTONDOWN:
                    waiting = False
            sw, sh = screen.get_width(), screen.get_height()
            screen.fill((20, 8, 28))
            t = font_title.render("THREAD SEVERED", True, (200,50,50))
            screen.blit(t, (sw//2 - t.get_width()//2, sh//5))
            sub = font_sub.render("Thred has unraveled...", True, (170,100,100))
            screen.blit(sub, (sw//2 - sub.get_width()//2, sh//5 + 65))
            lt = font_sm.render("Reached Level " + str(saved_level) + " of 3", True, (190,190,140))
            screen.blit(lt, (sw//2 - lt.get_width()//2, sh//2 - 20))
            tt = font_sm.render("Thread Collected: " + str(saved_thread), True, (220,200,100))
            screen.blit(tt, (sw//2 - tt.get_width()//2, sh//2 + 15))
            ps = font_sm.render("Press ENTER / click to return to menu", True, (140,140,170))
            screen.blit(ps, (sw//2 - ps.get_width()//2, sh*3//4))
            pygame.display.flip()
            clock.tick(30)
        # Reset and go back to title
        current_level = 1
        player_dead   = False
        all_backgrounds.empty(); all_buttons.empty(); all_items.empty()
        all_enemies.empty(); all_visuals.empty(); all_cursors.empty()
        all_attacksa.empty(); all_attacksb.empty(); all_mains.empty()
        all_text.empty(); all_lights.empty(); all_blocks.empty()
        all_temps.empty(); all_tempsback.empty(); all_numbers.empty()
        Layers.map = [[0 for i in range(65)] for j in range(35)]
        Room = -1
        loadscreen()

    def victory_screen():
        global screen
        pygame.font.init()
        font_title = pygame.font.Font(None, 64)
        font_sub   = pygame.font.Font(None, 34)
        font_sm    = pygame.font.Font(None, 26)
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
                    waiting = False
            sw, sh = screen.get_width(), screen.get_height()
            screen.fill((10, 10, 40))
            # Draw starfield
            for i in range(60):
                rx = (i * 37 + 7) % sw
                ry = (i * 53 + 11) % sh
                pygame.draw.circle(screen, (180 + (i % 3)*25, 180, 255 - (i % 4)*15), (rx, ry), 1 + (i%3))
            t = font_title.render("VICTORY!", True, (220, 180, 50))
            screen.blit(t, (sw//2 - t.get_width()//2, sh//6))
            sub = font_sub.render("The Wine King is defeated!", True, (200, 200, 180))
            screen.blit(sub, (sw//2 - sub.get_width()//2, sh//6 + 70))
            st = font_sm.render("Thred has reclaimed the Spool of Origins.", True, (160,160,220))
            screen.blit(st, (sw//2 - st.get_width()//2, sh//6 + 110))
            ts = font_sm.render("Total Thread: " + str(int(getattr(thred,'thread',0))), True, (220,200,100))
            screen.blit(ts, (sw//2 - ts.get_width()//2, sh//2 + 10))
            sk = font_sm.render("Skills Learned: " + str(len(getattr(thred,'skills',set()))), True, (140,220,140))
            screen.blit(sk, (sw//2 - sk.get_width()//2, sh//2 + 45))
            ps = font_sm.render("Click or press any key to return to menu", True, (150,150,190))
            screen.blit(ps, (sw//2 - ps.get_width()//2, sh*3//4 + 20))
            pygame.display.flip()
            clock.tick(30)

    def load_level():
        global thred, initial_enemy_count, player_dead, Room
        player_dead = False
        # Carry over player progression
        saved_thread  = int(getattr(thred, 'thread', 0))
        saved_skills  = set(getattr(thred, 'skills', set()))
        saved_hp      = thred.health
        saved_mhp     = thred.max_health
        saved_me      = thred.max_energy
        saved_e       = thred.energy
        saved_atk     = thred.attack
        saved_spd     = thred.speed
        saved_sight   = thred.sight
        saved_armor   = thred.armor
        saved_hand    = thred.hand
        saved_inv     = list(thred.inv)
        saved_def     = getattr(thred, 'defense_mult', 1.0)
        saved_tmult   = getattr(thred, 'thread_mult',  1.0)
        saved_crit    = getattr(thred, 'crit_chance',  0.0)
        # Wipe everything
        try: thred.kill()
        except Exception: pass
        all_backgrounds.empty(); all_buttons.empty(); all_items.empty()
        all_enemies.empty(); all_visuals.empty(); all_cursors.empty()
        all_attacksa.empty(); all_attacksb.empty(); all_mains.empty()
        all_text.empty(); all_lights.empty(); all_blocks.empty()
        all_temps.empty(); all_tempsback.empty(); all_numbers.empty()
        Layers.map = [[0 for i in range(65)] for j in range(35)]
        Layers.Map = pygame.surface.Surface((65*32, 35*32))
        Layers.Map.set_colorkey((100,90,50))
        Layers.Light_Layer = pygame.surface.Surface((65*32, 35*32))
        # Load new level (creates fresh thred)
        new_file()
        # Restore carried-over stats
        thred.thread        = saved_thread
        thred.skills        = saved_skills
        thred.health        = min(saved_hp, thred.max_health)
        thred.max_health    = saved_mhp
        thred.max_energy    = saved_me
        thred.energy        = min(saved_e, saved_me)
        thred.attack        = saved_atk
        thred.speed         = saved_spd
        thred.sight         = saved_sight
        thred.armor         = saved_armor
        thred.hand          = saved_hand
        thred.inv           = saved_inv
        thred.defense_mult  = saved_def
        thred.thread_mult   = saved_tmult
        thred.crit_chance   = saved_crit
        initial_enemy_count = len(all_enemies)
        Room = 2

    # Creates Main Loop for the Game
    # Uses Room Codes To Dictate Room Loops
    while Running:
        global screen
        global Room

        if Room == 0:
            Running = False
            break
        if Room == -1:
            loadscreen()
        if Room == 1:
            tutorial()
        if Room == 2:
            game()

    # Removes Sprites from Screen
    screen.fill((0, 0, 0))
    pygame.display.flip()

    # if no current save files uses current play through to make one
    if not Loaded:
        try:
            save_game()
        except Exception:
            pass

