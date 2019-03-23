
from pynput.keyboard import Key, Controller
from random import randint
import random

import numpy as np
from PIL import ImageGrab as ig
import cv2
import time
from .components import info
from keras.models import Sequential
from keras.layers import Dense, Activation, Conv2D, MaxPooling2D, Flatten, Dropout
from keras.optimizers import SGD
model_built = False
load_saved = True
save_current_pool = 1
current_pool = []
fitness = []
total_models = 14
generation = 1

def save_pool():
    for xi in range(total_models):
        current_pool[xi].save_weights("Current_Model_Pool/model_new" + str(xi) + ".keras")
    print("Saved current pool!")

def model_crossover(model_idx1, model_idx2):
    global current_pool
    weights1 = current_pool[model_idx1].get_weights()
    weights2 = current_pool[model_idx2].get_weights()
    weightsnew1 = weights1
    weightsnew2 = weights2
    weightsnew1[0] = weights2[0]
    weightsnew2[0] = weights1[0]
    return np.asarray([weightsnew1, weightsnew2])

def model_mutate(weights):
    for xi in range(len(weights)):
        for yi in range(len(weights[xi])):
            temp2 = random.uniform(0, 1)
            print("In mutation random value is ",temp2," > 0.85")
            if  temp2 > 0.85:
                change = random.uniform(-0.5,0.5)
                weights[xi][yi] += change
                # print(weights[xi][yi],change)
                # try:
                #     if weights[xi][yi]>=1.0:
                #         weights[xi][yi]-=0.5
                # except:
                #     pass
    return weights

def predict_action(neural_input, model_num):
    neural_input = np.expand_dims(neural_input,axis=3)
    neural_input = np.atleast_2d(neural_input) #(560, 750, 3)
    neural_input = np.expand_dims(neural_input,axis=0)
    
    output_prob = current_pool[model_num].predict([neural_input])
    x = np.argmax(output_prob)
    # print(output_prob," => ",generated_input[x])
    #if info.current_time % 5 == 0:
     #   x = 1
    #else:
     #   x = 0

    # print("===> ", model_num)
    # print(model_num)
    return generated_input[x]
    #return do_it_randomly()
    # if output_prob[0] <= 0.5:
    #     # Perform the jump action
    #     return 1
    # if output_prob[1] <= 0.5:
    #     # Perform the jump action
    #     return 1
    # return 2


generated_input = ['a',Key.right,Key.left]

def do_it_randomly():
    return generated_input[randint(0, len(generated_input)-1)]

def collect_frame():
    screen = np.array(ig.grab(bbox = (0,500,750,600)))
    grey_screen = cv2.Canny(screen,threshold1=200,threshold2=300)
    # we can also try retrurning colored screen here... inc processing by 3 
    # but removing ambiguity of bushes,pipe,enemy.
    # cv2.imshow('MARIO', screen)
    cv2.waitKey(1)
    return grey_screen
    
def do_it_genetically(model_num):
    global model_built
    if not model_built: #ek toh model built ki value jo hai woh 0 hai !!
        init_models()
        if load_saved:#load save ki boolean value kaha change hori hai?
            load_saved_pool()
        model_built = True
    frame = collect_frame()#frame of picture collect kr rhe
    return predict_action(frame,model_num)

def load_saved_pool():
    for i in range(total_models):
        current_pool[i].load_weights("Current_Model_Pool/model_new"+str(i)+".keras")
        fitness.append(0)

def init_models():
    for i in range(total_models):
        model = Sequential() 
        model.add(Conv2D(32,(3,3), activation='relu', input_shape=(100,750,1)))# dim of image
        model.add(Flatten())
#        model.add(Dropout(0.5))
#        model.add(Dense(16,activation='relu'))
        model.add(Dense(3,activation='sigmoid'))
        sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
        model.compile(loss="mse", optimizer=sgd, metrics=["accuracy"])
        current_pool.append(model)
        fitness.append(0)

