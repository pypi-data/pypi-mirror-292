import MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.TasksMode as TM
import MobileInventoryCLI.CodeProcessing.RecordCodesAndBarcodes.DB.db as db
import string
from datetime import datetime
fm_data={'Name':{
            'type':'str',
            'default':'',
            },
        'Value':{
            'type':'int',
            'default':0,
            },
        'Price':{
           'type':'float',
           'default':0.0,
            },
        'Barcode':{
            'type':'str',
            'default':'000000000000',
            },
        'Code':{
            'type':'str',
            'default':'12345678',
            },
        'DOE':{
            'type':'date',
            'default':None,
            },
        'TOE':{
            'type':'time',
            'default':None,
            },
        'DTOE':{
            'type':'datetime',
            'default':None,
            },
        'DEFAULT':{
            'type':'bool',
            'default':False,
            },
        'List':{
            'type':'list',
            'default':[],
            },
      }
def FormBuilderMkText(text,data):
    try:
        if text in ['f','m','p','d']:
            return text
        if text == '':
            return 'd'
        value=None
        if data.lower() == 'float':
            try:
                value=float(eval(text))
            except Exception as e:
                try:
                    value=float(text)
                except Exception as e:
                    return 'd'
        elif data.lower() in ['int','integer']:
            try:
                value=int(eval(text))
            except Exception as e:
                try:
                    value=int(text)
                except Exception as e:
                    return 'd'
        elif data.lower() in ['bool','boolean','boolean_basic']:
            try:
                value=bool(eval(text))
            except Exception as e:
                try:
                    if data.lower() in ['boolean_basic']:
                        for i in ['n','no','false','f']:
                            if i in text.lower():
                                return False
                        for i in ['y','yes','true','t']:
                            if i in text.lower():
                                return True
                        return None

                    if text.lower() in ['y','yes','true','t','1']:
                        value=True
                    elif text.lower() in ['n','no','false','f','0']:
                        value=False
                    else:
                        try:
                            if data.lower() not in ['boolean_basic']:
                                value=bool(eval(text))
                            else:
                                return False
                        except Exception as e:
                            return 'd'
                except Exception as e:
                    return 'd'
        elif data.lower() in ['str','string',"varchar"]:
            value=text
        elif data.lower() == 'date':
            if text.lower() in ['y','yes','1','t','true']:
                value=DatePkr()
        elif data.lower() == 'time':
            if text.lower() in ['y','yes','1','t','true']:
                value=TimePkr()
        elif data.lower() in ['datetime','datetime-']:
            if text.lower() in ['y','yes','1','t','true']:
                value=TM.Tasks.TasksMode(parent=None,engine=db.ENGINE,init_only=True).DateTimePkr()
            else:
                def try_date(ds,format='%m%d%Y'):
                    try:
                        #print(format)
                        return datetime.strptime(ds,format)
                    except Exception as e:
                        #print(e)
                        return None
                def process_ds(ds):
                    predate="%m{c}%d{c}{year}"
                    t1=[]
                    chars=[i for i in string.punctuation]
                    chars.pop(chars.index('%'))
                    for i in chars:
                        for year in ['%y','%Y']:
                            t1.append(predate.format(c=i,year=year))
                            for ii in chars:
                                for year in ['%y','%Y']:
                                    t1.append(f"%m{i}%d{ii}{year}")
                    for f in t1:
                            dt=try_date(format=f,ds=ds)
                            if dt:
                                return dt
                value=process_ds(text)
                if value == None:
                    if data.lower() == 'datetime':
                        value=TM.Tasks.TasksMode(parent=None,engine=db.ENGINE,init_only=True).DateTimePkr()
        elif data.lower() == 'list':
            value=text.split(',')
        return value
    except Exception as e:
        print(e)