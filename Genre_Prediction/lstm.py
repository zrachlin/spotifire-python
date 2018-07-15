#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 15 00:00:01 2018

@author: zrachlin
"""
import keras
from sklearn.model_selection import train_test_split
import numpy as np
import pickle

num_classes = 23
X = np.load('x.npy')
X_aux = np.load('x_aux.npy')
y_cat = np.load('y.npy')

X_train, X_test,y_train, y_test = train_test_split(X, y_cat, test_size=0.1,random_state=42)
Xaux_train, Xaux_test,y_train1, y_test1 = train_test_split(X_aux, y_cat, test_size=0.1,random_state=42)
print(X_train.shape,X_test.shape)
print(Xaux_train.shape,Xaux_test.shape)

def adjustMaxLen(maxlen,divisor):
    #makes the length divisible by 4
    while maxlen%divisor > 0:
        maxlen += 1
    return maxlen

from keras.layers import Input, LSTM, Dense,Lambda
from keras.models import Model

Xt1 = X_train[:,0:1041]
Xt2 = X_train[:,1041:2082]
Xt3 = X_train[:,2082:3123]
Xt4 = X_train[:,3123:]

Xte1 = X_test[:,0:1041]
Xte2 = X_test[:,1041:2082]
Xte3 = X_test[:,2082:3123]
Xte4 = X_test[:,3123:]
#main_input = Input(shape=(X_train.shape[1:]), name='main_input')
mi1 = Input(shape=Xt1.shape[1:],name='mi1')
mi2 = Input(shape=Xt2.shape[1:],name='mi2')
mi3 = Input(shape=Xt3.shape[1:],name='mi3')
mi4 = Input(shape=Xt4.shape[1:],name='mi4')
lstm_aux = []
lstm_out = []
for i in [mi1,mi2,mi3,mi4]:
    l = LSTM(32)(i)
    l = Dense(64,activation='relu')(l)
    lstm_aux.append(Dense(num_classes,activation='softmax')(l))
    lstm_out.append(l)


#maxlen_adj = X_train.shape[1]
#num_segments = 4
#start = 0
#step = maxlen_adj//num_segments
#lstm_aux = []
#lstm_out = []
#for i in range(num_segments):
#    end = start+step
#    print(start,end)
#    l = Lambda(lambda x: x[:,start:end,:])(main_input)
#    print(l.shape)
#    l = LSTM(32)(l)
#    l = Dense(64,activation='relu')(l)
#    lstm_aux.append(Dense(num_classes,activation='softmax')(l))
#    lstm_out.append(l)
#    start = end

auxiliary_output = keras.layers.Average(name='aux_output')(lstm_aux)


auxiliary_input = Input(shape=(12,), name='aux_input')
lstm_out = keras.layers.Average()(lstm_out)
x = keras.layers.concatenate([lstm_out, auxiliary_input])

# We stack a deep densely-connected network on top
x = Dense(64, activation='relu')(x)
x = Dense(64, activation='relu')(x)
x = Dense(64, activation='relu')(x)
main_output = Dense(num_classes, activation='softmax', name='main_output')(x)



from keras.utils import multi_gpu_model
from keras.callbacks import ModelCheckpoint, CSVLogger
#model = Model(inputs=[main_input, auxiliary_input], outputs=[main_output, auxiliary_output])
model = Model(inputs=[mi1,mi2,mi3,mi4,auxiliary_input], outputs=[main_output, auxiliary_output])


# Replicates `model` on 4 GPUs.
# This assumes that your machine has 4 available GPUs.
parallel_model = multi_gpu_model(model, gpus=4)
parallel_model.compile(optimizer='adam', loss='categorical_crossentropy',
              loss_weights=[1., 0.2],metrics=['accuracy'])

mc = ModelCheckpoint('4lstm.{epoch:02d}--{val_loss:.2f}.hdf5',save_best_only=True)
csv_logger=CSVLogger('training_4lstm.log')
#history = parallel_model.fit([X_train[:12000], Xaux_train[:12000].reshape(-1,12)], [y_train[:12000], y_train[:12000]],validation_data=([X_test,Xaux_test.reshape(-1,12)],[y_test,y_test]),
#          epochs=50, batch_size=60,callbacks = [mc,csv_logger])
history = parallel_model.fit([Xt1[:12000],Xt2[:12000],Xt3[:12000],Xt4[:12000],Xaux_train[:12000].reshape(-1,12)], [y_train[:12000], y_train[:12000]],validation_data=([Xte1,Xte2,Xte3,Xte4,Xaux_test.reshape(-1,12)],[y_test,y_test]),
          epochs=50, batch_size=60,callbacks = [mc,csv_logger])
pickle.dump(history.history,open('training_history_4lstm.p','wb'))