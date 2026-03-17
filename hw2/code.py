from random import randint
min_num=100
max_num=10000
#归并排序
def merge_sort(arg):
    if len(arg)<=1:
        return arg
    mid=len(arg)//2
    left=merge_sort(arg[:mid])
    right=merge_sort(arg[mid:])
    return merge(left,right)
def merge(left,right):
    i=j=0
    result=[]
    while i<len(left) and j<len(right):
        if left[i]<right[j]:
            result.append(left[i])
            i+=1
        else:
            result.append(right[j])
            j+=1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
#链表和列表转化
def link_to_list(arg):
    result=[]
    while arg is not None:
        result.append(arg[0])
        arg=arg[1]
    return result
def list_to_link(arg):
    l=None
    for i in reversed(arg):
        l=[i,l]
    return l
def main():
    test=[randint(0,1000) for _ in range(min_num)]
    sort_test=merge_sort(test)
    link=list_to_link(sort_test)
    print(link)

main()