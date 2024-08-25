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

trees = 100
Terms = 8
#Tree_no = 1
n_class = 2

# Load the saved result from the file
with open('Output/dt5.pickle', 'rb') as file:
    dt = pickle.load(file)
# Load the saved result from the file
with open('Output/test5.pickle', 'rb') as file:
    winetest = pickle.load(file)
with open('Output/bf5.pickle', 'rb') as file:
    bf = pickle.load(file)
with open('Output/eo5.pickle', 'rb') as file:
    mt = pickle.load(file)

pima = np.asarray(winetest)
[P,Q] = pima.shape
target = pima[:,-1]
pfeatures = pima[:,0:Q-1]

def dt_predict(dt, winetest):
    arg_dt = []
    arg_dtp = []
    correct = 0
    acc1 = 0
    #winetest = wine1
    for t in range(len(winetest)):
        post = []
        for d in range(trees):
            for n in range(len(dt[d][0])):
                if(dt[d][5][n]):
                    if(winetest[t][dt[d][4][n]]>dt[d][5][n]):
                        if(dt[d][2][n]):
                            if(not(dt[d][5][dt[d][2][n]])):
                                temp = dt[d][2][n]
                                post.append(dt[d][8][temp])
                                break
                    else:
                        if(dt[d][3][n]):
                            if(not(dt[d][5][dt[d][3][n]])):
                                temp = dt[d][3][n]
                                post.append(dt[d][8][temp])
                                break
        
        dic = class_counts(winetest)
        labels = list(dic.keys())
        labels.sort()

        sum_p = [ [] for i in range(len(labels)) ]
        leaf_p = []
        leaf_c = []
        for n in range(len(post)):
            leaf_p.append(post[n][0])
            leaf_c.append(post[n][1])

        for p in range(len(post)):
            for q in range(len(leaf_c[p])):
                for r in range(len(labels)):
                    if(labels[r] == leaf_c[p][q]):
                        sum_p[r].append(leaf_p[p][q])
        #print(sum(sum_p[0])/50,sum(sum_p[1])/50,sum(sum_p[2])/50,sum(sum_p[3])/50,sum(sum_p[4])/50)
        #print(sum(sum_p[0])/50+sum(sum_p[1])/50+sum(sum_p[2])/50+sum(sum_p[3])/50+sum(sum_p[4])/50)
        max_class = []
        for l in range(len(labels)):
            max_class.append(sum(sum_p[l])/trees)
        #print(max_class)
        arg_max = np.argmax(max_class)
        #print(max_class[arg_max])

        #print(winetest[t])
        arg_dt.append(arg_max)
        arg_dtp.append(max_class[arg_max])
        del sum_p,leaf_p,leaf_c,post

    #   for t in range(len(winetest)):
        if(int(winetest[t][-1]) == arg_dt[t]):
    #         print(int(winetest[t][-1]),arg[t])
            correct = correct+1
    #         print(correct)
    #     else:
    #         print(int(winetest[t][-1]),arg[t])
    #     stop_test = timeit.default_timer()

    acc1 = correct/len(winetest)
    print('-------------------------------------------')
    print('RF:',acc1)
    print('-------------------------------------------')
    return acc1, arg_dt
