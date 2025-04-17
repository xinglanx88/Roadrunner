import serial

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

print("Waiting for GPS data...")
for _ in range(20):  # Print 20 lines of raw data
    line = ser.readline().decode('ascii', errors='replace').strip()
    print(f"Raw data: {line}")