
# coding: utf-8

# OpenStreetMap Data Case study

# Map Area
# San Francisco, CA, United States
# * https://www.openstreetmap.org/export#map=11/8.4454/125.9525
# * https://mapzen.com/data/metro-extracts/metro/san-francisco_california/
# * This is the map area of my favorite and neighbors city . So, am interested to see what database querying reveals, and I would like an opportunity contribute to its improvement on OpenStreetMap.org.

# In[1]:

#!/usr/bin/env python


import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow

OSM_FILE = "san-francisco_california.osm"  # Replace this with your osm file
SAMPLE_FILE = "sample_sf.osm"

k = 15 # Parameter: take every k-th top level element

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>')


# Iterative Parsing

# In[2]:

import xml.etree.cElementTree as ET
import pprint

def count_tags(filename):
        
    tags = {}
    for event, elem in ET.iterparse(filename):
        if elem.tag not in tags:
            tags[elem.tag] = 1
        else:
            tags[elem.tag] += 1
    return tags


def test():

    tags = count_tags('sample_sf.osm')
    pprint.pprint(tags)
     

    

if __name__ == "__main__":
    test()


# Tag Types

# In[3]:

import xml.etree.cElementTree as ET
import pprint
import re


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys):
    if element.tag == "tag":
        key = element.attrib['k']
        if lower.match(key):
            keys["lower"] = keys["lower"] + 1
        elif lower_colon.match(key):
            keys["lower_colon"] = keys["lower_colon"] + 1
        elif problemchars.match(key):
            keys["problemchars"] = keys["problemchars"] + 1
        else:
            keys["other"] = keys["other"] + 1
       
    return keys



def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys



def test():
    # You can use another testfile 'map.osm' to look at your solution
    # Note that the assertion below will be incorrect then.
    # Note as well that the test function here is only used in the Test Run;
    # when you submit, your code will be checked against a different dataset.
    keys = process_map('sample_sf.osm')
    pprint.pprint(keys)
    


if __name__ == "__main__":
    test()


# Exploring Users

# In[4]:

import xml.etree.cElementTree as ET
import pprint
import re

def get_user(element):
    return


def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if "uid" in element.attrib:
            users.add(element.attrib["uid"])
        
    return users


def test():

    users = process_map('sample_sf.osm')
    pprint.pprint(users)
    


if __name__ == "__main__":
    test()


# Improving Street Names

# In[5]:

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "sample_sf.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]
# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Ave.": "Avenue",
            "Rd.": "Road",
            "Plz" : "Plaza"

            }
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    #print tag
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


def update_name(name, mapping):

    #print name
    '''
    name  == "Lincon Ave"
    m.group() = Ave
    
    finnaly name will become Lincon Avenue
    '''
    m = street_type_re.search(name)
    if m:
        street_type = m.group()
        if street_type not in expected and street_type in mapping.keys():
            name = re.sub(street_type_re, mapping[street_type], name)

   


    return name
        
    
def test():
    st_types = audit(OSMFILE)
#   #assert len(st_types) == 3
    pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name
            


if __name__ == '__main__':
    test()    


# Updating Postal codes

# In[6]:

import re  
d5 = re.compile(r'^\d{5}$')  
d5_d4 = re.compile(r'^(\d{5})-\d{4}$')  
w2_d5 = re.compile(r'^[a-zA-Z]{2}\s(\d{5})$')  
d5_c  = re.compile(r'^(\d{5}).+$')  

def audit_postcode(postcode):  
    """detects pattern and returns clean postcode"""  
    if re.match(d5, postcode):  
        return postcode  
    elif re.match(d5_d4, postcode):  
        clean_postcode = re.findall(d5_d4, postcode)[0]  
    elif re.match(w2_d5, postcode):                                                   
        clean_postcode = re.findall(w2_d5, postcode)[0]  
    elif re.match(d5_c, postcode):  
        clean_postcode = re.findall(d5_c, postcode)[0]  
    return clean_postcode  


