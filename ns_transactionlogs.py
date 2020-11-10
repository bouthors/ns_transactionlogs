"""
Download Netskope Transaction Logs
Author: Matthieu Bouthors
email: mbouthors@netskope.com
Copyright Netskope

Usage: --configfile config.yaml [--debug]

Requirements:
 requests and pyyaml libraries
 Tested with python3.7

"""
import argparse
import pprint
import requests
import yaml
import time
import os
import sys
import calendar

# pprint is used for troubleshooting
pp = pprint.PrettyPrinter(indent=4)

parser = argparse.ArgumentParser(usage='ns_transactionlogs --configfile config.yaml [--debug]', description='Download Netskope Transaction Logs')
parser.add_argument('--configfile', required=True)
parser.add_argument('--debug', action='store_true', help='enable debug')

args = parser.parse_args()
debug = args.debug

if debug:
    print("arguments:")
    pp.pprint(args)

# Read configuration
configfile = args.configfile

config = yaml.safe_load(open(configfile))
if debug:
    print("config:")
    pp.pprint(config)

nsurl = config['Netskope_API']['nsurl']
nstoken = config['Netskope_API']['nstoken']
nsproxy={}
nsproxy['http']=config['Netskope_API']['proxy']
nsproxy['https']=config['Netskope_API']['proxy']

location = config['download_location']
download_mode = config['existing_file']
allowed_modes = ['retry','replace','skip']
if not download_mode in allowed_modes:
    print("Invalid download mode, allowed values: retry,replace,skip")
    exit(10)

timeperiod = int(config['timeperiod'])
timeperiod_calc = time.time() - 3600*timeperiod
stats={
    'buckets':0,
    'total':0,
    'excluded':0,
    'skipped':0,
    'downloaded':0,
    'replaced':0,
    'new':0,
    'totalbytes':0
}

# check if the path exists
if not os.path.isdir(location):
    print("Error: path " + str(location) + " not found")
    exit(11)

loglevel = config['Log']['level']
logfile = config['Log']['file']

# open logfile if needed
if (loglevel > 0):
    logoutput = open(logfile, 'a')


def API_request(requesturl,mode="json"):
    """
    First API Request: get list of all buckets
    """
    if debug:
        print("API_request : "+requesturl)

    from requests.auth import HTTPBasicAuth
    nsauth = HTTPBasicAuth(nsurl, nstoken)
    error = None

    try:
        response = requests.get(requesturl, auth=nsauth, stream=(mode == "raw"), proxies=nsproxy)
        response.raise_for_status()
    except requests.exceptions.ProxyError as err:
        error = "A Proxy Error occurred:" + repr(err)
    except requests.exceptions.HTTPError as errh:
        error = "An Http Error occurred:" + repr(errh)
    except requests.exceptions.ConnectionError as errc:
        error = "An Error Connecting to the API occurred:" + repr(errc)
    except requests.exceptions.Timeout as errt:
        error = "A Timeout Error occurred:" + repr(errt)
    except requests.exceptions.RequestException as err:
        error = "An Unknown Error occurred" + repr(err)



    if error:
        print(error)
        exit(20)

    if response.status_code != 200:
        print("Netskope API Error: response code " + str(response.status_code))
        if mode == "json":
            pp.pprint(response.json())
        exit(21)

    if mode == "json":
        resp = response.json()
        return resp
    else:
        return  response


def get_bucket_list():
    """
    First API Request: get list of all buckets
    """
    if debug:
        print("Loading bucket list")

    request_buckets = "https://" + nsurl + "/txnlogs/api/v1/bucketlist"
    return API_request(request_buckets,"json")


def get_bucket_objects(name):
    """
    Second API Request: get the list of objects (file) in one bucket
    """
    if debug:
        print("Loading bucket " + name + " objects")

    request_bucket_objects = "https://" + nsurl + "/txnlogs/api/v1/bucket?bucket_name=" + str(name)
    return API_request(request_bucket_objects,"json")


def largenumber_to_text(num, suffix='B', decimal=3):
    """
    Format number into readable text
    """
    if num == 0:
        return "0" + suffix
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%.*f%s%s" % (decimal, num, unit, suffix)
        num /= 1024.0
    return "%.*f%s%s"


def download_object(bucket, object, localfile, mtime):
    """
    Third API Call: download an object
    """
    if debug:
        print("Downloading object " + str(object) + " from " + str(bucket))

    localfile_exists = os.path.exists(localfile)

