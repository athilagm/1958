''' Script name: SURFACE ENERGY ALGORITHMS FOR LAND (SEBAL)

# Author: Athila Montibeller

# Script designed to estimate Evapotranspiration (ET) using variables/images obtained on September 01, 2016. If another type of imagery/date used then change them as indicated below

# ------------------------------------------------------------------ FEED THIS SCRIPT WITH VARIABLES FROM FLUX TOWER #11 (Corn Field) ------------------------------------------------------------------ #
'''

'''

    The following variables must be populated in this script:
    
        Rasters:
            1) Land Surface Temperature (LST) in degrees Kelvin # OK
            2) Normalized Difference Vegetation Index (NDVI) # OK
            3) Leaf Area Index (LAI) # OK

        Constants:
'''            1) Coordinates for Anchor Pixels (cold and hot) #
'''         2) Integrated Surface Albedo (from FieldSpec) # OK
            3) Reference Evapotranspiration (ETr/ETo) from Ref-ET Software # OK
            4) DOY - Day of Year # OK
            5) Cosine of the Solar Zenith Angle # OK
            6) Surface Emissivity # OK
            7) Average LAI from Wolf's Measruements # OK

        Constants at the Weather Station:
            1) Vegetation Height (in meters) # OK
            2) Anemometer height (in meters) # OK
            3) Wind speed (m/s) # OK

'''

# Import arcpy, and arcpy.sa
import arcpy
from arcpy import env
from arcpy.sa import *
import math
from math import *
arcpy.CheckOutExtension("Spatial")

# DEFINING WORKSPACE, OUTPUT DIRECTORY, AND CALLING/CASTING INPUT RASTERS AND VECTORS # 

arcpy.env.workspace = "D:\Athila\Thesis\FieldWork\UAS_Imagery\SEBAL_Image_Processing\September01\F1\Sept01_F1.gdb" # <- change geodatabase according to the images date
outDir = r'D:\Athila\Thesis\FieldWork\UAS_Imagery\SEBAL_Image_Processing\September01\F1\Sept01_F1.gdb'

# Call for input rasters to be used in this script

LST = Raster("D:\Athila\Thesis\FieldWork\UAS_Imagery\SEBAL_Image_Processing\September01\F1\Sept01_F1.gdb\Thermal_Sept1_F1_QCC_Kelvin") # Thermal Mosaic in Degrees Kelvin
NDVI = Raster("D:\Athila\Thesis\FieldWork\UAS_Imagery\SEBAL_Image_Processing\September01\F1\Sept01_F1.gdb\NDVI_Sept01_QCC") # NDVI Mosaic
LAI = Raster("D:\Athila\Thesis\FieldWork\UAS_Imagery\SEBAL_Image_Processing\September01\F1\Sept01_F1.gdb\LAI_Sept01_QCC") # LAI Mosaic
LST_Celsius = LST - 273.15 #transform LST mosaic to from Kelvin to Celsius

# Get cold and hot values from anchor pixels - LST

lstcold = arcpy.GetCellValue_management(LST, "442576.448911 4647043.74019")
lstcold_value = float(lstcold.getOutput(0))
print 'LST at the cold pixel is ' + str(lstcold_value)

lsthot = arcpy.GetCellValue_management(LST, "442658.755505 4647141.71837")
lsthot_value = float(lsthot.getOutput(0))
print 'LST at the hot pixel is ' + str(lsthot_value)

# Part 1 - Cmopute Surface Albedo (SOYBEANS) - From FieldSpec - THIS IS A NUMBER <- VALUES ACCEPTED ARE BETWEEN 0.0 AND 1.0 

albedo = 0.24 #dimensionless
print 'The surface albedo is ' + str(albedo)

# Part 2 - Compute Incoming Shortwave Radiation (in_short) - THIS IS A NUMBER <- VALUES ACCEPTED ARE BETWEEN 200 AND 1000 W/m2

