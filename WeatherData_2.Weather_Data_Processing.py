
# -------------------------------------------------------------- #
# 2.Weather_Data_Processing.py                                   #
# Created on: 2013-04-06 9:33:01.00000                           #
# Author: Ting Zhao                                              #
# Description: write the original txt data into point shapefiles #
# Usage:  NARR_Weather_Data                                      #
# -------------------------------------------------------------- #

#Import os, arcpy module
import os, arcpy

# -------------------------------------------------------------------------------------------------------
# PARAMETERS NEED TO BE SPECIFIED BY USERS
# -------------------------------------------------------------------------------------------------------

# *** the user needs to define the workspace (folder) where the txt files are stored ***
arcpy.env.workspace = arcpy.GetParameterAsText(0)

# *** specify the year(s) of the txt files that need to be processed (1979 - 2012) ***
fileYears = arcpy.GetParameterAsText(1)

# *** specify the month(s) of the txt files that need to be processed (01 - 12) ***
fileMonths = arcpy.GetParameterAsText(2)

# *** specify the parameter(s) that need to be processed (tmp2m, snod, snowc, apcp) ***
fileTypes = arcpy.GetParameterAsText(3)

# *** specify the folder that the newly created point shapefiles will be saved ***
# *** Put all the point template files generated from 1.Generating_Point_Templates.py in this folder ***
outputPath = arcpy.GetParameterAsText(4)
# -------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------
# DEFINE THE PREPROCESSING FUNCTION
# -------------------------------------------------------------------------------------------------------

