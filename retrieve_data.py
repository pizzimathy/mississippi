
from census import Census
from us import states
from numpy import int64
import pandas as pd
import geopandas as gpd
import json

# Initialize the census api with the incredibly long api key.
cen = Census("599374066b9d48c54cbb2aa7738a4823f015a3bc")

# Get data for Mississippi tracts.
tracts = cen.acs5.state_county_tract("B02001_003E,B01003_001E,GEO_ID", states.MS.fips, Census.ALL, Census.ALL)

# Remove the weird prefix on geoids.
for tract in tracts:
    tract["GEO_ID"] = tract["GEO_ID"][9:]

# Convert to dataframe.
tracts = pd.DataFrame(tracts)

# Reset some column names.
tracts["GEOID"] = tracts["GEO_ID"]
tracts["BPOP"] = tracts["B02001_003E"]
tracts["POP10"] = tracts["B01003_001E"]

# Remove the old columns – we don't need them.
del tracts["GEO_ID"]
del tracts["B02001_003E"]
del tracts["B01003_001E"]

# Change the GEOID column to strings.
tracts["GEOID"] = tracts["GEOID"].apply(str)

# Load in tract shapefile and merge on the geoid column.
shp = gpd.read_file("./data/tl_2016_28_tract/tl_2016_28_tract.shp")
shp["GEOID"] = shp["GEOID"].apply(str)
shp = shp.merge(tracts, on="GEOID")
shp.to_file("./data/tl_2016_28_tract_merged/tl_2016_28_tract_merged.shp")