LAI_AVG = 4.31 # Average plot LAI from Wolf's Research Group
ETr = 0.32 # Reference Evapotranspiration Calculated using Ref-ET Software
z = 287 # altitude in meters
DOY = 245 # day of year
gsc = 1367 # solar constant - in watts per square meter W/m2
cos0 = 0.81  # cosine of the solar zenith angle in degrees - Calculator at https://www.esrl.noaa.gov/gmd/grad/solcalc/azel.html
dr = 1 + 0.033 * cos((DOY * (2*3.14/365))) # inverse squared relative earth-sun distance in degrees - https://www.esrl.noaa.gov/gmd/grad/neubrew/Calendar.jsp?view=DOY&year=2016&col=4
Tsw = 0.75 + 2 * pow(10, (-5)) * z # atmospheric transmissivity <- this shouldn't change in between dates
print 'The atmospheric transmissivity is '+ str(Tsw)

in_short = gsc * cos0 * dr * Tsw
print 'The incoming shortwave radiation is ' + str(in_short)

# Part 3 - Compute Outgoing Longwave Radiation (out_long) - THIS IS A RASTER < - VALUES ACCEPTED ARE BETWEEN 200 AND 700 W/m2

sfc = 0.0000000567 # Stefan-Boltzmann Constant (W/m2/K4)
Eo = 0.95 + (0.01 * (LAI_AVG)) # broadband surface emissivity 

out_long = Eo * sfc * Power(LST, 4) # Outgoing Longwave Radiation Formula, from SEBAL; page 22 
#out_long.save("out_long")
out_long_result = arcpy.GetRasterProperties_management(out_long, "MEAN")
out_long_mean = out_long_result.getOutput(0)
print 'The outgoing longwave radiation is ' + str(out_long_mean)

# Part 4 - Compute Incoming Longwave Radiation (in_long) - THIS IS A NUMBER <- VALUES FROM IN_LONG RANGE FROM 200 - 500 W/m2

neg_ln_Tsw = 0.31807 # from SEBAL formula
Ea = 0.85 * pow(neg_ln_Tsw, 0.9) # atmospheric emissivity - from SEBAL and empirical equation theorized by Bastiaanssen et al., (1998a) 
in_long = Ea * sfc * pow(lstcold_value, 4) 
print 'The incoming longwave radiation is ' + str(in_long)

# Part 5 - Compute Net Radiation (Rn) - THIS IS A RASTER <- VALUES FROM IN_LONG RANGE FROM 100 - 700 W/m2

RN = (1 - albedo) * in_short + in_long - out_long - (1 - Eo) * in_long
RN.save("Rn_Sept01_corn_F1")
rn_result = arcpy.GetRasterProperties_management("Rn_Sept01_corn_F1", "MEAN")
rn_result_mean = rn_result.getOutput(0)
print 'The mean net radiation for the corn field in the first flight at ~10:30 A.M. on September 01 is ' + str(rn_result_mean)


# ------------------------------------------------------------------ COMPUTE SOIL HEAT FLUX (G) ------------------------------------------------------------------ #

# 1st: calculate ratio G/Rn according to empirical equation developed by Bastiaanssen (2000):

g_rn = (LST_Celsius / albedo) * ((0.0038 * albedo) + 0.0074 * pow(albedo, 2)) * (1 - 0.98 * Power(NDVI, 4))
#g/rn.save("Ratio_G_RN")

# Readily calculate Soil Heat Flux (G) by multiplying the ratio g/rn by the value of Rn obtained before

G = g_rn * RN
G.save("G_Sept01_corn_F1")
g_result = arcpy.GetRasterProperties_management("G_Sept01_corn_F1", "MEAN")
g_result_mean = g_result.getOutput(0)
print 'The mean soil heat flux for the corn field in the first flight ~10:30 A.M. on September 01 is ' + str(g_result_mean)





# ------------------------------------------------------------------ INITIATE COMPUTATIONS FOR SENSIBLE HEAT FLUX (H) ------------------------------------------------------------------ #





# Import arcpy, and arcpy.sa
import arcpy
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

# Import scipy and stats package
from numpy import *
from scipy.interpolate import *
from matplotlib.pyplot import *
from scipy import stats
import numpy as np

