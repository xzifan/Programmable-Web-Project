"""
A submission script for the MusicMeta API, used as an example in the Programmable
Web Project course. Crawls through a local folder structure containing artist
folders containing album folders, e.g.

root
├── artist 1
│   ├── album 1
│   └── album 2
└── artist 2
    ├── album 1
    └── album 2

It also crawls through the API in the same order. When it finds an artist, album
or track that doesn't exist in the API, it sends a POST request to create it.
Furthemore, if it finds differences between local tag data and data stored in
the API, it sends a PUT request to update the API side based on local data.

The API server uses Mason hypermedia format.

@author: Mika Oja (University of Oulu)
"""

import json
import os
import re
import requests
import sys
import time
from tinytag import TinyTag, TinyTagException

API_URL = "FILL THIS"
ISO_DATE = "%Y-%m-%d"
ISO_TIME = "%H:%M:%S"
DATE_FORMATS = ["%Y", ISO_DATE]

API_TAG_ALBUM_MAPPING = {
    "title": "album",
    "discs": "disc_total",
    "genre": "genre",
    "release": "year",
}    

API_TAG_TRACK_MAPPING = {
    "title": "title",
    "disc_number": "disc",
    "track_number": "track",
    "length": "duration",
}

class APIError(Exception):
    """
    Exception class used when the API responds with an error code. Gives
    information about the error in the console.    
    """

    def __init__(self, code, error):
        """
        Initializes the exception with *code* as the status code from the response
        and *error* as the response body.
        """
    
        self.error = json.loads(error)
        self.code = code
        
    def __str__(self):
        """
        Returns all details from the error response sent by the API formatted into
        a string.
        """

        return "Error {code} while accessing {uri}: {msg}\nDetails:\n{msgs}".format(
            code=self.code,
            uri=self.error["resource_url"],
            msg=self.error["@error"]["@message"],
            msgs="\n".join(self.error["@error"]["@messages"])
        )

def make_iso_format_date(value):
    """
    make_iso_format_date(value) -> string
    
    Tries to create an ISO-8601 date timestamp from the given string by trying
    to parse the original string with different date formats. If unable to parse
    the date automatically, it prompts the conversion from the user.
    """

    for form in DATE_FORMATS:
        try:
            date = time.strptime(value, form)
            value = time.strftime(ISO_DATE, date)
            break
        except ValueError:
            pass
    else:
        value = input("Type ISO format date that matches {}".format(value))
    return value
    
def make_iso_format_time(value):
    """
    make_iso_format_time(value) -> string
    
    Creates an ISO-8601 time timestamp from the given floating point *value*.
    """

    return time.strftime(ISO_TIME, time.gmtime(value))

def prompt_artist_choice(name, hits):
    """
    prompt_artist_choice(name, hits) -> dict
    
    Prompts the user to choose an artist from a list of multiple *hits* that
    matched *name*. Returns the artist dictionary that matches the user's
    choice.
    """
    
    print("The following artists were found with '{}'".format(name))
    for i, artist in enumerate(hits, 1):
        print("{i}: {name} ({location}, {formed} - {disbanded})".format(i=i, **artist))
    choice = int(input("Choose artist by typing a number: "))
    return items[choice - 1]
    
def find_artist_href(name, collection):
    """
    find_artist_href(name, collection) -> string
    
    Finds a href for an artist from a *collection* (list of dictionaries) using
    *name* as the search criterion. If multiple artists match it prompts the user
    to choose the correct one. If there are no matches, returns None.
    """

    name = name.lower()
    hits = []
    for item in collection:
        if item["name"].lower() == name:
            hits.append(item)
    if len(hits) == 1:
        return hits[0]["@controls"]["self"]["href"]
    elif len(hits) >= 2:
        return prompt_artist_choice(name, hits)["@controls"]["self"]["href"]
    else:
        return None
    
def find_album_href(title, collection):
    """
    find_album_href(title, collection) -> string
    
    Finds a href for an album from *collection* (list of dictionaries) using
    *title* as the search criterion. Album names are unique per artist so this
    function cannot match multiple albums. Returns None if there are no matches.
    """

    title = title.lower()
    for item in collection:
        if item["title"].lower() == title:
            return item["@controls"]["self"]["href"]    
    return None