def dtv_predict(dt, winetest):
    arg_dt1 = []
    correct = 0
    acc2 =0
    #winetest = wine1
    for t in range(len(winetest)):
        post = []
        for d in range(trees):
    #             start_test = timeit.default_timer()
            for n in range(len(dt[d][0])):
                if(dt[d][5][n]):
                    if(winetest[t][dt[d][4][n]]>dt[d][5][n]):
                        if(dt[d][2][n]):
                            if(not(dt[d][5][dt[d][2][n]])):
                                temp = dt[d][2][n]
                                post.append(dt[d][8][temp])
                                break
                    else:
                        if(dt[d][3][n]):
                            if(not(dt[d][5][dt[d][3][n]])):
                                temp = dt[d][3][n]
                                post.append(dt[d][8][temp])
                                break
        start_test = timeit.default_timer()
        dic = class_counts(winetest)
        labels = list(dic.keys())
        labels.sort()

        sum_p = [ [] for i in range(len(labels)) ]
        leaf_p = []
        leaf_c = []
        for n in range(len(post)):
            leaf_p.append(post[n][0])
            leaf_c.append(post[n][1])

        for p in range(len(post)):
            for q in range(len(leaf_c[p])):
                for r in range(len(labels)):
                    if(labels[r] == leaf_c[p][q]):
                        sum_p[r].append(leaf_p[p][q])
        #print(sum_p)
        #break
        #print(sum(sum_p[0])/50,sum(sum_p[1])/50,sum(sum_p[2])/50,sum(sum_p[3])/50,sum(sum_p[4])/50)
        #print(sum(sum_p[0])/50+sum(sum_p[1])/50+sum(sum_p[2])/50+sum(sum_p[3])/50+sum(sum_p[4])/50)
        max_class = []
        for l in range(len(labels)):
            max_class.append(sum(sum_p[l])/trees)
        #print(max_class)
        arg_max = np.argmax(max_class)
        #print(arg_max)
        vote = []
        for d in range(len(post)):
            class_max_index = np.argmax(post[d][0])
            #print(class_max_index)
            vote.append(class_max_index)

        find_max_class = []
        for d in range(len(post)):
        #print(post[d][1][vote[d]])
            find_max_class.append(post[d][1][vote[d]])

        #most_frequent(find_max_class)
        #print(winetest[t])
        arg_dt1.append(most_frequent(find_max_class))
        del sum_p,leaf_p,leaf_c,post

    #   for t in range(len(winetest)):
        if(int(winetest[t][-1]) == arg_dt1[t]):
    #         print(int(winetest[t][-1]),arg[t])
            correct = correct+1
        #stop_test = timeit.default_timer()
        #avg_test_time = avg_test_time + (stop_test - start_test)

    #         print(correct)
    #     else:
    #         print(int(winetest[t][-1]),arg[t])
    #     stop_test = timeit.default_timer()

    acc2 = correct/len(winetest)
    print('-------------------------------------------')
    print('RF-V:',acc2)
    #print('Table Time: ', avg_test_time)
    print('-------------------------------------------')
    return acc2, arg_dt1

def has_empty_lists(list_of_lists):
    for sublist in list_of_lists:
        if isinstance(sublist, list) and len(sublist) == 0:
            return True
    return False

