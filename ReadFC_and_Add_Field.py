import os
import arcpy
from arcpy.sa import *

env = arcpy.env.workspace = r'C:\Users\athil\Desktop\as'

# identificar e printar feature class de linhas no env workspace folder
## -- adiciona um campo distancia

featureclasses = arcpy.ListFeatureClasses()
for fc in featureclasses:
    print(featureclasses)
    arcpy.AddField_management(fc,'distancia','DOUBLE')
 
    

