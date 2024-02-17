def two_sum(num_list, val):
    seen = {}
    coomb_list = []
    ind_list = []
    for i, num in enumerate(num_list):
        complement = val - num
        if complement in seen:
            coomb_list.append(str(complement) + "," + str(num_list[i]))
            ind_list.append(str(seen[complement]) + "," + str(i))
        else:
            seen[num] = i
    return coomb_list, ind_list   
            
print(two_sum([2, 4, 3, 5, 6, -2, 4, 7, 8, 9],7))