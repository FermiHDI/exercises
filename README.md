<p align="left">
  <img src="https://github.com/FermiHDI/images/blob/main/logos/FermiHDI%20Logo%20Hz%20-%20Dark.png?raw=true" width="500" alt="logo"/>
</p>

# FermiHDI Python Socket Programming Exercise
## Challenge
Write a program using Python 3.12+ that uses the Socket library to receive connections from test_head.py.  test_head.py will send a number of records using the wire protocol bellow on TCP Port 9000 using a number of connections.  The application per connection should decode each packet and load all records into a Pandas DataFrame.  The DataFrame should be aggregated by grouping on columns A and E, simple average of column B, the sum of column C and the minimum of column D.  The aggregated DataFrame should then be printed out to the console.

This means that your application should generate and print a DataFrame for each connections established by test_head.py

Your application should additional display the time in seconds that it took to receive all packets, process the records, and print the resulting DataFrame for each connection.  It should also display the rate in the form of records per second processed by each connection.

Note: test_head will send a record with all 0s ([0]*267) at the end of each connection.  This all 0s records indicates that all records for that connection has been sent.

Your solution must include a Dockerfile to build containers to run your solution and test_head.py. It also must include a Compose file to build and run your solutions containers.

Your solution should be well documented both in a readme file and inline to such extent that any average developer can follow along with what and why you have done.  Your inline documentation should also enable type hinting.  Your solution does not need to have extensive error correction or catching.

## Incoming Socket and Packet Format

TCP Port 9000

#### Wire Protocol Format (All values are encoded with Big Endian):

Packet Format

| Total Length Value (TLV) | Record A  | ...               | Record N  |
| :----------------------: | :-------: | :---------------: | :-------: |
| uint32                   | 267 Bytes | 267 Bytes * (N-2) | 267 Bytes |

** TLV is the packets total length including this element, this should be 4 + (267 * number of records included in the payload)

Record Format

| A      | B      | C     | D     | E                                             |
| :----: | :----: | :---: | :---: | :-------------------------------------------- |
| uint32 | uint16 | fp32  | int8  | ASCII (256 Byte Zero Padded w/ Trailing 0x20) |

