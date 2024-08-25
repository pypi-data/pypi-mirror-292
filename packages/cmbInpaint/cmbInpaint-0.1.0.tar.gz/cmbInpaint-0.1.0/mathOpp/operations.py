def add(*x):
    s = 0
    for i in x:
        s += i
    return s

def product(*x):
    s = 0
    for i in x:
        s *= i
    return s

def mean(*x):
    s = 0
    c = 0
    for i in x:
        s += i
        c += 1
    return s/c
