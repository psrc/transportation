import pandas as pd
import geopandas as gpd
from shapely import wkt
from pymssql import connect
import sqlalchemy
import urllib
import pyodbc
import toml
import h5py

def load_elmer_table(table_name, sql=None):
    conn_string = "DRIVER={ODBC Driver 17 for SQL Server}; SERVER=AWS-PROD-SQL\Sockeye; DATABASE=Elmer; trusted_connection=yes"
    sql_conn = pyodbc.connect(conn_string)
    params = urllib.parse.quote_plus(conn_string)
    engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

    if sql is None:
        sql = "SELECT * FROM " + table_name

    df = pd.read_sql(
        sql=sql,
        con=engine,
    )

    return df


def load_elmer_geo(table_name):
    """Load ElmerGeo feature class as geodataframe."""

    con = connect("AWS-Prod-SQL\Sockeye", database="ElmerGeo")

    cursor = con.cursor()
    feature_class_name = table_name
    geo_col_stmt = (
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME="
        + "'"
        + feature_class_name
        + "'"
        + " AND DATA_TYPE='geometry'"
    )
    geo_col = str(pd.read_sql(geo_col_stmt, con).iloc[0, 0])
    query_string = (
        "SELECT *,"
        + geo_col
        + ".STGeometryN(1).ToString()"
        + " FROM "
        + feature_class_name
    )
    df = pd.read_sql(query_string, con)

    df.rename(columns={"": "geometry"}, inplace=True)
    df["geometry"] = df["geometry"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry="geometry")

    con.close()

    return gdf

def load_h5(file_dir, table_name):
    h5_file = h5py.File(file_dir)
    df = pd.DataFrame()
    for col in h5_file[table_name].keys():
        df[col] = h5_file[table_name][col][:]

    return df