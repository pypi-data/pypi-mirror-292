import numpy

def arr(size):
    x = numpy.random.normal(0, 1.0, size=(size,))
    factor = 1 - 1 / (size ** 0.5) + numpy.log(size)
    x = numpy.exp(x * factor)
    return x / numpy.sum(x)

def ent(x):
    return - numpy.sum(x * numpy.log(x))

def stat_ent(size, stat=1024):
    ents = 0
    print("factor", (numpy.log(size) + 1 / numpy.sqrt(size)))
    for _ in range(stat):
        ents += ent(arr(size))
    return ents / stat

print(stat_ent(8))
print(stat_ent(16))
print(stat_ent(32))
print(stat_ent(64))
print(stat_ent(128))
print(stat_ent(256))
print(stat_ent(4096))
print(stat_ent(10000))
print(stat_ent(40000))
