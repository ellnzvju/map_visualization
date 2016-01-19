
# coding: utf-8
# version: 0.01
# used normalization 20,40,60,80 to define each categories

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colorz
from matplotlib.colors import Normalize
from matplotlib.collections import PatchCollection
from mpl_toolkits.basemap import Basemap
from shapely.geometry import Point, Polygon, MultiPoint, MultiPolygon
from shapely.prepared import prep
from descartes import PolygonPatch
from itertools import chain
from pysal.esda.mapclassify import Natural_Breaks as nb
import fiona
import datetime
import random

# figure 1
_code_version = '0.01'
fig = plt.figure()
# read province income data
income_data = pd.read_csv('income_data_thailand_2013.csv',header=0)

# read provinces shape information.
shapefile = '/Users/Critical/Documents/ML/visualization/THA_adm1/THA_adm1'
shp = fiona.open(shapefile + '.shp')
coords = shp.bounds
shp.close()

# create map by latitude and longitude from shape file.
# Actually we can fill any value here because we just want to use readshapefile() and ditch every things from base map out.
m = Basemap(
    projection='tmerc',
    lon_0=np.mean([coords[0],coords[2]]), #center of longitude
    lat_0=np.mean([coords[1],coords[3]]), #center of latitude
    llcrnrlon=coords[0] ,
    llcrnrlat=coords[1] ,
    urcrnrlon=coords[2] ,
    urcrnrlat=coords[3] ,
    resolution='i',
    suppress_ticks=True)

# read shape file but dont draw the map
m.readshapefile(shapefile,name='thailand',color='none',zorder=2)

# incase if we want to show ocean, other coast lines, etc
# but we actually dont need it, since we have all polygons from shape file,
# So we will render all provinces from shape file information
# m.drawmapboundary(fill_color='#111111')
# m.fillcontinents(color='#D1F5FF',lake_color='#78E3FD')
# m.drawcoastlines()

#prepare shape file into polygon
df_map = pd.DataFrame({
    'polygon': [Polygon(xy) for xy in m.thailand],
    'province': [province['NAME_1'] for province in m.thailand_info]})

# create income base on provices (last year only 2013 (y10))
df_map['income'] = df_map['province'].map(lambda x: income_data.loc[ income_data['Area']== x ].y10)

#plot map
plt.clf()   # clear previous map render (from basemap)
ax = fig.add_subplot(111,axisbg='w', frame_on=False)
ax.set_axis_bgcolor('white')

# normalize data into colour range (cmap) and add it to collections
cmap = plt.get_cmap('Oranges')
df_map['patches'] = df_map['polygon'].map(lambda x: PolygonPatch(x, ec='#ffffff', lw=.2, alpha=1., zorder=4))
pc = PatchCollection(df_map['patches'], match_original=True)
norm = Normalize()
#normalized data
normalized_income = norm(df_map['income'].values)
pc.set_facecolor(cmap(normalized_income))
ax.add_collection(pc)

#calculate range (0-20) (20 -40) (40 - 60) (60 - 80) (80 - 100)
pct100 = income_data['y10'].max() # 100 percentile
pct = []
for a in [0, 20, 40, 60, 80]:
    pct.append(np.round(np.percentile(normalized_income,a) * pct100))
labels = [" %0.2f - %0.2f" % ( a , b ) for a , b in zip(pct,pct[1::])]
labels.append(" %0.2f or more" % pct[-1])
colors_range = len(labels)
# create colorbar by discretizing cmap we got from normalized
# 5 levels color bar
colors_i = np.concatenate((np.linspace(0, 1., colors_range), (0., 0., 0., 0.)))
colors_rgba = cmap(colors_i)
indices = np.linspace(0, 1., colors_range + 1)
cdict = {}
for ki, key in enumerate(('red', 'green', 'blue')):
    cdict[key] = [(indices[i], colors_rgba[i - 1, ki], colors_rgba[i, ki]) for i in xrange(colors_range + 1)]
cmap = colorz.LinearSegmentedColormap(cmap.name + "_%d" % colors_range, cdict, 1024)

mappable = cm.ScalarMappable(cmap=cmap)
mappable.set_array([])
mappable.set_clim(-0.5, colors_range + 0.5)
colorbar = plt.colorbar(mappable, shrink=0.5)
colorbar.set_ticks(np.linspace(0,colors_range,colors_range))
colorbar.set_ticklabels(labels)

#copyright
copyright = ax.text(1.03, 0, 'Created by Rittha A. \nN28P02-income Database from www.data.go.th\n Thailand Provinces shapes file from www.arcgis.com by THA_adm1',
ha='right', va='bottom', size=6, color='#444444',transform=ax.transAxes)
# Draw a map scale
m.drawmapscale(
    coords[0]  , coords[1] ,
    coords[0], coords[1],
    6.,
    barstyle='fancy', labelstyle='simple',
    fillcolor1='w', fillcolor2='w',
    fontcolor='#222222',
    zorder=5)

#Set center
plt.tight_layout()
# Save png if need
plt.savefig('thailand_income_map_2013_' + _code_version + '.png', dpi=300, alpha=True)

plt.show()
