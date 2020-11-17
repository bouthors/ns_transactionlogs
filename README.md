# ns_transaction.py
This python script is designed to easily download and archive Netskope transaction logs.

## Requirements
Tested with python3.7 and the following librairies:
- requests
- pyyaml

## Installation
Download the script and copy the sample configuration file.

## Configuration
Edit the yaml config file.

Settings:
- Netskope API Section
    - url : domain of your netskope tenant like "mytenant.goskope.com" or "mytenant.eu.goskope.com"
    - token : API Token found in the admin console under "Settings > Tools > REST API" ("Advance Settings" admin right is required)
    - location: where you want to store the files
    - verifyssl : used to configure destination ssl check. Can be True, False or root CA file used to check destination url. Provided root CA is useful if you apply SSL inspection with Netskope Proxy.

- existing_file: Select mode for existing files in destination location, allowed values:
  - "replace": overwrite any existing file with new ones
  - "retry": overwrite if size is different
  - "skip": skip all existing file, even if the file has different size
existing_file: "retry"

- timeperiod: number of previous hours to retrieve  (0 to retrieve all)

- Log section
  - level: level of verbosity
    - 0 : disabled
    - 1 : downloaded files only
    - 2 : all files (log skipped files)
    - 3 : all files + all objects excluded by timeperiod setting
  - file: destination file for logs

## Usage

ns_transactionlogs.py --configfile config.yaml [--debug]

