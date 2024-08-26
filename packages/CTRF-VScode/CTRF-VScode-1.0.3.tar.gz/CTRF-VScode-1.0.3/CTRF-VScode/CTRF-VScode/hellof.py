import matplotlib.pyplot as plt
import numpy as np
import random
import math
import pandas
import timeit
import re
import scipy
import itertools
from sklearn.model_selection import StratifiedKFold
from gmm_mml import GmmMml
from sklearn import datasets
import pickle
import copy
from pyeda.inter import *
#from graphviz import Source 
from pyeda.boolalg.expr import exprvar
from basic_functions import *
from IG_func import *
from bds import *
from obds import *
from eobds import *

Terms = 8
trees = 100
n_class = 2

def tree_table(wine_list1, sublist_size):

    data[0],data[1],max_feature[0], max_value[0] = node(wine_list1)

    tree_node = []
    tree = []
 ############################################### MIN LEAF #####################################
    Minleaf = sublist_size*0.4
    for i in range(buff2):
        if (len(data[i])>Minleaf):
            data[2*i+2],data[2*i+3],max_feature[i+1], max_value[i+1] = node(data[i])

    tree_node.append(wine_list1)

    for i in range(buff2):
            tree_node.append(data[i])
            tree.append(i)

    for i in range(buff2):
            dict  =  class_counts(tree_node[i])
            node_classes[i]  = [ v for v in dict.items() ]

            if(i%2 == 1):
                parent[i] = int((i-1)/2)
            else:
                parent[i] = int((i-2)/2)
    #       if(i<400):
            if(max_value[i]):
                    left_child[i] = int(2*i+1)
                    right_child[i] = int(2*i+2)

    tree1 = []
    tree2 = []
    for i in range(buff2):
        if(node_classes[i] and len(tree_node[i])>Minleaf):
            tree1.append(i)
        if(node_classes[i]):
            tree2.append(i)

    tree1 = tree2

    parent1 = [ [] for i in range(len(tree1)) ]

    for i in range(len(tree1)):
            if(tree1[i]%2 == 1):
                parent1[i] = int((tree1[i]-1)/2)
            else:
                parent1[i] = int((tree1[i]-2)/2)

    left_child1 = [ [] for i in range(len(tree1)) ]
    right_child1 = [ [] for i in range(len(tree1)) ]

    for i in range(len(tree1)):
        if(max_value[tree1[i]]):
                    left_child1[i] = int(2*tree1[i]+1)
                    right_child1[i] = int(2*tree1[i]+2)

    parent2 = [ [] for i in range(len(tree1)) ]

    for i in range(len(tree1)):
        for j in range(len(tree1)):
            if(tree1[i] == parent1[j]):
                parent2[j] = i
            elif(parent1[j] == -1):
                parent2[j] = -1
    left_child2 = [ [] for i in range(len(tree1)) ]
    right_child2 = [ [] for i in range(len(tree1)) ]

    for i in range(len(tree1)):
        for j in range(len(tree1)):
            if(tree1[i] == left_child1[j]):
                left_child2[j] = i
            if(tree1[i] == right_child1[j]):
                right_child2[j] = i

    max_feature2 = [ [] for i in range(len(tree1)) ]
    max_value2 = [ [] for i in range(len(tree1)) ]
    node_classes2 = [ [] for i in range(len(tree1)) ]

    for x in range(0,len(tree1)):
        max_feature2[x] = max_feature[tree1[x]]
        max_value2[x] = max_value[tree1[x]]
        node_classes2[x] = node_classes[tree1[x]]
    node_probs = node_classes2

    class_probs = []

    for n in range(len(tree1)):
        theSum = 0
        prob = []
        cls = []
        for c in range(len(node_classes2[n])):
            theSum = theSum + node_classes2[n][c][1]
        for c in range(len(node_classes2[n])):
            prob.append(node_classes2[n][c][1]/theSum)
            cls.append(node_classes2[n][c][0])
    #  if(not(max_value[n])):
        class_probs.append([prob,cls])

    #  wine_test_list = wine_list

    node_max_class = []

    n1 = -1
    for n in range(len(tree1)):
        for c in range(len(node_classes2[n])):
            if(class_probs[n][0][c] == max(class_probs[n][0])):
                if( n1 != n ):
                    node_max_class.append(class_probs[n][1][c])
                n1 = n

    return [tree1,parent2,left_child2,right_child2,max_feature2,max_value2,node_classes2,node_max_class,class_probs]