# Calculate Roughness Length (z0m) from LAI

z0m = LAI * 0.018

# Calculate Meteorological Variables at the Weather Station

# Weather Station Parameters # FLUX 10 (SOYBEANS FIELD)

veg_height = 2.0
anemo_height = 4.0
win_speed = 3.11

zom_flux10 = 0.12 * veg_height
uStar_flux10 = (0.41 * win_speed) / Ln(anemo_height / zom_flux10)
print 'Friction Velocity at the Weather Station is ' + str(uStar_flux10)
u200m = uStar_flux10 * ((Ln(200/zom_flux10)) / 0.41)
print 'Wind speed at blending height (200m) equals ' + str(u200m)

# Call for input features to be used in this script
##anchor_pixels = (r"D:\Athila\Thesis\FieldWork\UAS_Imagery\SEBAL_Image_Processing\June_27.gdb\Anchor_Pixels\Jun27_F2")

# ------------------------------------------------------------------------------------------------------------------ #

#print 'Extracting values from anchor pixels'

# Get value from rasters to the anchor pixels using 'Get cell Value' - to be used in the dT calculation

# From the Land Surface Temperature (LST) Raster

lstcold = arcpy.GetCellValue_management(LST, "442576.448911 4647043.74019")
lstcold_value = float(lstcold.getOutput(0))
#print 'LST at the cold pixel is ' + str(lstcold_value)

lsthot = arcpy.GetCellValue_management(LST, "442658.755505 4647141.71837")
lsthot_value = float(lsthot.getOutput(0))
#print 'LST at the hot pixel is ' + str(lsthot_value)

# ----------------------------------------------------------------------------

# From the Net Radiation (RN) Raster

rncold = arcpy.GetCellValue_management(RN, "442576.448911 4647043.74019")
rncold_value = float(rncold.getOutput(0))
#print 'Net Radiation at the cold pixel is ' + str(rncold_value)

rnhot = arcpy.GetCellValue_management(RN, "442658.755505 4647141.71837")
rnhot_value = float(rnhot.getOutput(0))
#print 'Net Radiation at the hot pixel is ' + str(rnhot_value)

# ----------------------------------------------------------------------------

# From the Soil Heat Flux (G) Raster

gcold = arcpy.GetCellValue_management(G, "442576.448911 4647043.74019")
gcold_value = float(gcold.getOutput(0))
#print 'Soil Heat Flux at the cold pixel is ' + str(gcold_value)

ghot = arcpy.GetCellValue_management(G, "442658.755505 4647141.71837")
ghot_value = float(ghot.getOutput(0))
#print 'Soil Heat Flux at the hot pixel is ' + str(ghot_value)

# Pt 1 - Calculate Friction Velocity (uStaR)

uStar = (0.41 * 7.526) / Ln(200 / z0m)
#uStar.save("uStar")

# Pt 2 - Calculate Aerodynamic Resistance to Heat Transport (rAh)
rah = Ln(2.0/1.0) / (uStar * 0.41)
#rah.save("rah")

# Pt 2.1 - Extract rAh to cold and hot pixels

# Pt 2.1 - Extract rAh for cold pixel
rahcold = arcpy.GetCellValue_management(rah, "442576.448911 4647043.74019")
rahcold_value = float(rahcold.getOutput(0))
#print 'Aerodynamic Resistance to Heat Transfer at the cold pixel is ' + str(rahcold_value) 

# pt 2.2 - Extract rAh for hot pixel
rahhot = arcpy.GetCellValue_management(rah, "442658.755505 4647141.71837")
rahhot_value = float(rahhot.getOutput(0))
#print 'Aerodynamic Resistance to Heat Transfer at the hot pixel is ' + str(rahhot_value) 


# Pt 3 - Calculate H_hot and H_cold for the whole scene and obtaining its value for anchor pixels

hcold_value = 0
#print 'Sensible Heat Flux at the cold pixel is ' + str(hcold_value)

hhot_value = (rnhot_value - ghot_value)
#print 'Sensible Heat Flux at the hot pixel is ' + str(hhot_value)

