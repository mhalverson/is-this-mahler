import requests
from requests_html import HTML
import xml.etree.ElementTree as ET

def kupu_o_te_ra():
    KUPO_O_TE_RA_URL = 'https://kupu.maori.nz/feed.xml'
    r = requests.get(KUPO_O_TE_RA_URL, params={})
    r.encoding = 'utf-8' # requests guesses the encoding incorrectly, should be utf-8
    text = r.text
    rss = ET.fromstring(text)
    channel = rss[0]
    items = channel.findall('item')
    item = items[0] # this is the kupu we are after
    # title = item[0].text
    description_raw = item[1].text
    description_cleaned = '<p>' + description_raw.replace('\n','') + '</p>'
    description_html = HTML(html=description_cleaned)
    description = description_html.text
    # link = item[2].text
    segments = []
    current_segment = []
    is_first_line = True
    for line in description.split('\n'):
        if line.startswith('- this is an example'):
            continue
        elif line == '':
            segments.append(' '.join(current_segment))
            current_segment = []
        elif is_first_line:
            is_first_line = False
            definition, first_example_part_1 = line.split('. ', 1)
            segments.append(definition)
            current_segment.append(first_example_part_1)
        else:
            current_segment.append(line)
    segments.append(' '.join(current_segment))
    return segments
