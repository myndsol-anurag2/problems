# Write a function that takes an array of numbers as input
#  and finds all the sequences present in the array.
# Sequence is a set of 2 or more consecutive numbers.
# e.g.
# inp = [112, 320, 230, 431, 233, 231,432,232, 412, 598]`
# There are 2 sequences present in this array. 230, 231, 232, 233 and 431,432
# Rest of the number do not form any sequence. So the output will be
# output: [[230,231,232,233],[431,432]]


def find_sequence(nums):
    seq_list = []
    seen = []
    for i in range(len(nums)):
        done_flag = False
        print("i", nums[i])
        sub_list = []
        sub_list.append(nums[i])
        seen.append(nums[i])
        while not done_flag and nums[i]:
            if sub_list[-1] + 1 in nums and sub_list[-1] + 1 not in seen:
                sub_list.append(sub_list[-1] + 1)    
            else:
                done_flag = True
        if len(sub_list) > 1:
            seq_list.append(sub_list)
            seen.extend(sub_list)
    return seq_list

seq_list = find_sequence([112, 320, 230, 431, 233, 231,432,232, 412, 598])
print(seq_list)