# Pt 4 - Calculate dT_cold and dT_hot 

dT_cold = 0
#print 'dT_cold is ' + str(dT_cold)

dT_hot = (hhot_value * rahhot_value) / (1004 * 1.15)
#print 'dT_hot is ' + str(dT_hot)

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Pt 5 - Run Linear Regression to get coefficients slope and intercept to be used in the calculation of dT - Near Surface Temperature Difference

print 'Running linear regression from dT_cold dT_hot and T_cold and T_hot to get a and b parameters'

x = array([lstcold_value, lsthot_value])
y = array([dT_cold, dT_hot])

x = np.array([lstcold_value, lsthot_value])
y = np.array([dT_cold, dT_hot])
slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
print 'parameter a (slope) equals: ' + str(slope)
print 'parameter b (intercept) equals: ' + str(intercept)

##p1 = polyfit(x,y,1)
##
##plot(x,polyval(p1,x),'r-')
##show()

# ------------------------------------------------------------------- #




# INITIATE ITERATIVE PROCES






# Pt 6 - Calculate dT (01)

dT = (intercept + (slope * LST))
#dT.save('dT')

# Pt 7 - > Calculate 1st Interaction of Sensible Heat Flux (H)

H = (1004 * 1.15) * (dT / rah)
#H.save('H')

# Pt 8 - > Calculate the Monin-Obukhob Length
print 'Start Computations for Unstable Atmospheric Conditions'

L = (Power(-uStar, 3)) / (0.41 * (9.81/LST) * H)
#L.save('L')

# Pt 9 - Apply equations to calculate Iterative Process from MODEL 14 - Stabilizing Buoyancy Effects

# Interaction #9.1 - Corrected Friction Velocity - Below creating variables to be utilized in the process

x200m = ((1 - 16 * (200 / L) * 0.25))
x2m = (1-16 * (2 / L) * 0.25)
x01m = ((1 - 16) * (0.1 / L) * 0.25)

# if L < 0; unstable conditions

L_Meanresult = arcpy.GetRasterProperties_management(L, "Mean")
L_MEAN = L_Meanresult.getOutput(0)
if L_MEAN < 0:
    Ym_200m = 2 * Ln((1 + x200m) / 2) + Ln((1 + Power(x200m, 2)) / 2)  - ATan2(x200m) + 0.5 * 3.14
    Yh_2m = 2 * Ln(1 + Power(x_2m, 2) / 2)
    Yh_01m = 2 * Ln(1 + Power(x_01m, 2) / 2)
else:
    Ym_200m = -5 * (2/L)
    Yh_2m = -5 * (2/L)
    Yh_01m = -5 * (0.1/L)
   
uStar_corrected_01 = u200m * 0.41 / Ln(200/z0m) - Ym_200m
#uStar_corrected_01.save("uStar_01")
rah_corrected_01 = Ln(2/0.1) - (Yh_2m + Yh_01m) / (uStar_corrected_01 * 0.41)
#rah_corrected_01.save('rah_corrected_01')

# pt 10 - Extract rah corrected for hot pixel 

rahhot01 = arcpy.GetCellValue_management(rah_corrected_01, "442658.755505 4647141.71837")
rahhot01_value = float(rahhot01.getOutput(0))
#print 'The new value for Aerodynamic Resistance to Heat Transfer at the hot pixel is ' + str(rahhot01_value)

# Pt 11 - Re-Calculate dT_cold and dT_hot 

dT_hot_01 = (hhot_value * rahhot01_value) / (1004 * 1.15)
#dT_hot_01.save('dT_hot_01')
#print 'New value for dT_hot is ' + str(dT_hot_01)

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Pt 12 - Run Linear Regression to get coefficients slope and intercept to be used in the calculation of dT - Near Surface Temperature Difference
print 'Running linear regression from dT_cold dT_hot and T_cold and T_hot to get new a and b parameters'

x = array([lstcold_value, lsthot_value])
y = array([dT_cold, dT_hot_01])

