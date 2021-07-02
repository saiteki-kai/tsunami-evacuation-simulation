#!env/bin/python3
import json
import xml.etree.ElementTree as ET

tree = ET.parse("../../data/data.xml")
root = tree.getroot()

data = {"bounds": {}, "nodes": {}, "ways": {}}

for el in root:
    if el.tag == "node":
        id = el.attrib["id"]
        tags = {child.attrib["k"]: child.attrib["v"] for child in el.findall("tag")}

        node = {
            "id": id,
            "lon": el.attrib["lon"],
            "lat": el.attrib["lat"],
            "tags": tags,
        }

        data["nodes"][id] = node
    elif el.tag == "way":
        id = el.attrib["id"]
        tags = {child.attrib["k"]: child.attrib["v"] for child in el.findall("tag")}
        nodes = [nd.attrib["ref"] for nd in el.findall("nd")]

        way = {
            "id": id,
            "nodes": nodes,
            "tags": tags,
        }

        data["ways"][id] = way
    elif el.tag == "bounds":
        data["bounds"] = el.attrib

with open("../../data/data.json", "w") as outfile:
    json.dump(data, outfile, indent=2)

print(f"nodes: {len(data['nodes'])}, ways: {len(data['ways'])}")
