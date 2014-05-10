
# ----------------------------------------------------------------------------------- #
# 1.Generating_Point_Templates.py                                                     #
# Created on:  2013-04-06 9:33:01.00000                                               #
# Author:      Ting Zhao                                                              #
# Description: create point template files for different weather parameters regarding #
#              to different month lengths                                             #
# Usage:       NARR Weather data                                                      # 
# ----------------------------------------------------------------------------------- #

#Import arcpy module
import arcpy

try:
    #Specify the folder that the template files will be stored
    arcpy.env.workspace = arcpy.GetParameterAsText(0)

    #Specify weather parameters that being processed ('tmp2m','snowc','snod','apcp')
    DataTypes = arcpy.GetParameterAsText(1)
    DataTypesSplit = DataTypes.split(";")

    #Define days within a month
    Days = ["{0:02d}".format(num) for num in range(1,32)]
    
    #Create Point Template files
    for DataType in DataTypesSplit:

        #Define the field for montly averaged value for a certain weather parameter
        MonthAvgField = "Month" + DataType
        
        #Define prefix and suffixes of data names
        prefix = "PointTemplate_"
        Suffixes = ['_Feb.shp','_FebLeap.shp','_Big.shp','_Sma.shp']

        for Suffix in Suffixes:

            #Define the full name of the templates based on data types and months
            DataName = prefix + DataType + Suffix

            #Examine whether the data has been already created
            if not arcpy.Exists(DataName):
            
                #Create empty Point shapefiles using the full name
                arcpy.CreateFeatureclass_management (arcpy.env.workspace, DataName, "POINT","", "DISABLED", "DISABLED", "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;.001;.001;IsHighPrecision", "", "0", "0", "0")

                #Add fields of Latitude, Lontitude and Monthly averaged value for a certain weather parameter
                for fieldName in ["Lat", "Lon", MonthAvgField]:
                    arcpy.AddField_management (DataName, fieldName, "FLOAT")

                # in case of regular february:
                if Suffix == Suffixes[0]:
                    for x1 in Days[:28]:
                        fieldName = DataType + x1
                        arcpy.AddField_management (DataName, fieldName, "FLOAT")
                # in case of leap february:
                elif Suffix == Suffixes[1]:
                    for x2 in Days[:29]:
                        fieldName = DataType + x2
                        arcpy.AddField_management (DataName, fieldName, "FLOAT")
                # in case of 31-day month:
                elif Suffix == Suffixes[2]:
                    for x3 in Days[:31]:
                        fieldName = DataType + x3
                        arcpy.AddField_management (DataName, fieldName, "FLOAT")
                # in case of 30-day month:
                elif Suffix == Suffixes[3]:
                    for x4 in Days[:30]:
                        fieldName = DataType + x4
                        arcpy.AddField_management (DataName, fieldName, "FLOAT")
            else:
                arcpy.AddMessage(DataName + " has already been created!")
                continue

except arcpy.ExecuteError:
    print arcpy.GetMessages()
    
