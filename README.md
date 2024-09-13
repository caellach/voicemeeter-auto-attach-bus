# voicemeeter-auto-attach-bus

Auto attaches output sound devices to VoiceMeeter

I had issues with my Audeze Maxwell headset not automatically reconnecting to the audio output in Voicemeeter even though it was listed as if it were still connected. My previous Logitech headset did not have an issue with this and I suspect it could be related to how the Audeze dongle will disconnect and reconnect multiple times on headset start/stop.

This python script can be run in the background using Task Scheduler to automatically handle reconnecting the device to the output.

Some minor tuning of the "connect-delay" parameter may be necessary, depending on how long it takes your device to be responsive to output after connecting. 4 seconds works for the Audeze Maxwell on my system.



For easy reference, these are the options:

options:
  -h, --help
			show this help message and exit
  --vendor-id VENDOR_ID
                        Hexadecimal Vendor ID of the device
  --product-id PRODUCT_ID
                        Hexadecimal Product ID of the device
  --connect-delay CONNECT_DELAY
                        Delay in seconds before setting Voicemeeter output after connection
  --bus-index BUS_INDEX
                        The bus index to use in Voicemeeter
  --device-name DEVICE_NAME
                        The name of the device as recognized by Voicemeeter (Name from --list-
                        devices)
  --list-devices
			List all available output devices and exit
  --check-delay CHECK_DELAY
                        Delay in seconds between checking if the device is connected
  --voicemeeter-version {1,2,3,6}
                        Specify the Voicemeeter version to run. (1=Voicemeeter, 2=Banana, 3=Potato, 6=Potato x64)
  --device-type {wdm,ks,mme,asio}
                        Specify the device type (valid values: wdm, ks, mme, asio)
