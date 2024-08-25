## RTKPOINT Python Package

Welcome to the RTKPOINT Python package, a comprehensive solution for handling RTK (Real-Time Kinematic) corrections through NTRIP (Networked Transport of RTCM via Internet Protocol) caster services. This package allows you to seamlessly connect to an NTRIP caster, manage RTK data streams, and ensure accurate positioning for your applications.

### Installation

You can install the RTKPOINT package via pip:
```sh
pip install rtkpoint
```

### Usage

Basic Example
```python
from rtkpoint import RTKPOINT

# Initialize the RTKPOINT client with your API key and mountpoint
client = RTKPOINT(key='your_api_key', mountpoint='your_mountpoint')

# Connect to the NTRIP caster
client.connect()

# Receive RTCM data from the stream
for raw_data, parsed_data in client.receive_data():
    print(raw_data, parsed_data)
```

### Error Handling

RTKPOINT handles common issues such as invalid API keys, connection errors, and data streaming interruptions.

Example:
```python
try:
    client.connect()
except PermissionError:
    print("Unauthorized access. Please check your API key.")
except FileNotFoundError:
    print("Mountpoint not found. Please check the mountpoint URL.")
except ValueError:
    print("Invalid request.")
except ConnectionError as e:
    print(f"Connection failed: {e}")
```

This README provides a concise overview of your package and directs users to the [official documentation] (https://rtkpoint.com/docs) for more information.