x = np.array([lstcold_value, lsthot_value])
y = np.array([dT_cold, dT_hot_01])
slope1, intercept1, r_value1, p_value1, std_err1 = stats.linregress(x,y)
print 'parameter a (slope1) equals: ' + str(slope1)
print 'parameter b (intercept1) equals: ' + str(intercept1)

##p2 = polyfit(x,y,1)
##
##plot(x,polyval(p2,x),'r-')
##show()

# ------------------------------------------------------------------- #




# INITIATE SECOND ITERATIVE PROCESS






# Pt 13 - Recalculate dT

dT_01 = (intercept1 + (slope1 * LST))
#dT_01.save('dT_01')

#print 'First interaction successfully calculated'

# Pt 14 - > Calculate 1st Interaction of Sensible Heat Flux (H)

H_01 = (1004 * 1.15) * (dT_01 / rah_corrected_01)
#H_01.save("H_01")

L_01 = (Power(-uStar_corrected_01, 3)) / (0.41 * (9.81/LST) * H_01)
#L_01.save('L_01')

# Interaction #15 - Corrected Friction Velocity - Below creating variables to be utilized in the process

x200m_01 = ((1 - 16 * (200 / L_01) * 0.25))
x2m_01 = (1-16 * (2 / L_01) * 0.25)
x01m_01 = ((1 - 16) * (0.1 / L_01) * 0.25)

# if L < 0; unstable conditions

L_01_Meanresult = arcpy.GetRasterProperties_management(L_01, "Mean")
L_MEAN_01 = L_01_Meanresult.getOutput(0)
if L_MEAN_01 < 0:
    Ym_200m_01 = 2 * Ln((1 + x200m_01) / 2) + Ln((1 + Power(x200m_01, 2)) / 2)  - ATan2(x200m_01) + 0.5 * 3.14
    Yh_2m_01 = 2 * Ln(1 + Power(x_2m_01, 2) / 2)
    Yh_01m_01 = 2 * Ln(1 + Power(x_01m_01, 2) / 2)
else:
    Ym_200m_01 = -5 * (2/L_01)
    Yh_2m_01 = -5 * (2/L_01)
    Yh_01m_01 = -5 * (0.1/L_01)
   
uStar_corrected_02 = u200m * 0.41 / Ln(200/z0m) - Ym_200m_01
#uStar_corrected_02.save("uStar_02")
rah_corrected_02 = Ln(2/0.1) - (Yh_2m_01 + Yh_01m_01) / (uStar_corrected_02 * 0.41)
#rah_corrected_02.save('rah_corrected_02')
#print 'Recalculate dT and H'

# ---------------------------------------------------------------------------------------------------------- #

# pt 16 - Extract rah corrected for hot pixel #

rahhot02 = arcpy.GetCellValue_management(rah_corrected_02, "442658.755505 4647141.71837")
rahhot02_value = float(rahhot02.getOutput(0))
print 'The new value for Aerodynamic Resistance to Heat Transfer at the hot pixel is ' + str(rahhot02_value)

# --------------------------------------------------------------------------------------- #

# Pt 17 - Calculate dT_cold and dT_hot 

dT_hot_02 = (hhot_value * rahhot02_value) / (1004 * 1.15)
#print 'New value for dT_hot is ' + str(dT_hot_02)

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Pt 18 - Run Linear Regression to get coefficients slope and intercept to be used in the calculation of dT - Near Surface Temperature Difference
print 'Running linear regression from dT_cold dT_hot and T_cold and T_hot to get new a and b parameters'

x = array([lstcold_value, lsthot_value])
y = array([dT_cold, dT_hot_02])

x = np.array([lstcold_value, lsthot_value])
y = np.array([dT_cold, dT_hot_02])
slope2, intercept2, r_value2, p_value2, std_err2 = stats.linregress(x,y)
print 'parameter a (slope2) equals: ' + str(slope2)
print 'parameter b (intercept2) equals: ' + str(intercept2)

##p3 = polyfit(x,y,1)
##
##plot(x,polyval(p3,x),'r-')
##show()

# ------------------------------------------------------------------- #




# INITIATE THIRD ITERATIVE PROCESS






# Pt 19 - Recalculate dT


