import xml.etree.ElementTree as ET
from datetime import datetime
import random
import json
import os

#Third-party Libraries 
#All of them are available in python 3.6+
import httpx
import trio
from fake_useragent import UserAgent

class Save_to_local:
    def __init__(self):
        pass

    def save_response(self, url, response_content):
        content_type = response_content.headers.get("content-type")
        if "xml" in content_type:
            self.save_as_xml(url, response_content)
        elif "json" in content_type:
            self.save_as_json(url, response_content)
        else:
            print(f"Unhandled content type: {content_type}. Response not saved.")

    def save_as_xml(self, url, response_content):
        filename = "response.xml"
        count = 1
        while os.path.exists(filename):
            filename = f"({count})_response.xml"
            count += 1
        with open(filename, "w") as file:
            file.write(response_content.text)
            
    def save_as_json(self, url, response_content):
        filename = "response.json"
        count = 1
        while os.path.exists(filename):
            filename = f"({count})_response.json"
            count += 1
        with open(filename, "w") as file:
            json.dump(response_content.json(), file)

class SystemTime:
    @staticmethod
    def format_current_time(format_string="%m/%d %H:%M:%S"):
        now = datetime.now()
        return now.strftime(format_string)


class HTTP3Requester:
    def __init__(self, url):
        self.url = url

    async def make_request(self):
        ua = UserAgent()
        headers = {
            "user-agent": ua.random
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.url, headers=headers, timeout=10)
                if 200 <= response.status_code < 300:
                    filename = "response.xml"
                    count = 1
                    while os.path.exists(filename):
                        filename = f"({count})_response.xml"
                        count += 1
                    print(
                        f"System current time: \033[90m{SystemTime.format_current_time()}\033[0m "
                        f"http response code: \033[38;2;153;255;214m{response.status_code}\033[0m "
                    )
                    #Only when the status code is 200, the Save_to_local class is called to save the response content to the local
                    saver = Save_to_local()
                    saver.save_response(self.url, response)
                elif 200 < response.status_code < 300:
                    print (
                        f"http response code: \033[38;2;153;255;214m{response.status_code}\033[0m "
                        f"Unhandled content type: {response.status_code}. Response didn't get saved."
                    )
            except httpx.HTTPError as exc:
                print(
                    f"System current time: \033[90m{SystemTime.format_current_time()}\033[0m "
                    f"Error: {exc}"
                )
            

    async def start_requests(self, num_requests):  # Declare the method as asynchronous
        async with trio.open_nursery() as nursery:
            for _ in range(num_requests):
                nursery.start_soon(self.make_request)
                sleep_time = random.randint(3, 7)
                print(f"\033[91mWaiting for \033[92m{sleep_time}s\033[0m" )  # Display waiting time
                await trio.sleep(sleep_time)  # Use asynchronous waiting method

    def run(self, num_requests):
        trio.run(self.start_requests, num_requests)



if __name__ == "__main__":
    url = "https:example.com/url"
    requester = HTTP3Requester(url)
    num_requests = 2  # Let the user decide how many times to send
    requester.run(num_requests)
