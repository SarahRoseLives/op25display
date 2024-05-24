import time
import requests
import threading

# Global variable to track connection status
connection_successful = False


def jsoncmd(command, arg1, arg2, url):
    global connection_successful

    try:
        # Define the JSON payload
        payload = [{"command": command, "arg1": arg1, "arg2": arg2}]

        # Send the POST request
        response = requests.post(url, json=payload)

        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            connection_successful = True
            return response.json()
        else:
            connection_successful = False
            return {"error": f"Failed to retrieve data. Status Code: {response.status_code}"}
    except Exception as e:
        connection_successful = False
        return {"error": f"An error occurred: {e}"}


def get_latest_values(url):
    try:
        # Call the jsoncmd function to send the command
        response_data = jsoncmd("update", 0, 0, url)

        # Check if response_data is empty
        if not response_data:
            # print("Response data is empty")
            return {}

        # Initialize a dictionary to store the latest values
        latest_values = {}

        # Iterate through the list of dictionaries in the response
        for item in response_data:
            # Extract values for 'change_freq' json_type
            if item.get("json_type") == "change_freq":
                latest_values['change_freq'] = {
                    "freq": item.get("freq"),
                    "tgid": item.get("tgid"),
                    "offset": item.get("offset"),
                    "tag": item.get("tag"),
                    "nac": item.get("nac"),
                    "system": item.get("system"),
                    "center_frequency": item.get("center_frequency"),
                    "tdma": item.get("tdma"),
                    "wacn": item.get("wacn"),
                    "sysid": item.get("sysid"),
                    "tuner": item.get("tuner"),
                    "sigtype": item.get("sigtype"),
                    "fine_tune": item.get("fine_tune"),
                    "error": item.get("error"),
                    "stream_url": item.get("stream_url"),
                }

            # Extract values for 'trunk_update' json_type
            elif item.get("json_type") == "trunk_update":
                trunk_update_data = item.get(str(item.get("nac")))  # Corrected line
                if trunk_update_data:
                    latest_values['trunk_update'] = {
                        "top_line": trunk_update_data.get("top_line"),
                        "syid": trunk_update_data.get("syid"),
                        "rfid": trunk_update_data.get("rfid"),
                        "stid": trunk_update_data.get("stid"),
                        "sysid": trunk_update_data.get("sysid"),
                        "rxchan": trunk_update_data.get("rxchan"),
                        "txchan": trunk_update_data.get("txchan"),
                        "wacn": trunk_update_data.get("wacn"),
                        "secondary": trunk_update_data.get("secondary"),
                        "frequencies": trunk_update_data.get("frequencies"),
                        "frequency_data": trunk_update_data.get("frequency_data"),
                        "last_tsbk": trunk_update_data.get("last_tsbk"),
                        "tsbks": trunk_update_data.get("tsbks"),
                        "adjacent_data": trunk_update_data.get("adjacent_data"),
                    }

            # Extract values for 'rx_update' json_type
            elif item.get("json_type") == "rx_update":
                latest_values['rx_update'] = {
                    "error": item.get("error"),
                    "fine_tune": item.get("fine_tune"),
                    "files": item.get("files"),
                }

        return latest_values

    except Exception as e:
        print("An error occurred while fetching latest values:", e)
        return {}


# Function to run in a loop
def run_loop(url):
    while True:
        latest_values = get_latest_values(url)
        # print(latest_values)
        time.sleep(2)


# Function to initialize the thread with a given URL
def initialize(url):
    thread = threading.Thread(target=run_loop, args=(url,))
    thread.daemon = True
    thread.start()



# Example of initializing with a URL
# if __name__ == "__main__":
#    initialize("http://192.168.1.245:8080")
