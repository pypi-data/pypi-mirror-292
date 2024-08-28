"A module to extract large volume datasets for machine learning from Google Earth Engine."

import numpy as np
import pandas as pd
import ee
import geemap
from datetime import datetime, timedelta
from tqdm import tqdm


def generate_date_ranges(start_date_str, end_date_str, interval_days, label_prefix=None):
    """
    Generates a DataFrame containing date ranges between a start and end date with a specified interval.

    Args:
        start_date_str (str): The start date as a string in the format 'YYYY-MM-DD'.
        end_date_str (str): The end date as a string in the format 'YYYY-MM-DD'.
        interval_days (int): The number of days between the start and end of each interval.
        label_prefix (str, optional): A prefix to be used in labeling each date range. Defaults to None.

    Returns:
        pd.DataFrame: A DataFrame with columns 'start_date', 'end_date', and 'label' where each row represents a date range.

    Raises:
        ValueError: If 'start_date_str' or 'end_date_str' is not in the 'YYYY-MM-DD' format.
        ValueError: If 'interval_days' is not a positive integer.
    """

    # Validate input formats
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError("start_date_str and end_date_str must be in the format 'YYYY-MM-DD'.")
    
    # Validate that end_date is greater than start_date
    if end_date <= start_date:
        raise ValueError("end_date_str must be greater than start_date_str.")

    if not isinstance(interval_days, int) or interval_days <= 0:
        raise ValueError("interval_days must be a positive integer.")
    
    start_dates = []
    end_dates = []

    while start_date <= end_date:
        start_dates.append(start_date)
        interval_end_date = start_date + timedelta(days=interval_days)
        end_dates.append(interval_end_date)
        start_date = interval_end_date

    # Create DataFrame with the date ranges and labels
    date_ranges_df = pd.DataFrame({
        "start_date": start_dates, 
        "end_date": end_dates
    })

    # Generate labels if label_prefix is provided
    if label_prefix is not None:
        date_ranges_df["label"] = [f"{label_prefix}_{i + 1}" for i in range(date_ranges_df.shape[0])]
    
    return date_ranges_df


def extract_pixel_values_by_points(image_collection, points_gdf, date_ranges_df, scale=250, 
                                   copy_properties=["point_id"], reducer="mean", dtype=None,
                                   constant_value=0):
    """
    Extracts pixel values from an Earth Engine image collection for specified points over defined date ranges
    using a specified statistical reducer (e.g., mean, median, sum).

    Args:
        image_collection (ee.ImageCollection): The Earth Engine image collection from which to extract data.
        points_gdf (geopandas.GeoDataFrame): A GeoDataFrame containing the points with associated properties.
        date_ranges_df (pd.DataFrame): A DataFrame with columns 'start_date', 'end_date', and 'label_prefix' defining date ranges.
        scale (int, optional): The spatial resolution in meters at which to extract data. Defaults to 250.
        copy_properties (list of str, optional): List of properties from the points_gdf to retain in the output. Defaults to ["point_id"].
        reducer (str, optional): The statistical reducer to apply to the image collection. Options include "mean", "median", "min", "max", "sum", "stdDev", "variance". Defaults to "mean".
        dtype (str or np.dtype, optional): Data type to which the extracted values should be cast. Defaults to None.
        constant_value (int or float, optional): The value to use for constant bands if no bands are present in the image. Defaults to 0.
        
    Returns:
        pd.DataFrame: A DataFrame containing the extracted pixel values, with one row per point per date range.
        
    Raises:
        ValueError: If 'date_ranges_df' does not contain 'start_date' or 'end_date'.
        ValueError: If 'reducer' is not a valid Earth Engine reducer.
        ValueError: If 'dtype' is not a valid data type.
    """

    # Validate date_ranges_df input
    if 'start_date' not in date_ranges_df.columns or 'end_date' not in date_ranges_df.columns:
        raise ValueError("date_ranges_df must contain 'start_date' and 'end_date' columns.")
    
    # Map reducer strings to corresponding Earth Engine reducer functions
    reducers = {
        "mean": ee.Reducer.mean(),
        "median": ee.Reducer.median(),
        "min": ee.Reducer.min(),
        "max": ee.Reducer.max(),
        "sum": ee.Reducer.sum(),
        "stdDev": ee.Reducer.stdDev(),
        "variance": ee.Reducer.variance()
    }
    
    if reducer not in reducers:
        raise ValueError(f"Invalid reducer '{reducer}'. Valid options are {list(reducers.keys())}.")

    # Store the band names from the image collection
    band_names = image_collection.first().bandNames().getInfo()

    # Split the points into batches if the number of points exceeds 1000
    batch_ranges = []
    total_points = len(points_gdf)
    batch_interval = 1000
    
    for start in range(0, total_points, batch_interval):
        end = min(start + batch_interval, total_points)
        batch_ranges.append((start, end))

    # Prepare images for all date ranges using the specified reducer
    daterange_images = ee.List([])

    for _, row in date_ranges_df.iterrows():
        start_date = row["start_date"].strftime("%Y-%m-%d")
        end_date = row["end_date"].strftime("%Y-%m-%d")
        label = row.get("label", None)

        image = image_collection.filterDate(start_date, end_date).reduce(reducers[reducer])

        # If the image has no bands, add constant bands for each expected band
        if image.bandNames().size().getInfo() == 0:
            constant_image = ee.Image.constant(constant_value).rename(band_names)
            image = constant_image

        if label:
            image = image.select([f"{band}_{reducer}" for band in band_names], [f"{band}_{label}" for band in band_names])

        daterange_images = daterange_images.add(image)

    # Convert the list of images into an ImageCollection and then to bands
    daterange_images = ee.ImageCollection(daterange_images).toBands()

    # Get and adjust band names
    daterange_band_names = daterange_images.bandNames().getInfo()
    if label:
        adjusted_band_names = ["_".join(name.split("_")[1:]) for name in daterange_band_names]
        daterange_images = daterange_images.select(daterange_band_names, adjusted_band_names)
    
    # Initialize an empty DataFrame to store the extracted data
    extracted_data = pd.DataFrame()

    print("Processing in batches...")
    for batch_start, batch_end in tqdm(batch_ranges):
        points_batch = points_gdf.iloc[batch_start:batch_end]
        points_batch = points_batch[copy_properties + ["geometry"]]
        points_batch_ee = geemap.gdf_to_ee(points_batch)
            
        # Extract data for the current batch
        batch_data = daterange_images.reduceRegions(
            collection=points_batch_ee,
            reducer=ee.Reducer.first(),
            scale=scale
        )
        
        # Convert the Earth Engine result to a DataFrame
        batch_df = geemap.ee_to_df(batch_data)
        
        if dtype:
            try:
                batch_df[adjusted_band_names] = batch_df[adjusted_band_names].astype(dtype)
                batch_df = batch_df[copy_properties + adjusted_band_names]
            except ValueError:
                raise ValueError("Provided dtype is not a valid data type.")
        
        # Concatenate the batch data to the final DataFrame
        extracted_data = pd.concat([extracted_data, batch_df], axis=0, ignore_index=True)

    return extracted_data

