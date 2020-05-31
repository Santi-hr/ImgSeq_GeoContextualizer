import json
from datetime import datetime
from datetime import timedelta
import csv


def extract_from_location_history(location_history_path, folder_out, from_datetime_utc, to_datetime_utc):
    """Extract data from google location history between the input dates in UTC and stores them in a csv"""
    from_datetime_utc = from_datetime_utc - timedelta(hours=1)
    to_datetime_utc = to_datetime_utc + timedelta(hours=1)

    print("Extracting Google Location History ...")
    print("From", from_datetime_utc, "To", to_datetime_utc, "UTC")
    with open(location_history_path, "r") as file:
        dict_location_history = json.load(file)

    list_locations = []
    for location in dict_location_history['locations']:
        loc_datetime = datetime.utcfromtimestamp(int(location["timestampMs"]) / 1000)
        if loc_datetime > from_datetime_utc:
            loc_lat = float(location['latitudeE7']) / 10000000.0
            loc_lon = float(location['longitudeE7']) / 10000000.0
            loc_accuracy = int(location['accuracy'])
            list_locations.append({"timestampMs": loc_datetime,
                                   "latitude": loc_lat,
                                   "longitude": loc_lon,
                                   "accuracy": loc_accuracy})
        elif loc_datetime > to_datetime_utc:
            break

    # Spanish CSV format. For author debugging
    # with open(folder_out+"location_history_es.csv", "w") as f_out:
    #     for i in range(len(list_locations)):
    #         f_out.write(("%s;%.8f;%.8f;%d\n" % (list_locations[i]["timestampMs"].strftime("%Y-%m-%d %H:%M:%S"),
    #                                             list_locations[i]["latitude"],
    #                                             list_locations[i]["longitude"],
    #                                             list_locations[i]["accuracy"])).replace('.', ','))

    with open(folder_out + "location_history.csv", "w") as f_out:
        for i in range(len(list_locations)):
            f_out.write(("%s,%.8f,%.8f,%d\n" % (list_locations[i]["timestampMs"].strftime("%Y-%m-%d %H:%M:%S"),
                                                list_locations[i]["latitude"],
                                                list_locations[i]["longitude"],
                                                list_locations[i]["accuracy"])))
    print("Done Extracting Google Location History")


def load_location_history_data(file_folder):
    """Load the extracted google location history data from the csv stored in file_folder."""
    accuracy_limit = 40
    with open(file_folder + "location_history.csv") as csvfile:
        reader = csv.reader(csvfile)
        data = list(reader)
    dict_google = {'timestampMs': [], 'latitude': [], 'longitude': [], 'accuracy': []}
    for i in range(len(data)):
        accuracy = int(data[i][3])
        if accuracy < accuracy_limit:
            dict_google['timestampMs'].append(datetime.strptime(data[i][0], "%Y-%m-%d %H:%M:%S"))
            dict_google['latitude'].append(float(data[i][1]))
            dict_google['longitude'].append(float(data[i][2]))
            # dict_google['accuracy'].append(accuracy)

    return dict_google
