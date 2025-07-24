#!/usr/bin/env python3
# -*- coding: ascii -*-

"""
Filename:      test_head.py
License:       None
Copyright:     Copyright 2025, FermiHDI Ltd.
Author:        Craig Yamato
Contact:       craig.yamato@fermihdi.com
Date:          2025-07-01
Version:       0.0.1
Status:        Proof of Concept (POC)
Description:   Test head for Python Socket Programming Exercise
Dependencies:  
"""

__version__ = "0.0.1"

__author__ = "Craig Yamato"
__copyright__ = "Copyright 2025, FermiHDI Ltd."
__credits__ = ["Craig Yamato"]
__license__ = "None"
__maintainer__ = "Craig Yamato"
__email__ = "craig.yamato@fermihdi.com"
__status__ = "Proof of Concept (POC)"


import multiprocessing
import random
import socket
import sys
import typing


class TestRecord(typing.TypedDict):
    A: bytes  # uint32_t
    B: bytes  # uint16_t
    C: bytes  # float
    D: bytes  # int8_t
    E: bytes  # char[256]
    

class TestHead:
    data: typing.List[TestRecord]
    target_ip: str    
    number_of_records: int
        
    def __init__(self, target_ip: str, number_of_records: int = 1000000):
        """
        Initialize the TestHead object.

        This constructor sets up the initial state of the TestHead object,
        including the target IP address and the number of records to generate.

        Parameters:
        -----------
        target_ip : str
            The IP address of the target server to which data will be sent.
        number_of_records : int, optional
            The number of test records to generate and send. Defaults to 1,000,000.

        Returns:
        --------
        None
        """
        self.target_ip = target_ip
        self.number_of_records = number_of_records
        
    def start(self):
        """
        Start the test data generation and sending process.

        This method initiates the test by generating the specified number of test records
        and then sending the generated data to the target server.

        Parameters:
        -----------
        None

        Returns:
        --------
        None
        """
        self.generate_test_data(self.number_of_records)
        self.send_data()
              
    def generate_test_data(self, number_of_records: int = 1000000):
        """
        Generate test data for the TestHead object.

        This method creates a list of test records, each containing random data
        for fields A, B, C, D, and E. The generated data is stored in the
        'self.data' attribute of the TestHead object.

        Parameters:
        -----------
        number_of_records : int, optional
            The number of test records to generate. Defaults to 1,000,000.

        Returns:
        --------
        None
            The generated data is stored in the 'self.data' attribute.
        """
        self.data = []
        number_list = random.sample(range(1, 256), 5)
        word_list = ['apple', 'banana', 'cherry', 'dates', 'elderberry']
        
        for _ in range(number_of_records):
            text = random.choice(word_list) + " " + random.choice(word_list)
            text_bytes = text.encode('ascii')
            text_bytes_ = bytearray([0x20]*256)
            text_bytes_[:len(text_bytes)] = text_bytes
            
            self.data.append({
                'A': random.choice(number_list).to_bytes(4, 'big'),
                'B': random.randint(0, 65535).to_bytes(2, 'big'),
                'C': random.uniform(1.18*10**-38, 3.40*10**38),
                'D': random.randint(-128, 127).to_bytes(1, 'big'),
                'E': bytes(text_bytes_)
            })
    
    def send_data(self):
        """
        Send the generated test data to the target server.

        This method creates a socket connection to the target server and sends the
        generated test data in packets. Each packet contains up to 4 records, with
        a maximum size of 1200 bytes. The method handles the packaging of data,
        sending of packets, and proper closure of the socket connection.

        Parameters:
        -----------
        None

        Returns:
        --------
        None

        Raises:
        -------
        Exception
            If there's an error while sending the packet, the exception is caught
            and its message is printed.

        Notes:
        ------
        - The method uses a TCP socket connection to send data.
        - The target IP and port (9000) are used for the connection.
        - Each packet starts with a 4-byte header (1072 in big-endian).
        - Records are packed into the packet using TLV (Type-Length-Value) format.
        - If less than 4 records are available for the last packet, the remaining
          space is filled with zeros.
        - The socket is closed after all data is sent or if an exception occurs.
        """
        packet:bytearray = bytearray(1200)
        packet[:4] = (1072).to_bytes(4, 'big')
        tlv: int = 4
        records_in_packet = 0
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.target_ip, 9000))
        
        try:
            for record in self.data:
                packet[tlv:tlv+4] = record['A']
                tlv += 4
                packet[tlv:tlv+2] = record['B']
                tlv += 2
                packet[tlv:tlv+4] = record['C'].to_bytes(4, 'big')
                tlv += 4
                packet[tlv:tlv+1] = record['D']
                tlv += 1
                packet[tlv:tlv+256] = record['E']
                tlv += 256
                records_in_packet += 1
                
                if records_in_packet == 4:
                    self.socket.sendall(packet[:tlv])
                    records_in_packet = 0
                    tlv = 4
            
            packet[tlv:tlv+267] = bytearray([0]*267)
            tlv += 267
            self.socket.sendall(packet[:tlv])
            
        except Exception as e:
            print(f"Error sending packet: {str(e)}")
            
        finally:
            self.socket.close()
            print("Socket closed")
    
        print(f"Sent {len(self.data)} records to {self.target_ip}")


if __name__ == "__main__":
    arg_list = sys.argv[1:]
    
    if len(arg_list) < 1 :
        print("Usage: python test_head.py <target_ip> <number_of_records> (default: 1,000,000)")
        sys.exit(1)
        
    target_ip = arg_list[0]
    number_of_records = 1000000 if len(arg_list) != 2 else int(arg_list[1])
    test_head = TestHead(target_ip)
    
    for _ in range(10):
        multiprocessing.Process(target=test_head.start).start()
        
    print("Finished sending packets on all processes")