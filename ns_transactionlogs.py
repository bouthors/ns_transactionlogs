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


pp = pprint.PrettyPrinter(indent=4)

parser = argparse.ArgumentParser(usage='ns_transactionlogs --configfile config.yaml [--debug]', description='Download Netskope Transaction Logs')
parser.add_argument('--configfile', required=True)
parser.add_argument('--debug', action='store_true', help='enable debug')

args = parser.parse_args()
debug = args.debug

if debug:
    print("arguments:")
    pp.pprint(args)

#Read configuration
configfile = args.configfile

config = yaml.safe_load(open(configfile))
if debug:
    print("config:")
    pp.pprint(config)

nsurl=config['Netskope_API']['nsurl']
nstoken=config['Netskope_API']['nstoken']
location=config['download_location']

if not os.path.isdir(location):
    print("Error: path " + str(location) + " not found")
    exit(11)

loglevel=config['Log']['level']
logfile=config['Log']['file']


#open logfile
if (loglevel>0):
    logoutput = open(logfile, 'a')


def get_bucket_list():
    print("Loading bucket list")

    request_buckets = "https://" + nsurl + "/txnlogs/api/v1/bucketlist"

    if debug:
        print(request_buckets)

    from requests.auth import HTTPBasicAuth
    resp = requests.get(request_buckets,auth=HTTPBasicAuth(nsurl, nstoken))

    return resp


def get_bucket_objects(name):
    print("Loading bucket objects")

    request_bucket_objects = "https://" + nsurl + "/txnlogs/api/v1/bucket?bucket_name=" + str(name)

    if debug:
        print(request_bucket_objects)

    from requests.auth import HTTPBasicAuth
    resp = requests.get(request_bucket_objects,auth=HTTPBasicAuth(nsurl, nstoken))

    return resp

def is_downloadable(url):
    """
    Does the url contain a downloadable resource
    """
    from requests.auth import HTTPBasicAuth
    h = requests.head(url, auth=HTTPBasicAuth(nsurl, nstoken))
    header = h.headers
    content_type = header.get('content-type')
    if debug:
            pp.pprint(content_type.lower())
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True

def largenumber_to_text(num, suffix='B', decimal=3):
    if num == 0:
        return "0" + suffix
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%.*f%s%s" % (decimal, num, unit, suffix)
        num /= 1024.0
    return "%.*f%s%s"

def download_object(bucket,object,local_filename):
    if debug:
        print("Downloading object "+str(object) + " from "+str(bucket))

    request_object = "https://" + nsurl + "/txnlogs/api/v1/transaction?bucket_name=" +str(bucket)+"&obj_name="+str(object)

    if debug:
        print(request_object)

    if not is_downloadable(request_object):
        print("Object " + request_object + " is not downloadable")
        return False

    from requests.auth import HTTPBasicAuth
    with requests.get(request_object,auth=HTTPBasicAuth(nsurl, nstoken), stream=True) as r:
        r.raise_for_status()
        r_size=int(r.headers['Content-Length'])
        current_size=0
        if debug:
            print("Object size:"+str(r_size))
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
                current_size+=len(chunk)
                sys.stdout.write('\r')
                sys.stdout.write(largenumber_to_text(current_size)+"/"+largenumber_to_text(r_size))
                sys.stdout.flush()
    print(" OK")
    return local_filename



class APIError(Exception):
    """An API Error Exception"""

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "APIError: status={}".format(self.status)


#SCRIPT

#read the list of buckets (1 bucket per day)
error = None
try:
    response = get_bucket_list()
    response.raise_for_status()
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
    exit(10)

if response.status_code != 200:
    print("Netskope API Error: response code " + str(response.status_code))
    pp.pprint(response.json())
    exit(11)

resp=response.json()

if debug:
    print("Buckets retrieved:")
    pp.pprint(resp)

#processing buckets
if resp:
    buckets=resp["ListAllMyBucketResult"]["Buckets"]["Bucket"]

    print("Got " + str(len(buckets)) + " buckets to process, starting...")

    #process each bucket
    for bucket in buckets:
        bucketname=bucket['Name']

        print("Processing bucket " + str(bucketname))



        # Download list of objects in each bucket
        error = None
        try:
            response2 = get_bucket_objects(bucketname)
            response2.raise_for_status()
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
            exit(10)

        if response2.status_code != 200:
            print("Netskope API Error: response code " + str(response2.status_code))
            pp.pprint(response2.json())
            exit(11)

        resp_objects = response2.json()

        if debug:
            print("Bucket objects retrieved:")
            pp.pprint(resp_objects)

        # processing buckets
        if resp_objects:
            objects = resp_objects["ListBucketResult"]

            for object in objects:
                object_name=object["Contents"]["Name"]
                object_lastmodified = object["Contents"]["LastModified"]

                print("Processing object "+object_name)
                path=str(location) + "/" + str(bucketname)
                filename=str(path) + "/" + str(object_name)

#create folder if needed
                if not os.path.isdir(path):
                    try:
                        os.mkdir(path)
                    except OSError:
                        print("Creation of the directory %s failed" % path)
                        exit(11)
                    else:
                        print("Successfully created the directory %s " % path)

                download_object(bucketname,object_name,filename)





                #generate the log from the alert
                curr_time = time.localtime()

                log = 'time="' + time.strftime('%Y-%m-%d %H:%M:%S %z',curr_time)
                log += '",bucket="' +str(bucketname)
                log += '",object="' + str(object_name)
                log += '",last_time="' + str(object_lastmodified) + '"'

                #print log on the command line
                print(log)

                #write log to file
                if loglevel > 0:
                    logoutput.write(log)
                    logoutput.write('\n')

    else:
        "Error reading bucket list"

if (loglevel>0):
    logoutput.close()