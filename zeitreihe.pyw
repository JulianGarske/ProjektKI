# -*- coding: utf-8 -*-
"""Time Prediction.ipynb
Automatically generated by Colaboratory.
Original file is located at
    https://colab.research.google.com/drive/1nJHBHpB3cv6xMYuanwOfrDpV-i_9zFNM
"""

#Installieren der Bibliotheken, falls in Google Coolab ausgeführt wird
#!pip install tensorflow #for prediction
#!pip install numpy  #for matrix multiplication
#!pip install pandas #define the data structures
#!pip install matplotlib #for visualization
#!pip install scikit-learn #for normalizing our data(scaling)

#importing the libraries
import tensorflow as tf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import ttk
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

import io

	
# Funktion, um die Datensätze zu kreieren
#Input: Genutzter Datensatz
#window_size - wie viele Tage sollen berücksichtigt werden, um den nächsten Tag vorauszusagen 

def window_data(data, window_size):
	X = []
	y = []
	
	i = 0
	
	while (i + window_size) <= len(data) - 1:
		X.append(data[i:i+window_size]) 
		y.append(data[i+window_size]) 
		
		i += 1  
	return X, y  


# Hauptsächliche Funktion. Erstellt das neuronale Netz und trainiert es. Das Ergebnis wird berechnet und zurückgegeben
def calculate(data_to_use):
	

	#Skalieren der Daten, sodass sie zwischen 0 und 1 liegen
	for i in range(len(data_to_use)):
		data_to_use[i] = data_to_use[i] / 24

	scaled_data = data_to_use.reshape(-1,1)


	laenge = len(data_to_use)

	# Einteilen der Daten mit der window_data Funktion
	X, y = window_data(scaled_data, 7) 
	# Aufteilung in Trainings- und Testset
	X_train  = np.array(X[:laenge-1]) # 99: bis zur  99. Stelle 
	y_train = np.array(y[:laenge-1]) # :99 ab 99. Stelle
	# Die ersten 99 Werte werden zum Trainieren genutzt, um dann den 100. Wert vorauszusagen

	# Die letzten 7 Werte, um den 100. Tag vorauszusagen
	X_test = np.array(X[laenge-8:laenge-1]) 
	#y_test = np.array(y[laenge-8:laenge-1])

	#print("X_train size: {}".format(X_train.shape))
	#print("y_train size: {}".format(y_train.shape))
	#print("X_test size: {}".format(X_test.shape)) 
	#print("y_test size: {}".format(y_test.shape))

	# Hier wird das Netz erstellt
	batch_size = 1 # Nummer der Datenreihen, die durchlaufen werden, bevor das Modell geupdatet wird
	window_size = 7 
	hidden_layer = 250 # Units der LSTM-Zelle
	clip_margin = 4 # Für Gradient clipping notwendig: wie genau soll das Netz sein?
	learning_rate = 0.001 # Wie viel ändert sich das Model bei fehlern?
	epochs = 300 # Nummer der kompletten Durchläufe bis zum Ende des Trainings

	
	#Definition der Platzhalter
	inputs = tf.placeholder(tf.float32, [batch_size, window_size, 1])
	targets = tf.placeholder(tf.float32, [batch_size, 1])


	# Gewichte der Zellen

	# Gewichte für die Input Layer
	#Es werden zufällig Gewichte verteilt:
	#truncates_normal: Zufällige Zahlen nahe 0
	#[1, hidden_layer]: Es soll ein Array von hidden_layer ausgegeben werden
	weights_input_gate = tf.Variable(tf.truncated_normal([1, hidden_layer], stddev=0.05))
	weights_input_hidden = tf.Variable(tf.truncated_normal([hidden_layer, hidden_layer], stddev=0.05))
	bias_input = tf.Variable(tf.zeros([hidden_layer]))

	#Gewichte für das forgot gate
	weights_forget_gate = tf.Variable(tf.truncated_normal([1, hidden_layer], stddev=0.05))
	weights_forget_hidden = tf.Variable(tf.truncated_normal([hidden_layer, hidden_layer], stddev=0.05))
	bias_forget = tf.Variable(tf.zeros([hidden_layer]))

	#Gewichte für das output gate
	weights_output_gate = tf.Variable(tf.truncated_normal([1, hidden_layer], stddev=0.05))
	weights_output_hidden = tf.Variable(tf.truncated_normal([hidden_layer, hidden_layer], stddev=0.05))
	bias_output = tf.Variable(tf.zeros([hidden_layer]))

	#Gewichte für die memory cell
	weights_memory_cell = tf.Variable(tf.truncated_normal([1, hidden_layer], stddev=0.05))
	weights_memory_cell_hidden = tf.Variable(tf.truncated_normal([hidden_layer, hidden_layer], stddev=0.05))
	bias_memory_cell = tf.Variable(tf.zeros([hidden_layer]))

	#Gewichte für die Output Layer
	weights_output = tf.Variable(tf.truncated_normal([hidden_layer, 1], stddev=0.05))
	bias_output_layer = tf.Variable(tf.zeros([1]))
	
	# Funktion, um die Zellen zu verknüpfen
	def LSTM_cell(input, output, state):
    
		input_gate = tf.sigmoid(tf.matmul(input, weights_input_gate) + tf.matmul(output, weights_input_hidden) + bias_input)
		
		forget_gate = tf.sigmoid(tf.matmul(input, weights_forget_gate) + tf.matmul(output, weights_forget_hidden) + bias_forget)
		
		output_gate = tf.sigmoid(tf.matmul(input, weights_output_gate) + tf.matmul(output, weights_output_hidden) + bias_output)
		
		memory_cell = tf.tanh(tf.matmul(input, weights_memory_cell) + tf.matmul(output, weights_memory_cell_hidden) + bias_memory_cell)
		
		state = state * forget_gate + input_gate * memory_cell
		
		output = output_gate * tf.tanh(state)
		return state, output
  
	# Definition der Schleife des Netzes
	outputs = []
	for i in range(batch_size): 
	  
		# Ausgangssituation sind nur Nullen
		batch_state = np.zeros([1, hidden_layer], dtype=np.float32) 
		batch_output = np.zeros([1, hidden_layer], dtype=np.float32)
		
		# an jedem Punkt wird durch den Input der Output bestimmt
		for ii in range(window_size):
			batch_state, batch_output = LSTM_cell(tf.reshape(inputs[i][ii], (-1, 1)), batch_state, batch_output)
			
		# Der letzte Output wird für die Prediction genutzt
		outputs.append(tf.matmul(batch_output, weights_output) + bias_output_layer)


	# Loss wird definiert
	losses = []

	for i in range(len(outputs)):
		losses.append(tf.losses.mean_squared_error(tf.reshape(targets[i], (-1, 1)), outputs[i])) # Loss-Funktion: Mittlerer quadratischer Fehler
		
	loss = tf.reduce_mean(losses)

	#Optimierer wird erstellt
	gradients = tf.gradients(loss, tf.trainable_variables())
	clipped, _ = tf.clip_by_global_norm(gradients, clip_margin)
	optimizer = tf.train.AdamOptimizer(learning_rate)
	trained_optimizer = optimizer.apply_gradients(zip(gradients, tf.trainable_variables()))

	# Netz wird trainiert
	session = tf.Session()
	session.run(tf.global_variables_initializer())
	for i in range(epochs):
		traind_scores = []
		ii = 0
		epoch_loss = []
		while(ii + batch_size) <= len(X_train):
			X_batch = X_train[ii:ii+batch_size]
			y_batch = y_train[ii:ii+batch_size]
			
			o, c, _ = session.run([outputs, loss, trained_optimizer], feed_dict={inputs:X_batch, targets:y_batch})
			
			epoch_loss.append(c)
			traind_scores.append(o)
			ii += batch_size
		if (i % 30) == 0:
			print('Epoch {}/{}'.format(i, epochs), ' Current loss: {}'.format(np.mean(epoch_loss))) # durchschn. Abweichung in dieser Epoche
		 
	
	# Daten werden berechnet
	tests = []
	i = 0
	while i+batch_size <= len(X_test):  
		o = session.run([outputs],feed_dict={inputs:X_test[i:i+batch_size]})
		i += batch_size
		tests.append(o)
	

	#Daten zurück auf 0 bis 24 formatieren
	result = tests[0][0][0]*24
	return(result)
	