def find_track_item(tag, collection):
    """
    find_track_item(tag, collection) -> dict
    
    Finds a track dictionary from a *collection* (list of dictionaries) by
    comparing items in the collection to data in the *tag*. Uses title as the
    primary match criterion, and track and disc numbers as secondary if there
    are multiple tracks with the same title, or no matches with the title.
    Returns None if unable to find a track.
    """

    title = tag.title.lower()
    hits = []
    for item in collection:
        if item["title"].lower() == title:
            hits.append(item)
    if len(hits) == 1:
        return hits[0]
    elif len(hits) >= 2:
        disc_n = tag.disc or 1
        track_n = tag.track
        for item in hits:
            if item["disc_number"] == disc_n and item["track_number"] == track_n:
                return item
        return None
    else:
        disc_n = tag.disc or 1
        track_n = tag.track
        for item in collection:
            if item["disc_number"] == disc_n and item["track_number"] == track_n:
                return item
        return None

def submit_data(s, ctrl, data):
    """
    submit_data(s, ctrl, data) -> requests.Response
    
    Sends *data* provided as a JSON compatible Python data structure to the API
    using URI and HTTP method defined in the *ctrl* dictionary (a Mason @control).
    The data is serialized by this function and sent to the API. Returns the 
    response object provided by requests.
    """
    
    resp = s.request(
        ctrl["method"],
        API_URL + ctrl["href"],
        data=json.dumps(data),
        headers = {"Content-type": "application/json"}
    )
    return resp

def create_artist(s, name, ctrl):
    """
    create_artist(s, name, ctrl) -> string
    
    Compiles a dictionary for creating an artist resource by using JSON schema
    from the *ctrl* as a template. Only fills required fields, and uses "TBA"
    for location because this information is not available in tags. In case new
    required fields are introduced in the API, prompts the user for the value.
    If creation is successful, returns the URI where the artist was placed by
    the API. Otherwise raises an APIError.
    """
    
    body = {}
    schema = ctrl["schema"]
    for field in schema["required"]:
        if field == "name":
            body[field] = name
        elif field == "location":
            body[field] = "TBA"
        else:
            print("Unknown required field '{}'".format(field))
            body[field] = input("Provide value: ")
    resp = submit_data(s, ctrl, body)
    if resp.status_code == 201:
        return resp.headers["Location"]
    else: 
        raise APIError(resp.status_code, resp.content)

def convert_value(value, schema_props):
    """
    convert_value(value, schema_props) -> value
    
    Converts a *value* to the type and format defined in the corresponding set
    of JSON schema properties. Returns the converted value, or the value as-is
    if no conversion was necessary.
    """

    if schema_props["type"] == "integer":
        value = int(value)
    elif schema_props["type"] == "string":
        if schema_props.get("format") == "date":
            value = make_iso_format_date(value)
        elif schema_props.get("format") == "time":
            value = make_iso_format_time(value)
    return value

def create_with_mapping(s, tag, ctrl, mapping):
    """
    create_with_mapping(s, tag, ctrl, mapping) -> string
    
    Creates an album or track dictionary for submitting a resource to the API.
    The data is constructed by using the *ctrl* object's schema as a template and
    reading corresponding values from *tag* by using the *mapping* dictionary.
    Values are converted to types and format required by the schema. If creation
    is successful, the new resource's URI is returned. Otherwiser APIError is 
    raised.
    """

    body = {}
    schema = ctrl["schema"]
    for name, props in schema["properties"].items():
        local_name = mapping[name]
        value = getattr(tag, local_name)
        if value is not None:
            value = convert_value(value, props)
            body[name] = value

    resp = submit_data(s, ctrl, body)
    if resp.status_code == 201:
        return resp.headers["Location"]
    else:
        raise APIError(resp.status_code, resp.content)


def compare_with_mapping(s, tag, body, schema, mapping):
    """
    compare_with_mapping(s, tag, body, schema, mapping) -> None
    
    Compares an album or track resource's JSON *body* with its local counterpart
    presented by *tag*. Comparison is done only with fields that are in the 
    resource's schema as these are the fields that can be edited. An edit 
    dictionary is constructed using local values when they exist, and API values
    otherwise. If at least one field differs, the edit is submitted to the API
    using a control element found from either the current resource representation
    or by following its "self" link relation.
    """
    
    edit = {}
    change = False
    for field, props in schema["properties"].items():
        api_value = body[field]
        local_name = mapping[field]
        tag_value = getattr(tag, local_name)
        if tag_value is not None:
            tag_value = convert_value(tag_value, props)
            if tag_value != api_value:
                change = True
                edit[field] = tag_value
                continue
        edit[field] = api_value

    if change:
        try:
            ctrl = body["@controls"]["edit"]
        except KeyError:
            resp = s.get(API_URL + body["@controls"]["self"]["href"])
            body = resp.json()
            ctrl = body["@controls"]["edit"]
        submit_data(s, ctrl, edit)

