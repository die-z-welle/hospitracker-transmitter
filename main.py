#!/usr/bin/python
import blescan
import sys
import datetime
import requests

import bluetooth._bluetooth as bluez

DEV_ID = 0
CHECK_INTERVAL = 10

def run():
    while True:
        returnedList = blescan.parse_events(sock, 250)
        measurements = {}
        results = []
        #loop through all, get values
        for beacon in returnedList:
            beaconAsArray = beacon.split(",", 6)
            if beaconAsArray[0] in measurements:
                measurements[beaconAsArray[0]].append(beaconAsArray[5])                
            else:
                measurements[beaconAsArray[0]] = [beaconAsArray[5]]
                results.append({'datetime': datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), 'mac': beaconAsArray[0], 'uuid': beaconAsArray[1], 'major': beaconAsArray[2], 'minor': beaconAsArray[3], 'value': 0})
        #calculate median and put result in results
        for k,v in measurements.iteritems():
            for entry in results:
                if entry['mac'] == k:
                    entry['value'] = median(v)        
        submit(results)
            
def median(array):
    array.sort()
    return array[len(array)/2]
            
def submit(values):
    tosubmit = {'deviceId': 1, 'measurements': values}
    #submit to server
    print "------------"
    print tosubmit
    r = requests.post('http://192.168.43.150:3000/measurements', json=tosubmit)

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
    
    run()

main()