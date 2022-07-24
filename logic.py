"""
Simluating a Pandemic using SIR Interactions

"""
import numpy as np
import random
import io
import base64
import matplotlib.pyplot as plt
import time
import copy

class SimData:
    Healthy_Population = 0
    Recovered_Population = 0
    Infected_Population = 0
    Dead_Population = 0
    Generation = 0
    Matrix = []
    Gen_Data = {}

    Array_Length = 4
    Population = 4
    Ani_Speed = 1000
    Disease_name = "----"

    Resistance_mod = 20
    Prob_move = 75
    Prob_init_infected = 50
    Prob_death = 5
    Prob_recovery = 60
    Prob_spread = 40


    colour_map = {0: np.array([0, 0, 0]), # black
        1: np.array([0, 255, 0]), # green
        2: np.array([255, 0, 0]), # red
        3: np.array([0, 0, 255]), # blue
        4: np.array([139,0,139])} # purple


# Create the Matrix to store the simulation
def init_matrix(length):
    matrix_init = [[0 for x in range(length)] for y in range(length)]
    return matrix_init



# Output the Raw Matrix Data for the State of the simulation
def output_matrix(matrix):
    for row in matrix:
        print(row)


# Popualtes the Matrix
def populate_matrix(length, population, matrix):
    pop_curr = 0
    while pop_curr < population:
        x = random.randint(0, length-1)
        y = random.randint(0, length-1)
        if matrix[x][y] == 1 or matrix[x][y] == 2:
            pass
        elif random.randint(0, 100) <= SimData.Prob_init_infected:
            matrix[x][y] = 2
            pop_curr += 1
        else:
            matrix[x][y] = 1
            pop_curr += 1
    return matrix


def count_population():
    SimData.Healthy_Population = 0
    SimData.Infected_Population = 0
    SimData.Dead_Population = 0
    SimData.Recovered_Population = 0

    for y_pos in range(0, SimData.Array_Length):

        for x_pos in range(0, SimData.Array_Length):

            if SimData.Matrix[y_pos][x_pos] == 1:
                SimData.Healthy_Population +=1

            elif SimData.Matrix[y_pos][x_pos] == 2:
                SimData.Infected_Population += 1

            elif SimData.Matrix[y_pos][x_pos] == 3:
                SimData.Recovered_Population += 1

            elif SimData.Matrix[y_pos][x_pos] == 4:
                SimData.Dead_Population += 1
    SimData.Gen_Data["{}".format(SimData.Generation)] = [SimData.Healthy_Population, SimData.Infected_Population, SimData.Dead_Population, SimData.Recovered_Population]
    print("/Population Counted")

# Moves Every Unit of the population
def move_population():

    for y_pos in range(0, SimData.Array_Length):

        for x_pos in range(0, SimData.Array_Length):

            if SimData.Matrix[y_pos][x_pos] != 0 and random.randint(0, 100) <= SimData.Prob_move and SimData.Matrix[y_pos][x_pos] != 4:
                move_x = random.choice([-1, 1, -2, 2])
                move_y = random.choice([-1, 1, -2, 2])
                final_x = x_pos + move_x
                final_y = y_pos + move_y
                if -1 < final_x < SimData.Array_Length and -1 < final_y < SimData.Array_Length and SimData.Matrix[final_y][final_x] == 0:
                    SimData.Matrix[final_y][final_x] = SimData.Matrix[y_pos][x_pos]
                    SimData.Matrix[y_pos][x_pos] = 0

    print("/Population Updated")

def disease_update():
    for y_pos in range(0, SimData.Array_Length):

        for x_pos in range(0, SimData.Array_Length):
            #Handles spread
            if SimData.Matrix[y_pos][x_pos] == 1 or SimData.Matrix[y_pos][x_pos] == 3:
                adjacent_items = []
                for y_check in range(-1, 2):
                    for x_check in range(-1, 2):
                        final_x = x_pos + x_check
                        final_y = y_pos + y_check
                        if -1 < final_x < SimData.Array_Length and -1 < final_y < SimData.Array_Length:
                            adjacent_items.append(str(SimData.Matrix[final_y][final_x]))

                #Spreading to an agent who has not been previously infected
                if SimData.Matrix[y_pos][x_pos] == 1 and random.randint(0, 100) <= SimData.Prob_spread and '2' in adjacent_items:
                    SimData.Matrix[y_pos][x_pos] = 2
                #Spreading to an agent who has been previously infected => some resistance to it
                elif SimData.Matrix[y_pos][x_pos] == 3 and random.randint(0, 100) <= SimData.Prob_spread - SimData.Resistance_mod and '2' in adjacent_items:
                    SimData.Matrix[y_pos][x_pos] = 2


            #Handles Death if infected
            elif random.randint(0, 100) <= SimData.Prob_death and SimData.Matrix[y_pos][x_pos] == 2:
                SimData.Matrix[y_pos][x_pos] = 4

            #Handles recovery if infected
            elif random.randint(0, 100) <= SimData.Prob_recovery and SimData.Matrix[y_pos][x_pos] == 2:
                SimData.Matrix[y_pos][x_pos] = 3



    print("/Disease Spread")


# Runs the Main Function
def main():
    global im
    SimData.Matrix = init_matrix(SimData.Array_Length)
    SimData.Matrix = populate_matrix(SimData.Array_Length, SimData.Population, SimData.Matrix)
    count_population()

    return show_sim()

def update_sim():
    global im
    SimData.Generation += 1
    disease_update()
    move_population()
    count_population()

    return show_sim()

def show_sim():
    fig = plt.figure()
    plt.axis('off')
    fig.patch.set_facecolor('xkcd:slate blue')

    sim_state = copy.deepcopy(SimData.Matrix)
    for y_pos in range(0, SimData.Array_Length):

        for x_pos in range(0, SimData.Array_Length):
            if SimData.Matrix[y_pos][x_pos] == 0:
                sim_state[y_pos][x_pos] = SimData.colour_map[0]
            elif SimData.Matrix[y_pos][x_pos] == 1:
                sim_state[y_pos][x_pos] = SimData.colour_map[1]

            elif SimData.Matrix[y_pos][x_pos] == 2:
                sim_state[y_pos][x_pos] = SimData.colour_map[2]

            elif SimData.Matrix[y_pos][x_pos] == 3:
                sim_state[y_pos][x_pos] = SimData.colour_map[3]

            elif SimData.Matrix[y_pos][x_pos] == 4:
                sim_state[y_pos][x_pos] = SimData.colour_map[4]



    im = plt.imshow(sim_state)
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    plt.close('all')
    return data

def sim_chart():
    fig = plt.figure()
    fig.patch.set_facecolor('xkcd:green teal')

    # Create data
    x=range(0,SimData.Generation + 1)
    y1_dead = []
    y2_healthy = []
    y3_recovered = []
    y4_infected = []

    for key,val in SimData.Gen_Data.items():

        y1_dead.append(round((val[2] / SimData.Population)*100, 2))
        y2_healthy.append(round((val[0] / SimData.Population)*100, 2))
        y3_recovered.append(round((val[3] / SimData.Population)*100, 2))
        y4_infected.append(round((val[1] / SimData.Population)*100, 2))

    # Basic stacked area chart.
    pal = ["#8B008B", "#00ff00", "#0000ff", "#ea433b"]
    plt.stackplot(x,y1_dead, y2_healthy, y3_recovered, y4_infected, labels=['Dead','Healthy','Recovered', 'infected'], colors=pal)
    plt.legend(loc='upper left')
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    plt.close('all')
    return data