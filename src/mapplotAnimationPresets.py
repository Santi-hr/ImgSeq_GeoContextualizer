import time
from datetime import timedelta
import src.mapplot as mapplot
import src.mapplotAnimationHelpers as mapplotAnimationHelpers
import src.helpers as helpers


def get_index_close_to_timestamp(data_in, datetime_target):
    """Returns the index of the closest timestamp
    :param data_in: Dictionary with exif/precise data
    :param datetime_target: Target datetime object in UTC
    :return: Index of data_in list
    """
    # Iterate through all data and check when the target is reached, then compare which sample is closest
    index_closest = 0
    for index_closest in range(1, len(data_in['timestampMs'])):
        if data_in['timestampMs'][index_closest] >= datetime_target:
            # Check if the previous google location is closest to the desired exif utc timestamp
            diff_time = data_in['timestampMs'][index_closest] - datetime_target
            diff_time_prev = datetime_target - data_in['timestampMs'][index_closest - 1]
            if diff_time_prev < diff_time:
                index_closest -= 1
            break
    return index_closest


def get_index_previous_timestamp(data_in, datetime_target, idx_start, idx_limit=0):
    """
    Returns index of the image with a timestamp previous of the input target
    :param data_in: Dictionary with exif/precise data
    :param datetime_target: Target datetime object in UTC
    :param idx_start: Sample from where the search is initiated. It goes backwards in the list
    :param idx_limit: Last valid sample in the list. To limit the search to part of the data
    :return:  Index of data_in list
    """
    if idx_limit < 0:
        idx_limit = 0

    if idx_start <= idx_limit:
        idx_return = idx_limit
    else:
        idx_return = idx_start + 1 #Loop starts by substracting

        target_found = False
        while not target_found:
            idx_return -= 1
            if idx_return > idx_limit:
                if data_in['timestampMs'][idx_return] <= datetime_target:
                    target_found = True
            else:
                # No more valid samples to analyze
                target_found = True
    return idx_return


def centered_on_location(data_exif, data_precise, img_start, img_end=-1, idx_continue=0, output_folder="test_output/"):
    """
    For each sample in data exif an image is generated centering the map view in the closest precise sample (by time)
    :param data_exif: Dictionary with exif data from the input images
    :param data_precise: Dictionary with the data used to draw the trayectory. Use google location if possible
    :param img_start: First image to be processed. Index from data_exif
    :param img_end: Last image to be processed. Index from data_exif. Set to negative to process all data in data_exif
    :param idx_continue: Index to continue exporting data. The fcn will start at this idx, use in case an Exception
    raises to start from the last run iteration and not have to export already processed images
    :param output_folder: Folder where images will be stored
    """
    # ---------- Sanitize inputs and initialize variables ----------
    if img_end < 0:
        img_end = len(data_exif['timestampMs'])
    idx_continue = idx_continue + img_start

    helpers.ensure_directory(output_folder)
    mapplotAnimationHelpers.sync_helper_file(img_start, img_end, data_exif['filename'], output_folder)

    # custom_obj_map = mapplot.MapPlot()
    custom_obj_map = mapplot.MapPlot(maxtiles=17)
    custom_obj_map.expect_const_area = True  # To reduce the number of map fetchs

    idx_precise_first = get_index_close_to_timestamp(data_precise, data_exif['timestampMs'][img_start])

    # ---------- Process loop ----------
    time_start = time.perf_counter()
    for i in range(idx_continue, img_end):
        time_start_it = time.perf_counter()
        # ---------- Set iteration values ----------
        idx_animation = i - img_start + 1

        datetime_target = data_exif['timestampMs'][i]
        dt_local_day_start_in_utc = (data_exif['timestampMs_localtime'][i].replace(
            hour=0, minute=0, second=0)) - timedelta(hours=data_exif['timezoneH'])

        idx_exif = i

        idx_precise = get_index_close_to_timestamp(data_precise, datetime_target)
        idx_precise_day_start = get_index_previous_timestamp(data_precise, dt_local_day_start_in_utc, idx_precise, idx_precise_first)

        # ---------- Generate map and draw on it ----------
        margin = 0.01
        custom_obj_map.set_map_around_point(
            data_precise['latitude'][idx_precise],
            data_precise['longitude'][idx_precise],
            margin)

        custom_obj_map.draw_list(
            data_precise['latitude'][idx_precise_first:idx_precise_day_start + 1],
            data_precise['longitude'][idx_precise_first:idx_precise_day_start + 1],
            lineop_in='-', c_in='#9a0200', ms_in=10, mew_in=1, lw_in=2)

        custom_obj_map.draw_list(
            data_precise['latitude'][idx_precise_day_start:idx_precise + 1],
            data_precise['longitude'][idx_precise_day_start:idx_precise + 1],
            lineop_in='-', c_in='r', ms_in=10, mew_in=1, lw_in=2)

        custom_obj_map.draw_single_marker(
            data_precise['latitude'][idx_precise],
            data_precise['longitude'][idx_precise],
            s_in=90, c_in='r', marker_in='o', zorder_in=100, edgecolors_in='k')  # moss green (#658b38)

        if data_exif['has_gps'][idx_exif]:
            custom_obj_map.draw_single_marker(
                data_exif['latitude'][idx_exif],
                data_exif['longitude'][idx_exif],
                s_in=120, c_in='#03719c', marker_in='o', zorder_in=110, edgecolors_in='k')

        # ---------- Export map and clear iteration variables ----------
        custom_obj_map.save_plot(output_folder + str(idx_animation) + ".png")
        custom_obj_map.clear()

        # ---------- Console output ----------
        mapplotAnimationHelpers.print_console(
            idx_animation, img_start, img_end, time_start, time_start_it, data_exif['filename'][idx_exif])
        custom_obj_map.print_stats()
        print("---- · ----")


