import requests
import json
from dataclasses import dataclass

API_URL = ""
#API_URL = "http://localhost:5000"

def make_iso_format_date(value):
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
    return time.strftime(ISO_TIME, time.gmtime(value))

def submit_data(s, ctrl, data):
    resp = s.request(
        ctrl["method"],
        API_URL+ctrl["href"],
        data=json.dumps(data),
        headers = {"Content-type": "application/json"}
    )
    return resp

def convert_value(value, schema_props):
    print(schema_props)
    if schema_props["type"] == "integer":
        value = int(value)
    elif schema_props["type"] == "number":
        value = float(value)
    elif schema_props["type"] == "string":
        if schema_props.get("format") == "date":
            value = make_iso_format_date(value)
        elif schema_props.get("format") == "time":
            value = make_iso_format_time(value)
    return value

def prompt_from_schema(s, ctrl):
    body = {}

    if "schema" in ctrl:
        schema = ctrl["schema"]
    else:
        resp = s.get(ctrl["schemaUrl"])
        schema = resp.json()

    for field in schema["required"]:
        props = schema["properties"][field]

        out = input(props["description"])

        value = convert_value(out, props)
        body[field] = value

    resp = submit_data(s, ctrl, body)
    if resp.status_code == 201:
        return resp.headers["Location"]

if __name__ == "__main__":

    with requests.Session() as s:
        s.headers.update({"Accept": "application/vnd.mason+json"})
        resp = s.get(API_URL+"/api/sensors/")
        if resp.status_code != 200:
            print("Unable to access API.")
        else:
            body = resp.json()
            prompt_from_schema(s, body["@controls"]["senhub:add-sensor"])

