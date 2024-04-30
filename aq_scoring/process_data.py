import os, datetime
import toml
import psrcelmerpy
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from util import load_h5

config = toml.load("configuration.toml")
start_time = datetime.datetime.now()

# Load OFM parcel population from Elmer
e_conn = psrcelmerpy.ElmerConn()
ofm_df = e_conn.get_query("select parcel_id, household_pop from ofm.parcelized_saep("+ \
                                str(config['ofm_vintage'])+", "+str(config['ofm_estimate_year'])+")")

# Load Parcel GeoDataFrame form ElmerGeo
eg_conn = psrcelmerpy.ElmerGeoConn()
parcel_gdf = eg_conn.read_geolayer('parcels_urbansim_2018_pts')
# Convert to WA State Plane Coordinate Reference System
parcel_gdf = parcel_gdf.to_crs(config["WA_STATE_PLANE_CRS"])

# Merge OFM data to geodata
parcel_gdf = parcel_gdf.merge(ofm_df, on='parcel_id', how='left')

# Load project shapefile
project_gdf = gpd.read_file(config['project_dir'])
project_gdf.crs = config["WA_STATE_PLANE_CRS"]

# Buffer  shapefile geometry
project_gdf.geometry = project_gdf.buffer(int(config['buffer_distance']))

# Intersect buffered area with parcel geodataframe
gdf = gpd.sjoin(project_gdf, parcel_gdf)

# Aggregate intersection to get population totals for each project
result_df = gdf[['projID','App_ID','household_pop']].groupby(['projID','App_ID']).sum()[['household_pop']].reset_index()
# OFM Estimates are not integers because they are calculated from higher-level geographies
# Round up total for each project to nearest integer
result_df['household_pop'] = np.ceil(result_df['household_pop']).astype(int)
# Rename for clarity
result_df.rename(columns={
    'household_pop': f'population_in_{config['buffer_distance']}_ft_buffer'},
    inplace=True
    )

if not os.path.exists(config['output_dir']):
    os.makedirs(config['output_dir'])
result_df.to_csv(os.path.join(config['output_dir'],'project_population.csv'))

end_time = datetime.datetime.now()
elapsed_total = end_time - start_time
print(f"Total processing time: {elapsed_total}.")