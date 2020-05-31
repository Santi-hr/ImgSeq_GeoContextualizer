import time
import math
import smopy
import matplotlib.pyplot as plt


class MapPlot:
    """Wrapper for smoopy maps to reduce tile download and provide easier plotting functions"""

    def __init__(self, maxtiles=16):
        """Increase maxtiles to allow for higher resolution mpas. (Keep in mind OSM terms of service)"""
        self.obj_map_ = None
        self.obj_plot_ax_ = None
        self.b_crop_to_area = True
        self.stats_downloaded_tiles = 0
        self.stats_map_downloaded = 0
        self.z = 16
        self.maxtiles = maxtiles

        # Other configuration
        self.expect_const_area = False

        # Current area
        self.x_min_px = 0
        self.x_max_px = 0
        self.y_min_px = 0
        self.y_max_px = 0

    def __update_map_object(self, y_min_deg, x_min_deg, y_max_deg, x_max_deg):
        """Creates new smopy object, updates statics and selected crop area"""
        self.obj_map_ = None
        self.obj_map_ = smopy.Map((y_min_deg, x_min_deg, y_max_deg, x_max_deg), z=self.z, maxtiles=self.maxtiles)

        # Update stats
        self.stats_downloaded_tiles += \
            self.obj_map_.w / self.obj_map_.tilesize * self.obj_map_.h / self.obj_map_.tilesize
        self.stats_map_downloaded += 1

        # Update crop area in px
        self.x_min_px, self.y_min_px = self.obj_map_.to_pixels(y_min_deg, x_min_deg)
        self.x_max_px, self.y_max_px = self.obj_map_.to_pixels(y_max_deg, x_max_deg)

        # Wait some time to not flood OSM servers
        time.sleep(0.5)

    def __is_new_area_smaller(self, x_min_px, x_max_px, y_min_px, y_max_px):
        """Compares input area with class current crop area. Returns True if new area is smaller"""
        b_return = False
        # If area is expected to be constant skip this check as numerical errors might result in additional map download
        if not self.expect_const_area:
            current_area = abs(self.y_max_px - self.y_min_px) * abs(self.x_max_px - self.x_min_px)
            new_area = abs(y_max_px - y_min_px) * abs(x_max_px - x_min_px)

            if new_area < current_area * 0.975:
                b_return = True
        return b_return

    def set_map(self, y_min_deg, x_min_deg, y_max_deg, x_max_deg, figsize_in=(9, 9)):
        """Updates map object with new area and creates a new plot. Downloads new tiles if necessary"""
        if not self.obj_map_:
            self.__update_map_object(y_min_deg, x_min_deg, y_max_deg, x_max_deg)
        else:
            # Check if the loaded tiles can be reused
            x_min_px, y_min_px = self.obj_map_.to_pixels(y_min_deg, x_min_deg)
            x_max_px, y_max_px = self.obj_map_.to_pixels(y_max_deg, x_max_deg)

            if x_max_px >= self.obj_map_.w or x_min_px <= 0 or y_min_px >= self.obj_map_.h or y_max_px <= 0:
                # If crop area is outside smopy map load new tiles
                self.__update_map_object(y_min_deg, x_min_deg, y_max_deg, x_max_deg)
            elif self.__is_new_area_smaller(x_min_px, x_max_px, y_min_px, y_max_px):
                # If crop area is smaller than the previous loaded area is best to try to download a higher res map
                self.__update_map_object(y_min_deg, x_min_deg, y_max_deg, x_max_deg)
            else:
                # Only update crop area if map is still valid
                self.x_min_px = x_min_px
                self.y_min_px = y_min_px
                self.x_max_px = x_max_px
                self.y_max_px = y_max_px

        # Set matplotlib with smopy map object
        self.obj_plot_ax_ = self.obj_map_.show_mpl(figsize=figsize_in)
        if self.b_crop_to_area:
            self.obj_plot_ax_.axis([self.x_min_px, self.x_max_px, self.y_min_px, self.y_max_px])


    def print_stats(self):
        """Prints the stats in the console"""
        print("Downloaded %d tiles in %d maps" % (self.stats_downloaded_tiles, self.stats_map_downloaded))

    def set_map_around_point(self, lat_deg, long_deg, margin_deg):
        """Sets map centered on a lat,lon point with a bounding box of a specified margin in degrees"""
        y_max_deg = lat_deg + margin_deg
        y_min_deg = lat_deg - margin_deg

        # Compensate margin in X due to latitude effect. A degree of longitude at higher latitudes covers less space
        margin_deg_x = margin_deg/math.cos(math.radians(lat_deg))
        x_max_deg = long_deg + margin_deg_x
        x_min_deg = long_deg - margin_deg_x

        self.set_map(y_min_deg, x_min_deg, y_max_deg, x_max_deg)


    def set_map_region_square(self, lat_min_deg, long_min_deg, lat_max_deg, long_max_deg, margin_deg):
        """Sets map around the box specified. This functions enlarges the shortest edge to square the area"""
        y_max_deg = lat_max_deg + margin_deg
        y_min_deg = lat_min_deg - margin_deg

        x_max_deg = long_max_deg + margin_deg
        x_min_deg = long_min_deg - margin_deg

        # Increase the smaller dimension so both match
        y_size = abs(lat_min_deg-lat_max_deg)
        x_size = abs(long_min_deg-long_max_deg)
        half_diff_size = abs(x_size - y_size)/2.0
        if y_size > x_size:
            x_min_deg -= half_diff_size
            x_max_deg += half_diff_size
        else:
            y_min_deg -= half_diff_size
            y_max_deg += half_diff_size

        # Leave margin for smoopy. Limiting at 90 can result in an out of range at smoppy box
        #Fixme: Not working well for large maps
        if y_max_deg >= 80:
            y_max_deg = 80
        if y_min_deg < -80:
            y_min_deg = -80

        if x_max_deg > 180:
            x_max_deg = 180
        if x_min_deg < -180:
            x_min_deg = -180

        self.set_map(y_min_deg, x_min_deg, y_max_deg, x_max_deg)

    def set_map_region_precise(self, lat_min_deg, long_min_deg, lat_max_deg, long_max_deg, margin_deg):
        """Sets map around the box specified"""
        y_max_deg = lat_max_deg + margin_deg
        y_min_deg = lat_min_deg - margin_deg

        x_max_deg = long_max_deg + margin_deg
        x_min_deg = long_min_deg - margin_deg

        self.set_map(y_min_deg, x_min_deg, y_max_deg, x_max_deg)

    def show_plot(self):
        """Shows matplotlib plot"""
        plt.show()

    def save_plot(self, filename):
        """Saves matplotlib plot. Filename is full path"""
        plt.savefig(filename)

    def clear(self):
        """Cleans plot and closes are opens figures. Prevents mem leaks"""
        plt.clf()
        plt.close('all')

    def reset(self):
        """Delete the smoopy object to force a tile redownload"""
        self.obj_map_ = None

    def draw_single_marker(self, lat_deg, long_deg, s_in=40, c_in='r', marker_in='o', zorder_in=100, edgecolors_in='k',
                           linewidth_in=1):
        """Draws a scatter marker at the specified lat,lon point"""
        x_px, y_px = self.obj_map_.to_pixels(lat_deg, long_deg)
        self.obj_plot_ax_.scatter(x_px, y_px, s=s_in, c=c_in,
                                  marker=marker_in, zorder=zorder_in, edgecolors=edgecolors_in, linewidths=linewidth_in)

    def draw_list(self, lat_deg, long_deg, lineop_in='-', c_in='r', ms_in=10, mew_in=1, lw_in=2):
        """Draw a list of lat,lon points using plot"""
        if len(lat_deg) != len(long_deg):
            raise Exception("List dimension mismatch")

        list_x_px = []
        list_y_px = []
        for i in range(len(lat_deg)):
            x, y = self.obj_map_.to_pixels(lat_deg[i], long_deg[i])
            list_x_px.append(x)
            list_y_px.append(y)

        self.obj_plot_ax_.plot(list_x_px, list_y_px, lineop_in, color=c_in, ms=ms_in, mew=mew_in, lw=lw_in)
