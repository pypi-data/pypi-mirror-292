from ultralytics import SAM
import numpy as np
from scipy import stats
import cv2

def sam_segment(image_path: str, bboxes: list[int] = None):
    sam = SAM(model="sam2_b.pt")
    results = sam.predict(image_path, bboxes=bboxes)

    r = results[0]
    masks = r.masks.data.numpy()

    mask = masks[0, :, :]
    binary = mask.astype(np.uint8)

    outside_mode = stats.mode(
        np.concatenate([binary[0, :], binary[:, 0], binary[-1, :],
                        binary[:, -1]]))
    
    if outside_mode[0] == 0:
        segmented_image = cv2.bitwise_and(r.orig_img, r.orig_img, mask=binary)
    else:
        inverted_binary = 1 - binary
        segmented_image = cv2.bitwise_and(r.orig_img, r.orig_img, mask=inverted_binary)
        
    return segmented_image, masks
