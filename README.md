#ns_transaction.py
This python script is designed to easily download and archive Netskope transaction logs.

##Requirements
Tested with python3.7 and the following librairies:
- requests
- pyyaml

##Installation
Download the script and copy the sample configuration file.

##Configuration
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

##Usage

ns_transactionlogs.py --configfile config.yaml [--debug]

