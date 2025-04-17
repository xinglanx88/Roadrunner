def gpsNMEA():
    import serial
    import pynmea2

    # Open serial connection
    # Will print data with or without connection
    ser = serial.Serial('/dev/ttyACM0', 38400, timeout=1)

    while True:
        line = ser.readline().decode('ascii', errors='replace').strip()
        
        if line.startswith('$GNGGA'):  # Adjust if needed (e.g., $GPGGA, $GNGGA, $GNRMC)
            try:
                msg = pynmea2.parse(line)
                print(f"Latitude:  {msg.latitude:.4f} {msg.lat_dir}")
                print(f"Longitude: {msg.longitude:.4f} {msg.lon_dir}")
                print(f"Altitude:  {msg.altitude}m")
                print(f"Satellites: {msg.num_sats}")
                print(f"Fix: {'No fix' if msg.gps_qual == 0 else 'GPS fix' if msg.gps_qual == 1 else 'DGPS fix'}")
                print("-" * 40)
            except pynmea2.ParseError:
                pass