## Example

    Got 7 buckets to process, using retry mode, starting...
    Processing bucket 20201110
    Processing bucket 20201111
    Processing bucket 20201105
    Processing bucket 20201116
    time="2020-11-17 13:44:37 +0100",bucket="20201116",object="transaction-events-c7688e38136dc5dfb5c5778d8dcbce47-50400-57600_0.gz",last_modified="Mon Nov 16 16:41:02 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:37 +0100",bucket="20201116",object="transaction-events-bb4571df972b0babfa58caad5ee74896-7200-14400_0.gz",last_modified="Mon Nov 16 05:06:27 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:37 +0100",bucket="20201116",object="transaction-events-bb4571df972b0babfa58caad5ee74896-64800-72000_0.gz",last_modified="Mon Nov 16 21:03:38 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:38 +0100",bucket="20201116",object="transaction-events-c7688e38136dc5dfb5c5778d8dcbce47-72000-79200_0.gz",last_modified="Mon Nov 16 23:12:10 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:38 +0100",bucket="20201116",object="transaction-events-bb4571df972b0babfa58caad5ee74896-0-7200_0.gz",last_modified="Mon Nov 16 02:09:09 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:38 +0100",bucket="20201116",object="transaction-events-c7688e38136dc5dfb5c5778d8dcbce47-7200-14400_0.gz",last_modified="Mon Nov 16 05:06:27 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:38 +0100",bucket="20201116",object="transaction-events-bb4571df972b0babfa58caad5ee74896-43200-50400_0.gz",last_modified="Mon Nov 16 22:39:06 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:38 +0100",bucket="20201116",object="transaction-events-c7688e38136dc5dfb5c5778d8dcbce47-28800-36000_0.gz",last_modified="Mon Nov 16 10:22:15 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:38 +0100",bucket="20201116",object="transaction-events-c7688e38136dc5dfb5c5778d8dcbce47-79200-86400_0.gz",last_modified="Tue Nov 17 01:21:34 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:39 +0100",bucket="20201116",object="transaction-events-bb4571df972b0babfa58caad5ee74896-72000-79200_0.gz",last_modified="Mon Nov 16 23:12:11 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:39 +0100",bucket="20201116",object="transaction-events-bb4571df972b0babfa58caad5ee74896-50400-57600_0.gz",last_modified="Mon Nov 16 16:40:50 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:39 +0100",bucket="20201116",object="transaction-events-c7688e38136dc5dfb5c5778d8dcbce47-14400-21600_0.gz",last_modified="Mon Nov 16 06:38:24 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:39 +0100",bucket="20201116",object="transaction-events-c7688e38136dc5dfb5c5778d8dcbce47-64800-72000_0.gz",last_modified="Mon Nov 16 21:00:35 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:39 +0100",bucket="20201116",object="transaction-events-bb4571df972b0babfa58caad5ee74896-21600-28800_0.gz",last_modified="Mon Nov 16 08:22:38 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:39 +0100",bucket="20201116",object="transaction-events-c7688e38136dc5dfb5c5778d8dcbce47-43200-50400_0.gz",last_modified="Mon Nov 16 22:39:12 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:40 +0100",bucket="20201116",object="transaction-events-c7688e38136dc5dfb5c5778d8dcbce47-21600-28800_0.gz",last_modified="Mon Nov 16 08:22:38 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:40 +0100",bucket="20201116",object="transaction-events-c7688e38136dc5dfb5c5778d8dcbce47-36000-43200_0.gz",last_modified="Mon Nov 16 13:12:22 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:40 +0100",bucket="20201116",object="transaction-events-c7688e38136dc5dfb5c5778d8dcbce47-0-7200_0.gz",last_modified="Mon Nov 16 02:09:09 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:40 +0100",bucket="20201116",object="transaction-events-bb4571df972b0babfa58caad5ee74896-14400-21600_0.gz",last_modified="Mon Nov 16 06:38:24 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:40 +0100",bucket="20201116",object="transaction-events-bb4571df972b0babfa58caad5ee74896-28800-36000_0.gz",last_modified="Mon Nov 16 10:22:21 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:40 +0100",bucket="20201116",object="transaction-events-bb4571df972b0babfa58caad5ee74896-57600-64800_0.gz",last_modified="Mon Nov 16 18:50:40 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:40 +0100",bucket="20201116",object="transaction-events-bb4571df972b0babfa58caad5ee74896-36000-43200_0.gz",last_modified="Mon Nov 16 13:12:22 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:41 +0100",bucket="20201116",object="transaction-events-c7688e38136dc5dfb5c5778d8dcbce47-57600-64800_0.gz",last_modified="Mon Nov 16 18:50:16 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:41 +0100",bucket="20201116",object="transaction-events-bb4571df972b0babfa58caad5ee74896-79200-86400_0.gz",last_modified="Tue Nov 17 01:21:40 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    Processing bucket 20201108
    Processing bucket 20201115
    time="2020-11-17 13:44:41 +0100",bucket="20201115",object="transaction-events-c7688e38136dc5dfb5c5778d8dcbce47-72000-79200_0.gz",last_modified="Sun Nov 15 22:00:01 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:41 +0100",bucket="20201115",object="transaction-events-c7688e38136dc5dfb5c5778d8dcbce47-79200-86400_0.gz",last_modified="Mon Nov 16 07:14:03 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:42 +0100",bucket="20201115",object="transaction-events-bb4571df972b0babfa58caad5ee74896-72000-79200_0.gz",last_modified="Sun Nov 15 21:59:22 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    time="2020-11-17 13:44:42 +0100",bucket="20201115",object="transaction-events-bb4571df972b0babfa58caad5ee74896-79200-86400_0.gz",last_modified="Mon Nov 16 00:38:47 2020",size="0",action="skip",reason="same size and same time",mode="retry",size=""
    Processing bucket 20201117
    175.099KB/175.099KB OK
    time="2020-11-17 13:44:42 +0100",bucket="20201117",object="transaction-events-bb4571df972b0babfa58caad5ee74896-7200-14400_0.gz",last_modified="Tue Nov 17 05:41:00 2020",size="0",action="download",reason="new file",mode="retry",size="179301"
    198.417KB/198.417KB OK
    time="2020-11-17 13:44:42 +0100",bucket="20201117",object="transaction-events-bb4571df972b0babfa58caad5ee74896-0-7200_0.gz",last_modified="Tue Nov 17 03:35:32 2020",size="0",action="download",reason="new file",mode="retry",size="203179"
    197.014KB/197.014KB OK
    time="2020-11-17 13:44:43 +0100",bucket="20201117",object="transaction-events-c7688e38136dc5dfb5c5778d8dcbce47-7200-14400_0.gz",last_modified="Tue Nov 17 05:40:47 2020",size="0",action="download",reason="new file",mode="retry",size="201742"
    170.731KB/170.731KB OK
    time="2020-11-17 13:44:43 +0100",bucket="20201117",object="transaction-events-c7688e38136dc5dfb5c5778d8dcbce47-14400-21600_0.gz",last_modified="Tue Nov 17 07:52:44 2020",size="0",action="download",reason="new file",mode="retry",size="174829"
    208.995KB/208.995KB OK
    time="2020-11-17 13:44:43 +0100",bucket="20201117",object="transaction-events-c7688e38136dc5dfb5c5778d8dcbce47-0-7200_0.gz",last_modified="Tue Nov 17 03:35:31 2020",size="0",action="download",reason="new file",mode="retry",size="214011"
    170.844KB/170.844KB OK
    time="2020-11-17 13:44:43 +0100",bucket="20201117",object="transaction-events-bb4571df972b0babfa58caad5ee74896-14400-21600_0.gz",last_modified="Tue Nov 17 07:52:56 2020",size="0",action="download",reason="new file",mode="retry",size="174944"
    Stats: 7 buckets found with a total of 34 objects processed with retry mode
     - 0 excluded with timeperiod
     - 28 skipped
     - 6 downloaded
       - 0 replaced
       - 6 new
     Total bytes downloaded: 1.095MB