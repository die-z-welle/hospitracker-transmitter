#!/usr/bin/python
import blescan
import sys
import datetime
import requests
import Queue
import threading
import time

import bluetooth._bluetooth as bluez

DEV_ID = 0
CHECK_INTERVAL = 10

def run():
    while True:        
        returnedList = blescan.parse_events(sock, 250)
        currenttime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        measurements = {}
        results = []
        #loop through all, get values
        for beacon in returnedList:
            beaconAsArray = beacon.split(",", 6)
            if beaconAsArray[0] in measurements:
                measurements[beaconAsArray[0]].append(beaconAsArray[5])                
            else:
                measurements[beaconAsArray[0]] = [beaconAsArray[5]]
                results.append({'datetime': currenttime, 'mac': beaconAsArray[0], 'uuid': beaconAsArray[1], 'major': beaconAsArray[2], 'minor': beaconAsArray[3], 'value': 0})
        #calculate median and put result in results
        for k,v in measurements.iteritems():
            for entry in results:
                if entry['mac'] == k:
                    entry['value'] = median(v)        
        #insert into queue
        q.put(results)
            
def median(array):
    array.sort()
    return array[len(array)/2]
            
def submitWorker():
    while True:
        tosubmit = {'deviceId': 1, 'measurements': q.get()}
        #try seding 5 times, if all fail, move on to the next
        attempts = 0
        while attempts<5:
            try:
                r = requests.post('http://192.168.43.150:3000/measurements', json=tosubmit)
            except:
                attempts += 1
                print "POST to server failed, retry..."
                time.sleep(2)
                continue
            break
            
        q.task_done()
        print "------------"
        print tosubmit

def main():
    try:
        global sock
        sock = bluez.hci_open_dev(DEV_ID)
        print "BLE thread started"
    except:
	   print "error accessing bluetooth device..."
    	   sys.exit(1)

    blescan.hci_le_set_scan_parameters(sock)
    blescan.hci_enable_le_scan(sock)
    
    global q
    q = Queue.Queue()
    t = threading.Thread(target=submitWorker)
    t.daemon = True
    t.start()
    
    run()
    
    q.join()
main()