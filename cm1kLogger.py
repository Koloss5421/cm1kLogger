#!/bin/ptyhon3
# NetGear CM1000 Logging
# Created By: Koloss5421

import requests, datetime, argparse
from bs4 import BeautifulSoup
from time import sleep

parser = argparse.ArgumentParser(description='Netgear CM-1000 Docsis Status Logger')
parser.add_argument("logfile",help='The destination of the json log output.')
parser.add_argument("--debug", "--d", action="store_true", default=False, help="Enable debug logging.")
args = parser.parse_args()

modem_docis = "http://192.168.100.1/DocsisStatus.asp"
modem_user = "admin"
modem_pass = "<PASSWORD>"

def printd(string):
    if args.debug:
        print(string)

def iterateTable(x, obj_name, table_objects):
    print("[+] Iterating over table: {}...".format(obj_name))
    headings = []
    for y in x.findAll('tr'):
        temp_data = {}
        temp_obj_name = ""
        tds = y.findAll('td')
        for k in tds:
            ## lets add the heading names to the headings temp var
            if (k.findChild('span') != None ):
                if k.findChild('span').get('class')[0] == "thead":
                    ## Replace spaces with _ and / with -
                    headings.append( k.text.replace(" ", "_").replace("_/_", "-") )
            else:
                if tds.index(k) == 0:
                    temp_obj_name = k.text.replace(" ", "_")
                else:
                    ## take the current index - get the heading
                    ## and add the value and index to the the temp object
                    temp_data[ headings[ tds.index(k) ] ] = k.text
        if (len(temp_data) > 0):
            if ( not obj_name in table_objects ):
                ## Create an empty object if one does not exist for that subtable
                table_objects[obj_name] = {}
            ## append the temp object to the subobject
            table_objects[obj_name][temp_obj_name] = temp_data

def makeRequest():
    attempts = 0
    success = False
    table_objects = {}
    ## Requests sometimes fail - try it 3 times or until success.
    while (attempts < 3 or success == False):
        printd("[+] Attempting Request...")
        r = requests.get(modem_docis, auth=(modem_user, modem_pass))
        if r.status_code == 200:
            table_objects['date'] = str(datetime.datetime.now())
            soup = BeautifulSoup(r.content, features="lxml")
            tables = soup.findAll('table')
            ## Let's iterate over the tables we found in the soup
            for x in tables:
                ## lets find the Startup Procedure
                ## ~maybe~ a better way to do this. Maybe not. 
                ## but I don't want all the tables really
                if x.get('id') == "startup_procedure_table":
                    ## iterate over each procedure
                    iterateTable(x, 'procedures', table_objects)
                if x.get('id') == "dsTable":
                    ## iterate over each downstream channel
                    iterateTable(x, 'downstream_channels', table_objects)
                if x.get('id') == "usTable":
                    ## iterate over each downstream channel
                    iterateTable(x, 'upsstream_channels', table_objects)
                if x.get('id') == "d31dsTable":
                    ## iterate over each downstream channel
                    iterateTable(x, 'downstream_ofdm_channels', table_objects)
            success = True
            break
        else:
            if (attempts == 2):
                table_objects['date'] = str(datetime.datetime.now())
                table_objects["Error"] = "All attempts to create request failed!"
                break
            printd("[!] [Attempt: {}] [ERROR] Could not get docsis information: {}".format(attempts + 1, r.status_code ) )
            attempts += 1

    ## lets write to the log file once done either error or success!
    with open(args.logfile, 'a') as f:
        printd("[!] Writing to file: {}".format(args.logfile))
        ## Have to replace the quotes here to get splunk to auto-parse the fields.
        f.write( str(table_objects).replace("'", '"') + "\n" )
    ## clear table_objects after done
    table_objects = {}

## I planned this to run with cron every minute but I want it to run every 30 seconds
makeRequest()
printd("[+] Waiting 30 Secs...")
sleep(30)
makeRequest()
