# (c) 2016 Open Source Geospatial Foundation - all rights reserved
# (c) 2014 - 2015 Centre for Maritime Research and Experimentation (CMRE)
# (c) 2013 - 2014 German Aerospace Center (DLR)
# This code is licensed under the GPL 2.0 license, available at the root
# application directory.

__author__ = "Alessio Fabiani"
__copyright__ = "Copyright 2016 Open Source Geospatial Foundation - all rights reserved"
__license__ = "GPL"

import threading
import thread
import time
import psutil
import logging

logger = logging.getLogger("servicebot.resource_monitor")


class ResourceMonitor(threading.Thread):

    load_average_scan_minutes = 15
    cores = psutil.cpu_count()
    cpu_perc  = []
    vmem_perc = []
    lock = threading.Lock()

    def __init__(self, load_average_scan_minutes):
        threading.Thread.__init__(self)
        ResourceMonitor.load_average_scan_minutes = load_average_scan_minutes
        ResourceMonitor.lock.acquire()

        ResourceMonitor.vmem_perc.append(psutil.virtual_memory().percent)
        ResourceMonitor.vmem_perc.append(psutil.virtual_memory().percent)

        ResourceMonitor.cpu_perc.append(psutil.cpu_percent(interval = 0, percpu= False))
        ResourceMonitor.cpu_perc.append(psutil.cpu_percent(interval = 0, percpu= False))

        ResourceMonitor.lock.release()

    def proc_is_running(self, proc_defs):
        for proc in psutil.process_iter():
            try:
                process = psutil.Process(proc.pid) # Get the process info using PID
                if process.is_running():
                    #pid    = str(process.pid)
                    #ppid   = str(process.ppid)
                    procDict = process.as_dict()
                    status = procDict["status"]

                    #cpu_percent = process.cpu_percent()
                    #mem_percent = process.memory_percent()

                    #rss = str(process.memory_info().rss)
                    #vms = str(process.memory_info().vms)
                    #username = process.username()
                    name     = procDict["name"] # Here is the process name
                    path     = procDict["cwd"]
                    cmdline  = ' '.join(procDict["cmdline"])

                    print("Get the process info using (path, name, cmdline): [%s = %s = %s]" % (path, name, cmdline))
                    print("Get the process status: [%s]" % (status))
                    for _p in proc_defs:
                        logger.info("Look for process: [%s] / Status [%s]" % (_p, status.lower()))
                        print("Look for process: [%s] / Status [%s]" % (_p, status.lower()))
                        if ('name' in _p and _p['name'] in name) and \
                                (path != None and ('cwd' in _p and _p['cwd'] in path) or path == None) and \
                                    ('cmdline' in _p and _p['cmdline'] in cmdline):
                            return True
            except:
                import traceback
                tb = traceback.format_exc()
                logger.debug(tb)
                print(tb)
        return False

    def run(self):
        while True:
            ResourceMonitor.lock.acquire()

            ResourceMonitor.vmem_perc[1] = (ResourceMonitor.vmem_perc[0] + ResourceMonitor.vmem_perc[1]) / 2.0
            ResourceMonitor.vmem_perc[0] = (ResourceMonitor.vmem_perc[1] + psutil.virtual_memory().percent) / 2.0

            ResourceMonitor.cpu_perc[1] = ResourceMonitor.cpu_perc[0]
            ResourceMonitor.cpu_perc[0] = psutil.cpu_percent(interval = (ResourceMonitor.load_average_scan_minutes*60), percpu= False)

            ResourceMonitor.lock.release()
