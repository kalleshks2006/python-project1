def linear_search(list1,n,key):
    for i in range(0,n):
        if(list1[i]==key):
            return i
        return -1
    list1=[1,2,3,4,5]
    key=7
    n=len(list1)
    res=linear_search(list1,n,key)
    if(res==-1):
        print("Element not found in the list")
    else:
        print("Element found at index:",res)
        