def check_artist(s, name, path, artists_href):
    """
    check_artist(s, name, path, artists_href) -> None
    
    Checks whether an artist resource exists in the API by fetching the artist
    collection resource from *artists_href* and trying to find an artist with
    the given *name* (corresponding to the local *path*). If the artist does
    not exist it's created. Once the artist is located, moves to checking that
    artist's albums.
    """
    
    print("Checking artist", name)
    resp = s.get(API_URL + artists_href)
    body = resp.json()
    artist_href = find_artist_href(name, body["items"])
    if artist_href is None:
        artist_href = create_artist(s, name, body["@controls"]["mumeta:add-artist"])
    
    resp = s.get(API_URL + artist_href)
    body = resp.json()
    albums_href = body["@controls"]["mumeta:albums-by"]["href"]
    iterate_albums(s, path, albums_href)
    
def check_album(s, title, path, albums_href):
    """
    check_album(s, title, path, albums_href) -> None
    
    Checks whether an album resource exists in the API by fetching the 
    corresponding artist's album collection from *album_href* and trying to 
    find an album with the given *title* (corresponding to the local *path*).
    If the album does not exist it's created, otherwise its data is compared to
    data found in the first track's tag in the album's folder. Differences are
    submitted as an edit, favoring local data. 
    
    After checking the album itself, its tracks are also checked.
    """

    new = False
    print("Checking album", title)
    resp = s.get(API_URL + albums_href)
    body = resp.json()
    for name in os.listdir(path):
        if name.endswith(".mp3"):
            break
    else:
        print("Album folder {} has no tracks.".format(path))
        return

    try:
        tag = TinyTag.get(os.path.join(path, name))
    except TinyTagException:
        print("Unable to read tag from {}".format(os.path.join(path, name)))
        return

    album_href = find_album_href(title, body["items"])
    if album_href is None:
        album_href = create_with_mapping(s, tag, body["@controls"]["mumeta:add-album"], API_TAG_ALBUM_MAPPING)
        new = True

    resp = s.get(API_URL + album_href)
    body = resp.json()
    if not new:
        album_schema = body["@controls"]["edit"]["schema"]
        compare_with_mapping(s, tag, body, album_schema, API_TAG_ALBUM_MAPPING)
    iterate_tracks(s, path, body)

def check_track(s, path, album_res):
    """
    check_track(s, path, album_res) -> None
    
    Checks whether a track resource exists within the *album_res* dictionary's
    "items" list. If the track does not exist it is created. If it does exist,
    its data is compared to local data found from the track's tag. 
    """

    try:
        tag = TinyTag.get(path)
    except TinyTagException:
        print("Unable to read tag from {}".format(os.path.join(path, name)))
        return

    track = find_track_item(tag, album_res["items"])
    if track is None:
        create_with_mapping(s, tag, album_res["@controls"]["mumeta:add-track"], API_TAG_TRACK_MAPPING)
    else:
        track_schema = album_res["@controls"]["mumeta:add-track"]["schema"]
        compare_with_mapping(s, tag, track, track_schema, API_TAG_TRACK_MAPPING)

def iterate_tracks(s, album_path, album_res):
    """
    iterate_tracks(s, album_path, album_res) -> None
    
    Goes through all tracks found in *album_path*, using check_track for each
    to compare them with API side tracks on the *album_res*.
    """

    for name in os.listdir(album_path):
        if name.endswith(".mp3"):
            path = os.path.join(album_path, name)
            check_track(s, path, album_res)

def iterate_albums(s, artist_path, albums_href):
    """
    iterate_albums(s, artist_path, albums_href) -> None
    
    Goes through all album folders in *artist_path*, using check_album for each
    to compare them with API side albums found by accessing *albums_href*.
    """

    for name in os.listdir(artist_path):
        path = os.path.join(artist_path, name)
        if os.path.isdir(path):
            check_album(s, name, path, albums_href)

def iterate_artists(s, root_path, artists_href):
    """
    iterate_artists(s, root_path, artists_href) -> None
    
    Goes through all artist folders in *root_path*, using check_artist for each
    to compare them with API side artists found by accessing *artists_href*.
    """

    for name in os.listdir(root_path):
        path = os.path.join(root_path, name)
        if os.path.isdir(path):
            check_artist(s, name, path, artists_href)

if __name__ == "__main__":
    try:
        root_path = sys.argv[1]
    except IndexError:
        root_path = "."

    with requests.Session() as s:
        s.headers.update({"Accept": "application/vnd.mason+json, */*"})
        resp = s.get(API_URL + "/api/")
        if resp.status_code != 200:
            print("Unable to access API.")
        else:
            body = resp.json()
            iterate_artists(s, root_path, body["@controls"]["mumeta:artists-all"]["href"])
