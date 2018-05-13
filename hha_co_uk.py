import requests
from lxml import etree
from pprint import pformat as pf
from decimal import Decimal

url = 'http://apps.hha.co.uk/mis/Api/getlivesensors.aspx?key={key}'.format(
    key='your api key here'
)
debug = False


def info(description, obj):
    if debug:
        print(description, pf(obj).strip('\''))


def get_xml(url_to_get, use_test_file=False):
    """
    Fetches the xml from their public API endpoint using a HTTP GET request
    """
    if use_test_file:
        with open('hha_co_uk.xml', 'r') as xml_file:
            xml_contents = xml_file.read()
        return xml_contents.encode('utf-8')
    else:
        r = requests.get(url=url_to_get)
        if r.status_code == 200:
            response = r.text.encode('utf-8')
            info('response', response)
            return response
        else:
            return None


def get_tree(xml_string):
    """
    Parses the xml string input to a lxml tree
    """
    utf8_parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
    tree = etree.XML(xml_string, parser=utf8_parser)
    return tree


def get_sensors(xml_string):
    """
    Lists the available sensors in the XML source
    """
    tree = get_tree(xml_string)
    for sensor in tree:
        sensor_name = sensor.findtext('Name', default=None)
        sensor_id = sensor.findtext('ID', default=None)
        sensor_series = sensor.findtext('Series', default=None)
        sensor_unit = sensor.findtext('Unit', default=None)
        print(sensor_id, sensor_name, sensor_series, sensor_unit)


def get_latest_sensor_value(xml_string, sensor_to_get):
    """
    Gets the latest sensor value out of a list of value tags.
    Simplifies by assuming you can string sort on timestamp to get the latest value
    """
    latest = ''
    latest_value = 0
    tree = get_tree(xml_string)
    # loop over the sensor tags under the root xml element
    for sensor in tree:
        sensor_id = sensor.findtext('ID', default=None)
        info('sensor_id', sensor_id)
        if sensor_id == sensor_to_get:
            for tags in sensor:
                if tags.tag == 'Values':
                    for value_tag in tags.getiterator():
                        timestamp = value_tag.attrib.get('CreatedOn', None)
                        value = value_tag.attrib.get('Value', None)
                        if timestamp > latest:
                            latest = timestamp
                            latest_value = value
                    latest_value = Decimal(latest_value)
                    info('latest', latest)
                    info('latest_value', latest_value)
    return latest_value


# Actual code needed: get the XML (here we are using the test file, set to False to fetch live)
xml = get_xml(url, use_test_file=True)

# Get the values out of the XML by ID
WL_water_level = get_latest_sensor_value(xml, '1046')
print(WL_water_level)

EFM_water_level = get_latest_sensor_value(xml, '12')
print(EFM_water_level)
