# insta360

This python package implements both [RTMP (Real-Time Messaging Protocol)](https://en.wikipedia.org/wiki/Real-Time_Messaging_Protocol) and [OSC (Open Spherical Camera)](https://developers.google.com/streetview/open-spherical-camera) protocols for interacting with Insta360 cameras.

While OSC is an open standard for controlling spherical cameras, RTMP is a proprietary protocol used by Insta360 cameras for many of its core functionalities. This package aims to provide a unified interface for interacting with Insta360 cameras by reverse engineering the proprietary RTMP protocol and implementing the open OSC protocol.

The RTMP protocol is implemented by reverse engineering the communication between Insta360 cameras and the official Android app. OSC is implemented with respect to the official [OSC API v2 specification](https://developers.google.com/streetview/open-spherical-camera).

Documentation is available at [https://insta360.whitebox.aero](https://insta360.whitebox.aero).

# Compatibility

While the package is developed and tested with Insta360 X3 and X4, it should work with other Insta360 cameras as well. If you find any compatibility issues, please open an issue. PRs are also welcome to improve the compatibility with other Insta360 cameras.

Here is a list all the functions that are implemented and tested and their compatibility with different Insta360 cameras:

**Stream Resolutions:**

- X3: 1440 × 720 at 30fps (Any higher or lower resolution yields glitchy stream)
- X4: 2880 × 1440 at 30fps (Hardcoded at hardware level)

**Legend:**

- ✅: Implemented and tested
- ❌: Not implemented
- 🟡: Implemented but broken
- 🚫: Not suppported by device

**RTMP Module:**

| Functionality              | Implemented | X3  | X4  |
| :------------------------- | :---------: | :-: | :-: |
| sync_local_time_to_camera  |     ✅      | ✅  | ✅  |
| get_camera_info            |     ✅      | ✅  | ✅  |
| take_picture               |     ✅      | ✅  | ✅  |
| get_camera_files_list      |     ✅      | ✅  | ✅  |
| set_normal_video_options   |     ✅      | ✅  | ✅  |
| get_normal_video_options   |     ✅      | ✅  | ✅  |
| start_capture              |     ✅      | ✅  | ✅  |
| stop_capture               |     ✅      | ✅  | ✅  |
| get_capture_current_status |     ✅      | ✅  | ✅  |
| start_live_stream          |     🟡      | 🟡  | 🚫  |
| stop_live_stream           |     ✅      | ✅  | 🚫  |
| start_preview_stream       |     ✅      | ✅  | ✅  |
| stop_preview_stream        |     ✅      | ✅  | ✅  |
| get_camera_type            |     ❌      | ❌  | ❌  |
| get_serial_number          |     ❌      | ❌  | ❌  |
| get_exposure_settings      |     ❌      | ❌  | ❌  |
| set_exposure_settings      |     ❌      | ❌  | ❌  |
| set_capture_settings       |     ❌      | ❌  | ❌  |
| get_capture_settings       |     ❌      | ❌  | ❌  |
| get_camera_uuid            |     ❌      | ❌  | ❌  |
| set_time_lapse_options     |     ❌      | ❌  | ❌  |
| start_time_lapse           |     ❌      | ❌  | ❌  |
| stop_time_lapse            |     ❌      | ❌  | ❌  |
| is_camera_connected        |     ❌      | ❌  | ❌  |
| get_battery_status         |     ❌      | ❌  | ❌  |
| get_storage_state          |     ❌      | ❌  | ❌  |

**OSC Module:**

| Functionality    | Implemented | X3  | X4  |
| :--------------- | :---------: | :-: | :-: |
| list_files       |     ✅      | ✅  | ✅  |
| delete_files     |     ✅      | ✅  | ✅  |
| download_file    |     ✅      | ✅  | ✅  |
| take_picture     |     ❌      | ❌  | ❌  |
| process_picture  |     ❌      | ❌  | ❌  |
| start_capture    |     ❌      | ❌  | ❌  |
| stop_capture     |     ❌      | ❌  | ❌  |
| get_live_preview |     ❌      | ❌  | ❌  |
| set_options      |     ❌      | ❌  | ❌  |
| get_options      |     ❌      | ❌  | ❌  |
| reset            |     ❌      | ❌  | ❌  |
| switch_wifi      |     ❌      | ❌  | ❌  |
| upload_file      |     ❌      | ❌  | ❌  |

# Installation

To install the package, run the following command:

```bash
pip install insta360
```

# Usage

First make sure you are [connected](#connecting-to-the-wifi) to the camera's WiFi network.

The package provides two modules, `rtmp` and `osc`, for interacting with Insta360 cameras using RTMP and OSC protocols, respectively. OSC being an open standard, could be considered as more reliable and stable compared to RTMP. However, RTMP provides some functionalities that are not available in OSC. Depending on your use case, you can choose to use either of the modules.

Below are some examples of how to use the `rtmp` and `osc` modules. For more detailed information, refer to the [documentation](https://insta360.whitebox.aero).

Here is an example of how to use the `rtmp` module:

```python
import time
from insta360.rtmp import Client

# Create an RTMP client
client = Client()

# Start capturing video
client.start_capture()
time.sleep(10)

# Stop capturing video
client.stop_capture()
time.sleep(5)

# Close the client
client.close()
```

And here is an example of how to use the `osc` module:

```python
import time
from insta360.osc import Client

# Create an OSC client
client = Client()

# List all files on the camera
files = client.list_files()
print(files)

# Download the first file
file = files.results.entries[0]
self.osc_client.download_file(file.fileUrl, f"./{file.name}")

# Delete the first file
client.delete_files([file.fileUrl])
```

# Connecting to the WiFi

<a id="connecting-to-the-wifi"></a>
Start your camera and soon after you will see a WiFi network with the name `YOUR_CAMERA_MODEL_NAME.OSC`. Connect to this network using the password `88888888`. If you are using Insta360 X4, the password is randomly generated during the device setup. In this case, you can find the password on your camera by navigating to `Settings > WiFi Settings > Password`.

Although the security issue of having a fixed password is no longer present in recent models like the Insta360 X4 and you can change the wifi password on cameras like this Insta360 X3, this is an **huge security hole** for older models.

Any host in the nearby can connect to these older models as soon they are turned on; once estabilished the connection they can also do a **telnet** into the Insta360's GNU/Linux operating system as **root** (the IP address of the camera is **192.168.42.1**) and do whaterver they want, even to damage permanently (brick) the camera.

## The Protobuf problem

The messages exchanged from the Android app and the camera
use the **Protocol Buffers**, which is an open standard by Google.

Unfortunately the protobuf messages are not self-describing;
that is, there is no way to tell the names, meaning, or full
datatypes of exchanged messages without an external
specification. To write an understandable source code you need
to extract the specific language description files from a
compiled binary file, e.g. a library from the Android app. To
run the insta360.py module you need such files compiled for
Python. Follow the link at the bottom of this page to get more
instructions.

## The insta360_cmd program

The **insta360_cmd** is a somewhat working example using the insta360.py module. It has the basic functionality required for a remote control: start and stop recording, get livestream or preview stream. You can run it from an Android smartphone if you install the [Termux](https://termux.dev/en/) app and the required Python libraries.

We are working to make installing this program easier, but for now you can clone the repository and run the following command to install the required packages:

```bash
pip3 install -r ./requirements.txt
```

Then, run the following command to run the program:

```bash
# Previw and capture simultaneously
python3 insta360_cmd -o ./output/dump.mp4 -c preview -c capture

# Get live stream
python3 insta360_cmd -o ./output/dump.mp4 -c livestream

# Start recording
python3 insta360_cmd -c capture

# Know all the options
python3 insta360_cmd -h
```

![insta360_cmd screenshot](https://gitlab.com/whitebox-aero/insta360/-/raw/main/assets/insta360_cmd.jpg "insta360_cmd screenshot")

## Docs

Documentation is auto-generated generated with [MkDocs](https://www.mkdocs.org/). While contributing, make sure to follow [google docstring conventions](https://mkdocstrings.github.io/griffe/docstrings/#google-style) when documenting the code.

To generate the docs, first install the required packages:

```bash
pip3 install -r ./requirements/requirements.docs.txt
```

Then, run the following command to run the server:

```bash
mkdocs serve
```
