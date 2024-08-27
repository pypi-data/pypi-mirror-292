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

    
# def extract_by_points(ee_image_collection, points_gdf, dateranges_df, copy_properties, apply_function, dtype):

#     # Store the name of the bands available in the image collection
#     band_names = ee_image_collection.bandNames().getInfo()

#     # Split the points in batches if the length of point exceeds 1000
#     ranges = []
#     batch_start = 0
#     batch_end = len(points_gdf)
#     interval = 1000
    
#     while batch_start < batch_end:
#         range_end = min(batch_start + interval, batch_end)
#         ranges.append((batch_start, range_end))
#         batch_start = range_end

#     # Create a blank dataframe to store all the yearly climate data
#     extracted_data = pd.DataFrame()

#     # Prepare images for all the dateranges
#     daterange_images = ee.List([])

#     for i, row in dateranges_df.iterrows():
#         start_date = row["start_date"].strftime("%Y-%m-%d")
#         end_date = row["end_date"].strftime("%Y-%m-%d")
#         label_prefix = row["label_prefix"]
            
#         image = ee_image_collection.filterDate(start_date, end_date)\
#                                    .mean()\
#                                    .select(band_names, [f"{band}_{label_prefix}" for band in band_names])

#         daterange_images = daterange_images.add(image)

#         # Convert the images into an image collection
#         daterange_images = ee.ImageCollection(daterange_images).toBands()

#         # Change the name of the bands
#         clim_columns = clim_dekad_imgs.bandNames().getInfo()
#         clim_new_columns = ["_".join(col.split("_")[1:]) for col in clim_columns]
#         clim_dekad_imgs = clim_dekad_imgs.select(clim_columns, clim_new_columns)

#         # Create a blank dataframe to store all the range data
#         range_data = pd.DataFrame()

#         print("Processing in Batches...")
#         for range in tqdm(ranges):

#             points_batch = country_samples.iloc[range[0]:range[1]]
#             points_batch = points_batch[copy_properties + ["geometry"]]
#             points_batch = geemap.gdf_to_ee(points_batch)
            
#             # Extract the data for the current batch
#             points_batch_data = clim_dekad_imgs.reduceRegions(
#                 collection=points_batch,
#                 reducer=ee.Reducer.first(),
#                 scale=250
#             )

#             # Convert the data into pandas dataframe
#             points_batch_data = geemap.ee_to_df(points_batch_data)
#             points_batch_data["year"] = year # Add the year information
#             points_batch_data = points_batch_data[copy_properties + ["year"] + clim_new_columns]

#             range_data = pd.concat((range_data, points_batch_data), axis=0, ignore_index=True)

#         # Add the range data to the yearly data
#         yearly_data = pd.concat((yearly_data, range_data), axis=0, ignore_index=True)

#         # Round off the decimal places
#         yearly_data[clim_new_columns] = yearly_data[clim_new_columns].round(decimal_places)

#     return yearly_data