def region_all_data(data_exif, data_precise, img_start, img_end=-1, idx_continue=0, output_folder="test_output/"):
    """
    For each sample in data exif an image is generated centering the map region the whole images take
    :param data_exif: Dictionary with exif data from the input images
    :param data_precise: Dictionary with the data used to draw the trayectory. Use google location if possible
    :param img_start: First image to be processed. Index from data_exif
    :param img_end: Last image to be processed. Index from data_exif. Set to negative to process all data in data_exif
    :param idx_continue: Index to continue exporting data. The fcn will start at this idx, use in case an Exception
    raises to start from the last run iteration and not have to export already processed images
    :param output_folder: Folder where images will be stored
    """
    # ---------- Sanitize inputs and initialize variables ----------
    if img_end < 0:
        img_end = len(data_exif['timestampMs'])
    idx_continue = idx_continue + img_start

    helpers.ensure_directory(output_folder)
    mapplotAnimationHelpers.sync_helper_file(img_start, img_end, data_exif['filename'], output_folder)

    idx_precise_first = get_index_close_to_timestamp(data_precise, data_exif['timestampMs'][img_start])
    idx_precise_last = get_index_close_to_timestamp(data_precise, data_exif['timestampMs'][img_end-1])

    region_lat_min = min(data_precise['latitude'][idx_precise_first: idx_precise_last])
    region_lon_min = min(data_precise['longitude'][idx_precise_first: idx_precise_last])
    region_lat_max = max(data_precise['latitude'][idx_precise_first: idx_precise_last])
    region_lon_max = max(data_precise['longitude'][idx_precise_first: idx_precise_last])

    custom_obj_map = mapplot.MapPlot(maxtiles=32)

    # ---------- Process loop ----------
    time_start = time.perf_counter()
    for i in range(idx_continue, img_end):
        time_start_it = time.perf_counter()
        # ---------- Set iteration values ----------
        idx_animation = i - img_start + 1

        datetime_target = data_exif['timestampMs'][i]
        dt_local_day_start_in_utc = (data_exif['timestampMs_localtime'][i].replace(
            hour=0, minute=0, second=0)) - timedelta(hours=data_exif['timezoneH'])

        idx_exif = i

        idx_precise = get_index_close_to_timestamp(data_precise, datetime_target)
        idx_precise_day_start = get_index_previous_timestamp(data_precise, dt_local_day_start_in_utc, idx_precise, idx_precise_first)

        # ---------- Generate map and draw on it ----------
        margin = 0.1
        custom_obj_map.set_map_region_precise(region_lat_min,region_lon_min, region_lat_max, region_lon_max, margin)

        custom_obj_map.draw_list(
            data_precise['latitude'][idx_precise_first:idx_precise_day_start + 1],
            data_precise['longitude'][idx_precise_first:idx_precise_day_start + 1],
            lineop_in='-', c_in='#9a0200', ms_in=10, mew_in=1, lw_in=2)

        custom_obj_map.draw_list(
            data_precise['latitude'][idx_precise_day_start:idx_precise + 1],
            data_precise['longitude'][idx_precise_day_start:idx_precise + 1],
            lineop_in='-', c_in='r', ms_in=10, mew_in=1, lw_in=2)

        custom_obj_map.draw_single_marker(
            data_precise['latitude'][idx_precise],
            data_precise['longitude'][idx_precise],
            s_in=150, c_in='r', marker_in='o', zorder_in=110, edgecolors_in='k', linewidth_in=2)

        if data_exif['has_gps'][idx_exif]:
            custom_obj_map.draw_single_marker(
                data_exif['latitude'][idx_exif],
                data_exif['longitude'][idx_exif],
                s_in=50, c_in='#03719c', marker_in='o', zorder_in=100, edgecolors_in='k')

        # ---------- Export map and clear iteration variables ----------
        custom_obj_map.save_plot(output_folder + str(idx_animation) + ".png")
        custom_obj_map.clear()

        # ---------- Console output ----------
        mapplotAnimationHelpers.print_console(
            idx_animation, img_start, img_end, time_start, time_start_it, data_exif['filename'][idx_exif])
        custom_obj_map.print_stats()
        print("---- · ----")


