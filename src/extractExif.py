import os
import csv
from datetime import datetime
from datetime import timedelta
import exifread


def extract_gps_exif(exif_tags):
    """Extracts and returns GPS in degrees from exif_tags"""
    # Invalid values if tags do not exist
    gps_lat_out = 91
    gps_lon_out = 181

    if 'GPS GPSLatitude' in exif_tags:
        gps_lat = exif_tags['GPS GPSLatitude'].values
        gps_lat_ref = exif_tags['GPS GPSLatitudeRef'].values
        gps_lon = exif_tags['GPS GPSLongitude'].values
        gps_lon_ref = exif_tags['GPS GPSLongitudeRef'].values

        gps_lat_out = gps_lat[0].num + gps_lat[1].num / 60.0 + gps_lat[2].num / 3600.0
        if gps_lat_ref == 'S':
            gps_lat_out = -gps_lat_out

        gps_lon_out = gps_lon[0].num + gps_lon[1].num / 60.0 + gps_lon[2].num / 3600.0
        if gps_lon_ref == 'W':
            gps_lon_out = -gps_lon_out

    return gps_lat_out, gps_lon_out


def extract_datetime_exif(exif_tags):
    """Extract and returns local time and date from exif_tags"""
    # Invalid values if tags do not exist
    datetime_out = datetime(year=1900, month=1, day=1)

    if 'Image DateTime' in exif_tags:
        datetime_out = datetime.strptime(exif_tags['Image DateTime'].values, "%Y:%m:%d %H:%M:%S")

    return datetime_out


def extract_exif_data(img_path):
    """Extracts GPS and time data from the exif data of image at img_path"""
    exif_tags = {}
    with open(img_path, 'rb') as f:
        exif_tags = exifread.process_file(f, details=False)
    gps_lat_out, gps_lon_out = extract_gps_exif(exif_tags)
    img_datetime = extract_datetime_exif(exif_tags)

    return gps_lat_out, gps_lon_out, img_datetime


def extract_exif_folder(pics_folder, output_folder):
    """Extracts all relevant exif data from images in a folder and stores them in a csv at the output_folder"""
    list_pics = os.listdir(pics_folder)

    count_no_gps = 0
    list_gps_valid = []
    list_gps_lat = []
    list_gps_lon = []
    list_idx = []
    list_datetime = []
    list_filename = []

    for i in range(len(list_pics)):
        name_pic = list_pics[i]
        path_pic = pics_folder + '/' + name_pic

        gps_lat, gps_lon, img_datetime = extract_exif_data(path_pic)

        b_gps_valid = True
        if gps_lat > 90:
            b_gps_valid = False
            count_no_gps += 1

        print(i, path_pic, b_gps_valid, gps_lat, gps_lon)
        list_idx.append(i)
        list_gps_valid.append(b_gps_valid)
        list_gps_lat.append(gps_lat)
        list_gps_lon.append(gps_lon)
        list_datetime.append(img_datetime)
        list_filename.append(name_pic)

    print("Images with no gps data:", count_no_gps)
    # Spanish CSV format. For author debugging
    # with open(output_folder+"exif_es.csv", "w") as f_out:
    #     separator = ';'
    #     for i in range(len(list_idx)):
    #         f_out.write(
    #             separator.join([
    #                 list_datetime[i].strftime("%Y-%m-%d %H:%M:%S"),
    #                 "%d" % list_gps_valid[i],
    #                 "%.8f" % list_gps_lat[i],
    #                 "%.8f" % list_gps_lon[i],
    #                 "%d" % list_gps_valid[i],
    #                 list_filename[i]
    #             ]).replace('.', ',') + '\n')

    with open(output_folder + "exif.csv", "w") as f_out:
        separator = ','
        for i in range(len(list_idx)):
            f_out.write(
                separator.join([
                    list_datetime[i].strftime("%Y-%m-%d %H:%M:%S"),
                    "%d" % list_gps_valid[i],
                    "%.8f" % list_gps_lat[i],
                    "%.8f" % list_gps_lon[i],
                    "%d" % list_gps_valid[i],
                    list_filename[i]
                ]) + '\n')


def check_time_order(dict_exif_in, autofix):
    """Check if timestamps are ordered by looking for negative diferences between images"""
    b_error_detected = False

    if len(dict_exif_in['timestampMs']) > 1:
        for i in range(1, len(dict_exif_in['timestampMs'])):
            date_diff = dict_exif_in['timestampMs'][i]-dict_exif_in['timestampMs'][i-1]
            if date_diff.total_seconds() < 0:
                if autofix:
                    #Simple fix, set time to that of previous picture
                    dict_exif_in['timestampMs'][i-1] = dict_exif_in['timestampMs'][i]
                    dict_exif_in['timestampMs_localtime'][i-1] = dict_exif_in['timestampMs_localtime'][i]
                else:
                    print("File:", dict_exif_in['filename'][i - 1],
                          "Exif time", dict_exif_in['timestampMs_localtime'][i-1])
                    b_error_detected = True

    if b_error_detected:
        print("\nERROR: Timestamps not chronologically ordered.")
        print("Please check EXIF timestamp for above images")
        print("SOLUTIONS:")
        print("    - Modify manually the auxiliar/exif.csv or the image exif")
        print("    - Set autofix to True in extractExif.load_exif_data()")
        exit(-5)


def load_exif_data(file_folder, timezone_diff_h, autofix):
    """Load the extracted exif data from the csv stored in file_folder.
    timezone_diff_h: Timezone correction to get a UTC timestamp (Only one timezone can be set)
    Autofix: Set to True to correct bad stored exif time. Set to False to only get the ERROR and manually fix.
    """
    with open(file_folder + "exif.csv") as csvfile:
        reader = csv.reader(csvfile)
        data = list(reader)
    dict_exif = {'timestampMs_localtime': [], 'timezoneH': timezone_diff_h, 'timestampMs': [],
                 'pic_idx': [], 'filename': [], 'has_gps': [], 'latitude': [], 'longitude': [], }
    for i in range(len(data)):
        local_datetime = datetime.strptime(data[i][0], "%Y-%m-%d %H:%M:%S")
        dict_exif['timestampMs_localtime'].append(local_datetime)
        dict_exif['has_gps'].append(bool(int(data[i][1])))
        dict_exif['latitude'].append(float(data[i][2]))
        dict_exif['longitude'].append(float(data[i][3]))
        dict_exif['pic_idx'].append(int(data[i][4]))
        dict_exif['filename'].append(data[i][5])
        dict_exif['timestampMs'].append(local_datetime - timedelta(hours=timezone_diff_h))

    check_time_order(dict_exif, autofix)
    return dict_exif


def exif_data_to_loc_hist(dict_exif_in):
    """Converts exif dictionary to location history dictionary"""
    dict_exif_out = {'timestampMs': [], 'latitude': [], 'longitude': []}
    for i in range(len(dict_exif_in['timestampMs'])):
        if dict_exif_in['has_gps'][i]:
            dict_exif_out['timestampMs'].append(dict_exif_in['timestampMs'][i])
            dict_exif_out['latitude'].append(dict_exif_in['latitude'][i])
            dict_exif_out['longitude'].append(dict_exif_in['longitude'][i])

    return dict_exif_out
