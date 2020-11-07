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
location = config['download_location']
download_mode = config['existing_file']
timeperiod = int(config['timeperiod'])
timeperiod_calc = time.time() - 3600*timeperiod

# check if the path exists
if not os.path.isdir(location):
    print("Error: path " + str(location) + " not found")
    exit(11)

loglevel = config['Log']['level']
logfile = config['Log']['file']

# open logfile if needed
if (loglevel > 0):
    logoutput = open(logfile, 'a')


def get_bucket_list():
    """
    First API Request: get list of all buckets
    """
    if debug:
        print("Loading bucket list")

    request_buckets = "https://" + nsurl + "/txnlogs/api/v1/bucketlist"

    if debug:
        print(request_buckets)

    from requests.auth import HTTPBasicAuth
    resp = requests.get(request_buckets, auth=HTTPBasicAuth(nsurl, nstoken))

    return resp


def get_bucket_objects(name):
    """
    Second API Request: get the list of objects (file) in one bucket
    """

    if debug:
        print("Loading bucket " + name + " objects")

    request_bucket_objects = "https://" + nsurl + "/txnlogs/api/v1/bucket?bucket_name=" + str(name)

    if debug:
        print(request_bucket_objects)

    from requests.auth import HTTPBasicAuth
    resp = requests.get(request_bucket_objects, auth=HTTPBasicAuth(nsurl, nstoken))

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

def check_download(url,localfile,mtime):
    """
    Check if the file should be downloaded by performing a head request and compare with destination location
    """

    if debug:
        print("Check download " + url + ", file:" + localfile)

#perform head request to check the file
    from requests.auth import HTTPBasicAuth
    h = requests.head(url, auth=HTTPBasicAuth(nsurl, nstoken))
    header = h.headers
    content_type = header.get('content-type')
    size = int(header.get('Content-Length'))

    if debug:
        pp.pprint(content_type.lower())
        print("size:"+str(size))
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False

#check exisiting files
    if os.path.exists(filename):
        local_size=os.stat(localfile).st_size
        local_mtime = os.stat(localfile).st_mtime
        if download_mode == "skip":
            print("SKIP mode, " + localfile + " already exists, skipping")
            return False
        if download_mode == "replace":
            print("REPLACE mode, " + localfile + " already exists, replacing")
            return True
        if download_mode == "retry":
            if local_size != size:
                print("RETRY mode, " + localfile + " already exists with different size, replacing")
                return True
            elif local_mtime != mtime:
                print("RETRY mode, " + localfile + " already exists with different last modified time, replacing")
                return True
            else:
                print("RETRY mode, " + localfile + " already exists with same size and same time, skipping")
                return False

    else:
        return True


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


def download_object(bucket, object, local_filename,mtime):
    """
    Third API Call: download an object
    """
    if debug:
        print("Downloading object " + str(object) + " from " + str(bucket))

    request_object = "https://" + nsurl + "/txnlogs/api/v1/transaction?bucket_name=" + str(bucket) + "&obj_name=" + str(object)

    if debug:
        print(request_object)

    if not check_download(request_object,local_filename,mtime):
        if debug:
            print("Object " + request_object + " should not be dowloaded")
        return False

    from requests.auth import HTTPBasicAuth
    with requests.get(request_object, auth=HTTPBasicAuth(nsurl, nstoken), stream=True) as r:
        r.raise_for_status()
        r_size = int(r.headers['Content-Length'])
        current_size = 0
        if debug:
            print("Object size:" + str(r_size))

        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
                current_size += len(chunk)
                sys.stdout.write('\r')
                sys.stdout.write(largenumber_to_text(current_size) + "/" + largenumber_to_text(r_size))
                sys.stdout.flush()

    os.utime(local_filename, (mtime, mtime))
    print(" OK")
    return local_filename


# SCRIPT

# read the list of buckets (1 bucket per day)
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

resp = response.json()

if debug:
    print("Buckets retrieved:")
    pp.pprint(resp)

# processing buckets
if resp:
    buckets = resp["ListAllMyBucketResult"]["Buckets"]["Bucket"]

    print("Got " + str(len(buckets)) + " buckets to process, starting...")

    # process each bucket
    for bucket in buckets:
        bucketname = bucket['Name']

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
                object_name = object["Contents"]["Name"]
                object_lastmodified = object["Contents"]["LastModified"]
                object_lastmodified_date = time.strptime(object_lastmodified, "%a %b %d %X %Y")
                object_mtime = calendar.timegm(object_lastmodified_date)

                if timeperiod>0 and object_mtime < timeperiod_calc:
                    print("Skipping too old object " + object_name + ",last modified " + object_lastmodified + ",bucket " + bucketname)
                else:
                    print("Processing object " + object_name)
                    path = str(location) + "/" + str(bucketname)
                    filename = str(path) + "/" + str(object_name)

                    # create folder if needed
                    if not os.path.isdir(path):
                        try:
                            os.mkdir(path)
                        except OSError:
                            print("Creation of the directory %s failed" % path)
                            exit(11)
                        else:
                            print("Successfully created the directory %s " % path)


                    if download_object(bucketname, object_name, filename, object_mtime):

                        object_size=os.stat(filename).st_size

                        # generate the log from the alert
                        curr_time = time.localtime()

                        log = 'time="' + time.strftime('%Y-%m-%d %H:%M:%S %z', curr_time)
                        log += '",bucket="' + str(bucketname)
                        log += '",object="' + str(object_name)
                        log += '",last_time="' + str(object_lastmodified)
                        log += '",size="' + str(object_size) + '"'

                        # print log on the command line
                        print(log)

                        # write log to file
                        if loglevel > 0:
                            logoutput.write(log)
                            logoutput.write('\n')

    else:
        "Error reading bucket list"

if (loglevel > 0):
    logoutput.close()