# Preparing for Database

# In[7]:

# Note: The schema is stored in a .py file in order to take advantage of the
# int() and float() type coercion functions. Otherwise it could easily stored as
# as JSON or another serialized format.

schema = {
    'node': {
        'type': 'dict',
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'lat': {'required': True, 'type': 'float', 'coerce': float},
            'lon': {'required': True, 'type': 'float', 'coerce': float},
            'user': {'required': False, 'type': 'string'},
            'uid': {'required': False, 'type': 'integer', 'coerce': int},
            'version': {'required': True, 'type': 'string'},
            'changeset': {'required': True, 'type': 'integer', 'coerce': int},
            'timestamp': {'required': True, 'type': 'string'}
        }
    },
    'node_tags': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'key': {'required': True, 'type': 'string'},
                'value': {'required': True, 'type': 'string'},
                'type': {'required': True, 'type': 'string'}
            }
        }
    },
    'way': {
        'type': 'dict',
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'user': {'required': True, 'type': 'string'},
            'uid': {'required': True, 'type': 'integer', 'coerce': int},
            'version': {'required': True, 'type': 'string'},
            'changeset': {'required': True, 'type': 'integer', 'coerce': int},
            'timestamp': {'required': True, 'type': 'string'}
        }
    },
    'way_nodes': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'node_id': {'required': True, 'type': 'integer', 'coerce': int},
                'position': {'required': True, 'type': 'integer', 'coerce': int}
            }
        }
    },
    'way_tags': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'key': {'required': True, 'type': 'string'},
                'value': {'required': True, 'type': 'string'},
                'type': {'required': True, 'type': 'string'}
            }
        }
    }
}


# In[8]:

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus



OSM_PATH = "sample_sf.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    
    if element.tag == 'node':
        for e  in element.attrib:
            if e  in NODE_FIELDS:
                node_attribs[e]= element.attrib[e]

                    
        for child in element.iter('tag'):
            tag_dict = {}
            key = child.attrib['k']
            if PROBLEMCHARS.search(key):
                continue
            if ':' in key:
                #first extract part before the colon : type
                #part aftetr the colon is key
                index = key.find(':')
                tag_dict['type'] = key[:index] #before the colon
                tag_dict['key'] = key[index+1:] #after the colon
                
            else : 
                tag_dict['type'] = 'regular'
                tag_dict['key'] = key
            tag_dict['id'] = element.attrib['id']
            #<tag 'k' = 'addr:streetname', v= 'Lincoln Ave.'>
            if is_street_name(child):
                tag_dict['value']  = update_name(child.attrib['v'],mapping)
            else:
                tag_dict['value'] = child.attrib['v']
            tags.append(tag_dict)
        return {'node': node_attribs, 'node_tags': tags}
            
    if element.tag == 'way':
        for field in WAY_FIELDS:
            way_attribs[field] = element.attrib[field]
            
        for child in element.iter('tag'):
            tag_dict = {}
            key = child.attrib['k']
            if PROBLEMCHARS.search(key):
                continue
            if ':' in key:
                #first extract part before the colon : type
                #part aftetr the colon is key
                index = key.find(':')
                tag_dict['type'] = key[:index] #before the colon
                tag_dict['key'] = key[index+1:] #after the colon
                
            else : 
                tag_dict['type'] = 'regular'
                tag_dict['key'] = key
            tag_dict['id'] = element.attrib['id']
            if is_street_name(child):
                tag_dict['value']  = update_name(child.attrib['v'],mapping)
            else:
                tag_dict['value'] = child.attrib['v']
            
            tags.append(tag_dict)    
        position = 0   
        for child in element.iter('nd'):
            nd_dict = {}
            nd_dict['id'] = element.attrib['id']
            nd_dict['node_id'] = child.attrib['ref']
            nd_dict['position'] = position
            position = position + 1
            way_nodes.append(nd_dict)
    
        
        
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w') as ways_file,          codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)


# In[ ]:



