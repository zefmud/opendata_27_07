import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from time import sleep

INPUT_FILE = "green_zones.csv"
OUTPUT_FILE = "green_zones_coord.csv"

def get_cadaster_coordinates(number):
	browser.refresh()
	sleep(1)
	mySelect = Select(browser.find_element(by=By.ID, value="leaflet-control-geosearch-sel"))
	mySelect.select_by_value("3")
	input_select = browser.find_element(by=By.ID, value="leaflet-control-geosearch-qry").send_keys(number)
	sleep(1)
	input_result = browser.find_element(by=By.ID, value="leaflet-control-geosearch-result_0").click()

	sleep(1)
	select_marker = browser.find_element(by=By.CLASS_NAME, value="leaflet-clickable").click()

	sleep(1)
	lat_coordinate = browser.find_element_by_xpath('//div[text()="Широта:"]/parent::li').text.split(':')[1]
	lng_coordinate = browser.find_element_by_xpath('//div[text()="Довгота:"]/parent::li').text.split(':')[1]
	lat_coordinate = lat_coordinate.strip()
	lng_coordinate = lng_coordinate.strip()
	return [lat_coordinate,lng_coordinate]
	
browser = webdriver.Firefox()
browser.get('http://gisfile.com/map/')

input_f = open(INPUT_FILE, "r")
inp = csv.reader(input_f)
rows = [r for r in inp]
input_f.close()

output_headers = rows[0] + ["latitude", "longitude"]

output_f = open(OUTPUT_FILE, "w")
out_writer = csv.writer(output_f)
out_writer.writerow(output_headers)

for r in rows[1:]:
	cadaster_number = r[0].strip()
	print(r)
	print(type(r))
	out_r = r + get_cadaster_coordinates(cadaster_number)
	out_writer.writerow(out_r)
	print(out_r)
	
output_f.close()
