from random import randint
##判断24点
def poke(arg):
    if len(arg)==1:
        return arg[0]==24
    for i in range(len(arg)):
        for j in range(len(arg)):
            if i!=j:
                rest=[]
                for k in range(len(arg)):
                    if k!=i and k!=j:
                        rest.append(arg[k])
                if arg[j]!=0 and arg[i]%arg[j]==0:
                    result= poke(rest+[arg[i]+arg[j]]) or poke(rest+[(arg[i]-arg[j])]) or poke(rest+[(arg[i]*arg[j])]) or poke(rest+[(arg[i]/arg[j])] )
                else:
                    result= poke(rest+[arg[i]+arg[j]]) or poke(rest+[(arg[i]-arg[j])]) or poke(rest+[(arg[i]*arg[j])])
                if result==True:
                    return True        
    return False
test=[randint(1,13) for _ in range(4)]
acc=0
test_num=10000
for i in range(test_num):
    test=[randint(1,13) for _ in range(4)]
    if poke(test)==True:
        acc+=1
print(acc/test_num)