dT_02 = (intercept2 + (slope2 * LST))
#dT_02.save('dT_02')

print 'Second interaction successfully calculated'

# --------------------------------------------------------------------------- #

# Pt 20 - > Calculate 1st Interaction of Sensible Heat Flux (H)

H_02 = (1004 * 1.15) * (dT_02 / rah_corrected_02)
#H_02.save("H_02")

L_02 = (Power(-uStar_corrected_02, 3)) / (0.41 * (9.81/LST) * H_02)
#L.save('L_02')

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Pt 21 - Apply equations to calculate Iterative Process from MODEL 14 - Stabilizing Buoyancy Effects

# Interaction #20 - Corrected Friction Velocity - Below creating variables to be utilized in the process

x200m_02 = ((1 - 16 * (200 / L_02) * 0.25))
x2m_02 = (1-16 * (2 / L_02) * 0.25)
x01m_02 = ((1 - 16) * (0.1 / L_02) * 0.25)

# if L < 0; unstable conditions

L_02_Meanresult = arcpy.GetRasterProperties_management(L_02, "Mean")
L_MEAN_02 = L_02_Meanresult.getOutput(0)
if L_MEAN_02 < 0:
    Ym_200m_02 = 2 * Ln((1 + x200m_02) / 2) + Ln((1 + Power(x200m_02, 2)) / 2)  - ATan2(x200m_02) + 0.5 * 3.14
    Yh_2m_02 = 2 * Ln(1 + Power(x_2m_02, 2) / 2)
    Yh_01m_02 = 2 * Ln(1 + Power(x_01m_02, 2) / 2)
else:
    Ym_200m_02 = -5 * (2/L_02)
    Yh_2m_02 = -5 * (2/L_02)
    Yh_01m_02 = -5 * (0.1/L_02)
   
uStar_corrected_03 = u200m * 0.41 / Ln(200/z0m) - Ym_200m_02
#uStar_corrected_03.save("uStar_03")
rah_corrected_03 = Ln(2/0.1) - (Yh_2m_02 + Yh_01m_02) / (uStar_corrected_03 * 0.41)
#rah_corrected_03.save('rah_corrected_03')

# ---------------------------------------------------------------------------------------------------------- #

# pt 21 - Extract rah corrected for hot pixel #

rahhot03 = arcpy.GetCellValue_management(rah_corrected_03, "442658.755505 4647141.71837")
rahhot03_value = float(rahhot03.getOutput(0))
#print 'The new value for Aerodynamic Resistance to Heat Transfer at the hot pixel is ' + str(rahhot03_value)

# Pt 22 - Calculate dT_cold and dT_hot 

dT_hot_03 = (hhot_value * rahhot03_value) / (1004 * 1.15)


# Pt 23 - Run Linear Regression to get coefficients slope and intercept to be used in the calculation of dT - Near Surface Temperature Difference
print 'Running linear regression from dT_cold dT_hot and T_cold and T_hot to get new a and b parameters'

x = array([lstcold_value, lsthot_value])
y = array([dT_cold, dT_hot_03])

x = np.array([lstcold_value, lsthot_value])
y = np.array([dT_cold, dT_hot_03])
slope3, intercept3, r_value3, p_value3, std_err3 = stats.linregress(x,y)
print 'parameter a (slope3) equals: ' + str(slope3)
print 'parameter b (intercept3) equals: ' + str(intercept3)

##p4 = polyfit(x,y,1)
##
##plot(x,polyval(p4,x),'r-')
##show()

# ------------------------------------------------------------------- #




# INITIATE FORTH ITERATIVE PROCESS






# Pt 24 - Recalculate dT

dT_03 = (intercept3 + (slope3 * LST))
#dT_03.save('dT_03')

H_03 = (1004 * 1.15) * (dT_03 / rah_corrected_03)
#H_03.save("H_03")

L_03 = (Power(-uStar_corrected_03, 3)) / (0.41 * (9.81/LST) * H_03)
#L_03.save("L_03")

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Interaction #25 - Corrected Friction Velocity - Below creating variables to be utilized in the process

