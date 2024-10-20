import csv
import numpy as np

with open('tournaments.csv', newline='') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    avgs = {}
    wins = {}
    stdevs = {}
    for x in range(1,11):
        wins[x] = {'NS': {1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0},
            'EW': {1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0}}
        avgs[x] = {'NS': {1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0},
            'EW': {1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0}}
        stdevs[x] = {'NS': {1:[],2:[],3:[],4:[],5:[],6:[],7:[],8:[],9:[],10:[]},
            'EW': {1:[],2:[],3:[],4:[],5:[],6:[],7:[],8:[],9:[],10:[]}}
    next(csvreader)


    for row in csvreader:
        values  = row[0].split(",")
        avgs[int(values[0])]['NS'][int(values[1])] += int(values[2])
        avgs[int(values[1])]['EW'][int(values[0])] += int(values[3])
        stdevs[int(values[0])]['NS'][int(values[1])].append(int(values[2]))
        stdevs[int(values[1])]['EW'][int(values[0])].append(int(values[3]))
        if int(values[2]) > int(values[3]):
            wins[int(values[0])]['NS'][int(values[1])] += 1
        else:
            wins[int(values[1])]['EW'][int(values[0])] += 1
    
    minimum = 156
    maximum = 0
    for x in range(1,11):
        if min(stdevs[3]['NS'][x]) < minimum:
            minimum = min(stdevs[3]['NS'][x])
        if min(stdevs[3]['EW'][x]) < minimum:
            minimum = min(stdevs[3]['EW'][x])
        if max(stdevs[3]['NS'][x]) > maximum:
            maximum = max(stdevs[3]['NS'][x])
        if max(stdevs[3]['EW'][x]) > maximum:
            maximum = max(stdevs[3]['EW'][x])
    print("Minimum Score for Group 3: " + str(minimum))
    print("Maximum Score for Group 3: " + str(maximum))
    
    print("\n")
    print("Wins: ")
    for key, value in wins.items():
        total_wins = 0
        for x in range(1,11):
            total_wins += wins[key]['NS'][x]
            total_wins += wins[key]['EW'][x]
        print("Total wins for player "+str(key)+": "+str(total_wins))
        print(key, value)

    print("\n")
    print("Averages: ")
    for key, value in avgs.items():
        overall_average = 0
        for x in range(1,11):
            overall_average += avgs[key]["NS"][x]
            overall_average += avgs[key]["EW"][x]
            avgs[key]["NS"][x] = float(avgs[key]["NS"][x]/1000)
            avgs[key]["EW"][x] = float(avgs[key]["EW"][x]/1000)
        print("Overall average for player "+str(key)+": "+str(float(overall_average/20000)))
        print(key, value)
    
    print("\n")
    print("Standard Deviations: ")
    for key, value in stdevs.items():
        all_outcomes = []
        for x in range(1,11):
            all_outcomes = all_outcomes + stdevs[key]["NS"][x]
            all_outcomes = all_outcomes + stdevs[key]["EW"][x]
            stdevs[key]["NS"][x] = round(np.std(stdevs[key]["NS"][x]),3)
            stdevs[key]["EW"][x] = round(np.std(stdevs[key]["EW"][x]), 3)
        print("STD of all trials for player "+str(key)+": "+str(round(np.std(all_outcomes),3)))
        print(key, value)

# We perform badly as NS on Seed 350 (achieved minimum score here)
# We tend to perform slightly better overall as EW -- N's played card is factored into the seed we choose
# 5th in terms of total wins and overall average score
# Bottom 3 in STD (2, 7, 10) are within bottom 4 for overall average score
