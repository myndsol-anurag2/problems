def count_case(sample_str):
    str_list = sample_str.split(' ')
    case_count = {'small_case':0, 'large_case':0, 'mix_case': 0}
    
    for i in str_list:
        small_count = 0
        large_count = 0
        print(i)
        for j in i:
            if ord(j)>=65 and ord(j)<=90:
                large_count += 1
            elif ord(j)>=97 and ord(j)<=122:
                small_count += 1
        
        if small_count == len(i):
            case_count['small_case'] += 1
        elif large_count == len(i):
            case_count['large_case'] += 1
        else:
            case_count['mix_case'] += 1
            
    return case_count
            

a='aa AA Aa Aa AA aaaa'
dict = count_case(a)
print(dict)
    