import arcpy
import os

# specify workspace folder by user
workspace = arcpy.getParameterAsText(0)
# specify (multiple) shapefile(s) to remove attribute fields
delFieldsFiles = arcpy.getParameterAsText(1)
# specify the mask shapefile for masking out the to-be-mask input files
maskFile = arcpy.getParameterAsText(2)
# specify the to-be-mask input files
toBeMaskedFiles = arcpy.getParameterAsText(3)
# specify the buffer input files
bufferFile = arcpy.getParameterAsText(4)
# specify the point input files
pointFile = arcpy.getParameterAsText(5)

class ParamExtraction:
    
    def __init__(self, delFieldsFiles, maskFile, toBeMaskedFiles, bufferFile, pointFile):
        arcpy.env.workspace = workspace
        self.delFieldsFiles = delFieldsFiles
        self.maskFile = maskFile
        self.toBeMaskedFiles = toBeMaskedFiles
        self.toBeExtractedFiles = []
        self.bufferFile = bufferFile
        self.pointFile = pointFile

    # delete attribute field for input shapefiles
    def DeleteField (self):
        for inFile in self.delFieldsFiles: # in case there are multiple input files
            for fieldName in arcpy.ListFields(inFile): # list all the fields of the file
                if "0" in fieldName.name:
                    arcpy.DeleteField_management(inFile,fieldName.name)

    def MaskImage(self):
        arcpy.env.extent = arcpy.Describe(self.maskFile).Extent
        for inFile in self.toBeMaskedFiles:
            outExtractByMask = arcpy.sa.ExtractByMask(inFile,self.maskFile)
            newName = os.path.basename(inFile) + "_sub.tif"
            self.toBeExtractedFiles.append(newName)
            outExtractByMask.save(newName)

    def ExtractParams(self):
        for inFile in self.toBeExtractedFiles:
            for i in range(1, 20):
                inBand = inFile + r"\band_" + str(i)
                outBand = os.path.basename(inFile) + "_band_" + str(i) + ".tif"
                arcpy.CopyRaster_management(inBand, outBand)
                ZonalResult = arcpy.sa.ZonalStatistics(self.bufferFile, "FID", outBand, "MEAN", "NODATA")
                outZonalBand = os.path.basename(inFile) + "_Zonalband_" + str(i) + ".tif"
                ZonalResult.save(outZonalBand)
                arcpy.sa.ExtractMultiValuesToPoints(self.pointFile, [[outZonalBand, os.path.basename(inFile) +"band" + str(i)]], "NONE")

if __name__ == "__main__":
    
    paramExt = ParamExtraction(delFieldsFiles, maskFile, toBeMaskedFiles, bufferFile, pointFile)
    if len(delFieldsFiles) > 0:
        paramExt.DeleteField()
    paramExt.MaskImage()
    paramExt.ExtractParams()
    
    
