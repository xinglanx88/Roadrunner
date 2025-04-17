import os
import subprocess

# Function to run shell commands
def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")

# 1. Install Dependencies
def install_dependencies():
    print("\nInstalling required dependencies...")
    dependencies = [
        "sudo apt-get update",
        "sudo apt-get install -y gstreamer1.0-plugins-base gstreamer1.0-plugins-good",
        "sudo apt-get install -y gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly",
        "sudo apt-get install -y v4l-utils",
        "sudo apt-get install -y nvidia-l4t-multimedia"
    ]
    
    for dep in dependencies:
        run_command(dep)

# 2. Check Camera Connection
def check_camera():
    run_command("sudo systemctl restart nvargus-daemon")
    print("\nChecking connected video devices...\n")
    run_command("v4l2-ctl --list-devices")

    print("\nChecking supported video formats...\n")
    run_command("v4l2-ctl --device=/dev/video0 --list-formats-ext")

# 3. Run GStreamer Pipeline with Custom Input
def run_gstreamer():
    print("\nEnter camera settings:")
    
    SENSOR_ID=0
    FRAMERATE= input("Enter framerate (default: 21): ") or "21"
    width= input("Enter width (default: 4032): ") or "4032"
    height= input("Enter height (default: 3040): ") or "3040"
    gst_command3 = f"GST_DEBUG=3 gst-launch-1.0 nvarguscamerasrc sensor-id=0 ! 'video/x-raw(memory:NVMM),width=1920,height=1080,framerate=30/1' ! nvvidconv ! nveglglessink"



    print(f"\nStarting GStreamer with {width}x{height} at {FRAMERATE} FPS...\n")


    
    # gst_command2 = f"gst-launch-1.0 nvarguscamerasrc sensor-id=0 ! 'video/x-raw(memory:NVMM), width={width}, height={height}, framerate={framerate}/1, format=NV12' ! nvvidconv ! videoconvert ! autovideosink"

    # gst_command = f"gst-launch-1.0 v4l2src device=/dev/video0 ! 'video/x-raw,format=NV12,width={width},height={height},framerate={framerate}/1' ! videoconvert ! autovideosink"
    run_command(gst_command3)

# Main Menu
def main():
    while True:
        print("\nJetson Camera Setup & Testing")
        print("1. Install Dependencies")
        print("2. Check Camera Connection")
        print("3. Run GStreamer Display (Custom Resolution & FPS)")
        print("4. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            install_dependencies()
        elif choice == "2":
            check_camera()
        elif choice == "3":
            run_gstreamer()
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice, please select a valid option.")

if __name__ == "__main__":
    main()
