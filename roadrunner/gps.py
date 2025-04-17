import serial
from pyubx2 import UBXReader
import time

# Outdated, but original version of what I was running

# Open the serial port (try common baud rates: 9600, 38400, 115200)
try:
    ser = serial.Serial('/dev/ttyACM0', 38400, timeout=1)
    print("GPS Module Connected (UBX Mode)")
except Exception as e:
    print(f"Error opening serial port: {e}")
    exit(1)

# Create a UBX reader
ubr = UBXReader(ser)

print("Waiting for GPS data...")

try:
    while True:
        try:
            # Read and parse UBX message
            (raw_data, parsed_data) = ubr.read()
            
            # Check if it's a valid navigation message
            if parsed_data.identity == "NAV-PVT":
                print("\n--- GPS Position & Time (UBX) ---")
                
                # Latitude & Longitude (degrees)
                lat = parsed_data.lat / 1e7  # Convert from 1e-7 degrees
                lon = parsed_data.lon / 1e7
                print(f"Latitude: {lat:.6f}° {'N' if lat >= 0 else 'S'}")
                print(f"Longitude: {lon:.6f}° {'E' if lon >= 0 else 'W'}")
                
                # Altitude (meters)
                print(f"Altitude: {parsed_data.height / 1000:.2f} m")
                
                # Speed (km/h)
                speed_kmh = parsed_data.gSpeed * 0.0036  # Convert mm/s to km/h
                print(f"Speed: {speed_kmh:.2f} km/h")
                
                # Time (UTC)
                print(f"Time: {parsed_data.hour:02d}:{parsed_data.min:02d}:{parsed_data.second:02d}")
                print(f"Date: {parsed_data.day:02d}/{parsed_data.month:02d}/{parsed_data.year}")
                
                # Fix Type
                fix_type = {
                    0: "No Fix",
                    1: "Dead Reckoning",
                    2: "2D Fix",
                    3: "3D Fix",
                    4: "GNSS + Dead Reckoning"
                }.get(parsed_data.fixType, "Unknown")
                print(f"Fix Type: {fix_type}")
                
                # Satellites
                print(f"Satellites: {parsed_data.numSV}")
                print("-" * 40)
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)
            
finally:
    ser.close()