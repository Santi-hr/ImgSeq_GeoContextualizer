import os.path
import src.helpers as helpers
import src.extractExif as extractExif
import src.extractGoogleLocationHistory as extractGoogleLocation
import src.mapplotAnimationPresets as mapplotAnimationPresets
import src.extraAnimationPresets as extraAnimationPresets

# ---------- 1. Input variables ----------
# Remember that photos must be already ordered chronologically
project_name = "Example"
pics_folder = "C:/User/Raw/Photos"  # Can be full path "C:/.../.../..."
timezone_hour_diff = 1  # Won't sync properly photos from different timezones
force_regenerate = False  # To create again the csv from images and history location
use_location_history = True  # Set to True if location history is available. Set to False to use exif data
location_history_path = "location history.json"  # Can be full path

# Proceed to step 3 to configure what plots are generated

# ---------- 2. Data Loading ----------
aux_folder = project_name + "/auxiliar/"
helpers.ensure_directory(aux_folder)

if not os.path.isfile(aux_folder+"exif.csv") or force_regenerate:
    extractExif.extract_exif_folder(pics_folder, aux_folder)
dict_exif = extractExif.load_exif_data(aux_folder, timezone_hour_diff, autofix=False)

if use_location_history:
    if not os.path.isfile(aux_folder+"location_history.csv") or force_regenerate:
        extractGoogleLocation.extract_from_location_history(
            location_history_path, aux_folder, dict_exif['timestampMs'][0], dict_exif['timestampMs'][-1])
    dict_Loc_History = extractGoogleLocation.load_location_history_data(aux_folder)
else:
    dict_Loc_History = extractExif.exif_data_to_loc_hist(dict_exif)

# ---------- 3. Data plotting ----------
img_start = 0
img_start_middle = 0
img_end = -1  # Set to -1 to process all images in folder

mapplotAnimationPresets.region_all_data(
    dict_exif, dict_Loc_History, img_start, img_end, img_start_middle, project_name+"/region/")

mapplotAnimationPresets.centered_on_location(
    dict_exif, dict_Loc_History, img_start, img_end, img_start_middle, project_name+"/centered/")

mapplotAnimationPresets.region_expanding_by_day(
    dict_exif, dict_Loc_History, img_start, img_end, img_start_middle, project_name+"/region_expanding_day/")

mapplotAnimationPresets.region_expanding_by_last_n_pics(
    dict_exif, dict_Loc_History, img_start, img_end, img_start_middle, output_folder= project_name+"/region_expanding_last/")

extraAnimationPresets.clocks(dict_exif, img_start, img_end, img_start_middle, project_name+"/extra/clocks/")
extraAnimationPresets.timeline(dict_exif, img_start, img_end, img_start_middle, project_name+"/extra/timeline/")
extraAnimationPresets.frame_count(dict_exif, img_start, img_end, img_start_middle, project_name+"/extra/frame_count/")

print("PLOTTING ENDED -")