k=5
skf = StratifiedKFold(n_splits=k, shuffle = True)
df = pandas.read_csv('TrainingFiles/sonar.csv')

# print(df) /content/drive/MyDrive/KLIV CON - June 2022/L5featurespneumonia.csv
list_df = df.values.tolist()
pima = np.asarray(list_df)
[P,Q] = pima.shape
target = pima[:,-1]
pfeatures = pima[:,0:Q-1]

times = 1
for f in range(times):
    k_count = 0
    for train_index, test_index in skf.split(pfeatures, target):
        k_count = k_count + 1
        X_train, X_test = pfeatures[train_index], pfeatures[test_index]
        y_train, y_test = target[train_index], target[test_index]

        wine= np.column_stack((X_train,y_train))
        wine_list= wine.tolist()

        wine_test= np.column_stack((X_test,y_test))
        wine_test_list= wine_test.tolist()
        winetest = np.asarray(wine_test_list)

        num_sublists = trees
        sublist_size = int(P*0.9)

        sublists = []
        for i in range(num_sublists):
            sublist = random.choices(wine_list, k=sublist_size)
            sublists.append(sublist)
        dic = class_counts(wine)
        dic1 = class_counts(winetest)
    #     print(dic)
    #     print(dic1)

        start = timeit.default_timer()

        dt = []
        mt = []
        bf = []
        
        for i in range(trees):

            #[max_feature, max_value] = info_gain(wine_list)

            buff = 300000
            buff2 = 150000

            data = [ [] for i in range(buff) ]
            max_feature = [ [] for i in range(buff2) ]
            max_value = [ [] for i in range(buff2) ]
            node_classes = [ [] for i in range(buff2) ]
            parent = [ [] for i in range(buff2) ]
            left_child = [ [] for i in range(buff2) ]
            right_child = [ [] for i in range(buff2) ]

            [tree,parent,left_child,right_child,max_feature,max_value,node_classes,node_max_class,class_probs] = tree_table(sublists[i], sublist_size)

    # table = PrettyTable(['S.N.','#node','Parent','Left_child','Right_child','Atrribute','Atribute_value','Class_distribution'])
    # for x in range(0,len(tree)):
    # table.add_row([x,tree[x],parent[x],left_child[x],right_child[x],max_feature[x],max_value[x],node_classes[x]])
    # print(table)

            dt.append([tree,parent,left_child,right_child,max_feature,max_value,node_classes,node_max_class,class_probs])
    # Save the result to a file
        if(k_count == 1):
          with open('Output/dt1.pickle', 'wb') as file:
              pickle.dump(dt, file)
          with open('Output/test1.pickle', 'wb') as file:
              pickle.dump(winetest, file)
          with open('Output/train1.pickle', 'wb') as file:
              pickle.dump(wine, file)
        elif(k_count == 2):
          with open('Output/dt2.pickle', 'wb') as file:
              pickle.dump(dt, file)
          with open('Output/test2.pickle', 'wb') as file:
              pickle.dump(winetest, file)
          with open('Output/train2.pickle', 'wb') as file:
              pickle.dump(wine, file)
        elif(k_count == 3):
          with open('Output/dt3.pickle', 'wb') as file:
              pickle.dump(dt, file)
          with open('Output/test3.pickle', 'wb') as file:
              pickle.dump(winetest, file)
          with open('Output/train3.pickle', 'wb') as file:
              pickle.dump(wine, file)
        elif(k_count == 4):
          with open('Output/dt4.pickle', 'wb') as file:
              pickle.dump(dt, file)
          with open('Output/test4.pickle', 'wb') as file:
              pickle.dump(winetest, file)
          with open('Output/train4.pickle', 'wb') as file:
              pickle.dump(wine, file)
        else:
          with open('Output/dt5.pickle', 'wb') as file:
              pickle.dump(dt, file)
          with open('Output/test5.pickle', 'wb') as file:
              pickle.dump(winetest, file)
          with open('Output/train5.pickle', 'wb') as file:
              pickle.dump(wine, file)

