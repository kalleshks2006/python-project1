import math
num1=float(input("enter first number:"))
operator=input("enter operator(=,-,*,/):")
num2=float(input("enter second number:"))

if operator=="+":
    print("result:",num1+num2)
elif operator=="-":
    print("result",num1-num2)
elif operator=="*":
    print("result:",num1*num2)
elif operator=="/":
    if num2!=0:
        print("result",num1/num2)
    else:
        print("error!division by zero")
else:
    print("invalid operator!")                        