def bds_predict(dt,bf, winetest):
    correct = 0
    arg2 = []
    #winetest = wine1
    for v in range(len(winetest)):
      count_list = []
      count1 = 0
      count2 = 0
      count3 = 0
      count4 = 0
      count5 = 0
      count6 = 0
      count7 = 0
      count8 = 0
      count99 = 0
      count100 = 0
      count111 = 0
      count122 = 0
      #num_literals1 = 0
      #num_literals2 = 0
      class1_f = []
      class2_f = []
      class1_fm = []
      class2_fm = []
      var1 = []
      var2 = []
      for cc in range(0, Terms, 4):
        count = 0
        for d in range(0,trees-1,1):
          #result = has_empty_lists(bf[d])
          #if(result == False):
            my_list = bf[d][cc]
          
            my_list1 = dt[d][4]
            #print(my_list1)
            my_list2 = dt[d][5]
            my_list3 = dt[d][0]
            #my_list4 = [-0.00092,  0.01001]

            list1 = my_list1
            list2 = winetest[v][0:Q-1]

            # Find the indices in list1 that correspond to indices in list2
            indices1 = [i for i, x in enumerate(list1) if isinstance(x, int) and x < len(list2)]

            # Create a new list with the values from list2 based on the indices in list1
            new_list = [list2[list1[i]] if i in indices1 else x for i, x in enumerate(list1)]

            indices = []

            for i in range(len(my_list1)):
                if not isinstance(my_list1[i], list) or my_list1[i]:
                    indices.append(i)
            list_f = [my_list1[i] for i in indices]
            list_v = [my_list2[i] for i in indices]
            list_n = [my_list3[i] for i in indices]
            list_r = [new_list[i] for i in indices]
            #print(list_f)
            #print(list_v)
            #print(list_n)
            #print(list_r)
            bool_list = [x > y for x, y in zip(list_v, list_r)]
            #print(bool_list)

            # Example usage
            #num = len(list_v)
            #alphabets_str = get_alphabets_str(num)
            #print(alphabets_str) # Output: 'abcde'

            #alphabet_list = list(alphabets_str)
            #alphabet_with_commas = ",".join(alphabet_list)
            #print(alphabet_with_commas)

            #alphabet_with_commas = map(exprvar, alphabets_str)

            #if(mt[d][cc] != []):
            #  my_list = mt[d][cc]

            num = len(list_v)
            variable_names = ['x[{}]'.format(i) for i in range(num)]
            alphabet_with_commas = ",".join(variable_names)

            alphabet_with_commas = map(exprvar, variable_names)

            reversed_list = []
            for lst in my_list:
                if isinstance(lst, list):
                    reversed_inner_list = lst[::-1]
                    reversed_list.append(reversed_inner_list)

            #print(reversed_list)

            for sub_list in reversed_list:
                for element in sub_list:
                    #print('')
                    pass
            keys   = list_n
            values = variable_names
            my_dict = dict(zip(keys, values))

            list1 = []
            list2 = []
            for my_list in reversed_list:
              for element in my_list:
                for i in range(len(my_list)-1):
                    if my_list[i+1] % 2 == 1: # if next element is odd
                        #print("~" + my_dict[my_list[i]])
                        literal = "~" + my_dict[my_list[i]]
                    else:
                        #print(my_dict[my_list[i]])
                        literal = my_dict[my_list[i]]

                    if i == 0:
                        s = literal
                    else:
                        s += " & " + literal
              list1.append(expr(s)) # convert s to a Boolean expression using expr()
              list2.append(s)

            # Create a Boolean expression by taking the OR of all expressions in list1
            f1 = Or(*list1)

            # define the input expression as a string
            expression = repr(f1)

            # use regular expressions to extract the And clauses
            and_clauses = re.findall("And\((.*?)\)", expression)

            # split each And clause into a list of its components
            and_lists = [clause.split(", ") for clause in and_clauses]

            # print the resulting list of lists
            #print(and_lists)
            #print(list2)

            lst = list2
            new_lst1 = []
            for s in lst:
                literals = [literal.strip() for literal in s.split('&')]
                new_lst1.append(literals)

            #print(new_lst1)

            values = bool_list
            variable_names = variable_names
            variable_dict = dict(zip(variable_names, values))

            #print(variable_dict)

            expression = new_lst1
            variable_values = variable_dict
            result = evaluate_boolean_function(expression, variable_values)
            #print(result)
            #print(new_lst1)

            expression = and_lists
            variable_values = variable_dict
            result = evaluate_boolean_function(expression, variable_values)
            if(result == True):
              count = count+1
            #print(result)
            #print(and_lists)
            #print('------')
            #for clause in f1.cover:
            #   num_literals1 += len(clause)
            #for clause in fm.cover:
            #    num_literals2 += len(clause)
            f1 = f1.to_binary()
            #fm = fm.to_binary()

            #count1 =count1 + f1.size
            
            #count3 =count3 + f1.depth
            
            #count5 =count5 + f1.cardinality
            
            #count7 =count7 + len(f1.inputs)
            
            count99 =count99 + len(re.findall(r"\bAnd\b", str(f1)))
            
            count111 = count111 + len(re.findall(r"\bOr\b", str(f1)))
              
          #else:
          #  d = d+1
        count_list.append(count)
        #print(count)

      max_index = count_list.index(max(count_list))
      #print(max_index)

      if(max_index == int(winetest[v][-1])):
        correct = correct+1
      arg2.append(max_index)
    #print(correct)
    print('-------------------------------------------')
    print('BDS:',correct/len(winetest))
    acc3 = correct/len(winetest)
    #print(f1)
    #print(len(re.findall(r"\bAnd\b", str(f1))))
    #print(len(re.findall(r"\bOr\b", str(f1))))
    print('-----------------------------')
    return acc3, arg2, count99, count111

