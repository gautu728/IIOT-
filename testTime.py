from datetime import time
from datetime import datetime,timedelta

CurrentDate=datetime.now().date()
CurrentTime=datetime.now().time()
sihTime=time(6, 59,00)
if(CurrentTime<=sihTime):
          date=CurrentDate-timedelta(1)
else:
         date=CurrentDate
presentTime=date.strftime('%Y-%m-%d')      
print(CurrentDate)
print(CurrentTime)
print(presentTime)


Count=0
CurrentDate=datetime.now().date()
CurrentTime=datetime.now().time()
endTime=time(0, 00,00)
sihTime=time(6, 59,00)
if(CurrentTime>=endTime and CurrentTime>=sihTime):
      filterDate=CurrentDate-timedelta(1)
      print("filterDate",filterDate)
else:
      filterDate=CurrentDate
      print("filterDate",filterDate)
presentDate=filterDate.strftime("%Y-%m-%d")
print(presentDate)   


