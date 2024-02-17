'''Given a string s, find the length of the longest 
substring
 without repeating characters.
s = "abcabcbb"
output = "abc"'''

def find_substr(sample_str):
    seq = ''
    seq_list = []
    for i in range(len(sample_str)):
        seq = sample_str[i]
        if sample_str.count(seq) > 1 and seq not in seq_list:
                seq_list.append(seq)
        for j in range(i+1, len(sample_str)):
            if seq[-1] == sample_str[j]:
                break
            seq = seq + sample_str[j]
            if sample_str.count(seq) > 1 and seq not in seq_list:
                seq_list.append(seq)
    print(seq_list)
    max_len_str = ''
    for seq1 in seq_list:
        if len(seq1) > len(max_len_str):
            print(max_len_str)
            max_len_str = seq1
            
    return max_len_str


print(find_substr('pkwwaw'))