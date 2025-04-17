import serial
import pynmea2
import time

# Same as gpsNMEA, but waits till it finds a GPS signal

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

print("Waiting for GPS fix... This may take several minutes")
while True:
    line = ser.readline().decode('ascii', errors='replace').strip()
    
    if line.startswith('$GNGGA'):
        try:
            msg = pynmea2.parse(line)
            print(f"Latitude:  {msg.latitude if msg.latitude else 'No fix'}")
            print(f"Longitude: {msg.longitude if msg.longitude else 'No fix'}")
            print(f"Satellites: {msg.num_sats}")
            print(f"Fix quality: {msg.gps_qual} (0=No fix, 1=GPS fix)")
            print("-" * 40)
        except pynmea2.ParseError:
            pass
    
    time.sleep(10)
    print("Still waiting for GPS fix...")