# FOREground segMENTation
A collection of unsupervised clustering tools for foreground segmentation of an image to isolate an object of interest.

### Requirements:
- ultralytics
- opencv-python
- orchard-bouman

Developed in Python 3.10, but anything over Python 3.7 should work

### Installation:
```
pip install forement
```

### Usage:
To use from the command line use the command:
```
python forement.py -image_path -method -k -channel -output_dir -save_image -show_image
```
Arguments:
- image_path, type=str, help=Input the path to the image to perform clustering on.
- method, type=str, help=Method to segment images by, options include "sam", "kmeans", "ob", "em", "ob-em".
- k, type=int | None, default=None, help=How many clusters to generate. For method "ob" or "ob-em" clusters is 2^k.
- channel, type=int, default=0, help=Color channel to use when running mode counts on images.
- output_dir, type=str | None, default=None, help=Folder to save images to. If None, created images are saved in the folder of the original image.
- save_image, type=bool, default=False, help=Whether or not to save the segmented image.
- show_image, type=bool, default=False, help=Whether or not to display the segmented image.

Available methods:
- kmeans: "kmeans"
- Orchard Bouman: "ob"
- Expectation Maximization: "em"
- Expectation Maximization using Orchard Bouman: "ob-em"
- SAM (Segment anything model): "sam"


In addition to the command line call, all functions can be imported to your own scripts and used as part of a larger program.