#bf5 = []
#for d in range(50):
#    [MinT, MinF, MinV, T] = minterm_now(dt[d][0],dt[d][4],dt[d][5],dt[d][7],2)
#    bf5.append([MinT[0],MinF[0],MinV[0],T[0],MinT[1],MinF[1],MinV[1],T[1]])
              
with open('Output/dt1.pickle', 'rb') as file:
    dt = pickle.load(file)
bf5 = []
for d in range(trees):
    [MinT, MinF, MinV, T] = minterm_now(dt[d][0],dt[d][4],dt[d][5],dt[d][7],n_class)
    #bf5.append([MinT[0],MinF[0],MinV[0],T[0],MinT[1],MinF[1],MinV[1],T[1]])
    list_length = len(MinT)
    # Iterate over the indices of the lists
    sublist = []
    for j in range(list_length):
        sublist.extend([MinT[j], MinF[j], MinV[j], T[j]])
    bf5.append(sublist)

bf = copy.deepcopy(bf5)
with open('Output/bf1.pickle', 'wb') as file:
        pickle.dump(bf, file)

var_ob1 = 0
remove_f1 = []
remove_v1 = []

while True:
    # code block to be executed
    mt= obdt4(dt,bf,pfeatures)
    [bf, cut_tree, remove_f1, remove_v1] = obdt5(mt, 1, Terms,remove_f1,remove_v1)
    unique_list_tree = list(set(remove_consecutive_duplicates(cut_tree)))
    var_ob1 = var_ob1+len(unique_list_tree)
    if len(unique_list_tree) == 0:
        break
with open('Output/eo1.pickle', 'wb') as file:
        pickle.dump(mt, file)

with open('Output/dt2.pickle', 'rb') as file:
    dt = pickle.load(file)
bf5 = []
for d in range(trees):
    [MinT, MinF, MinV, T] = minterm_now(dt[d][0],dt[d][4],dt[d][5],dt[d][7],n_class)
    #bf5.append([MinT[0],MinF[0],MinV[0],T[0],MinT[1],MinF[1],MinV[1],T[1],MinT[2],MinF[2],MinV[2],T[2]])
    list_length = len(MinT)
    # Iterate over the indices of the lists
   
    sublist = []
    for j in range(list_length):
        sublist.extend([MinT[j], MinF[j], MinV[j], T[j]])
    bf5.append(sublist)
bf = copy.deepcopy(bf5)
with open('Output/bf2.pickle', 'wb') as file:
        pickle.dump(bf, file)

var_ob2 = 0
remove_f2 = []
remove_v2 = []

while True:
    # code block to be executed
    mt= obdt4(dt,bf,pfeatures)
    [bf, cut_tree, remove_f2, remove_v2] = obdt5(mt, 1, Terms,remove_f2,remove_v2)
    unique_list_tree = list(set(remove_consecutive_duplicates(cut_tree)))
    var_ob2 = var_ob2+len(unique_list_tree)
    if len(unique_list_tree) == 0:
        break
with open('Output/eo2.pickle', 'wb') as file:
        pickle.dump(mt, file)

with open('Output/dt3.pickle', 'rb') as file:
    dt = pickle.load(file)
bf5 = []
for d in range(trees):
    [MinT, MinF, MinV, T] = minterm_now(dt[d][0],dt[d][4],dt[d][5],dt[d][7],n_class)
    #bf5.append([MinT[0],MinF[0],MinV[0],T[0],MinT[1],MinF[1],MinV[1],T[1],MinT[2],MinF[2],MinV[2],T[2]])
    list_length = len(MinT)
    # Iterate over the indices of the lists
    
    # Inner loop to construct each sublist in the desired format
    sublist = []
    for j in range(list_length):
        sublist.extend([MinT[j], MinF[j], MinV[j], T[j]])
    bf5.append(sublist)
