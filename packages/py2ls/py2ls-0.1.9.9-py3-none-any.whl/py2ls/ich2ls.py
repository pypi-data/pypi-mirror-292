import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from PIL import Image
from skimage import filters, morphology, measure, color


def img_preprocess(dir_img, subtract_background=True, size_obj=50, size_hole=50):
    """
    Processes an image by performing thresholding, morphological operations,
    and region labeling.

    Parameters:
    - dir_img: Path to the image file.
    - size_obj: Minimum size of objects to keep (default: 50).
    - size_hole: Maximum size of holes to fill (default: 50).

    Returns:
    - output: Dictionary containing the overlay image, threshold value, and regions.
    """
    props_list = [
        "area",  # Number of pixels in the region. Useful for determining the size of regions.
        "area_bbox",
        "area_convex",
        "area_filled",
        "axis_major_length",  # Lengths of the major and minor axes of the ellipse that fits the region. Useful for understanding the shape's elongation and orientation.
        "axis_minor_length",
        "bbox",  # Bounding box coordinates (min_row, min_col, max_row, max_col). Useful for spatial localization of regions.
        "centroid",  # Center of mass coordinates (centroid-0, centroid-1). Helps locate the center of each region.
        "centroid_local",
        "centroid_weighted",
        "centroid_weighted_local",
        "coords",
        "eccentricity",  # Measure of how elongated the region is. Values range from 0 (circular) to 1 (line). Useful for assessing the shape of regions.
        "equivalent_diameter_area",  # Diameter of a circle with the same area as the region. Provides a simple measure of size.
        "euler_number",
        "extent",  # Ratio of the region's area to the area of its bounding box. Indicates how much of the bounding box is filled by the region.
        "feret_diameter_max",  # Maximum diameter of the region, providing another measure of size.
        "image",
        "image_convex",
        "image_filled",
        "image_intensity",
        "inertia_tensor",  # ensor describing the distribution of mass in the region, useful for more advanced shape analysis.
        "inertia_tensor_eigvals",
        "intensity_max",  # Maximum intensity value within the region. Helps identify regions with high-intensity features.
        "intensity_mean",  # Average intensity value within the region. Useful for distinguishing between regions based on their brightness.
        "intensity_min",  # Minimum intensity value within the region. Useful for regions with varying intensity.
        "intensity_std",
        "label",  # Unique identifier for each region.
        "moments",
        "moments_central",
        "moments_hu",  # Hu moments are a set of seven invariant features that describe the shape of the region. Useful for shape recognition and classification.
        "moments_normalized",
        "moments_weighted",
        "moments_weighted_central",
        "moments_weighted_hu",
        "moments_weighted_normalized",
        "orientation",  # ngle of the major axis of the ellipse that fits the region. Useful for determining the orientation of elongated regions.
        "perimeter",  # Length of the boundary of the region. Useful for shape analysis.
        "perimeter_crofton",
        "slice",
        "solidity",  # Ratio of the area of the region to the area of its convex hull. Indicates how solid or compact a region is.
    ]
    if isinstance(dir_img, str):
        # Step 1: Load the image
        image = Image.open(dir_img)

        # Step 2: Convert the image to grayscale and normalize
        gray_image = image.convert("L")
        image_array = np.array(gray_image)
        normalized_image = image_array / 255.0
    else:
        cleaned_image = dir_img
        image_array = cleaned_image
        normalized_image = cleaned_image
        image = cleaned_image
        binary_image = cleaned_image
        thr_val = None
    if subtract_background:
        # Step 3: Apply thresholding to segment the image
        thr_val = filters.threshold_otsu(image_array)
        print(f"Threshold value is: {thr_val}")

        # Apply thresholds and generate binary images
        binary_image = image_array > thr_val

        # Step 4: Perform morphological operations to clean the image
        # Remove small objects and fill small holes
        cleaned_image_rm_min_obj = morphology.remove_small_objects(
            binary_image, min_size=size_obj
        )
        cleaned_image = morphology.remove_small_holes(
            cleaned_image_rm_min_obj, area_threshold=size_hole
        )

    # Label the regions
    label_image = measure.label(cleaned_image)

    # Optional: Overlay labels on the original image
    overlay_image = color.label2rgb(label_image, image_array)
    regions = measure.regionprops(label_image, intensity_image=image_array)
    region_props = measure.regionprops_table(
        label_image, intensity_image=image_array, properties=props_list
    )
    df_regions = pd.DataFrame(region_props)
    # Pack the results into a single output variable (dictionary)
    output = {
        "img": image,
        "img_array": image_array,
        "img_scale": normalized_image,
        "img_binary": binary_image,
        "img_clean": cleaned_image,
        "img_label": label_image,
        "img_overlay": overlay_image,
        "thr_val": thr_val,
        "regions": regions,
        "df_regions": df_regions,
    }

    return output


def cal_pearson(img1, img2):
    """Compute Pearson correlation coefficient between two images."""
    img1_flat = img1.flatten()
    img2_flat = img2.flatten()
    r, p = pearsonr(img1_flat, img2_flat)
    return r, p


def cal_manders(img1, img2):
    """Compute Manders' overlap coefficient between two binary images."""
    img1_binary = img1 > filters.threshold_otsu(img1)
    img2_binary = img2 > filters.threshold_otsu(img2)
    overlap_coef = np.sum(img1_binary & img2_binary) / np.sum(img1_binary)
    return overlap_coef
