import os
import psutil
from .config import MAX_LOAD_1, MAX_MEM

MAX_PAGE_NUMBER=100
def is_valid_page_param(request):
    page = request.GET.get('page')
    if page is None:
        return True
    try:
        page_num = int(page)
        return 1 <= page_num <= MAX_PAGE_NUMBER
    except ValueError:
        return False

def check_server_status():
    try:
        load1, load5, load15 = os.getloadavg() # CPU load average        
        cpu_cores = os.cpu_count()
        # rule 1 - load
        if load1 > ( cpu_cores * MAX_LOAD_1 ):
            return False

        # rule 2 - ram 
        mem = psutil.virtual_memory()
        if mem.percent > MAX_MEM:
            return False

        return True
    except Exception as e:
        return True # Default to allowing 