def region_expanding_by_day(data_exif, data_precise, img_start, img_end=-1, idx_continue=0, output_folder="test_output/"):
    """
    For each sample in data exif an image is generated showing all samples of the day in the map. The region expands to
    fit all samples of that day.
    :param data_exif: Dictionary with exif data from the input images
    :param data_precise: Dictionary with the data used to draw the trayectory. Use google location if possible
    :param img_start: First image to be processed. Index from data_exif
    :param img_end: Last image to be processed. Index from data_exif. Set to negative to process all data in data_exif
    :param idx_continue: Index to continue exporting data. The fcn will start at this idx, use in case an Exception
    raises to start from the last run iteration and not have to export already processed images
    :param output_folder: Folder where images will be stored
    """
    # ---------- Sanitize inputs and initialize variables ----------
    if img_end < 0:
        img_end = len(data_exif['timestampMs'])
    idx_continue = idx_continue + img_start

    helpers.ensure_directory(output_folder)
    mapplotAnimationHelpers.sync_helper_file(img_start, img_end, data_exif['filename'], output_folder)

    custom_obj_map = mapplot.MapPlot()

    idx_precise_first = get_index_close_to_timestamp(data_precise, data_exif['timestampMs'][img_start])

    # ---------- Process loop ----------
    time_start = time.perf_counter()
    for i in range(idx_continue, img_end):
        time_start_it = time.perf_counter()
        # ---------- Set iteration values ----------
        idx_animation = i - img_start + 1

        datetime_target = data_exif['timestampMs'][i]
        dt_local_day_start_in_utc = (data_exif['timestampMs_localtime'][i].replace(
            hour=0, minute=0, second=0)) - timedelta(hours=data_exif['timezoneH'])

        idx_exif = i

        idx_precise = get_index_close_to_timestamp(data_precise, datetime_target)
        idx_precise_day_start = get_index_previous_timestamp(data_precise, dt_local_day_start_in_utc, idx_precise, idx_precise_first)

        # ---------- Generate map and draw on it ----------
        margin = 0.01

        if idx_precise_day_start == idx_precise:
            custom_obj_map.set_map_around_point(
                data_precise['latitude'][idx_precise],
                data_precise['longitude'][idx_precise],
                margin)
        else:
            region_lat_min = min(data_precise['latitude'][idx_precise_day_start: idx_precise])
            region_lon_min = min(data_precise['longitude'][idx_precise_day_start: idx_precise])
            region_lat_max = max(data_precise['latitude'][idx_precise_day_start: idx_precise])
            region_lon_max = max(data_precise['longitude'][idx_precise_day_start: idx_precise])

            custom_obj_map.set_map_region_precise(region_lat_min,region_lon_min, region_lat_max, region_lon_max, margin)

        custom_obj_map.draw_list(
            data_precise['latitude'][idx_precise_first:idx_precise_day_start + 1],
            data_precise['longitude'][idx_precise_first:idx_precise_day_start + 1],
            lineop_in='-', c_in='#9a0200', ms_in=10, mew_in=1, lw_in=2)

        custom_obj_map.draw_list(
            data_precise['latitude'][idx_precise_day_start:idx_precise + 1],
            data_precise['longitude'][idx_precise_day_start:idx_precise + 1],
            lineop_in='-', c_in='r', ms_in=10, mew_in=1, lw_in=2)

        custom_obj_map.draw_single_marker(
            data_precise['latitude'][idx_precise],
            data_precise['longitude'][idx_precise],
            s_in=90, c_in='r', marker_in='o', zorder_in=100, edgecolors_in='k')  # moss green (#658b38)

        if data_exif['has_gps'][idx_exif]:
            custom_obj_map.draw_single_marker(
                data_exif['latitude'][idx_exif],
                data_exif['longitude'][idx_exif],
                s_in=120, c_in='#03719c', marker_in='o', zorder_in=110, edgecolors_in='k')

        # ---------- Export map and clear iteration variables ----------
        custom_obj_map.save_plot(output_folder + str(idx_animation) + ".png")
        custom_obj_map.clear()

        # ---------- Console output ----------
        mapplotAnimationHelpers.print_console(
            idx_animation, img_start, img_end, time_start, time_start_it, data_exif['filename'][idx_exif])
        custom_obj_map.print_stats()
        print("---- · ----")


