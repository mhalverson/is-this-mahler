from datetime import datetime, time, timezone
from html.parser import HTMLParser
import re
import requests
from requests_html import HTML
import xml.etree.ElementTree as ET

def radio():
    RADIO_URL = 'https://www.rnz.co.nz/rss/concert-schedule.xml'
    # see also https://www.rnz.co.nz/concert/schedules
    r = requests.get(RADIO_URL)
    text = r.text
    rss = ET.fromstring(text)
    channel = rss[0]
    items = channel.findall('item')
    # find the first item with a pubDate in the future - that's the NEXT item so we want the item before it
    utc_now_dt = datetime.now(timezone.utc)
    now_dt = utc_now_dt.astimezone()
    item_strptime_format = '%a, %d %b %Y %H:%M:%S %z'
    prev = None
    for item in items:
        pub_date = item[2].text
        item_time = datetime.strptime(pub_date, item_strptime_format)
        if item_time > now_dt:
            break
        else:
            prev = item
    if prev is None:
        raise RuntimeError('unable to identify active block of schedule')
    currently_playing_item = prev
    currently_playing_item_desc = currently_playing_item[1].text
    html = HTML(html=currently_playing_item_desc)
    lines = html.text.split('\n')
    if len(lines) == 1:
        return lines
    chunks = list(filter(lambda line: re.fullmatch('\d{1,2}\.\d{2}', line), lines))
    if not chunks:
        return lines
    # find the first chunk with a time in the future - that's the NEXT chunk so we want the chunk before it
    now_t = now_dt.time()
    chunk_strptime_format = '%H.%M'
    for current_chunk, next_chunk in zip([None]+chunks, chunks+[None]):
        if next_chunk is None:
            # we got to the end
            break
        next_chunk_time = datetime.strptime(next_chunk, chunk_strptime_format).time()
        if now_t.hour > 12:
            # the string doesn't include am/pm, account for it manually
            next_chunk_time = next_chunk_time.replace(hour=next_chunk_time.hour+12)
        if next_chunk_time > now_t:
            break
    if current_chunk is None:
        # it's the first chunk
        i = None
        j = lines.index(next_chunk)
    elif next_chunk is None:
        # it's the last chunk
        i = lines.index(current_chunk) + 1
        j = None
    else:
        # it's a middle chunk
        i = lines.index(current_chunk) + 1
        j = linex.index(next_chunk)
    return lines[i:j]
