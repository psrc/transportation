import os, datetime
import toml
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from util import load_h5

config = toml.load("configuration.toml")
start_time = datetime.datetime.now()

# Load parcel data as Pandas DataFrame
parcel_df = pd.read_csv(config["parcel_file_dir"], sep=r'\s+')

# Create GeoDataFrame from parcel data using XY coordinate values (in WA State Plane coordinates)
parcel_gdf = gpd.GeoDataFrame(
    parcel_df,
    geometry=gpd.points_from_xy(
        parcel_df['xcoord_p'],
        parcel_df['ycoord_p'],
        crs=config["WA_STATE_PLANE_CRS"]
    ),
)

# Load synthetic population from Soundcast to get parcel-level population
hh_df = load_h5(config['population_file'], 'Household')
# Total population is sum of household size for all households at each parcel
df = hh_df.groupby('hhparcel').sum()[['hhsize']].reset_index()
# Merge population totals to parcels gdf and rename hhsize to represent the transformation (to population)
parcel_gdf = parcel_gdf.merge(df, left_on='parcelid', right_on='hhparcel', how='left')
parcel_gdf.rename(columns={'hhsize': 'population'}, inplace=True)

# Load the project shapefile
project_gdf = gpd.read_file(config['project_dir'])
project_gdf.crs = config["WA_STATE_PLANE_CRS"]

# Buffer the shapefile geometry
project_gdf.geometry = project_gdf.buffer(int(config['buffer_distance']))

# Intersect the buffered area with the parcel geodataframe
gdf = gpd.sjoin(project_gdf, parcel_gdf)

# Aggregate the intersection to get population totals
result_df = gdf[['Fullname','population']].groupby('Fullname').sum()['population']

if not os.path.exists(config['output_dir']):
    os.makedirs(config['output_dir'])
result_df.to_csv(os.path.join(config['output_dir'],'project_population.csv'))

end_time = datetime.datetime.now()
elapsed_total = end_time - start_time
print(f"Total processing time: {elapsed_total}.")