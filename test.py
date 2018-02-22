res=[1,2,3,4]
resStr=map(str, res)
file = open("items.txt", "w")
file.write(','.join(resStr));
file.close()
