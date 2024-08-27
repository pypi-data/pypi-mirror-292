import requests
import base64
from datetime import datetime
import validators
import os
from .exceptions import (Unauthorized, Nothing, EmptyFile, ServerError)

def is_base64(s):
    """
    This function checks if a given string is a base64 encoded string.

    Args:
        s (str): The string to check.

    Returns:
        bool: True if the string is a base64 encoded string, False otherwise.

    Raises:
        TypeError: If the input is not a string.
        ValueError: If the input is a string that cannot be decoded using base64.
    """
    try:
        base64.b64decode(s)
        return True
    except (TypeError, ValueError):
        return False

class kaspersky_response:
    """
    This class represents a response from the Kaspersky API.
    """
    def __init__(self, response: requests.Response):
        """
        Initializes a new instance of the kaspersky_response class.

        Args:
            response (requests.Response): The API response.
        """
        self.content = response.json()
        self.type = self.content["type"]

        if self.type == "Hash":
            if self.content["GeneralInfo"]["Hash_Report"]["HashGeneralInfo"]["Zone"] == "Green":
                self.is_safe = True
            elif self.content["GeneralInfo"]["Hash_Report"]["HashGeneralInfo"]["Zone"] == "Red":
                self.is_safe = False
            else:
                self.is_safe = None

            self.status = self.content["GeneralInfo"]["Hash_Report"]["HashGeneralInfo"]["Status"]
            self.size = self.content["GeneralInfo"]["Hash_Report"]["HashGeneralInfo"]["Size"]
            self.filetype = self.content["GeneralInfo"]["Hash_Report"]["HashGeneralInfo"]["Type"]

            if "FirstNotificationDate" in self.content["GeneralInfo"]["Hash_Report"]["HashGeneralInfo"].keys():
                self.first_seen = datetime.fromtimestamp(self.content["GeneralInfo"]["Hash_Report"]["HashGeneralInfo"]["FirstNotificationDate"] // 1000)
                self.last_seen = datetime.fromtimestamp(self.content["GeneralInfo"]["Hash_Report"]["HashGeneralInfo"]["LastNotificationDate"] // 1000)
            
            if "HitsCount" in self.content["GeneralInfo"]["Hash_Report"]["HashGeneralInfo"].keys():
                self.hits_count = self.content["GeneralInfo"]["Hash_Report"]["HashGeneralInfo"]["HitsCount"]

            if "Threats" in self.content["GeneralInfo"]["Hash_Report"]["HashGeneralInfo"].keys():
                self.threats = [i["Threat"] for i in self.content["GeneralInfo"]["Hash_Report"]["HashGeneralInfo"]["Threats"]]

            if ("SandboxReport" in self.content["GeneralInfo"]["Hash_Report"].keys()) and ("Strings" in self.content["GeneralInfo"]["Hash_Report"]["SandboxReport"].keys()):
                try:
                    self.strings = [i["Data"] for i in self.content["GeneralInfo"]["Hash_Report"]["SandboxReport"]["Strings"]]
                except UnicodeDecodeError:
                    pass
        elif self.type == "Host":
            self.is_safe = True if self.content["GeneralInfo"][self.type]["Zone"] == "Green" else False
        elif self.type == "Ip":
            self.is_safe = True if self.content["GeneralInfo"][self.type]["Zone"] == "Green" else False
            self.status = self.content["GeneralInfo"][self.type]["Status"]

            if "CountryCode" in self.content["GeneralInfo"][self.type].keys():
                self.country_code = self.content["GeneralInfo"][self.type]["CountryCode"]

            if "HitsCount" in self.content["GeneralInfo"][self.type].keys():
                self.hits_count = self.content["GeneralInfo"][self.type]["HitsCount"]
            
            if "FirstNotificationDate" in self.content["GeneralInfo"][self.type].keys():
                self.first_seen = datetime.fromtimestamp(self.content["GeneralInfo"][self.type]["FirstNotificationDate"] // 1000)

class kaspersky_tip:
    """
    This class represents a connection to the Kaspersky Threat Intelligence Portal.

    Attributes:
        headers (dict): The headers to use for API requests.
    """
    def __init__(self) -> None:
        req = requests.get("https://opentip.kaspersky.com/ui/checksession")

        if req.status_code == 200:
            for i in req.headers.keys():
                if is_base64(req.headers[i]) is True:
                    self.headers = {i: req.headers[i]}
                    break
        else:
            raise ServerError("Failed to get headers.")

    def search(self, query: str, silent: bool = False) -> kaspersky_response:
        if (isinstance(query, str) and len(query) > 0):
            if (validators.md5(query) or validators.sha1(query) or validators.sha256(query) or validators.domain(query) or validators.url(query) or validators.ipv4(query) or validators.ipv6(query)):
                req = requests.post("https://opentip.kaspersky.com/ui/lookup", headers=self.headers, json={"query": query, "silent": silent})
                
                if req.status_code == 200:
                    return kaspersky_response(req)
                elif req.status_code == 404:
                    raise Nothing("Nothing found.")
                elif req.status_code == 401:
                    raise Unauthorized("Session expired.")
                else:
                    raise ServerError("Failed to get response from server.")
            else:
                raise ValueError("Query must be a valid hash, IP address, domain, or web address.")
        else:
            raise ValueError("Query must be a non-empty string.")

    def upload(self, filepath: str, silent: bool = False) -> kaspersky_response:
        if isinstance(filepath, str) and len(filepath) > 0:
            if os.path.isfile(filepath):
                with open(filepath, "rb") as file:
                    sample = file.read()

                    if len(sample) > 0:
                        data = {
                            "name": (None, "sample"),
                            "body": ("sample", sample, "application/octet-stream"),
                            "silent": (None, silent),
                            "fullReportNeeded": (None, False)
                        }

                        req = requests.post("https://opentip.kaspersky.com/ui/uploadsample", headers=self.headers, files=data)
                    else:
                        raise EmptyFile("File is empty.")

                if req.status_code == 200:
                    return kaspersky_response(req)
                elif req.status_code == 401:
                    raise Unauthorized("Session expired.")
                else:
                    raise ServerError("Failed to get response from server.")
            else:
                raise ValueError("Invalid file path.")
        else:
            raise ValueError("File path must be string.")