item={
'item1':{'pri':3,'hv':5,'cate':'a'},
'item2':{'pri':4,'hv':7,'cate':'b'},
'item3':{'pri':2,'hv':4,'cate':'a'},
'item4':{'pri':5,'hv':8,'cate':'b'},
'item5':{'pri':3,'hv':6,'cate':'b'}
}
M=15
dict1={(0,0):(0,[])}
#(花费，差值)：(幸福，[商品列表])
for i in range(5):
    dict_new=dict1.copy()
    for (x,y) in dict1:
        new_pri=x+item[f'item{i+1}']['pri']
        (hv,ite)=dict1[(x,y)]
        (new_hv,new_item)=(hv+item[f'item{i+1}']['hv'],ite+[f'item{i+1}'])
        if new_pri>M:
            continue
        if item[f'item{i+1}']['cate']=='a':
            y+=1
        else:
            y-=1
        if (new_pri,y)not in dict_new or dict_new[(new_pri,y)][0]<new_hv:
            dict_new[(new_pri,y)]=(new_hv,new_item)
    dict1=dict_new
max_hv=0
max_item=[]
for x in dict1:
    if x[0]<=M and x[1]<=0 and dict1[x][0]>max_hv:
        max_hv=dict1[x][0]
        max_item=dict1[x][1]

print(max_hv,max_item)


