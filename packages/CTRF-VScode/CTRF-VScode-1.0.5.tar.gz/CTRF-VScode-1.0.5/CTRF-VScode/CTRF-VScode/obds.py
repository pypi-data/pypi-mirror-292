from gmm_mml import GmmMml
from basic_functions import *
import numpy as np

Terms = 8
trees = 100

def replace_common_with_mean(list1, list2):
    """
    Replaces the common values between list1 and list2 in list1 with the mean value of list2.

    Args:
    - list1: a list of numbers
    - list2: a list of numbers

    Returns:
    - The modified list1 with common values replaced with the mean value of list2.
    """
    common = set(list1).intersection(set(list2))
    mean = sum(list2) / len(list2)
    for i in range(len(list1)):
        if list1[i] in common:
            list1[i] = mean
    return list1

def remove_consecutive_duplicates(lst):
    new_lst = []
    for i, element in enumerate(lst):
        if i == 0 or element != lst[i-1]:
            new_lst.append(element)
    return new_lst

def obdt4(dt,bf,pfeatures):
    unsupervised=GmmMml(plots=True)
    cluster = [[] for i in range(len(pfeatures.T))]
    for d in range(trees):
        for n in range(len(dt[d][0])):
            if(dt[d][5][n]):
                for f in range(len(pfeatures.T)):
                    if(dt[d][4][n]==f):
                        cluster[dt[d][4][n]].append(dt[d][5][n])

    samples = []
    samples_index = []
    samples_cluster = []
    samples_cluster_mean = []
    for f in range(len(pfeatures.T)):
        #Creating histogram
        #fig, ax = plt.subplots(figsize =(10, 7))
        #ax.hist(cluster[f], bins = 10)
        b = np.array(cluster[f])
        arr = b.reshape(len(cluster[f]),1)
        samples.append(arr)
        unsupervised=unsupervised.fit(arr)
        mixture = unsupervised.predict(arr)
        samples_index.append(mixture)
        comp = unique(mixture)
        sum_p = [ [] for i in range(len(comp)) ]
        for d in range(len(arr)):
            for l in range(len(comp)):
                if(comp[l] == mixture[d]):
                    sum_p[l].append(arr[d])
        samples_cluster.append(sum_p)
        mean_p = []
        for d in range(len(comp)):
            mean_p.append(np.average(sum_p[d]))
        samples_cluster_mean.append(mean_p)

    cluster_lists = [ [] for i in range(len(samples_cluster)) ]
    for i in range(len(samples_cluster)):
        for array in samples_cluster[i]:
            new_list = []
            for item in array:
                new_list.append(item[0])
            cluster_lists[i].append(new_list)

    for t in range(trees):
        for cc in range(0,Terms,4):
            #print(bf[t][cc+1])
            #print(bf[t][cc+2])
            f_repeat = []
            for d in range(len(bf[t][cc+1])):
                #print(Repeat(bf[t][cc+1][d]))
                #print(t)
                f_repeat = Repeat(bf[t][cc+1][d])
                if(len(Repeat(bf[t][cc+1][d]))>0):
                    #print(bf[t][cc+1][d])
                    #print(Repeat(bf[t][cc+1][d]))
                    #print(bf[t][cc+2][d])
                    #print(f_repeat[0])
                    #print(cluster_lists[f_repeat[0]])

                    #for i in range(len(cluster_lists)):
                    common_elements = replace_common_with_mean(bf[t][cc+2][d], cluster_lists[f_repeat[0]][0])
                        #new_list = replace_common_with_mean(list1, list2)
                        #if (common_elements == bf[t][cc+2][d]):
                        #  print('No change')
                        #else:
                        #  print(t)
                    #print(common_elements)
                        #print(t)
                #print(len(bf[t][cc+1]))
                #print(cc)
    return bf

def obdt5(bf, var,Terms,remove_f,remove_v):
      cut_tree = []
      for d in range(len(bf)):
        for cc in range(0, Terms, 4):
            if(bf[d][cc]!=[]):
                  for x in range(len(bf[d][cc+2])):
                    duplicates = set()
                    removed_indices = []
                    for i, value in enumerate(bf[d][cc+2][x]):
                        if value in duplicates:
                            removed_indices.append(i)
                        else:
                            duplicates.add(value)
                    unique_list = list(duplicates)
                    if(len(removed_indices)>0):
                      cut_tree.append(d)
                      #print(d)
                      #if (not(d == d+1)):

                    #print(removed_indices)
                    #print(d)
                    #if(len(cut_tree)<var):
                    for i in sorted(removed_indices, reverse=True):
                        remove_f.append(bf[d][cc+1][x][i])
                        remove_v.append(bf[d][cc+2][x][i])
                        del bf[d][cc][x][i+1]
                        del bf[d][cc+1][x][i]
                        del bf[d][cc+2][x][i]
      return bf, cut_tree, remove_f, remove_v
