import numpy as np

def list_to_string(list):
    full_string=""
    for string in list:
        full_string=full_string+" "+string
    return full_string    

def list_difference(list_1, list_2):
    return [item for item in list_1 if item not in list_2]

def rstrip_list(iterable):
    list=[]
    for string in iterable:
        string=str(string)
        list.append(string.rstrip())
    return list

def upper_list(lst):
    lst=list(map(lambda x: x.upper(),lst))
    return lst

def unique_list(lst):
    array=np.array(lst)
    unique=np.unique(array)
    unique=list(unique)
    return unique

def list_intersection(list_of_lists:list):
    intersection_list=[]
    for index,List in enumerate(list_of_lists):
        if index==0:
            intersection_list=list(set(list_of_lists[index]).intersection(set(list_of_lists[index+1])))

        else:
            intersection_list=list(set(intersection_list).intersection(set(List)))
    return intersection_list