def obds_predict(dt,mt,winetest):
    correct = 0
    arg2 = []
    #winetest = wine1
    for v in range(len(winetest)):
      count_list = []
      count1 = 0
      count2 = 0
      count3 = 0
      count4 = 0
      count5 = 0
      count6 = 0
      count7 = 0
      count8 = 0
      count99 = 0
      count100 = 0
      count111 = 0
      count122 = 0
      #num_literals1 = 0
      #num_literals2 = 0
      class1_f = []
      class2_f = []
      class1_fm = []
      class2_fm = []
      var1 = []
      var2 = []
      for cc in range(0, Terms, 4):
        count = 0
        for d in range(0,trees-1,1):
          #result = has_empty_lists(mt[d])
          #if(result == False):
            my_list = mt[d][cc]
            
            my_list1 = dt[d][4]
            my_list2 = dt[d][5]
            my_list3 = dt[d][0]
            #my_list4 = [-0.00092,  0.01001]

            list1 = my_list1
            list2 = winetest[v][0:Q-1]

            # Find the indices in list1 that correspond to indices in list2
            indices1 = [i for i, x in enumerate(list1) if isinstance(x, int) and x < len(list2)]

            # Create a new list with the values from list2 based on the indices in list1
            new_list = [list2[list1[i]] if i in indices1 else x for i, x in enumerate(list1)]

            indices = []

            for i in range(len(my_list1)):
                if not isinstance(my_list1[i], list) or my_list1[i]:
                    indices.append(i)
            list_f = [my_list1[i] for i in indices]
            list_v = [my_list2[i] for i in indices]
            list_n = [my_list3[i] for i in indices]
            list_r = [new_list[i] for i in indices]
            #print(list_f)
            #print(list_v)
            #print(list_n)
            #print(list_r)
            bool_list = [x > y for x, y in zip(list_v, list_r)]
            #print(bool_list)

            # Example usage
            #num = len(list_v)
            #alphabets_str = get_alphabets_str(num)
            #print(alphabets_str) # Output: 'abcde'

            #alphabet_list = list(alphabets_str)
            #alphabet_with_commas = ",".join(alphabet_list)
            #print(alphabet_with_commas)

            #alphabet_with_commas = map(exprvar, alphabets_str)

            #if(mt[d][cc] != []):
            #  my_list = mt[d][cc]

            num = len(list_v)
            variable_names = ['x[{}]'.format(i) for i in range(num)]
            alphabet_with_commas = ",".join(variable_names)

            alphabet_with_commas = map(exprvar, variable_names)

            reversed_list = []
            for lst in my_list:
                if isinstance(lst, list):
                    reversed_inner_list = lst[::-1]
                    reversed_list.append(reversed_inner_list)

            #print(reversed_list)

            for sub_list in reversed_list:
                for element in sub_list:
                    #print('')
                    pass
            keys   = list_n
            values = variable_names
            my_dict = dict(zip(keys, values))

            list1 = []
            list2 = []
            for my_list in reversed_list:
              for element in my_list:
                for i in range(len(my_list)-1):
                    if my_list[i+1] % 2 == 1: # if next element is odd
                        #print("~" + my_dict[my_list[i]])
                        literal = "~" + my_dict[my_list[i]]
                    else:
                        #print(my_dict[my_list[i]])
                        literal = my_dict[my_list[i]]

                    if i == 0:
                        s = literal
                    else:
                        s += " & " + literal
              list1.append(expr(s)) # convert s to a Boolean expression using expr()
              list2.append(s)

            # Create a Boolean expression by taking the OR of all expressions in list1
            f1 = Or(*list1)

            # define the input expression as a string
            expression = repr(f1)

            # use regular expressions to extract the And clauses
            and_clauses = re.findall("And\((.*?)\)", expression)

            # split each And clause into a list of its components
            and_lists = [clause.split(", ") for clause in and_clauses]

            # print the resulting list of lists
            #print(and_lists)
            #print(list2)

            lst = list2
            new_lst1 = []
            for s in lst:
                literals = [literal.strip() for literal in s.split('&')]
                new_lst1.append(literals)

            #print(new_lst1)

            values = bool_list
            variable_names = variable_names
            variable_dict = dict(zip(variable_names, values))

            #print(variable_dict)

            expression = new_lst1
            variable_values = variable_dict
            result = evaluate_boolean_function(expression, variable_values)
            #print(result)
            #print(new_lst1)

            expression = and_lists
            variable_values = variable_dict
            result = evaluate_boolean_function(expression, variable_values)
            if(result == True):
              count = count+1
            #print(result)
            #print(and_lists)
            #print('------')
            #for clause in f1.cover:
            #   num_literals1 += len(clause)
            #for clause in fm.cover:
            #    num_literals2 += len(clause)
            f1 = f1.to_binary()
            #fm = fm.to_binary()

            #count1 =count1 + f1.size
            
            #count3 =count3 + f1.depth
            
            #count5 =count5 + f1.cardinality
            
            #count7 =count7 + len(f1.inputs)
            
            count99 =count99 + len(re.findall(r"\bAnd\b", str(f1)))
            
            count111 = count111 + len(re.findall(r"\bOr\b", str(f1)))
              
          #else:
          #  d = d+1
        count_list.append(count)
        #print(count)

      max_index = count_list.index(max(count_list))
      #print(max_index)

      if(max_index == int(winetest[v][-1])):
        correct = correct+1
      arg2.append(max_index)
    #print(correct)
    print('-------------------------------------------')
    print('OBDS:',correct/len(winetest))
    acc4 = correct/len(winetest)
    #print(f1)
    #print(len(re.findall(r"\bAnd\b", str(f1))))
    #print(len(re.findall(r"\bOr\b", str(f1))))
    print('-----------------------------')
    return acc4, arg2, count99, count111

