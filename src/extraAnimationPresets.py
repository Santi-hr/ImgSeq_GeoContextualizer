import time
import math
import matplotlib.pyplot as plt
import src.mapplotAnimationHelpers as mapplotAnimationHelpers
import src.helpers as helpers


def timeline(data_exif, img_start, img_end=-1, idx_continue=0, output_folder="test_output/"):
    """
    For each sample in data exif a plot is generated showing the local time of capture of all the images of the day up
    to the current sample timedate
    :param data_exif: Dictionary with exif data from the input images
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

    time_start = time.perf_counter()
    for i in range(idx_continue, img_end):
        time_start_it = time.perf_counter()

        # ---------- Set iteration values ----------
        idx_animation = i - img_start + 1

        list_aux_x = []
        list_aux_y = []
        target_found = False
        idx_limit = img_start
        idx_loop = i
        dt_local_day_start = data_exif['timestampMs_localtime'][i].replace(hour=0, minute=0, second=0)
        while not target_found:
            if idx_loop >= idx_limit:
                if data_exif['timestampMs_localtime'][idx_loop] <= dt_local_day_start:
                    target_found = True
                else:
                    secs_since_day_start = data_exif['timestampMs_localtime'][idx_loop].hour*3600 + \
                                           data_exif['timestampMs_localtime'][idx_loop].minute*60 + \
                                           data_exif['timestampMs_localtime'][idx_loop].second
                    list_aux_x.append(secs_since_day_start)
                    list_aux_y.append(1)
            else:
                # No more valid samples to analyze
                target_found = True
            idx_loop -= 1

        list_ref_x = [0]
        list_ref_y = [0.9]
        for j in range(25):
            list_ref_x.append(j*3600)
            list_ref_y.append(0.9)

        fig, ax = plt.subplots(nrows=1, ncols=1)
        fig.set_size_inches(8, 1.5)

        ax.scatter(list_ref_x, list_ref_y, 180, color='#0485d1', marker='|');
        ax.scatter(list_ref_x[0], list_ref_y[0], 200, color='White', marker='|');
        ax.scatter(list_ref_x[13], list_ref_y[13], 200, color='White', marker='|');
        ax.scatter(list_ref_x[-1], list_ref_y[-1], 200, color='White', marker='|');
        ax.scatter(list_aux_x, list_aux_y, 180, color='White', marker='|');
        ax.scatter(list_aux_x[0], list_aux_y[0], 180, color='Red', marker='|');

        ax.text(list_ref_x[0], list_ref_y[0] - 0.6, "0", color='White', fontsize=18, horizontalalignment='center')
        ax.text(list_ref_x[13], list_ref_y[13] - 0.6, "12", color='White', fontsize=18, horizontalalignment='center')
        ax.text(list_ref_x[-1], list_ref_y[-1] - 0.6, "24", color='White', fontsize=18, horizontalalignment='center')

        for i in range(3,24,3):
            if i == 12:
                continue
            ax.text(list_ref_x[i+1], list_ref_y[i+1] - 0.6, "%d" % (i), color='#0485d1', fontsize=16, horizontalalignment='center')



        ax.set_facecolor((0, 0 ,0))
        # ax.axis("equal")
        ax.axis([-3600, 86400.0+3600, 0, 2]);

        plt.savefig(output_folder + str(idx_animation) + ".png")
        # plt.show()
        fig.clf()
        plt.close('all')

        mapplotAnimationHelpers.print_console(
            idx_animation, img_start, img_end, time_start, time_start_it, data_exif['filename'][i])


def clocks(data_exif, img_start, img_end=-1, idx_continue=0, output_folder="test_output/"):
    """
    For each sample in data exif a plot is generated showing an analog and digital clock with the local time and date
    :param data_exif: Dictionary with exif data from the input images
    :param img_start: First image to be processed. Index from data_exif
    :param img_end: Last image to be processed. Index from data_exif. Set to negative to process all data in data_exif
    :param idx_continue: Index to continue exporting data. The fcn will start at this idx, use in case an Exception
    raises to start from the last run iteration and not have to export already processed images
    :param output_folder: Folder where images will be stored
    """
    # Port from an older matlab script
    # ---------- Sanitize inputs and initialize variables ----------
    if img_end < 0:
        img_end = len(data_exif['timestampMs'])
    idx_continue = idx_continue + img_start

    helpers.ensure_directory(output_folder)
    mapplotAnimationHelpers.sync_helper_file(img_start, img_end, data_exif['filename'], output_folder)

    th = [x * (math.pi/50) for x in range(0, 100)]
    xunit = []
    yunit = []
    for i in range(len(th)):
        xunit.append(math.cos(th[i]))
        yunit.append(math.sin(th[i]))
    agujaH_l = 0.5
    agujaM_l = 0.85

    time_start = time.perf_counter()
    for i in range(idx_continue, img_end):
        time_start_it = time.perf_counter()
        # ---------- Set iteration values ----------
        idx_animation = i - img_start + 1
        datetime_target = data_exif['timestampMs_localtime'][i]

        hour = datetime_target.hour
        minute = datetime_target.minute

        agujaHx = [0, agujaH_l * math.cos(-(hour * math.pi / 6) + (math.pi / 2))]
        agujaHy = [0, agujaH_l * math.sin(-(hour * math.pi / 6) + (math.pi / 2))]
        agujaMx = [0, agujaM_l * math.cos(-(minute * math.pi / 30) + (math.pi / 2))]
        agujaMy = [0, agujaM_l * math.sin(-(minute * math.pi / 30) + (math.pi / 2))]


        fig, ax = plt.subplots(nrows=1, ncols=1)
        # fig.set_size_inches(9, 5)
        fig.set_size_inches(15, 5)

        ax.plot(xunit, yunit, lw=8, color='White');
        ax.plot(agujaHx, agujaHy, lw=8, color='White');
        ax.plot(agujaMx, agujaMy, lw=8, color='White');
        ax.text(1.3, 0.4, datetime_target.strftime("%H:%M"), color='White', fontsize=75)
        # ax.text(1.2, -0.65, datetime_target.strftime("%d/%m"), color='White', fontsize=75)
        ax.text(3.4, 0.4, datetime_target.strftime("%d/%m"), color='White', fontsize=75)
        ax.set_facecolor((0, 0 ,0))
        ax.axis("equal")
        ax.axis([-1.3, 5.5, -1.2, 1.2]);


        plt.savefig(output_folder + str(idx_animation) + ".png")
        # plt.show()
        fig.clf()
        plt.close('all')

        mapplotAnimationHelpers.print_console(
            idx_animation, img_start, img_end, time_start, time_start_it, data_exif['filename'][i])


def frame_count(data_exif, img_start, img_end=-1, idx_continue=0, output_folder="test_output/"):
    """
    For each sample in data exif a plot is generated showing the frame number of the animation
    :param data_exif: Dictionary with exif data from the input images
    :param img_start: First image to be processed. Index from data_exif
    :param img_end: Last image to be processed. Index from data_exif. Set to negative to process all data in data_exif
    :param idx_continue: Index to continue exporting data. The fcn will start at this idx, use in case an Exception
    raises to start from the last run iteration and not have to export already processed images
    :param output_folder: Folder where images will be stored
    """
    # Port from an older matlab script
    # ---------- Sanitize inputs and initialize variables ----------
    if img_end < 0:
        img_end = len(data_exif['timestampMs'])
    idx_continue = idx_continue + img_start

    helpers.ensure_directory(output_folder)
    mapplotAnimationHelpers.sync_helper_file(img_start, img_end, data_exif['filename'], output_folder)

    time_start = time.perf_counter()
    for i in range(idx_continue, img_end):
        time_start_it = time.perf_counter()
        # ---------- Set iteration values ----------
        idx_animation = i - img_start + 1
        datetime_target = data_exif['timestampMs_localtime'][i]


        fig, ax = plt.subplots(nrows=1, ncols=1)
        fig.set_size_inches(10, 2)

        ax.text(1, 0.2, "%d/%d" % (idx_animation, img_end-img_start), color='White', fontsize=75,
                horizontalalignment='right')
        ax.set_facecolor((0, 0 ,0))


        plt.savefig(output_folder + str(idx_animation) + ".png")
        # plt.show()
        fig.clf()
        plt.close('all')

        mapplotAnimationHelpers.print_console(
            idx_animation, img_start, img_end, time_start, time_start_it, data_exif['filename'][i])
