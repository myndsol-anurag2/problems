def sample_decorator(func):
    def func_to_call(func):
        if func() % 2 == 0:
            return True
        else: 
            return False
    


@sample_decorator
def display(num):
    return num
    
    
display(2)