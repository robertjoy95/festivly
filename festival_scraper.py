import requests
import json
import copy
import functools
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}

@functools.lru_cache(maxsize=None)
def webpage_get(url):
    req = requests.get(url, 'html.parser', headers=headers)
    return req.text

def get_artists(html_text):
    # concat the html to just contain the section with the artists
    # TODO: reformat &amp; to meet spotify convention
    artists = []
    ind = html_text.find('Lineup</div>')
    html_text = html_text[ind:]
    end_ind = html_text.find('<!--')
    text = html_text[:end_ind]
    artists_remaining = True
    ind = text.find('<li>')
    if ind == -1:
        artists_remaining = False
    while(artists_remaining):
        end_ind = text.find('</li>')
        artist_text = text[ind+4:end_ind]
        if artist_text.find('</a>') == -1:
            artists.append(artist_text)
        else:
            artist_ind = artist_text.find('>')
            end_artist_ind = artist_text.find('</a>')
            artist_text = artist_text[artist_ind + 1:end_artist_ind]
            artists.append(artist_text)
        text = text[end_ind+4:]
        ind = text.find('<li>')
        if ind == -1:
            artists_remaining = False
    return artists

def get_info_by_keyword(info_str, kw, kw2='NONE'):
    # since the html string won't load as a json use this to get info
    info = copy.copy(info_str)
    ind = info.find(kw)
    if ind < 0:
        return 'NONE'
    if kw2 != 'NONE':
        info = info[ind+len(kw)+1:]
        ind = info.find(kw2)
        if ind < 0:
            return 'NONE'
        temp_str = info[ind+len(kw2)+3:]
    else:
        temp_str = info[ind+len(kw)+3:]

    end_ind = temp_str.find(',')
    temp_str = temp_str[:end_ind]
    disallowed_chars = ['\"', '}', '{', '\n']
    for d in disallowed_chars:
        temp_str = temp_str.replace(d, "")
    return temp_str

def get_festivals(url):
    # get all urls to link festivals, along with their location and date
    festivals = {}
    remaining = True
    page = 1
    wpg = webpage_get(url)
    while remaining:
        page_text = str(wpg)
        ind = page_text.find('var countries')
        page_text = page_text[ind:]
        fests_remaining = True
        ind = page_text.find('<script type="application/ld+json"')
        page_text = page_text[ind:]
        ind = page_text.find('{')
        end_ind = page_text.find('</script>')
        if ind == -1:
            fests_remaining = False
        else:
            fest_info = page_text[ind:end_ind]

        while fests_remaining:
            # get info from current festival and store it in dict format
            fest_name = get_info_by_keyword(fest_info, 'name')
            fest_url = get_info_by_keyword(fest_info, 'url')
            if fest_url == 'NONE':
                break
            festivals[fest_name] = {}
            festivals[fest_name]['url'] = fest_url
            festivals[fest_name]['location_name'] = get_info_by_keyword(fest_info, 'location', 'name')
            festivals[fest_name]['location_city'] = get_info_by_keyword(fest_info, 'addressLocality')
            festivals[fest_name]['location_country'] = get_info_by_keyword(fest_info, 'addressRegion')
            festivals[fest_name]['location_coords'] = [get_info_by_keyword(fest_info, 'latitude'), get_info_by_keyword(fest_info, 'longitude')]
            fest_page = webpage_get(festivals[fest_name]['url'])
            festivals[fest_name]['lineup'] = get_artists(fest_page)
            # isolate the next section to get info from
            page_text = page_text[end_ind+10:]
            ind = page_text.find('{')
            end_ind = page_text.find('</script>')
            fest_info = page_text[ind:end_ind]
            if end_ind == -1:
                fests_remaining = False
            else:
                fest_info = page_text[ind:end_ind]
        page += 1
        try:
            wpg = webpage_get(url + '/page/' + str(page) + '/')
        except:
            remaining = False
        if page > 50:
            break
    return festivals

festival_hub = 'https://www.musicfestivalwizard.com/all-festivals/'
fests = get_festivals(festival_hub)
with open('festival_list.json', 'w') as outfile:
    json.dump(fests, outfile)