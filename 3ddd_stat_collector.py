import traceback
import time
import os 
from datetime import datetime
import sys
    
try:
    from login import driver
    import parse2
except Exception as e:
    str_exc = str(traceback.format_exc())
    str_exc = str_exc.replace('\\', '\\\\')
    print(f'!Python script error ({str_exc}!')
    driver.execute_script(
        f'console.log(`!Python script error ({str_exc})!`)'
    )
    list_json = os.listdir(path='dates/')
   
    if(os.path.isfile(f'{datetime.now().strftime("%d.%m.%y")}.csv')):
        os.remove(f'{datetime.now().strftime("%d.%m.%y")}.csv')

time.sleep(2**20)
