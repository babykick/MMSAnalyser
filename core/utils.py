import datetime
def calTimeSpent(time1, time2):
    '''
    Calculate the time between time1,time2, the time format should be as "20100411231249,20100413231321"
    '''
    return int((datetime.datetime(int(time2[0:4]),int(time2[4:6]),int(time2[6:8]),int(time2[8:10]),int(time2[10:12]),int(time2[12:14]))- \
                   datetime.datetime(int(time1[0:4]),int(time1[4:6]),int(time1[6:8]),int(time1[8:10]),int(time1[10:12]),int(time1[12:14]))).seconds)
    