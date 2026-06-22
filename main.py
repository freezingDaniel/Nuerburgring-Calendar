# -*- coding: utf-8 -*-
"""## Fetch Open Hours"""

import json

import requests
from bs4 import BeautifulSoup

# URL of the webpage to fetch
url = 'https://nuerburgring.de/open-hours'

# Fetch the HTML content of the page
response = requests.get(url)
html_content = response.content

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Find all div elements with a data-location-id attribute
elements = soup.find_all('div', {'data-location-id': True})

# Dictionary to hold data-location-id as key and data-schedule JSON as value
schedule_dict = {}

# Check if any elements were found
if elements:
    for element in elements:
        # Extract the data-location-id attribute
        location_id = element.get('data-location-id')
        # Extract the JSON data from the data-schedule attribute
        json_data = element.get('data-schedule')
        if location_id and json_data:
            # Parse the JSON string to a Python dictionary
            parsed_data = json.loads(json_data)
            # Add to the dictionary
            schedule_dict[location_id] = parsed_data

    # Save the dictionary to a JSON file
    # with open('schedule.json', 'w') as json_file:
    #    json.dump(schedule_dict, json_file, indent=4)
else:
    print("No elements with data-location-id attribute found")

"""## Convert to ics-files

### Locations/Information from https://nuerburgring.de/open-hours
"""

location_names = {
    '12': {'name': 'Tourist Drives Nordschleife',
           'addr': 'Nürburgring Tourist Drives\\, 53520 Nürburg\\, Germany',
           'desc': 'https://nuerburgring.de/driving/touristdrives'},
    '11': {'name': 'Tourist Drives Grand Prix Track',
           'addr': '',
           'desc': 'https://nuerburgring.de/driving/touristdrives'},
     '6': {'name': 'info°center'},
    '36': {'name': 'ring°kino'},
    '34': {'name': 'Backstage Tour'},
     '9': {'name': 'ring°kartbahn'},
     '8': {'name': 'ring°werk'},
    '20': {'name': 'Nürburgring eSports Bar'},
    '31': {'name': 'Trackdays, Courses & Test Days - Nordschleife'},
    '32': {'name': 'Trackdays, Courses & Test Days - Grand Prix Track'},
    '35': {'name': 'Driving Academy Showroom'},
    '14': {'name': 'ring°fanshop'},
    '24': {'name': 'Atomic-Shop'},
    '38': {'name': 'CATERHAM BRAND STORE'},
    '27': {'name': 'GetSpeed RaceTaxi'},
    '26': {'name': 'RingTaxi'},
     '3': {'name': 'Bitburger Gasthaus'},
     '4': {'name': "Devil's Diner"},
    '23': {'name': 'LUCIA'},
    '15': {'name': 'Parkbistro at Nürburgring Ferienpark'},
     '7': {'name': 'Restaurant Nuvolari'},
    '18': {'name': 'ring°casino'},
    '28': {'name': 'lenarzFood'},
}

location_names = {
    '12': {'name': 'Tourist Drives Nordschleife',
           'addr': 'Nürburgring Tourist Drives\\, 53520 Nürburg\\, Germany',
           'desc': 'https://nuerburgring.de/driving/touristdrives'
                   + '\n \\n'
                   + '\n \\nNordschleife emergency number: 0800 0302 112'
                   + '\n \\n'
                   + '\n \\nPlease note:'
                   + '\n \\nThe track can be closed at any time for unforeseeable'
                   + '\n  reasons (e.g. due to an accident or bad weather conditions).'
                   + '\n \\nThis may result in a postponement'
                   + '\n of the opening hours or in waiting times.'},

    '11': {'name': 'Tourist Drives Grand Prix Track',
           'addr': '',
           'desc': 'https://nuerburgring.de/driving/touristdrives'
                   + '\n \\n'
                   + '\n \\nNordschleife emergency number: 0800 0302 112'
                   + '\n \\n'
                   + '\n \\nPlease note:'
                   + '\n \\nThe track can be closed at any time for unforeseeable'
                   + '\n  reasons (e.g. due to an accident or bad weather conditions).'
                   + '\n \\nThis may result in a postponement'
                   + '\n of the opening hours or in waiting times.'},
}

"""### Calendar Templates"""

# Calendar definitions

calendar_start = """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:github.com/freezingDaniel/nuerburgring-calendar
X-PUBLISHED-TTL:PT4H
"""

berlin_tz = """BEGIN:VTIMEZONE
TZID:Europe/Berlin
BEGIN:DAYLIGHT
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
TZNAME:CEST
DTSTART:19700329T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
TZNAME:CET
DTSTART:19701025T030000
RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU
END:STANDARD
END:VTIMEZONE
"""

