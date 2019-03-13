import os
import time
import pygame as pg
from pynput.keyboard import Key, Controller
from random import randint
import random
from . import kk

kkb = Controller()
gap_between_keypress = 0
to_press = 'a'

keybinding = {
    'action':pg.K_s,
    'jump':pg.K_a,
    'left':pg.K_LEFT,
    'right':pg.K_RIGHT,
    'down':pg.K_DOWN
}

model_number = 1
current_pool = kk.current_pool
temp_for_model_num_bug = False
models_fitness = kk.fitness
current_fitness = 0

class Control(object):
    """Control class for entire project. Contains the game loop, and contains
    the event_loop which passes events to States as needed. Logic for flipping
    states is also found here."""
    def __init__(self, caption):
        self.screen = pg.display.get_surface()
        self.done = False
        self.clock = pg.time.Clock()
        self.caption = caption
        self.fps = 60
        self.show_fps = False
        self.current_time = 0.0
        self.keys = pg.key.get_pressed()
        self.state_dict = {}
        self.state_name = None
        self.state = None
        self.generated_input = [Key.right,'a',Key.left]
        # removed "s" as speed running was a bug in the game

    def setup_states(self, state_dict, start_state):
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]

    def update(self):
        self.current_time = pg.time.get_ticks()
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.mar_gya()
            self.flip_state()
        self.state.update(self.screen, self.keys, self.current_time)

    def flip_state(self):
        previous, self.state_name = self.state_name, self.state.next
        persist = self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup(self.current_time, persist)
        self.state.previous = previous

    
    def event_loop(self):
        global gap_between_keypress
        global to_press
        gap_between_keypress+=1
        if gap_between_keypress % 30 == 0:
            gap_between_keypress = 1
            global model_number
            to_press = kk.do_it_genetically(model_number) #logic
        kkb.press(to_press)
        # print(self.state_dict,self.state,self.state_name)
        if to_press == Key.right:
            global current_fitness
            current_fitness += 2

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN:
                self.keys = pg.key.get_pressed()
                self.toggle_show_fps(event.key)
            elif event.type == pg.KEYUP:
                self.keys = pg.key.get_pressed()
            self.state.get_event(event)
        kkb.release(to_press)

    def mar_gya(self):
        global model_number,temp_for_model_num_bug
        if not temp_for_model_num_bug:
            temp_for_model_num_bug = True
        else:
            temp_for_model_num_bug = False
            global models_fitness
            models_fitness[model_number] = current_fitness
            model_number += 1
        print("===> ", model_number)
        print(model_number)
        model_number%=kk.total_models
        if model_number == 0:
            self.mutate_etc() #code aayga

    def mutate_etc(self):
        global current_pool
        global models_fitness
        global generation
        total_models = kk.total_models
        new_weights = []
        total_fitness = 0
        for select in range(total_models):
            total_fitness += models_fitness[select]
        for select in range(total_models):
            models_fitness[select] /= total_fitness#make sures ki fitness har model ki 0 aur 1 k beech m ho.
            if select > 0:
                models_fitness[select] += models_fitness[select-1]#yeh ni samjha. baad m htana hai dheere se
        for select in range(int(total_models/2)):#mtln half hi models ko hum iterate kr rhe hai.
            parent1 = random.uniform(0, 1)#randomly choose kr rhe hai
            parent2 = random.uniform(0, 1)#same
            idx1 = -1
            idx2 = -1
            for idxx in range(total_models):
                if models_fitness[idxx] >= parent1:#puts the last model jiski fitness jyada ho parent1 se.
                    idx1 = idxx
                    break
            for idxx in range(total_models):
                if models_fitness[idxx] >= parent2:
                    idx2 = idxx
                    break
            new_weights1 = kk.model_crossover(idx1, idx2)#new weight kaise milre cause idx1 idx2 are just integer values.
    #new_weights1 ek array hai jis m idx1 aur idx2 k models k weight ka crossover kr k as return hora hai as array. 
            updated_weights1 = kk.model_mutate(new_weights1[0])#new weights of model at idx1
    #okay man just thode random changes kr k wapas aare hai hume
            updated_weights2 = kk.model_mutate(new_weights1[1])
            new_weights.append(updated_weights1)
            new_weights.append(updated_weights2)
        for select in range(len(new_weights)):
            models_fitness[select] = -100
            current_pool[select].set_weights(new_weights[select])
        kk.save_pool()
        return

    def toggle_show_fps(self, key):
        if key == pg.K_F5:
            self.show_fps = not self.show_fps
            if not self.show_fps:
                pg.display.set_caption(self.caption)
        if key == pg.K_F6:
            print("F6 pressed! Saving pool")
            kk.save_pool()

    def main(self):
        """Main loop for entire program"""
        print("Adjust the screen !!")
        time.sleep(5)
        ccc = 0
        print("Starting Game")
        while (not self.done and ccc<100):
            ccc=+1
            self.event_loop()
            self.update()
            pg.display.update()
            self.clock.tick(self.fps)
            if self.show_fps:
                fps = self.clock.get_fps()
                with_fps = "{} - {:.2f} FPS".format(self.caption, fps)
                pg.display.set_caption(with_fps)


class _State(object):
    def __init__(self):
        self.start_time = 0.0
        self.current_time = 0.0
        self.done = False
        self.quit = False
        self.next = None
        self.previous = None
        self.persist = {}

    def get_event(self, event):
        pass

    def startup(self, current_time, persistant):
        self.persist = persistant
        self.start_time = current_time

    def cleanup(self):
        self.done = False
        return self.persist

    def update(self, surface, keys, current_time):
        pass



def load_all_gfx(directory, colorkey=(255,0,255), accept=('.png', 'jpg', 'bmp')):
    graphics = {}
    for pic in os.listdir(directory):
        name, ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pg.image.load(os.path.join(directory, pic))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
                img.set_colorkey(colorkey)
            graphics[name]=img
    return graphics


def load_all_music(directory, accept=('.wav', '.mp3', '.ogg', '.mdi')):
    songs = {}
    for song in os.listdir(directory):
        name,ext = os.path.splitext(song)
        if ext.lower() in accept:
            songs[name] = os.path.join(directory, song)
    return songs


def load_all_fonts(directory, accept=('.ttf')):
    return load_all_music(directory, accept)


def load_all_sfx(directory, accept=('.wav','.mpe','.ogg','.mdi')):
    effects = {}
    for fx in os.listdir(directory):
        name, ext = os.path.splitext(fx)
        if ext.lower() in accept:
            effects[name] = pg.mixer.Sound(os.path.join(directory, fx))
    return effects