def region_expanding_by_last_n_pics(data_exif, data_precise, img_start, img_end=-1, idx_continue=0, n_pics=7, output_folder="test_output/"):
    """
    For each sample in data exif an image is generated showing the last N samples in the map. The region expands to
    fit all N samples.
    :param data_exif: Dictionary with exif data from the input images
    :param data_precise: Dictionary with the data used to draw the trayectory. Use google location if possible
    :param img_start: First image to be processed. Index from data_exif
    :param img_end: Last image to be processed. Index from data_exif. Set to negative to process all data in data_exif
    :param idx_continue: Index to continue exporting data. The fcn will start at this idx, use in case an Exception
    raises to start from the last run iteration and not have to export already processed images
    :param output_folder: Folder where images will be stored
    """
    # ---------- Sanitize inputs and initialize variables ----------
    if img_end < 0:
        img_end = len(data_exif['timestampMs'])
    idx_continue = idx_continue + img_start

    if n_pics < 2:
        n_pics = 2

    helpers.ensure_directory(output_folder)
    mapplotAnimationHelpers.sync_helper_file(img_start, img_end, data_exif['filename'], output_folder)

    custom_obj_map = mapplot.MapPlot()

    idx_precise_first = get_index_close_to_timestamp(data_precise, data_exif['timestampMs'][img_start])

    # ---------- Process loop ----------
    time_start = time.perf_counter()
    for i in range(idx_continue, img_end):
        time_start_it = time.perf_counter()
        # ---------- Set iteration values ----------
        idx_animation = i - img_start + 1

        datetime_target = data_exif['timestampMs'][i]
        dt_local_day_start_in_utc = (data_exif['timestampMs_localtime'][i].replace(
            hour=0, minute=0, second=0)) - timedelta(hours=data_exif['timezoneH'])

        idx_exif = i

        idx_precise = get_index_close_to_timestamp(data_precise, datetime_target)
        idx_precise_day_start = get_index_previous_timestamp(data_precise, dt_local_day_start_in_utc, idx_precise, idx_precise_first)

        # ---------- Generate map and draw on it ----------
        margin = 0.005

        idx_prev = idx_precise_first
        if idx_animation == 1:
            region_lat_min = data_precise['latitude'][idx_precise_first] - margin
            region_lon_min = data_precise['longitude'][idx_precise_first] - margin
            region_lat_max = data_precise['latitude'][idx_precise_first] + margin
            region_lon_max = data_precise['longitude'][idx_precise_first] + margin
        elif idx_animation <= n_pics:
            region_lat_min = min(data_precise['latitude'][idx_precise_first: idx_precise + 1])
            region_lon_min = min(data_precise['longitude'][idx_precise_first: idx_precise + 1])
            region_lat_max = max(data_precise['latitude'][idx_precise_first: idx_precise + 1])
            region_lon_max = max(data_precise['longitude'][idx_precise_first: idx_precise + 1])
        else:
            idx_prev = get_index_close_to_timestamp(data_precise, data_exif['timestampMs'][i-n_pics])
            region_lat_min = min(data_precise['latitude'][idx_prev: idx_precise + 1])
            region_lon_min = min(data_precise['longitude'][idx_prev: idx_precise + 1])
            region_lat_max = max(data_precise['latitude'][idx_prev: idx_precise + 1])
            region_lon_max = max(data_precise['longitude'][idx_prev: idx_precise + 1])


        # Map will automatically download if the new region is smaller
        custom_obj_map.set_map_region_square(region_lat_min, region_lon_min, region_lat_max, region_lon_max, margin)

        custom_obj_map.draw_list(
            data_precise['latitude'][idx_precise_first:idx_precise_day_start + 1],
            data_precise['longitude'][idx_precise_first:idx_precise_day_start + 1],
            lineop_in='-', c_in='#9a0200', ms_in=10, mew_in=1, lw_in=2)

        custom_obj_map.draw_list(
            data_precise['latitude'][idx_precise_day_start:idx_precise + 1],
            data_precise['longitude'][idx_precise_day_start:idx_precise + 1],
            lineop_in='-', c_in='r', ms_in=10, mew_in=1, lw_in=2)

        custom_obj_map.draw_single_marker(
            data_precise['latitude'][idx_precise],
            data_precise['longitude'][idx_precise],
            s_in=100, c_in='r', marker_in='o', zorder_in=110, edgecolors_in='k')  # moss green (#658b38)

        # Print degrading circles fixme
        mark_s_max = 180
        for j in range(n_pics):
            mark_s_max = mark_s_max/1.5
            if data_exif['has_gps'][idx_exif-j]:
                custom_obj_map.draw_single_marker(
                    data_exif['latitude'][idx_exif-j],
                    data_exif['longitude'][idx_exif-j],
                    s_in=mark_s_max, c_in='#03719c', marker_in='o', zorder_in=100, edgecolors_in='k')

        # ---------- Export map and clear iteration variables ----------
        custom_obj_map.save_plot(output_folder + str(idx_animation) + ".png")
        custom_obj_map.clear()

        # ---------- Console output ----------
        mapplotAnimationHelpers.print_console(
            idx_animation, img_start, img_end, time_start, time_start_it, data_exif['filename'][idx_exif])
        custom_obj_map.print_stats()
        print("---- · ----")