class NARRData(object):

        # -----------------------------------------------------------------------------------------------
        # DEFINE THE CONSTRUCTOR
        # -----------------------------------------------------------------------------------------------
        def __init__(self,txtFolder, outputFolder):
                self.txtFolder = txtFolder
                self.outputFolder = outputFolder
                self.Point_names = []
                self.fileType = []
                self.LatNum = 0
                self.LonNum = 0
                
        # -----------------------------------------------------------------------------------------------
        # DEFINE THE CREATE POINT FILES FUNCTION
        # -----------------------------------------------------------------------------------------------
        def CreatePointFiles(self, fileYears, fileMonths, fileTypes):

                try:
                        #Pass parameters into the DataProcessing function
                        fileYearsSplit = fileYears.split(";")
                        fileMonthsSplit = fileMonths.split(";")
                        fileTypesSplit = fileTypes.split(";")
                        self.fileTypes = fileTypesSplit
                        
                        #Predifine the day numbers for each month
                        bigMonth = ['01','03','05','07','08','10','12']
                        smaMonth = ['04','06','09','11']
                        Days = ["{0:02d}".format(num) for num in range(1,32)]

                        #Define prefix and suffixes of template names
                        prefix = "PointTemplate_"
                        Suffixes = ['_Feb.shp','_FebLeap.shp','_Big.shp','_Sma.shp']

                        #Iterate types of data (tmp2m, snowc, snod, apcp)
                        for fileType in fileTypesSplit:
                                #Iterate years of data (1979 - 2012)
                                for fileYear in fileYearsSplit:
                                        #Iterate months of data (01 - 12)
                                        for fileMonth in fileMonthsSplit:
                                                #Create a point file for each month, which stores all the daily data 
                                                Point_name = fileYear + fileMonth + "_narr_" + fileType + "_points.shp"
                                                self.Point_names += Point_name.split()
                                                
                                                #Judge if the file name has already been created
                                                if not arcpy.Exists(self.outputFolder+"\\"+Point_name):
                                                        
                                                        #If Feburary is selected, whether the year is leap year or not needs to examined
                                                        if fileMonth == "02":
                                                                # if the year is leap year, use the point template designed for Feburary of leap year
                                                                if (int(fileYear)%4 == 0 and (int(fileYear)%100 != 0 or int(fileYear)%400 == 0)):
                                                                        PointTemplate = outputPath + "\\" + prefix + fileType + Suffixes[1]
                                                                        arcpy.CreateFeatureclass_management(outputPath, Point_name, "POINT", PointTemplate)
                                                                # if the year is not leap year, use the point template for Feburary of regular year
                                                                else:
                                                                        PointTemplate = outputPath + "\\"+ prefix + fileType + Suffixes[0]
                                                                        arcpy.CreateFeatureclass_management(outputPath, Point_name, "POINT", PointTemplate)

                                                        #If 31-day month is selected:
                                                        elif fileMonth in bigMonth:
                                                                PointTemplate = outputPath + "\\"+ prefix + fileType + Suffixes[2]
                                                                arcpy.CreateFeatureclass_management(outputPath, Point_name, "POINT", PointTemplate)
                                                                
                                                        #If 30-day month is selected:
                                                        elif fileMonth in smaMonth:
                                                                PointTemplate = outputPath + "\\"+ prefix + fileType + Suffixes[3]
                                                                arcpy.CreateFeatureclass_management(outputPath, Point_name, "POINT", PointTemplate)
                                                else:
                                                        arcpy.AddMessage(Point_name + " has already been created!")
                                                        continue

                except arcpy.ExecuteError:
                        msg = arcpy.GetMessages()
                        arcpy.AddError(msg)
                except:
                        arcpy.AddError("Error occured!")
                        
        # -----------------------------------------------------------------------------------------------
        # DEFINE THE ADD LON LAT FUNCTION
        # -----------------------------------------------------------------------------------------------  
        #Assign the longitude and latitude values to the attribute table of each point file
        def AddLonLat(self,Point_name):

                try: 
                        #Randomly select a file, since all data share the same lat and lon values
                        dataFile = self.txtFolder + "\\" + "19790102_narr_tmp2m.txt"

                        #Define the full path of the newly created point shapefiles
                        inputTable = self.outputFolder + "\\" + Point_name
                        
                        #Find and iterate lon and lat values to create records/rows in point shapefile
                        LatLon = open (dataFile)

                        #Obtain the number of lines in the dataFile
                        lineNum = len(LatLon.readlines())
                        LatLon.seek(0)

                        #Locate the line number of latitude and store values in lineSplitLat
                        for lineLat in LatLon.readlines()[lineNum-3:lineNum-2]:
                                lineSplitLat = lineLat.split(",")
                        LatLon.seek(0)

                        #Locate the line number of longitude and store values in lineSplitLon
                        for lineLon in LatLon.readlines()[lineNum-1:]:
                                lineSplitLon = lineLon.split(",")

                        #Obtain the number of lon and lat values
                        self.LatNum = len(lineSplitLat)
                        self.LonNum = len(lineSplitLon)

                        #Create an insert cursor and store lon and lat values within
                        rows = arcpy.InsertCursor(inputTable)
                        for lat in range(2,self.LatNum):
                                for lon in range(2,self.LonNum):
                                        inPoint = arcpy.Point(lineSplitLon[lon],lineSplitLat[lat])
                                        row = rows.newRow()
                                        row.SHAPE = inPoint
                                        row.Lon = lineSplitLon[lon]
                                        row.Lat = lineSplitLat[lat]
                                        rows.insertRow(row)
                        del row
                        del rows
                        LatLon.close()

                except arcpy.ExecuteError:
                        msg = arcpy.GetMessages()
                        arcpy.AddError(msg)
                except:
                        arcpy.AddError("Error occured when read data from txt files!")
                        
        # -----------------------------------------------------------------------------------------------
        # DEFINE THE DATA PROCESSING FUNCTION
        # -----------------------------------------------------------------------------------------------

        #Read daily data from the original txt files and write them into the point files 
        def DataProcessing(self, Point_name, fileName):
                
                try:
                        #Set path, name and file type for the point shapefile
                        dataFile = self.txtFolder + "\\" + fileName
                        inputTable = self.outputFolder + "\\" + Point_name
                        self.fileType = Point_name.split("_")[2]
                        
                        #Assign the eight measured values within a day to the corresponding fields of point files
                        Data = open (dataFile)

                        #Create eight lists storing eight measured values within a day respectively
                        line0, line1, line2, line3, line4, line5, line6, line7 = [],[],[],[],[],[],[],[]
                        for lineData in Data:
                                if not lineData.find('[0][') == -1:
                                        lineSplit0 = lineData.split(",")
                                        line0 += lineSplit0[2:self.LonNum]
                                elif not lineData.find('[1][') == -1:
                                        lineSplit1 = lineData.split(",")
                                        line1 += lineSplit1[2:self.LonNum]
                                elif not lineData.find('[2][') == -1:
                                        lineSplit2 = lineData.split(",")
                                        line2 += lineSplit2[2:self.LonNum]
                                elif not lineData.find('[3][') == -1:
                                        lineSplit3 = lineData.split(",")
                                        line3 += lineSplit3[2:self.LonNum]
                                elif not lineData.find('[4][') == -1:
                                        lineSplit4 = lineData.split(",")
                                        line4 += lineSplit4[2:self.LonNum]
                                elif not lineData.find('[5][') == -1:
                                        lineSplit5 = lineData.split(",")
                                        line5 += lineSplit5[2:self.LonNum]
                                elif not lineData.find('[6][') == -1:
                                        lineSplit6 = lineData.split(",")
                                        line6 += lineSplit6[2:self.LonNum]
                                elif not lineData.find('[7][') == -1:
                                        lineSplit7 = lineData.split(",")
                                        line7 += lineSplit7[2:self.LonNum]
                                        
                        #Create a update cursor, calculate and store the averaged values into the corresponding fields      
                        rows = arcpy.UpdateCursor(inputTable)
                        row = rows.next()
                        d2 = 0
                        while d2 < (self.LonNum - 2) * (self.LatNum - 2):
                                fieldName = self.fileType + fileName[6:8]
                                meanValue = ((float(line0[d2]) + float(line1[d2]) + float(line2[d2]) + float(line3[d2]) + float(line4[d2]) + float(line5[d2]) + float(line6[d2]) + float(line7[d2])) / 8) - 273.15 
                                row.setValue(fieldName, meanValue)               
                                rows.updateRow(row)
                                rows.next()
                                d2 += 1
                                
                        del row, rows
                        del line0, line1, line2, line3, line4, line5, line6, line7
                        Data.close()
                        
                except arcpy.ExecuteError:
                        msg = arcpy.GetMessages()
                        arcpy.AddError(msg)
                except:
                        arcpy.AddError("Error occured when temporarily storing the data of txt files!")                

# -----------------------------------------------------------------------------------------------
# DEFINE THE MAIN BODY OF THE CODE
# -----------------------------------------------------------------------------------------------
if __name__ == "__main__":
        
        try:
                #Create an instance
                NarrData = NARRData(arcpy.env.workspace,outputPath)
                #Call the CreatePointFiles function to create point shapefiles
                NarrData.CreatePointFiles(fileYears, fileMonths, fileTypes)
                
                for Point_name in NarrData.Point_names:
                        #Call the AddLonLat function to add lon and lat values in the point shapefiles
                        NarrData.AddLonLat(Point_name)
                        
                        #Find all the txt files corresponding to the point shapefiles
                        os.chdir(arcpy.env.workspace)
                        for txtfileName in os.listdir("."):
                                if not fileName.find(Point_name[0:5]) == -1:
                                        if not fileName.find(NarrData.fileType) == -1:
                                                #Call the DataProcessing function to transfer values to the point shapefiles
                                                NarrData.DataProcessing(Point_name, fileName)
        except:
                arcpy.AddError("Something is wrong when segmenting names of txt files!")
