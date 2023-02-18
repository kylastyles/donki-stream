#! /usr/bin/env python3

import json
import requests


class DONKI():
    """
    Space weather notifications pulled from NASA API
    """
    NOTIFICATIONS_URL = "https://kauai.ccmc.gsfc.nasa.gov/DONKI/WS/get/notifications"

    def __init__(self, dates_list):
        self.raw_data = DONKI.notification_pull(dates_list)
        self.clean_data = [DONKI.message_parser(x) for x in self.raw_data]


    @staticmethod
    def notification_pull(dates_list):
        """
        :param dates_list: [("2020-01-01", "2020-01-31"),
              ("2020-02-01", "2020-02-29"),
              ("2020-03-01", "2020-03-31")]
        :return: [{"messageType": "Report", "messageID": "20200101-7D-001", ...}, {...}]
        """
        print(f"Attempting to pull {dates_list} events from API")
        data = []
        for dates in dates_list:
            headers = {"Content-Type": "application/json"}
            payload = {
                "startDate": dates[0][0],
                "endDate": dates[0][1],
                # "api_key": DONKI.API_KEY,
                "type": "all"
            }
            try:
                r = requests.get(url=DONKI.NOTIFICATIONS_URL, params=payload, headers=headers)
                data.extend(json.loads(r.content))  # type(r.content) => bytes
            except Exception as e:
                print(f"ERROR: Request Get - {e}")
        return data


    @staticmethod
    def message_parser(msg):
        """
        Specifically breaks down the "messageBody" portion of the DONKI messages into child components.
        :param msg: {
            "messageType": "Report",
            "messageID": "20191218-7D-001",
            "messageURL": "https://kauai.ccmc.gsfc.nasa.gov/DONKI/view/Alert/15228/1",
            "messageIssueTime": "2019-12-18T21:22Z",
            "messageBody": "## NASA Goddard Space Flight Center, ..."
            }
        :return: {
            "messageType": "Report",
            "messageID": "20191218-7D-001",
            "messageURL": "https://kauai.ccmc.gsfc.nasa.gov/DONKI/view/Alert/15228/1",
            "messageIssueTime": "2019-12-18T21:22Z",
            'messageBody': {
                'message_type': 'Weekly Space Weather Summary Report for December 11, 2019 - December 17, 2019 ',
                'message_issue_date': '2019-12-18T21:22:11Z',
                'report_coverage_begin_date': '2019-12-11T00:00Z',
                'report_coverage_end_date': '2019-12-17T23:59Z',
                'message_id': '20191218-7D-001 ',
                'summary': '  Solar activity was at low levels during this reporting period...',
                'space_weather_outlook': '',
                'outlook_coverage_begin_date': '2019-12-18T00:00Z ',
                'outlook_coverage_end_date': '2019-12-24T23:59Z  The solar activity is expected to be low for the upcoming week...',
                'notes': {
                    'SCORE CME typification system': {
                        'S-type': ' CMEs with speeds less than 500 km/s ',
                        'C-type': ' CMEs with speeds less than 500 km/s Common 500-999 km/s ',
                        'O-type': ' CMEs with speeds less than 500 km/s Common 500-999 km/s Occasional 1000-1999 km/s ',
                        'R-type': ' CMEs with speeds less than 500 km/s Common 500-999 km/s Occasional 1000-1999 km/s Rare 2000-2999 km/s ',
                        'ER-type': ' CMEs with speeds less than 500 km/s Common 500-999 km/s Occasional 1000-1999 km/s Rare 2000-2999 km/s Extremely Rare >3000 km/s http://swc.gsfc.nasa.gov/main/score   NASA Community Coordinated Modeling Center/Space Weather Research Center ( SWRC, http://swrc.gsfc.nasa.gov )  '
                    }
                }
            }
        }
        """
        # Start a new message
        new_msg = {
            "messageType": msg["messageType"],
            "messageID": msg["messageID"],
            "messageURL": msg["messageURL"],
            "messageIssueTime": msg["messageIssueTime"],
            'messageBody': {}
        }
        # Break down the incoming message's messageBody and save to new message
        sections = msg["messageBody"].split("\n## ")
        for part in sections:
            try:
                header, body = part.split(":", 1)  # only split on first occurrence of colon, not all occurrences (ie dates)
                header = header.strip("##").replace(" ", "_").lower()  # clean up headers
                body = body.lstrip(" ").replace("\n", " ").replace("#", "")
                if header:
                    new_msg["messageBody"][header] = body
            except ValueError:
                continue
        # Break down notes if present and save to new message
        if "notes" in new_msg["messageBody"] and new_msg["messageBody"]["notes"]:
            try:
                notes_wo_dsc = new_msg["messageBody"]["notes"].split("Disclaimer")[0]  # First set the important stuff to a var
                new_msg["messageBody"]["notes"] = {}  # now turn notes into an object
                parent_header, children = notes_wo_dsc.split(":", 1)
                parent_header = parent_header.lstrip(" ")
                new_msg["messageBody"]["notes"][parent_header] = {}  # make a new object for more children
                child_parts = children.split(" ")
                child_header = None
                new_body = ""
                for part in child_parts:
                    if part.endswith(":"):
                        child_header = part.strip(":")
                    else:
                        new_body += part + " "
                    if child_header:
                        new_msg["messageBody"]["notes"][parent_header][child_header] = new_body
            except ValueError:
                pass
        # We don't need the disclaimers taking up memory
        if "disclaimer" in new_msg["messageBody"]:
            del new_msg["messageBody"]["disclaimer"]
        return new_msg
