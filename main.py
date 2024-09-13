import argparse
import time
import pywinusb.hid as hid
import os
import ctypes

# Voicemeeter Remote API (default path)
VMR_PATH = "C:\\Program Files (x86)\\VB\\Voicemeeter\\VoicemeeterRemote64.dll"
VOICEMEETER_DLL = ctypes.WinDLL(VMR_PATH)

def voicemeeter_login(voicemeeter_version, retries=10, retry_delay=3):
    """
    Attempts to login to Voicemeeter. If Voicemeeter is not running, it will attempt
    to start it with the specified version. Retries a few times if the login fails.

    Args:
        voicemeeter_version (int): The version of Voicemeeter to run. (1=Voicemeeter, 2=Banana, 3=Potato, 6=Potato x64)
        retries (int): Number of retries for the login process.
        retry_delay (int): Delay in seconds between retry attempts.

    Returns:
        bool: True if successfully logged in, False if all attempts failed.
    """
    voicemeeter_started = False

    for attempt in range(retries):
        val = VOICEMEETER_DLL.VBVMR_Login()

        if val < 0:
            print(f"Voicemeeter connection failed on attempt {attempt + 1}. Retrying...")
            time.sleep(retry_delay)
            continue  # Retry

        elif val == 1 and not voicemeeter_started:
            print(f"Voicemeeter is not running, attempting to start Voicemeeter version {voicemeeter_version}...")
            # Start Voicemeeter with the specified version
            VOICEMEETER_DLL.VBVMR_RunVoicemeeter(voicemeeter_version)
            voicemeeter_started = True
            # Wait a bit for Voicemeeter to start
            time.sleep(5)
            print("Waiting for Voicemeeter to become available...")

        elif val == 0:
            # Successful login
            print("Successfully connected to Voicemeeter!")
            return True

        else:
            print(f"Attempt {attempt + 1}: Voicemeeter still not available, retrying...")
            time.sleep(retry_delay)

    print("Failed to connect to Voicemeeter after multiple attempts.")
    return False  # Failed after retries


def get_device_connected():
    devices = hid.HidDeviceFilter(vendor_id=VENDOR_ID, product_id=PRODUCT_ID).get_devices()
    return len(devices) > 0


def get_output_device_list():
    device_count = VOICEMEETER_DLL.VBVMR_Output_GetDeviceNumber()
    print("Voicemeeter Device Count: ", device_count)
    for i in range(device_count):
        device_type = ctypes.pointer(ctypes.c_long())
        device_name = ctypes.pointer(ctypes.create_string_buffer(256))
        device_hardware_id = ctypes.pointer(ctypes.create_string_buffer(256))
        
        # Get the device information
        VOICEMEETER_DLL.VBVMR_Output_GetDeviceDescA(i, device_type, device_name, device_hardware_id)
        print(f"Device {i}: Type={device_type.contents.value}, Name={device_name.contents.value.decode()}, Hardware ID={device_hardware_id.contents.value.decode()}")

#="Speakers (Game-Audeze Maxwell)"
def set_voicemeeter_output(bus_index, device_type, device_name):
    parameter_name = ctypes.pointer(ctypes.create_string_buffer(256))
    parameter_value = ctypes.pointer(ctypes.create_string_buffer(256))
    parameter_name.contents.value = f"Bus[{bus_index}].device.{device_type}".encode()
    parameter_value.contents.value = device_name.encode()
    VOICEMEETER_DLL.VBVMR_SetParameterStringA(parameter_name, parameter_value)
    print(f"Set Bus[{bus_index}].device.{device_type} to {device_name}")


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Voicemeeter Output Sound Device Connection Automation")
    parser.add_argument('--list-devices', action='store_true', help='List all available output devices and exit')
    parser.add_argument('--vendor-id', type=lambda x: int(x, 16), help='Hexadecimal Vendor ID of the device (0x1234)')
    parser.add_argument('--product-id', type=lambda x: int(x, 16), help='Hexadecimal Product ID of the device (0x5678)')
    parser.add_argument('--device-name', type=str, help='The name of the device as recognized by Voicemeeter (use Name from --list-devices)')
    parser.add_argument('--device-type', type=str, choices=['wdm', 'ks', 'mme', 'asio'], help='Specify the device type (wdm, ks, mme, asio)')
    parser.add_argument('--bus-index', type=int, help='The bus index to use in Voicemeeter (0=A1, 1=A2, 2=A3, etc)')
    parser.add_argument('--voicemeeter-version', type=int, default=6, choices=[1, 2, 3, 6], help='Specify the Voicemeeter version to run. (1=Voicemeeter, 2=Banana, 3=Potato, 6=Potato x64)')
    parser.add_argument('--check-delay', type=int, default=1, help='Delay in seconds between checking if the device is connected')
    parser.add_argument('--connect-delay', type=int, default=4, help='Delay in seconds before setting Voicemeeter output after connection')
    args = parser.parse_args()

    if args.list_devices:
        if not voicemeeter_login(args.voicemeeter_version):
            print("Exiting due to failed Voicemeeter login.")
            exit(1)
        get_output_device_list()
        exit()

    global VENDOR_ID, PRODUCT_ID, CONNECT_DELAY
    VENDOR_ID = args.vendor_id
    PRODUCT_ID = args.product_id
    CONNECT_DELAY = args.connect_delay

    if CONNECT_DELAY < 0:
        CONNECT_DELAY = 1
    
    if args.connect_delay < 0:
        args.connect_delay = 1
    
    if not (args.vendor_id and args.product_id and args.bus_index and args.device_name and args.device_type):
        parser.error("All required parameters (--vendor-id, --product-id, --bus-index, --device-name, --device-type) must be provided unless --list-devices is used.")

    previously_connected = False
    if not voicemeeter_login(args.voicemeeter_version):
        print("Exiting due to failed Voicemeeter login.")
        exit(1)

    while True:
        connected = get_device_connected()

        if connected and not previously_connected:
            # Headset was previously disconnected and is now connected
            print("Headset connected!")
            if CONNECT_DELAY > 0:
                print(f"Waiting {CONNECT_DELAY} seconds before setting Voicemeeter output")
                time.sleep(CONNECT_DELAY)
            set_voicemeeter_output(args.bus_index, args.device_type, args.device_name)
            previously_connected = True
        elif not connected and previously_connected:
            # Headset was previously connected but is now disconnected
            print("Headset disconnected!")
            previously_connected = False

        # Sleep for before checking again
        time.sleep(args.check_delay)
    VOICEMEETER_DLL.VBVMR_Logout()


if __name__ == "__main__":
    main()