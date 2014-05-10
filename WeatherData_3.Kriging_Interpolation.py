
# ---------------------------------------------------------------------------
# KrigingInterpolation.py
# Created on: 2013-05-30 16:33:01.00000
# Author: Ting Zhao
# Usage: interpolate point files into raster data in ArcGIS
# Description: 
# ---------------------------------------------------------------------------

# Import os, arcpy module
import os, arcpy
from arcpy.sa import *

# -------------------------------------------------------------------------------------------------------
# PARAMETERS NEED TO BE SPECIFIED BY USERS
# -------------------------------------------------------------------------------------------------------

# *** the user needs to define the workspace (folder) where the files are stored ***
arcpy.env.workspace = arcpy.GetParameterAsText(0)

# *** specify monthly and/or daily data should be interpolated
dataPeriods = arcpy.GetParameterAsText(1)

# *** specify the year(s) of the txt files that need to be processed  ***
fileYears = arcpy.GetParameterAsText(2)

# *** specify the month(s) of the txt files that need to be processed  ***
fileMonths = arcpy.GetParameterAsText(3)

# *** specify the parameter(s) that need to be processed  ***
fileTypes = arcpy.GetParameterAsText(4)

# *** specify the folder that the newly created point shapefiles will be saved ***
# *** please put all the point template files in this folder ***
outputPath = arcpy.GetParameterAsText(5)
# -------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------
# DEFINE THE MAIN BODY OF THE CODE
# -------------------------------------------------------------------------------------------------------

#pass parameters into the DataProcessing function
fileYearsSplit = fileYears.split(";")
fileMonthsSplit = fileMonths.split(";")
fileTypesSplit = fileTypes.split(";")
dataPeriodsSplit = dataPeriods.split(";")

#Define the abbr. of the weather parameters(t for tmp2m, s for snowc and snod, a for apcp)
dataTypeAbbr = ['t','s','a']

try:
        #Iterate types of data (temperature, snowdepth, etc.)
        for fileType in fileTypesSplit:
                #Iterate years of data (1979 - 2011)
                for fileYear in fileYearsSplit:
                        #Iterate months of data (Jan - Dec)
                        for fileMonth in fileMonthsSplit:
                                #Find the name of the input point shapefiles
                                inputTable = fileYear + fileMonth + "_narr_" + fileType + "_points.shp"
                                for dataPeriod in dataPeriodsSplit:
                                        #If monthly averaged data are interpolated
                                        if dataPeriod == "Monthly":
                                                Kriging_name = fileYear + fileMonth + "_narr_" + fileType + "_kriging_0.32.tif"
                                                outputKriging = outputPath + "\\" + Kriging_name
                                                fieldName = "Month" + fileType
                                                #Interpolate the point shapefile using kriging method
                                                outKrig = Kriging(inputTable, fieldName, KrigingModelOrdinary("SPHERICAL"),0.32)
                                                outKrig.save(outputKriging)
                                        #If daily data are interpolated
                                        else:
                                                fieldList = arcpy.ListFields(inputTable)
                                                for fieldname in fieldList:
                                                        if fieldname.name[0] in dataTypeAbbr:
                                                                Kriging_name = fileYear + fileMonth + fieldname.name[-2:] + "_narr_" + fileType + "_kriging_0.32.tif"
                                                                outputKriging = outputPath + "\\" + Kriging_name
                                                                outKrig = Kriging(inputTable, fieldname.name, KrigingModelOrdinary("SPHERICAL"),0.32)
                                                                outKrig.save(outputKriging)
except arcpy.ExecuteError:
        msg = arcpy.GetMessages()
        arcpy.AddError(msg)
except:
        arcpy.AddError("Error occured when trying kriging interpolation!")  
