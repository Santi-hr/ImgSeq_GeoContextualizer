import time


def print_console(idx_animation, img_start, img_end, time_start, time_start_it, filename):
    """Prints debug and status information on console. Needs outside timers for proper estimations """
    total_images = img_end - img_start
    remaining_images = total_images - idx_animation
    elapsed_time = time.perf_counter() - time_start
    elapsed_time_it = time.perf_counter() - time_start_it
    estimated_mins = (remaining_images * elapsed_time / idx_animation) / 60.0
    print("%d/%d (%s). Ellapsed time %.2fs, Iteration time %.2fs, estimated %.2fm remaining"
          % (idx_animation, total_images, filename, elapsed_time, elapsed_time_it, estimated_mins))


def sync_helper_file(img_start, img_end, filename, folder):
    """Generates a file that match image ID with filename to assist in syncing both"""
    with open(folder + "syncfile.txt", 'w') as f:
        total_images = img_end - img_start
        for i in range(total_images):
            f.write("%d/%d, %s\n" % (i+1, total_images, filename[i+img_start]))