def eobds_predict(dt,mt,winetest):
    correct = 0
    arg2 = []
    #winetest = wine1
    for v in range(len(winetest)):
      count_list = []
      count1 = 0
      count2 = 0
      count3 = 0
      count4 = 0
      count5 = 0
      count6 = 0
      count7 = 0
      count8 = 0
      count99 = 0
      count100 = 0
      count111 = 0
      count122 = 0
      #num_literals1 = 0
      #num_literals2 = 0
      class1_f = []
      class2_f = []
      class3_f = []
      class1_fm = []
      class2_fm = []
      class3_fm = []
      class_f = [[] for _ in range(n_class)]
      class_fm = [[] for _ in range(n_class)]
      var1 = []
      var2 = []
      for cc in range(0, Terms, 4):
        count = 0
        for d in range(0,trees-1,1):
          #result = has_empty_lists(mt[d])
          #if(result == False):
            my_list = mt[d][cc]
            
            my_list1 = dt[d][4]
            my_list2 = dt[d][5]
            my_list3 = dt[d][0]
            #my_list4 = [-0.00092,  0.01001]

            list1 = my_list1
            list2 = winetest[v][0:Q-1]

            # Find the indices in list1 that correspond to indices in list2
            indices1 = [i for i, x in enumerate(list1) if isinstance(x, int) and x < len(list2)]

            # Create a new list with the values from list2 based on the indices in list1
            new_list = [list2[list1[i]] if i in indices1 else x for i, x in enumerate(list1)]

            indices = []

            for i in range(len(my_list1)):
                if not isinstance(my_list1[i], list) or my_list1[i]:
                    indices.append(i)
            list_f = [my_list1[i] for i in indices]
            list_v = [my_list2[i] for i in indices]
            list_n = [my_list3[i] for i in indices]
            list_r = [new_list[i] for i in indices]
            #print(list_f)
            #print(list_v)
            #print(list_n)
            #print(list_r)
            bool_list = [x > y for x, y in zip(list_v, list_r)]
            #print(bool_list)

            # Example usage
            #num = len(list_v)
            #alphabets_str = get_alphabets_str(num)
            #print(alphabets_str) # Output: 'abcde'

            #alphabet_list = list(alphabets_str)
            #alphabet_with_commas = ",".join(alphabet_list)
            #print(alphabet_with_commas)

            #alphabet_with_commas = map(exprvar, alphabets_str)

            #if(mt[d][cc] != []):
            #  my_list = mt[d][cc]

            num = len(list_v)
            variable_names = ['x[{}]'.format(i) for i in range(num)]
            alphabet_with_commas = ",".join(variable_names)

            alphabet_with_commas = map(exprvar, variable_names)

            reversed_list = []
            for lst in my_list:
                if isinstance(lst, list):
                    reversed_inner_list = lst[::-1]
                    reversed_list.append(reversed_inner_list)

            #print(reversed_list)

            for sub_list in reversed_list:
                for element in sub_list:
                    #print('')
                    pass
            keys   = list_n
            values = variable_names
            my_dict = dict(zip(keys, values))

            list1 = []
            list2 = []
            for my_list in reversed_list:
              for element in my_list:
                for i in range(len(my_list)-1):
                    if my_list[i+1] % 2 == 1: # if next element is odd
                        #print("~" + my_dict[my_list[i]])
                        literal = "~" + my_dict[my_list[i]]
                    else:
                        #print(my_dict[my_list[i]])
                        literal = my_dict[my_list[i]]

                    if i == 0:
                        s = literal
                    else:
                        s += " & " + literal
              list1.append(expr(s)) # convert s to a Boolean expression using expr()
              list2.append(s)

            # Create a Boolean expression by taking the OR of all expressions in list1
            f1 = Or(*list1)

            # Minimize the expression 
            
            #print(f1.size)
            if len(f1.inputs) > 4:
              minimized = espresso_exprs(f1)
            else:
              minimized = [f1]

            #print(minimized)

            for fm in minimized:
                fm.to_dnf
              #print(fm.to_dnf())

            #print(fm)
            #print(fm.inputs)
            #print(f1.inputs)
            #print(fm.equivalent(f1))

            # define the input expression as a string
            expression = repr(fm)

            # use regular expressions to extract the And clauses
            and_clauses = re.findall("And\((.*?)\)", expression)

            # split each And clause into a list of its components
            and_lists = [clause.split(", ") for clause in and_clauses]

            # print the resulting list of lists
            #print(and_lists)
            #print(list2)

            lst = list2
            new_lst1 = []
            for s in lst:
                literals = [literal.strip() for literal in s.split('&')]
                new_lst1.append(literals)

            #print(new_lst1)

            values = bool_list
            variable_names = variable_names
            variable_dict = dict(zip(variable_names, values))

            #print(variable_dict)

            expression = new_lst1
            variable_values = variable_dict
            result = evaluate_boolean_function(expression, variable_values)
            #print(result)
            #print(new_lst1)

            expression = and_lists
            variable_values = variable_dict
            result = evaluate_boolean_function(expression, variable_values)
            if(result == True):
              count = count+1
            #print(result)
            #print(and_lists)
            #print('------')
            #for clause in f1.cover:
            #   num_literals1 += len(clause)
            #for clause in fm.cover:
            #    num_literals2 += len(clause)
            f1 = f1.to_binary()
            fm = fm.to_binary()
            
            count1 =count1 + f1.size
            count2 =count2 + fm.size
            count3 =count3 + f1.depth
            count4 =count4 + fm.depth
            count5 =count5 + f1.cardinality
            count6 =count6 + fm.cardinality
            count7 =count7 + len(f1.inputs)
            count8 =count8 + len(fm.inputs)
            count99 =count99 + len(re.findall(r"\bAnd\b", str(f1)))
            count100 =count100 + len(re.findall(r"\bAnd\b", str(fm)))
            count111 = count111 + len(re.findall(r"\bOr\b", str(f1)))
            count122 = count122 + len(re.findall(r"\bOr\b", str(fm)))
            if (cc == 0):
              class1_f.append(f1)
              class1_fm.append(fm)
            else:
              class2_f.append(f1)
              class2_fm.append(fm)

            for i in range(n_class):
                tr = i*4
                if cc == tr:
                    class_f[i].append(f1)
                    class_fm[i].append(fm)
          #else:
          #  d = d+1
        count_list.append(count)
        #print(count)

      max_index = count_list.index(max(count_list))
      #print(max_index)

      if(max_index == int(winetest[v][-1])):
        correct = correct+1
      arg2.append(max_index)
    #print(correct)
    print('-------------------------------------------')
    print('EOBDS:',correct/len(winetest))
    #print(correct/len(winetest))
    acc5 = correct/len(winetest)
    #print(fm)
    #print(len(re.findall(r"\bAnd\b", str(fm))))
    #print(len(re.findall(r"\bOr\b", str(fm))))
    print('-----------------------------')
    return acc5, class_f, class_fm, count99, count100, count111, count122, count1,count2,count3,count4,count5,count6

