import os
import cv2
import argparse
import numpy as np
from pathlib import Path
from orchard_bouman.orchard_bouman import OrchardBouman
from unsupervised import kmeans, exp_max, ob_exp_max, create_binary_mask, create_grabcut_mask
from sam import sam_segment

def main(image_path: str, method: str, k: int | None = None, channel: int = 0, output_dir: str | None = None, save_image: bool = False, show_image: bool = False):
    """Command Line Interface for image foreground segmentation.

    Args:
        image_path (str): Path to original image.
        method (str): Method to segment images by, options include "sam", "kmeans", "ob", "em", "ob-em".
        k (int | None, optional): How many clusters to generate. For method "ob" or "ob-em" clusters is 2^k. Defaults to None.
        channel (int, optional): Color channel to use when running mode counts on images. Should not have any effect. Defaults to 0.
        output_dir (str | None, optional): Folder to save images to. If None, created images are saved in the folder of the original image. Defaults to None.
        save_image (bool, optional): Whether or not to save the segmented image. Defaults to False.
        show_image (bool, optional): Whether or not to display the segmented image. Defaults to False.

    Raises:
        ValueError: Check if k is an integer greater than 0.
        ValueError: No valid method defined for method. Options include "sam", "kmeans", "ob", "em", "ob-em".

    Returns:
        np.ndarray: Segmented image
        np.ndarray | None: Resulting masks from SAM if method was "sam", else None
    """

    if method != "sam":
        masks = None

        image = cv2.imread(Path(image_path)).astype(np.uint8)

        if k < 1:
            raise ValueError("k must be greater than 1.")


        if method == "ob":
            ob = OrchardBouman(image=image, k=k)
            clustered_image = ob.construct_image()
            nodes = ob.nodes
            centers = [node.Q[0, channel] for node in nodes]

        elif method == "kmeans":
            clustered_image, centers = kmeans(image=image, k=k)

        elif method == "em":
            clustered_image, centers = exp_max(image=image, k=k)

        elif method == "ob-em":
            clustered_image, centers = ob_exp_max(image=image, k=k, channel=channel)
            
        else:
            raise ValueError(f"Incorrect or missing value for method argument.")

        binary_mask = create_binary_mask(clustered_image=clustered_image, centers=centers, channel=channel)

        segmented_image = create_grabcut_mask(image=image, binary_mask=binary_mask)
    
    else:
        segmented_image, masks = sam_segment(image_path=image_path)

    if save_image:
        if output_dir is None:
            output_dir = os.path.dirname(Path(image_path))
        output_filename = method + "_" + os.path.basename(Path(image_path))
        save_file = os.path.join(output_dir, output_filename)
        cv2.imwrite(filename=save_file, img=segmented_image)

    if show_image:
        cv2.imshow("Segmented", segmented_image)
        print("press any button to close image window")
        cv2.waitKey()


    return segmented_image, masks


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-image_path', type=str, help="Input the path to the image to perform clustering on.")
    parser.add_argument('-method', type=str)
    parser.add_argument('-k', type=int | None, default=None)
    parser.add_argument('-channel', type=int, default=0)
    parser.add_argument('-output_dir', type=str | None, default=None)
    parser.add_argument('-save_image', type=bool, default=False)
    parser.add_argument('-show_image', type=bool, default=False)

    args = parser.parse_args()

    main(args.image_path, args.method, args.k, args.channel, args.output_dir, args.save_image, args.show_image)
