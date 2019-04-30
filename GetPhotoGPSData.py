#-*- coding: utf-8 -*-

"""
Created on Fri Sep 14 09:27:37 2018
@author: mtroyer
"""

import os
import csv
import PIL.Image
import PIL.ExifTags


def convert_to_degress(value):
    """
    Convert exif GPS coordinate tuples to decimal degress
    """
    d = float(value[0][0]) / float(value[0][1])
    m = float(value[1][0]) / float(value[1][1])
    s = float(value[2][0]) / float(value[2][1])
    return d + (m / 60.0) + (s / 3600.0)


def getCoords(filepath):
    """
    Get lat/long gps coordinates from a photo.
    """
    img = PIL.Image.open(filepath)

    exif = {
        PIL.ExifTags.TAGS[key]: val
        for key, val in img._getexif().items()
        if key in PIL.ExifTags.TAGS
        }
    
    gpsinfo = {}
    for key in exif['GPSInfo'].keys():
        decode = PIL.ExifTags.GPSTAGS.get(key, key)
        gpsinfo[decode] = exif['GPSInfo'][key]

    latitude = gpsinfo['GPSLatitude']
    latitude_ref = gpsinfo['GPSLatitudeRef']
    lat_value = convert_to_degress(latitude)
    if latitude_ref == u'S':
        lat_value = -lat_value
                
    longitude = gpsinfo['GPSLongitude']
    longitude_ref = gpsinfo['GPSLongitudeRef']
    lon_value = convert_to_degress(longitude)
    if longitude_ref == 'W':
        lon_value = -lon_value

    return {'latitude': lat_value, 'longitude': lon_value}


def picsToCoordCSV(folder):
    '''Write photo coordinates to csv'''
    pic_formats = ('.PNG', '.JPEG', '.JPG')
    
    pics = [
        f for f in os.listdir(folder)
        if os.path.splitext(f)[1].upper() in pic_formats
        ]
        
    coords = {}
    for pic in pics:
        try:
            coords[pic] = getCoords(os.path.join(folder, pic))
        except:
            print('No GPS data: [{}]'.format(pic))

    out_csv = os.path.join(folder, 'coords.csv')
    with open(out_csv, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['name', 'path', 'latitude', 'longitude'])
        for name, coord in coords.items():
            row = (name, os.path.join(folder, name), coord['latitude'], coord['longitude'])
            csvwriter.writerow(row)

    return out_csv