#check if localfile already exists
    if localfile_exists:
        if download_mode == "skip":
            logtofile(2, bucketname, object_name, object_lastmodified, 0, "skip", "already exists")
            stats['skipped'] += 1
            return False
        localfile_size=os.stat(localfile).st_size
        localfile_mtime = os.stat(localfile).st_mtime

    request_object = "https://" + nsurl + "/txnlogs/api/v1/transaction?bucket_name=" + str(bucket) + "&obj_name=" + str(object)

    if debug:
        print(request_object)

    with API_request(request_object,"raw") as r:
        r_size = int(r.headers['Content-Length'])

        logreason=""
        #check if file should be replaced
        if localfile_exists:
            if download_mode == "replace":
                logreason="overwriting existing files"
            if download_mode == "retry":
                if localfile_size != r_size:
                    logreason="different size"
                elif localfile_mtime != mtime:
                    logreason = "different time"
                else:
                    logtofile(2, bucketname, object_name, object_lastmodified, 0, "skip", "same size and same time")
                    stats['skipped'] += 1
                    return False
            stats['replaced'] += 1
        else:
            logreason="new file"
            stats['new'] += 1

        current_size = 0
        if debug:
            print("Object size:" + str(r_size))
        #download by chunck
        with open(localfile, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                current_size += len(chunk)
                sys.stdout.write('\r')
                sys.stdout.write(largenumber_to_text(current_size) + "/" + largenumber_to_text(r_size))
                sys.stdout.flush()

        os.utime(localfile, (mtime, mtime))
        print(" OK")
        stats['downloaded'] += 1
        stats['totalbytes'] += r_size

    logtofile(1, bucketname, object_name, object_lastmodified, 0, "download", logreason, r_size)
    return localfile

def logtofile(level,bucket_name,object_name,object_lastmodified,object_size,action,reason,size=''):
    """
    Generate the log from the alert
    """

    curr_time = time.localtime()

    log = 'time="' + time.strftime('%Y-%m-%d %H:%M:%S %z', curr_time)
    log += '",bucket="' + str(bucket_name)
    log += '",object="' + str(object_name)
    log += '",last_modified="' + str(object_lastmodified)
    log += '",size="' + str(object_size)
    log += '",action="' + str(action)
    log += '",reason="' + str(reason)
    log += '",mode="' + str(download_mode)
    log += '",size="' + str(size) + '"'

    # print log on the command line
    print(log)

    # write log to file
    if level <= loglevel:
        logoutput.write(log)
        logoutput.write('\n')

"""
Script start
"""

# read the list of buckets (1 bucket per day)

resp=get_bucket_list()

if debug:
    print("Buckets retrieved:")
    pp.pprint(resp)

# processing buckets
if resp:
    buckets = resp["ListAllMyBucketResult"]["Buckets"]["Bucket"]

    print("Got " + str(len(buckets)) + " buckets to process, using "+download_mode+" mode, starting...")

    # process each bucket
    for bucket in buckets:
        bucketname = bucket['Name']
        stats['buckets']+=1

        print("Processing bucket " + str(bucketname))

        # Download list of objects in each bucket
        resp_objects = get_bucket_objects(bucketname)

        if debug:
            print("Bucket objects retrieved:")
            pp.pprint(resp_objects)

        # processing buckets
        if resp_objects:
            objects = resp_objects["ListBucketResult"]

            for object in objects:
                stats['total'] += 1
                object_name = object["Contents"]["Name"]
                object_lastmodified = object["Contents"]["LastModified"]
                object_lastmodified_date = time.strptime(object_lastmodified, "%a %b %d %X %Y")
                object_mtime = calendar.timegm(object_lastmodified_date)

                if timeperiod>0 and object_mtime < timeperiod_calc:
                    logtofile(3,bucketname,object_name,object_lastmodified,0,"skip","too old")
                    stats['excluded'] += 1
                else:
                    if debug:
                        print("Processing object " + object_name)
                    path = str(location) + "/" + str(bucketname)
                    filename = str(path) + "/" + str(object_name)

                    # create folder if needed
                    if not os.path.isdir(path):
                        try:
                            os.mkdir(path)
                        except OSError:
                            print("Creation of the directory %s failed" % path)
                            exit(15)
                        else:
                            print("Successfully created the directory %s " % path)


                    download_object(bucketname, object_name, filename, object_mtime)

    else:
        "Error reading bucket list"

if (loglevel > 0):
    logoutput.close()

if debug:
    pp.pprint(stats)

print("Stats: " + str(stats['buckets']) + " buckets found with a total of " + str(stats['total']) + " objects processed with "+download_mode+ " mode")
print(" - " + str(stats['excluded']) + " excluded with timeperiod")
print(" - " + str(stats['skipped']) + " skipped")
print(" - " + str(stats['downloaded']) + " downloaded")
print("   - " + str(stats['replaced']) + " replaced")
print("   - " + str(stats['new']) + " new")
print(" Total bytes downloaded: " + largenumber_to_text(stats['totalbytes']))