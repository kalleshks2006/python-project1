from datetime import date
def age(birthdate):
    today=date.today()
    age=today.year-birthdate.year-((today.month,today.day)<(birthdate.month,birthdate.day))
    return age
name=input("enter the name of a person:")
y=int(input("enter the year of the birthdate:"))
m=int(input("enter the month of the birthdate:"))
d=int(input("enter the date of the birthdate:"))

person_age=age(date(y,m,d))
print("the age of a person is:%d"%(person_age))
if person_age>60:
    print("%s is a senior citizen"%(name))
else:
    print("%s iis not a senior citizen"%(name))    
    
    
    
    
 