event_template = """BEGIN:VEVENT
UID:fd-{trackid}-{startdate}
DTSTAMP:{todaydate}T{todaytime}Z
LAST-MODIFIED:{todaydate}T{todaytime}Z
DTSTART;TZID=Europe/Berlin:{startdate}T{starttime}
DTEND;TZID=Europe/Berlin:{enddate}T{endtime}
SUMMARY:{summary}
DESCRIPTION:{description}
TRANSP:TRANSPARENT
LOCATION:{address}
END:VEVENT
"""

calendar_end = "END:VCALENDAR"

# Example ics
data = {'trackid': "12",
        'startdate': 'yyyymmdd',
        'starttime': 'hhmmss',
        'enddate': 'yyyymmdd',
        'endtime': 'hhmmss',
        'summary': 'Touristenfahrten Nordschleife',
        'description': 'No description provided',
        'address': 'Hauptstraße 1\\, 53520 Nürburg\\, Germany',
        'todaydate': 'yyyymmdd',
        'todaytime': 'hhmmss',
        }
ics = calendar_start + berlin_tz + '\n' + event_template.format(**data) + '\n' + calendar_end
# print("Example ics:\n", ics)

"""### Eventlist generation"""

from datetime import datetime


def generate_events(track_id="12"):
    return_value = ""

    for key_date in schedule_dict.get(track_id):
        value_json = schedule_dict.get(track_id).get(key_date)
        # print("Event-day-JSON:", value_json)

        now = datetime.now()

        # If Track is closed
        if (value_json.get('opened') is False
                or value_json.get('exclusion', {}).get('opened') is False):
            # print("Track Status c:", key_date,":",value_json.get('status'))
            pass

        # If Track is open
        elif (value_json.get('exclusion').get('opened') is True):
            # Get opening time
            open = value_json.get('exclusion').get('periods')[0].get('start')
            # Get closing time
            close = value_json.get('exclusion').get('periods')[0].get('end')
            # Get Title
            message = location_names.get(track_id)['name']
            if (value_json.get('exclusion').get('message').get('en')):
                message += "\n  - " + value_json.get('exclusion').get('message').get('en')
            # Get Description
            summary = ''
            if (location_names.get(track_id)['desc']):
                summary = location_names.get(track_id)['desc']

            # Prepare for ics
            data = {'trackid': track_id,
                    'startdate': key_date.replace("-", ""),
                    'starttime': open.replace(":", "") + "00",
                    'enddate': key_date.replace("-", ""),
                    'endtime': close.replace(":", "") + "00",
                    'summary': message,
                    'description': summary,
                    'address': 'Hauptstraße 1\\, 53520 Nürburg\\, Germany',
                    'todaydate': now.strftime('%Y%m%d'),
                    'todaytime': now.strftime('%H%M%S'),
                    }
            return_value += event_template.format(**data)

            print("Track Status o:", key_date, ":", "Open:", open, "Closed:", close, message)

        # Else more programming required if this happens
        else:
            raise ValueError(f"Unexpected data for track {track_id} on {key_date}: {value_json}")
    return return_value


"""### Filename generation"""

import re


def filename(name):
    # Ugly but gets the job done
    return re.sub('[^0-9a-zA-Z]+',
                  '-',
                  name.replace('ü', 'ue'
                    ).replace('Ü', 'Ue'
                    ).replace('ä', 'ae'
                    ).replace('Ä', 'Ae'
                    ).replace('ö', 'oe'
                    ).replace('Ö', 'Oe'
                    ).replace('ß', 'ss')
                  )


"""### Calendar generation and export"""


def convertLFtoCRLF(content):
    # replacement strings
    WINDOWS_LINE_ENDING = '\r\n'
    UNIX_LINE_ENDING = '\n'

    # CRLF to LF
    content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)

    # LF to CRLF
    content = content.replace(UNIX_LINE_ENDING, WINDOWS_LINE_ENDING)

    return content


# Generate Calendars
for loc in location_names:
    save_name = filename(location_names.get(loc)['name'])
    # if k is not '11' and k is not '12':
    #  continue

    ics = calendar_start
    ics += berlin_tz
    ics += generate_events(loc)
    ics += calendar_end

    # https://icalendar.org/iCalendar-RFC-5545/3-1-content-lines.html
    ics = convertLFtoCRLF(ics)
    # TODO: can't be bothered rn
    # ics = foldLongLines(ics)
    # print(ics)

    # Export the calendar to an .ics file
    with open(save_name + '.ics', 'w') as f:
        f.writelines(ics)
    print("Calendar exported to '" + save_name + ".ics'")
