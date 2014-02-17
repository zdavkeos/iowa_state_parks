#!/usr/bin/env python

# Data taken from University of Iowa GIS Repository. (Source: Iowa DNR)
#  ftp://ftp.igsb.uiowa.edu/gis_library/ia_state/admin_political_boundary/public_lands/cons_rec_lands_public.zip
# srid: 26915

# More info:
#  http://www.iowadnr.gov/Destinations/StateParksRecAreas/IowasStateParks.aspx

# getting data out of postgis:
#  select ST_AsGeoJson(ST_Transform(geom, 4326)), name, county, acres from dnr_lands_public where type = 'State Park';

import json

with open("state_parks.geojson.csv", 'r') as fd:
    lines = fd.readlines()

hdr = lines[0].strip().split(';')

parks = []
for line in lines[1:]:
    line = line.strip().split(';')
    geojson = {'type':"Feature"}

    geojson['geometry'] = json.loads(line[0])
    geojson['properties'] = dict(zip(hdr[1:], line[1:]))
    geojson['properties']['acres'] = float(geojson['properties']['acres'])

    parks.append(geojson)

# merge
parks2 = []
for park in parks:
    name = park['properties']['name']

    for p in parks:
        if p != park and p['properties']['name'] == name:
            park['geometry'][u'coordinates'].append(p['geometry'][u'coordinates'][0])
            park['properties']['acres'] += p['properties']['acres']
            parks.remove(p)

    parks2.append(park)

# verify geojson: optional
if False:
    import requests
    validate_url = 'http://geojsonlint.com/validate'
    for park in parks2:
        geojson = json.dumps(park)
        req = requests.post(validate_url, data=geojson)
        print park['properties']['name'] + ' - ' + req.json[u'status']

# export
for park in parks2:
    name = park['properties']['name']
    name = name.replace('State Park', '')
    name = name.replace(".", '')
    name = name.replace("'", '')
    name = name.strip()

    with open('output/' + name + '.geojson', 'w') as fd:
        json.dump(park, fd)

