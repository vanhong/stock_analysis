# Create your views here.
import urllib
import urllib2
from django.http import HttpResponse
from HTMLParser import HTMLParser
import time
from datetime import *
from decimal import Decimal
from us_stocks.models import *
from bs4 import BeautifulSoup

def update_finance(request):
    print 'Ready to update_us_finance'
    #get product list
    f = open('D:/1IFEELGOOD/NYSE.txt')
    for l in f:
        print('process ' + l.strip())
        symbol = l.strip()
        #get recent 10 seasons
        url = 'http://asia.advfn.com/exchanges/NYSE/' + symbol +'/financials?btn=istart_date&istart_date=1&mode=quarterly_reports'
        data = urllib.urlopen(url)
        soup = BeautifulSoup(data)
        selectOptions = [o.string for o in soup.findAll('option')]
        selectOptions = [x for x in selectOptions if '/' in x]
        print selectOptions
        # print a
        maxIndex = len(selectOptions) - 1
        print maxIndex
        index = maxIndex - 4, maxIndex - 9
        print index

        for i in index:
            url = 'http://asia.advfn.com/exchanges/NYSE/' + symbol +'/financials?btn=istart_date&istart_date=' + str(i) + '&mode=quarterly_reports'
            data = urllib.urlopen(url)
            print data
            #print(the_page)
            soup = BeautifulSoup(data)
            dataList = [td.string for td in soup.findAll('td', {'align' : 'left', 'width':'200'})]
            quarterList = []
            startSave = False
            for item in dataList:
                # print item
                if 'operating revenue' in item:
                    startSave = True
                if  'quarter end date' in item :
                    print 'in quarter end date'
                    quarterList.append(item.next.string.replace('/',''))
                    quarterList.append(item.next.next_sibling.string.replace('/',''))
                    quarterList.append(item.next.next_sibling.next_sibling.string.replace('/',''))
                    quarterList.append(item.next.next_sibling.next_sibling.next_sibling.string.replace('/',''))
                    quarterList.append(item.next.next_sibling.next_sibling.next_sibling.next_sibling.string.replace('/',''))
                elif len(quarterList) > 0 and startSave :
                    values = {}
                    values[quarterList[0]] = item.next.string
                    values[quarterList[1]] = item.next.next_sibling.string
                    values[quarterList[2]] = item.next.next_sibling.next_sibling.string
                    values[quarterList[3]] = item.next.next_sibling.next_sibling.next_sibling.string
                    values[quarterList[4]] = item.next.next_sibling.next_sibling.next_sibling.next_sibling.string
                    for key,value in values.iteritems():
                        obj = Finance()
                        obj.surrogate_key = key + '_' + item + '_' + 'NYSE_A'
                        obj.symbol = 'NYSE_A'
                        obj.date = int(key)
                        obj.time_type    = 'S'
                        obj.name = item
                        if value is None:
                            obj.value = 0
                        else:    
                            obj.value = value
                        obj.save()
                        print 'save data, key=' + obj.surrogate_key
                        # surrogate_key = models.CharField(max_length=50, primary_key=True)
                        # symbol = models.CharField(max_length=20, db_index=True)
                        # date = models.IntegerField(db_index=True)
                        # time_type = models.CharField(max_length=2, db_index=True)
                        # name = models.CharField(max_length=50, db_index=True)
                        # value = models.CharField(max_length=20)

    print quarterList

    return HttpResponse('Hello')