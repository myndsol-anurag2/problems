def decorator_func(func):
    def wrapper_func():
        print("wrapper called")
        return func()
    print("decorator called")
    return wrapper_func

@decorator_func
def show():
    print("show called")
    
# show()


def square(n):
    for i in range(1,n+1):
        yield i*i
        
        
a=square(3)
print(sum(a))

def cube():
    a = iter([1,8,27])
    return sum(a)

print(cube())

def fib():
    x, y = 0, 1
    while True:
        yield x
        x, y = y, x+y 
        
a=fib()       
print(next(a))
print(next(a))
print(next(a))
print(next(a))
print(next(a))