acc1,arg_dt = dt_predict(dt, winetest)
acc2,arg_dt1 = dtv_predict(dt, winetest)
acc3,arg, and1, or1 = bds_predict(dt, bf, winetest)
#acc4,arg1,and2, or2 = obds_predict(dt, mt, winetest)
acc5,class_f, class_fm, and2, and3, or2, or3,size2,size3,depth2,depth3,card2,card3 = eobds_predict(dt, bf, winetest)

#print(and1-and2,and2-and3,or1-or2,or2-or3)
#print(len(class1_fm),len(class2_fm),len(class3_fm))

hist_node = []
hist_depth = []
hist_leaf = []
for d in range(trees):
    count = 0
    for x in range(0,len(dt[d][0])):
        if(not(dt[d][5][x])):
            count = count+1
    hist_leaf.append(count)
    hist_node.append(len(dt[d][0]))
    hist_depth.append(int(np.log2(max(dt[d][0]))))

bf_total = []
for t in range(trees):
    for cc in range(0,Terms,4):
        #print(bf[t][cc+1])
        #print(bf[t][cc+2])
        f_repeat = []
        for d in range(len(bf[t][cc+1])):
            #print(Repeat(bf[t][cc+1][d])) 
            #print(len(bf[t][cc+1][d]))
            bf_total.append(len(bf[t][cc+1][d]))