bf = copy.deepcopy(bf5)
with open('Output/bf3.pickle', 'wb') as file:
        pickle.dump(bf, file)

var_ob3 = 0
remove_f3 = []
remove_v3 = []

while True:
    # code block to be executed
    mt= obdt4(dt,bf,pfeatures)
    [bf, cut_tree, remove_f3, remove_v3] = obdt5(mt, 1, Terms,remove_f3,remove_v3)
    unique_list_tree = list(set(remove_consecutive_duplicates(cut_tree)))
    var_ob3 = var_ob3+len(unique_list_tree)
    if len(unique_list_tree) == 0:
        break
with open('Output/eo3.pickle', 'wb') as file:
        pickle.dump(mt, file)

with open('Output/dt4.pickle', 'rb') as file:
    dt = pickle.load(file)
bf5 = []
for d in range(trees):
    [MinT, MinF, MinV, T] = minterm_now(dt[d][0],dt[d][4],dt[d][5],dt[d][7],n_class)
    #bf5.append([MinT[0],MinF[0],MinV[0],T[0],MinT[1],MinF[1],MinV[1],T[1],MinT[2],MinF[2],MinV[2],T[2]])
    list_length = len(MinT)
    # Iterate over the indices of the lists
    
    # Inner loop to construct each sublist in the desired format
    sublist = []
    for j in range(list_length):
        sublist.extend([MinT[j], MinF[j], MinV[j], T[j]])
    bf5.append(sublist)
bf = copy.deepcopy(bf5)
with open('Output/bf4.pickle', 'wb') as file:
        pickle.dump(bf, file)

var_ob4 = 0
remove_f4 = []
remove_v4 = []

while True:
    # code block to be executed
    mt= obdt4(dt,bf,pfeatures)
    [bf, cut_tree, remove_f4, remove_v4] = obdt5(mt, 1, Terms,remove_f4,remove_v4)
    unique_list_tree = list(set(remove_consecutive_duplicates(cut_tree)))
    var_ob4 = var_ob4+len(unique_list_tree)
    if len(unique_list_tree) == 0:
        break
with open('Output/eo4.pickle', 'wb') as file:
        pickle.dump(mt, file)

with open('Output/dt5.pickle', 'rb') as file:
    dt = pickle.load(file)
bf5 = []
for d in range(trees):
    [MinT, MinF, MinV, T] = minterm_now(dt[d][0],dt[d][4],dt[d][5],dt[d][7],n_class)
    #bf5.append([MinT[0],MinF[0],MinV[0],T[0],MinT[1],MinF[1],MinV[1],T[1],MinT[2],MinF[2],MinV[2],T[2]])
    list_length = len(MinT)
    # Iterate over the indices of the lists
   
    # Inner loop to construct each sublist in the desired format
    sublist = []
    for j in range(list_length):
        sublist.extend([MinT[j], MinF[j], MinV[j], T[j]])
    bf5.append(sublist)
bf = copy.deepcopy(bf5)
with open('Output/bf5.pickle', 'wb') as file:
        pickle.dump(bf, file)

var_ob5 = 0
remove_f5 = []
remove_v5 = []

while True:
    # code block to be executed
    mt= obdt4(dt,bf,pfeatures)
    [bf, cut_tree, remove_f5, remove_v5] = obdt5(mt, 1, Terms,remove_f5,remove_v5)
    unique_list_tree = list(set(remove_consecutive_duplicates(cut_tree)))
    var_ob5 = var_ob5+len(unique_list_tree)
    if len(unique_list_tree) == 0:
        break
with open('Output/eo5.pickle', 'wb') as file:
        pickle.dump(mt, file)

print(len(remove_f1),len(remove_f2),len(remove_f3),len(remove_f4),len(remove_f5))
print(count_unique_elements(remove_f1))
print(count_unique_elements(remove_f2))
print(count_unique_elements(remove_f3))
print(count_unique_elements(remove_f4))
print(count_unique_elements(remove_f5))

