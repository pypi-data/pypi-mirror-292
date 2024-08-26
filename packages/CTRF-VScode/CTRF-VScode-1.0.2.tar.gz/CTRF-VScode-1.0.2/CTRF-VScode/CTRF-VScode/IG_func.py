import numpy as np
import random
from basic_functions import *

def info_gain(wine_list1):

    wine = np.asarray(wine_list1)
    [P,Q] = wine.shape
    target = wine[:,-1]
    features = wine[:,0:Q-1]

    nums = [x for x in range(Q-1)]
    random.shuffle(nums)
    
    num = nums[0:int(Q)-1]

    features6 = features.T[num]
    training = np.column_stack((features6.T,target))

    ig = np.zeros((Q-1,int(Q)-1), dtype = float)

    for i in range(int(Q)):
        for j in range(Q-1):
            ig[j-1][i-1] = random.uniform(min(features[:,j-1]),max(features[:,j-1]))

    #ig1 = ig[num]
    #new_size = int(Q/2)-1
    
    new_size = 2
    N1 = 2
    N = 2
    ig1 = ig[:new_size, :N1]

    classes = unique_vals(training, -1)
    classes = list(classes)
    samples = 0
    count = np.zeros(len(classes))
    p = np.zeros(len(classes), dtype = float)

    for i in range(P):
        for j in range(len(classes)):
                if(training[:,0][i]>0):
                    if(training[:,-1][i] == classes[j]):
                        count[j] = count[j]+1
    for j in range(len(classes)):
        p[j] = count[j]/(len(training))

    Entropy_parent=0

    for j in range(len(classes)):
        Entropy_parent -= p[j]*np.log2(p[j])

    #N = int(Q/2)-1
    
    countL = np.zeros((len(classes),N,N1))
    countR = np.zeros((len(classes),N,N1))

    prL = np.zeros((len(classes),N,N1))
    prR = np.zeros((len(classes),N,N1))

    left_count = np.zeros((N,N1), dtype = float)
    right_count = np.zeros((N,N1), dtype = float)
    WL = np.zeros((N,N1), dtype = float)
    WR = np.zeros((N,N1), dtype = float)

    Entropy_right = np.zeros((N,N1), dtype = float)
    Entropy_left = np.zeros((N,N1), dtype = float)

    IG = np.zeros((N,N1), dtype = float)

    for c in range(len(classes)):
        for x in range(P):
            for i in range(N):
                 for j in range(N1):
                    if(training[:,i][x]>ig1[i][j]):
                        if(training[:,-1][x] == classes[c]):
                            countL[c][i][j] = countL[c][i][j]+1
                    else:
                        if(training[:,-1][x] == classes[c]):
                            countR[c][i][j] = countR[c][i][j]+1

    for c in range(len(classes)):
        left_count += countL[c]
        right_count += countR[c]

    eps = 10**-9

    for c in range(len(classes)):
        for i in range(N):
            for j in range(N1):

                prL[c][i][j] = (countL[c][i][j]+eps)/(left_count[i][j])

                WL[i][j] = (left_count[i][j])/(P)

                Entropy_left[i][j] -= prL[c][i][j]*np.log2(prL[c][i][j])

    for c in range(len(classes)):
        for i in range(N):
            for j in range(N1):

                prR[c][i][j] = (countR[c][i][j]+eps)/(right_count[i][j])

                WL[i][j] = (right_count[i][j])/(P)

                Entropy_right[i][j] -= prR[c][i][j]*np.log2(prR[c][i][j])

    IG = Entropy_parent - WL*Entropy_left - WR*Entropy_right

    IG_max = np.amax(IG)

    for i in range(N):
        for j in range(N1):
            if (IG_max == IG[i][j]):
                [f, g] = [i, j]
            else:
                f = 0
                g = 0

    [feature, max_value] = [num[f], ig1[f,g]]

    return [feature, max_value]

def node(wine_list1):
    left = []
    right = []

    wine = np.asarray(wine_list1)
    [P,Q] = wine.shape
    [max_feature, max_value] = info_gain(wine_list1)

    for i in range(P):
                if(wine[:,max_feature][i]>max_value):

                    left.append(wine[i])
                else:

                    right.append(wine[i])

    return left,right,max_feature, max_value

