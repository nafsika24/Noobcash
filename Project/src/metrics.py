
# compute Throughput

fd = open('../times/transactions_t0.txt', 'r')
res = 0
counter = 0
for line in fd:
    res += float(line)
    counter +=1

t0 = counter/res

fd = open('../times/transactions_t1.txt', 'r')
res = 0
counter = 0
for line in fd:
    res += float(line)
    counter +=1

t1 = counter/res

fd = open('../times/transactions_t2.txt', 'r')
res = 0
counter = 0
for line in fd:
    res += float(line)
    counter +=1

t2 = counter/res

fd = open('../times/transactions_t3.txt', 'r')
res = 0
counter = 0
for line in fd:
    res += float(line)
    counter +=1

t3 = counter/res


fd = open('../times/transactions_t4.txt', 'r')
res = 0
counter = 0
for line in fd:
    res += float(line)
    counter +=1

t4 = counter/res

print("Thr = ", (t0 + t1 + t2 + t3 + t4)/5)

#
# print("Average Mining Block Time = ", res/counter)
#
#
fd = open('../times/ValidateTime0.txt', 'r')
res = 0
counter = 0
for line in fd:
    res += float(line)
    counter +=1


print(counter,res)

fd = open('../times/mining.txt', 'r')
res1 = 0
counter1 = 0
for line in fd:
    res1 += float(line)
    counter1 +=1

print("Mean Block Time = ", res1/counter)


# compute Throughput

# fd = open('../times/transactions_t.txt', 'r')
# res = 0
# counter = 0
# for line in fd:
#     res += float(line)
#     counter +=1
#
# print(res,counter)
# print("Throughput = ", res/counter)
#
# fd = open('../times/mining.txt', 'r')
# res = 0
# counter = 0
# for line in fd:
#     res += float(line)
#     counter += 1
#
# print(res, counter)
#
# fd = open('../times/ValidateTime.txt', 'r')
# res = 0
# counter = 0
# for line in fd:
#     res += float(line)
#     counter += 1
#
# print(res, counter)