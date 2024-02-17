def fib(num):
    if num==1 or num==2:
        return 1
    elif num==0:
        return 0
    else:
        val = fib(num-1) + fib(num-2)
        return val


print(fib(6))


def find_subarray(nums, k):
    left = 0
    current_sum = 0
    for right in range(len(nums)):
        current_sum += nums[right]
        
        while current_sum > k:
            current_sum -= nums[left]
            left += 1
        
        if current_sum == k:
            return nums[left:right+1]
        
        return "no subarray foud"