#Button_action definieren
def button_action():
	#öffnet ein Fenster des Dateiexplorers, um eine Datei auszuwählen
	button_for_upload.config(state=DISABLED)
	file_path = askopenfilename()
	if not file_path:
		button_for_upload.config(state=NORMAL)
	else:
		btc = pd.read_csv(file_path)
		# nur die benötigte Spalte auswählen
		data_to_use=btc['Startuhrzeit'].values
		result = calculate(data_to_use)
		button_for_upload.config(state=NORMAL)
		
		hour = int(result)	
		result = str(result[0][0])
		minutes_string = str(result).split(".")
		minutes = int(float( "0." + minutes_string[1][0:1])*60)
		if (len(str(minutes)) == 1):
			minutes = "0" + str(minutes)
		time = "Die Standheizung soll um " + str(hour) + ":" + str(minutes) + " Uhr gestartet werden."
		print(time)
		
		popupmsg(time)

# Ausgabe des Ergebnisses in einem neuen Fenster
def popupmsg(msg):
    popup = Tk()
    popup.wm_title("Ergebnis")
    label = ttk.Label(popup, text=msg)
    label.pack()
    B1 = ttk.Button(popup, text="Okay", command=popup.destroy)
    B1.pack()
    popup.mainloop()
	
# Ein Fenster erstellen
fenster = Tk()
# Den Fenstertitel erstellen
fenster.title("Time Prediction")
fenster.geometry("500x100")
fenster.iconbitmap("car.ico")


file_path =  1
# Label und Buttons erstellen
button_for_upload_label = Label(fenster, text="Um die Voraussage zu starten bitte eine Datei hochladen:\n")
button_for_upload = Button(fenster, text="Datei angeben", command=button_action)
button_to_end = Button(fenster, text="Abbrechen", command=fenster.destroy)


# Komponenten dem Fenster hinzufügen
button_for_upload_label.pack()
button_for_upload.pack()
button_to_end.pack()

# In der Ereignisschleife auf Eingabe des Benutzers warten.
fenster.mainloop()