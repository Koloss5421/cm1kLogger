# cm1kLogger
Python based, Netgear CM-1000 Docsis Status Logger for splunk ingestion. Outputs Json Format. 

### Usage:
python3 cm1kLogger.py [-h] [--debug] logfile

#### positional arguments:
  logfile    |   The destination of the json log output.

#### optional arguments:
  -h, --help   | show this help message and exit
  
  --debug, --d | Enable debug logging.

### Splunk Sourcetype Settings:
```
KV_MODE = json
INDEXED_EXTRACTIONS = json
LINE_BREAKER = ([\r\n]+)
TIMESTAMP_FIELDS = \s\"date\":\s\"
TIME_FORMAT = %Y-%m-%d %H:%M:%S.%q
TZ = <YourTZ>
```