print(sum(hist_node)-sum(hist_leaf))
print(sum(bf_total))

var1 = []
var2 = []

# Iterate over each class
for c in range(n_class):
    # Initialize input_vars for var1
    input_vars1 = set()
    # Iterate over each instance in the class
    for d in range(len(class_f[c])):
        # Combine inputs from all classes
        input_vars1 |= set(class_f[c][d].inputs)
    # Append the length of unique input variables to var1
    var1.append(len(input_vars1))

# Iterate over each class
for c in range(n_class):
    # Initialize input_vars for var2
    input_vars2 = set()
    # Iterate over each instance in the class
    for d in range(len(class_fm[c])):
        # Combine inputs from all classes
        input_vars2 |= set(class_fm[c][d].inputs)
    # Append the length of unique input variables to var2
    var2.append(len(input_vars2))
print(sum(var1)-sum(var2))

import csv
#new_data = [acc1,acc2,acc3,acc4,acc5,and1, and2, and3,or1,or2, or3,sum(hist_node)-sum(hist_leaf),sum(var1)-sum(var2),sum(bf_total)] 
new_data = [acc1,acc2,acc3,acc5,and2, and3,or2,or3,size2,size3,depth2,depth3,card2,card3,sum(hist_node)-sum(hist_leaf),sum(bf_total),sum(var1)-sum(var2)]
file_path = 'Output/file.csv'  # Replace this with the actual path to your CSV file
with open(file_path, 'a', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(new_data)

