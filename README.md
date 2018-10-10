# tools_box
The script contains the following tools:

A. tool.py

1.create image list
create image list according to the image folder and files.

2.show image label
show object's label and boxes accordign to darknet-txt or json file(not support, will be added).

3.parse json file
read json file according to image label, and parse json file to darknet txt training files.

4.delete redundant pictures or label files

5.delete little object's label


B. final_txt.py

1.generate training dataset
this script shift the center x and y of the label boxes and padding the boxes w and h randomly to generate more ROI object-images first and then crop these ROI images from original label images.
