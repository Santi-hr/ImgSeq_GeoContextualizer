# ImgSeq_GeoContextualizer
Generates an image sequence of maps with the locations from a set of photos with GPS Exif data in order to give them context.
It can use a google location history json for better results. Usually the tracking is better than the GPS Tags.

![Comparison between exif and location history](https://raw.githubusercontent.com/Santi-hr/ImgSeq_GeoContextualizer/master/Examples/Comparison_Exif_LocationHist.png)

For best results, during your trip use some sports app (like Endomondo) to increase the rate of geolocation and achieve more resolution.

## How to use
Follow this steps:
1. Move into an empty folder all the photos you want to get context from. These photos must be ordered chronologically in order to get proper plots.
2. Open "main_script.py".
3. Configure the input variables. (Set paths to photo folder, location history, etc.)
4. Configure which plots will be generated.
5. Run "main_script.py".

The tool only genereates an image sequence. Use a video editing tool to load the sequence and render a video. I use Adobe After Effects.

If you don't have enabled google location tracking, set "use_location_history" to False and the exif GPS tags will be used to plot trayectories.

### Continue from exception
Did the script explode while working?
Just get the last processed frame number printed to console and set the "img_start_middle" to one or two frames before. Then run again the script.
Doing this avoids to generate already generated plots by not starting again from the begining.

## Examples
I created this tool to assist in creating videos [like this one](https://youtu.be/QxUa6SR3owk).

Currently the tool can generate the following img sequences:
### Centered
Centers the map around the photo GPS location. The area shown is constant.
![Example Centered](https://raw.githubusercontent.com/Santi-hr/ImgSeq_GeoContextualizer/master/Examples/Example_Centered.png)
### Region
The map area covers all photo GPS location. The area shown is constant.
![Example Region](https://github.com/Santi-hr/ImgSeq_GeoContextualizer/blob/master/Examples/Example_Region.png)
### Expanding by day
The map covers the GPS locations since the begining of the day of the current photo. The area shown expands.
This mode is not recomended as it is difficult to follow, specially when there are few photos between points.
![Example Expanding by day](https://github.com/Santi-hr/ImgSeq_GeoContextualizer/blob/master/Examples/Example_Region_Expanding_by_day.png)
### Expanding by n_last
The map covers the GPS locations for N photos. The area shown expands and contracts.
This mode is not recomended as it is difficult to follow, specially when there are few photos between points.
![Example Expanding by n](https://raw.githubusercontent.com/Santi-hr/ImgSeq_GeoContextualizer/master/Examples/Example_Region_Expanding_by_last.png)

## Requeriments
* Python3
* Matplotlib
* Smopy
* Exifread

## Terms of use
This module fetches image maps from OpenStreetMap's servers. [See the usage policy](https://operations.osmfoundation.org/policies/tiles/).
