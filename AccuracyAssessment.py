#----------------------------------------------------------------------------------------------------------
# Name:        AccuracyAssessment_python.py
# Author:      Ting Zhao
# Created on:  April 23, 2014
# Description: This code produces accuracy assessment matrix and calculates user's accuracy, producer's
#              accuracy, overall accuracy and kappa.
#              1. Input:  classified image, testing image and user-specified code for classes
#              2. Output: reclassified testing image, matrix image and csv file
#----------------------------------------------------------------------------------------------------------#

import os
import csv
import arcpy
from arcpy.sa import *

#----------------------------------------------------------------------------------------------------------
# Specify input parameters

# Classified image (raster)
classifiedImage = arcpy.GetParameterAsText(0)
# Validation image (raster)
validationImage = arcpy.GetParameterAsText(1)
# Reclassify code
reclCode = arcpy.GetParameterAsText(2)
# Output destination for reclassified image of validation file
outputRec = arcpy.GetParameterAsText(3)
# Output destination for matrix image (classified image * reclassified testing image)
outputMat = arcpy.GetParameterAsText(4)
# Output CSV file destination
outputCSV = arcpy.GetParameterAsText(5)

#----------------------------------------------------------------------------------------------------------
# Define AccuracyAssessment class

class AccuracyAssessment:

    # Define __init__() to initialize all the input parameters
    def __init__(self, clImage, valImage, reclCode, outRec, outMat, outCSV):
        self.clImage = clImage
        self.valImage = valImage
        self.oldCode = self.readCode()
        self.reclCode = reclCode
        self.outRec = outRec
        self.outMat = outMat
        self.outCSV = outCSV
        

    # Define readCode() to read values from classified image
    def readCode(self):
        codeList = []
        rows = arcpy.SearchCursor(self.clImage)
        for row in rows:
            codeList.append(str(row.Value))
        del row
        del rows
        return codeList

    # Define reclValidation() to reclassify validation image base on the new code
    def reclValidation(self):
        oldCode = map(int, self.oldCode)
        newCode = map(int, self.reclCode.split(","))
        recList = []
        if len(oldCode) == len(newCode):
            for i in range(len(oldCode)):
                recList.append([oldCode[i], newCode[i]])
            arcpy.AddMessage("Reclassification Code has been created!")
        else:
            arcpy.AddError("Input code: " + reclCode + " doesn't have same number of codes as classification image.")
            return
        outRecl = Reclassify(self.valImage, "Value", RemapValue(recList))
        outRecl.save(self.outRec)
        arcpy.AddMessage("Reclassification of testing image has completed!")

    # Define timesImage() to calculate matrix image
    def timesImage(self):
        if arcpy.Exists(self.outRec):
            outResult = Times(self.clImage, self.outRec)
            zeroVal = False
            rows = arcpy.SearchCursor(outResult)
            for row in rows:
                if row.Value == 0:
                    zeroVal = True
            del rows, row
            if zeroVal == True:
                outResultNew = Reclassify(outResult, "Value", RemapValue([[0, "NODATA"]]))
            else:
                outResultNew = outResult
            outResultNew.save(self.outMat)
            arcpy.AddMessage("Accuracy assessment image has been calculated!")
        else:
            arcpy.AddError(outRec + " doesn't exist!")
            return

    # Define writeCSV() to write accuracy assessment matrix
    def writeCSV(self):
        oldCode = self.oldCode
        newCode = self.reclCode.split(",")
        newLines = []
        # store count numbers of different values in a nested list
        # countList = [[],[],[],[],......]
        countList = self.createCountList()
        # First line
        firstLine = ["class_" + i for i in newCode]
        firstLine.insert(0, '')
        firstLine.append("User's Accuracy")
        newLines.append(firstLine)
        # The following three parameters will be used for overall accuracy and kappa calculation
        diagonalTotal = 0
        allTotal = 0
        rowColTotal = 0
        # Middle lines / last line
        midLine = []
        lastLine = ["producer's Accuracy"]
        codeLen1 = 0
        while codeLen1 < len(oldCode):
            midLine.append("class_" + str(oldCode[codeLen1]))
            for codeLen2 in range(len(oldCode)):
                midLine.append(countList[codeLen2][codeLen1])
            midLine.append(countList[codeLen1][codeLen1] / sum(midLine[1:]))
            lastLine.append(countList[codeLen1][codeLen1] / sum(countList[codeLen1]))
            newLines.append(midLine)
            diagonalTotal += countList[codeLen1][codeLen1]
            allTotal += sum(countList[codeLen1])
            rowColTotal += sum(midLine[1:]) * sum(countList[codeLen1])
            codeLen1 += 1
            midLine = [] 
        # last line
        newLines.append(lastLine)
        # Overall Accuracy line
        OALine = ["Overall Accuracy"]
        OALine.append(diagonalTotal / allTotal)
        newLines.append(OALine)
        # Kappa line
        kappaLine = ["Kappa"]
        kappaLine.append((allTotal * diagonalTotal - rowColTotal) / (allTotal * allTotal - rowColTotal))
        newLines.append(kappaLine)
        # Write matrix to csv file
        with open(self.outCSV, 'w+') as csvFile:
            lineWriter = csv.writer(csvFile, delimiter = ',', lineterminator = '\n')
            lineWriter.writerows(newLines)

    # Define createCountList() to find count number for a certain value
    def createCountList(self):
        oldCode = map(int, self.oldCode)
        newCode = map(int, self.reclCode.split(","))
        count1 = 0
        count2 = 0
        countList = []
        subList = []
        rows = arcpy.SearchCursor(self.outMat)
        for row in rows:
            if count1 < len(oldCode):
                if row.Value == oldCode[count1] * newCode[count2]:
                    subList.append(row.Count)
                    count1 += 1
                else:
                    subList.append(0)
                    count1 += 1
            else:
                count1 = 0
                count2 += 1
                countList.append(subList)
                subList = []
                if row.Value == oldCode[count1] * newCode[count2]:
                    subList.append(row.Count)
                    count1 += 1
                else:
                    subList.append(0)
                    count1 += 1
        countList.append(subList)
        del row
        del rows
        return countList

#----------------------------------------------------------------------------------------------------------
# Run the code
AA = AccuracyAssessment(classifiedImage, validationImage, reclCode, outputRec, outputMat, outputCSV)
arcpy.AddMessage("Start reclassifying testing image...")
AA.reclValidation()
arcpy.AddMessage("Start performing times operator...")
AA.timesImage()
arcpy.AddMessage("Start creating accuracy assessment matrix...")
AA.writeCSV()
