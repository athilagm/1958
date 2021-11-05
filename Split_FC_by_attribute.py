import arcpy
from arcpy.sa import *

linhas = r'C:\Users\athil\Desktop\as\Alternativas_Leilao0022021.shp'
env = arcpy.env.workspace = r'C:\Users\athil\Desktop\as'

##target_workspace = 'c:/data/output.gdb'
fields = ['NAME']

arcpy.SplitByAttributes_analysis(linhas, env, fields)
