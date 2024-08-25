from rtkpoint import RTKPOINT

client = RTKPOINT(
    mountpoint='mount2',
    key="7uWkU4RDwM14OP964df1_3vO_SRNgomyOagpD85RrvU45MRkHbCMS4CSp5vwY9k-J87JWSIpH9olQGsmVcbLaQDOxYNsGBRixpT-7eaDK_1LLsypcpd85aPV3Cpz4QuC"
    # username='mkurmot@hotmail.com',
    # password='123456'
)

try:
    client.connect()
except PermissionError:
    print("Invalid API Key or unauthorized access!")
except FileNotFoundError:
    print("Mountpoint not found!")
except ValueError:
    print("Invalid request sent to the server!")
except ConnectionError as ce:
    print(f"Failed to connect to the RTK caster! Error: {ce}")

try:
    for raw_data, parsed_data in client.receive_data():
        print(parsed_data)
        pass
except Exception as e:
    print(f"Error receiving RTK correction data: {e}")
finally:
    try:
        client.disconnect()
    except Exception as e:
        print(f"Failed to disconnect: {e}")