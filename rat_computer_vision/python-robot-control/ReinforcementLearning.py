"""
Reinforcement learning for robot control
Heavy use of this code:
https://github.com/harvitronix/reinforcement-learning-car/blob
"""
from keras.models import Sequential
from keras.layers.core import Dense, Activation, Dropout
from keras.optimizers import RMSprop
import numpy as np
import random

def init_neural_net(num_sensors, num_commands, layers_size, load=''):
    model = Sequential()

    # First layer.
    model.add(Dense(layers_size[0], 
                    init='lecun_uniform', input_shape=(num_sensors,)))
    model.add(Activation('relu'))
    model.add(Dropout(0.2))

    # Second layer.
    model.add(Dense(layers_size[1], init='lecun_uniform'))
    model.add(Activation('relu'))
    model.add(Dropout(0.2))

    # Output layer.
    model.add(Dense(num_commands, init='lecun_uniform'))
    model.add(Activation('linear'))

    rms = RMSprop()
    model.compile(loss='mse', optimizer=rms)

    if load:
        model.load_weights(load)

    return model

class DeepRLNetwork:
    """Deep neural network (theano + keras) for RL"""
    gamma = 0.9
    batch_size = 100
    num_init_cycles = 100
    buffer = 1000
    
    def init_network(self, num_sensors, num_commands, layers_size, load=''):
        self.num_commands = num_commands
        self.num_sensors = num_sensors
        self.model = init_neural_net(num_sensors, num_commands, layers_size, load)
        self.curr_time = 0
        self.epsilon = 1
        self.data_collect = []
        self.replay = []  # stores tuples of (S, A, R, S').
    
        self.action = None
        self.state = None

    def process_minibatch(self, minibatch):
        """This does the heavy lifting, aka, the training. It's super jacked."""
        X_train = []
        y_train = []
        # Loop through our batch and create arrays for X and y
        # so that we can fit our model at every step.
        for memory in minibatch:
            # Get stored values.
            old_state_m, action_m, reward_m, new_state_m = memory
            # Get prediction on old state.
            old_qval = self.model.predict(old_state_m, batch_size=1)
            # Get prediction on new state.
            newQ = self.model.predict(new_state_m, batch_size=1)
            # Get our best move. I think?
            maxQ = np.max(newQ)
            y = np.zeros((1, 3))
            y[:] = old_qval[:]

            update = (reward_m + (self.gamma * maxQ))
    
            # Update the value for the action we took.
            y[0][action_m] = update
            X_train.append(old_state_m.reshape(self.num_sensors,))
            y_train.append(y.reshape(3,))
    
        X_train = np.array(X_train)
        y_train = np.array(y_train)
    
        return X_train, y_train

    def reset_network(self):
        self.curr_time = 0
        return
    
    def save_weights(self, filename):
        return
    
    def update_weights(self):
        if self.curr_time < self.num_init_cycles:
            return

        # If we've stored enough in our buffer, pop the oldest.
        if len(self.replay) > self.buffer:
            self.replay.pop(0)

        # Randomly sample our experience replay memory
        minibatch = random.sample(self.replay, self.batch_size)

        # Get training values.
        X_train, y_train = self.process_minibatch(minibatch)

        self.model.fit(
            X_train, y_train, batch_size=self.batch_size,
            nb_epoch=1, verbose=0
        )
    
    def choose_action(self, state):
        # Choose an action.
        if random.random() < self.epsilon or \
                self.curr_time < self.num_init_cycles:
            self.action = np.random.randint(0, self.num_commands)  # random
        else:
            # Get Q values for each action.
            qval = self.model.predict(self.state, batch_size=1)
            self.action = (np.argmax(qval))  # best
        
        # Decrement epsilon over time.
        if self.epsilon > 0.01 and self.curr_time > self.num_init_cycles:
            self.epsilon *= 0.95
        
        self.state = state
        
        return self.action
    
    def report_action(self, reward, new_state):
        # Experience replay storage.
        self.replay.append((self.state, self.action, reward, new_state))
 

'''
init

while():
    get frame
    process frame
    
    define reward
    
    process result of the previous action
    update weights
    
    choose new action
    
    
# Connect to the transmitter
ser = serial.Serial('COM9', 9600)

# Connect to a webcam
cam = cv2.VideoCapture(0)
if (cam.isOpened() == False):
    print("Error opening video stream or file")

# Create a NN
network = DeepRLNetwork()
network.init_network
reward = 0

state = CREATE A NEW STATE()

# Process video
for curr_time in range(max_time):
    // MAKE ACTION BASED ON PREVIOUS SOLUTION
    action = network.choose_action(state)
    
    command = make_decision(rodeo_circles, obstacle_circles)

    # A temporary thing for flexible speed
    
    if command == 'w':
        command = 1
    elif command == 'c':
        command = 0
    elif command == 's':
        command = 2
    elif command == 'a':
        command = 3
    elif command == 'd':
        command = 6

    send_decision(ser, command)
    
    // LOOK AT THE RESULT
    
    if not cam.isOpened():
        print("Camera is not opened")
        break
        
    ret, rodeo_circles, obstacle_circles = \
        process_frame(cam, min_perimeter=min_perimeter)
    
    if ret:
        break  
    
    new_state, reward = SOMEHOW_CREATE_A_STATE()
    network.report_action(reward, new_state)
    network.update_weights()
    
    state = new_state
    
cam.release()
cv2.destroyAllWindows()
'''