x200m_03 = ((1 - 16 * (200 / L_03) * 0.25))
x2m_03 = (1-16 * (2 / L_03) * 0.25)
x01m_03 = ((1 - 16) * (0.1 / L_03) * 0.25)

# if L < 0; unstable conditions

L_03_Meanresult = arcpy.GetRasterProperties_management(L_03, "Mean")
L_MEAN_03 = L_03_Meanresult.getOutput(0)
if L_MEAN_03 < 0:
    Ym_200m_03 = 2 * Ln((1 + x200m_03) / 2) + Ln((1 + Power(x200m_03, 2)) / 2)  - ATan2(x200m_03) + 0.5 * 3.14
    Yh_2m_03 = 2 * Ln(1 + Power(x_2m_03, 2) / 2)
    Yh_01m_03 = 2 * Ln(1 + Power(x_01m_03, 2) / 2)
else:
    Ym_200m_03 = -5 * (2/L_03)
    Yh_2m_03 = -5 * (2/L_03)
    Yh_01m_03 = -5 * (0.1/L_03)
   
uStar_corrected_04 = u200m * 0.41 / Ln(200/z0m) - Ym_200m_03
#uStar_corrected_04.save("uStar_04")
rah_corrected_04 = Ln(2/0.1) - (Yh_2m_03 + Yh_01m_03) / (uStar_corrected_04 * 0.41)
#rah_corrected_04.save('rah_corrected_04')

# ---------------------------------------------------------------------------------------------------------- #

# pt # 26 - Extract rah corrected for hot pixel #

rahhot04 = arcpy.GetCellValue_management(rah_corrected_04, "442658.755505 4647141.71837")
rahhot04_value = float(rahhot04.getOutput(0))
#print 'The new value for Aerodynamic Resistance to Heat Transfer at the hot pixel is ' + str(rahhot04_value)

dT_hot_04 = (hhot_value * rahhot04_value) / (1004 * 1.15)

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Pt 27 - Run Linear Regression to get coefficients slope and intercept to be used in the calculation of dT - Near Surface Temperature Difference
print 'Running linear regression from dT_cold dT_hot and T_cold and T_hot to get new a and b parameters'

x = array([lstcold_value, lsthot_value])
y = array([dT_cold, dT_hot_04])

x = np.array([lstcold_value, lsthot_value])
y = np.array([dT_cold, dT_hot_04])
slope4, intercept4, r_value4, p_value4, std_err4 = stats.linregress(x,y)
print 'parameter a (slope4) equals: ' + str(slope4)
print 'parameter b (intercept4) equals: ' + str(intercept4)

p5 = polyfit(x,y,1)

plot(x,polyval(p5,x),'r-')
show()

# ------------------------------------------------------------------- #

# Pt 28 - Calculate dT

dT_04 = (intercept4 + (slope4 * LST))
#dT_04.save('dT_04')

H_04 = (1004 * 1.15) * (dT_04 / rah_corrected_04)
H_04.save("H_Sept01_corn_F1")


# ------------------------------------------------------------------ SOLVE ENERGY BUDGET EQUATION ------------------------------------------------------------------ #


# where

LE = RN - G - H_04
LE.save("LE_Sept01_corn_F1")
print 'Latent Heat Flux Successfully Obtained'

LST_Mean = arcpy.GetRasterProperties_management(LST_Celsius, "Mean")
LST_Mean_Value = float(LST_Mean.getOutput(0))
print(LST_Mean_Value)
lv = (2.501 - 0.00236 * LST_Mean_Value) * 1000000 # Latent heat Flux of Vaporization 
ET = 3600 * (LE/lv) # Instantaneous ET
ET.save("ET_Sept01_corn_F1")
print 'Evapotranspiration Successfully Obtained'

ETrF = ET/ETr # Calculates the Reference Evapotranspiration/Crop Coefficient (Kc)
ETrF.save("ETrF_Sept01_corn_F1")
print 'Reference Evapotranspiration/Crop Coefficient (Kc) Successfully obtained'

print 'Done'







                        
                                     

                                                                                                





             
