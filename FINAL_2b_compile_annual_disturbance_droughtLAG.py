# data in O:\Sierra-wide GPS Tagging Project\Anu\Helping\Elizabeth\Elizabeth_final_data_prep
# Anu Kramer
# 7-30-2024

# PURPOSE: add drought lag
#               see FINAL1 comments for breakdown of codes

# SPEED: 18 min (~1 min per year x 22 years = ) 624-642
# 
#
# TYPE THE FOLLOWING INTO CMD:
#       start c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat FINAL_2b_compile_annual_disturbance_droughtLAG.py

import arcpy  
from arcpy import env  
from arcpy.sa import *
import sys
import os
import functions

#################################################
############ ADJUST THE VALUES BELOW ############
#################################################
base_folder = functions.base_folder_master
coordinate_system = functions.coordinate_system_master
step4_folder = functions.step4_master # NEW
step5_folder = functions.step5_master
FINAL_2_folder = functions.FINAL_2_master
FINAL_1_folder = functions.FINAL_1_master
FINAL_3_folder = functions.FINAL_3_master
MMI_min_year = functions.MMI_min_year_master
#disturb_path = base_folder+"ANALYSIS/"+FINAL_1_folder+"/"+str_year+"/disturbance_"+str_year+".tif"
###############################################################
############ EVERYTHING BELOW SHOULD BE GOOD TO GO ############
###############################################################
# if the folder doesn't exist, make it
single_rasters = base_folder+"ANALYSIS/"+FINAL_2_folder+"/"
drought_single_rasters = base_folder+"ANALYSIS/"+FINAL_2_folder+"/drought_single_year/"
final_disturbance = base_folder+"ANALYSIS/"+FINAL_3_folder+"/"
os.makedirs(final_disturbance, exist_ok=True) # NEW

for year in range(2002,2023):
    str_year=str(year)
    print(str_year)
    disturb_raster = base_folder+"ANALYSIS/"+FINAL_1_folder+"/Disturbance/disturbance_"+str_year+".tif"
    
    drought_rasters = drought_single_rasters+"Drought_"+str_year+".tif"
    for drought_lag in (1,2,3): # NEW
        if (year-drought_lag) >= MMI_min_year:
            # make list of drought rasters
            drought_rasters = drought_rasters+";"+drought_single_rasters+"Drought_"+str(year-drought_lag)+".tif"
    # mosaic max of all drought rasters and disturb_raster 
    arcpy.management.MosaicToNewRaster(
        input_rasters=disturb_raster+";"+drought_rasters,
        output_location=drought_single_rasters,
        raster_dataset_name_with_extension="disturbance_"+str_year+"_droughtLag3.tif",
        coordinate_system_for_the_raster=coordinate_system, pixel_type="16_BIT_UNSIGNED", cellsize=None, number_of_bands=1, mosaic_method="MAXIMUM", mosaic_colormap_mode="FIRST")
    # split disturb raster into single rasters
    out_raster = arcpy.sa.Reclassify(
        in_raster=drought_single_rasters+"disturbance_"+str_year+"_droughtLag3.tif",
        reclass_field="Value", remap="0 0 0; 1 1 1; 2 10000 0",
        missing_values="DATA")
    out_raster.save(drought_single_rasters+"drought_"+str_year+"_droughtLag3.tif")
    
    # NO DISTURBANCE - 0
    out_raster = arcpy.sa.Reclassify(
        in_raster=drought_single_rasters+"disturbance_"+str_year+"_droughtLag3.tif",
        reclass_field="Value", remap="0 0 1; 1 10000 0",
        missing_values="DATA")
    out_raster.save(drought_single_rasters+"NoDisturbance_"+str_year+"_droughtLag3.tif")

    ### incorporate back full MMI range for drought ###
    MMI_rast = base_folder+"ANALYSIS/"+step5_folder+"/"+str_year+"/MMI_"+str(year)+"_0s_nofireUSFS_gt10.tif"
    drought_path = drought_single_rasters+"drought_"+str_year+"_droughtLag3.tif"
    droughtx100 = Times(drought_path,100)+MMI_rast
    droughtx100.save(single_rasters+"drought_"+str_year+"_droughtLag3_fullMMI.tif")
    # mosaic max of all drought rasters and disturb_raster 
    arcpy.management.MosaicToNewRaster(
        input_rasters=drought_single_rasters+"disturbance_"+str_year+"_droughtLag3.tif;"+single_rasters+"drought_"+str_year+"_droughtLag3_fullMMI.tif",
        output_location=final_disturbance,
        raster_dataset_name_with_extension="disturbance_"+str_year+".tif",
        coordinate_system_for_the_raster=coordinate_system, pixel_type="16_BIT_UNSIGNED", cellsize=None, number_of_bands=1, mosaic_method="MAXIMUM", mosaic_colormap_mode="FIRST")
    
    # clip to unbuffered study area
    print("clipping to unbuffered study area")
    disturbance_final = Times(final_disturbance+"disturbance_"+str_year+".tif",final_disturbance+"study_area_rast_nobuff.tif")
    disturbance_final.save(drought_single_rasters+"disturbance_"+str_year+"_nobuff.tif") # NEW
    # clip to USFS only # NEW
    print("clipping to USFS only")
    usfs_path = base_folder+"ANALYSIS/"+step4_folder+"/usfs_final_OsNull.tif"
    disturbance_final2 = Times(usfs_path,drought_single_rasters+"disturbance_"+str_year+"_nobuff.tif")
    disturbance_final2.save(final_disturbance+"disturbance_"+str_year+"_nobuff.tif")
    
print("DONE!")

