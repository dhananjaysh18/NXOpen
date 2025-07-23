# -*- coding: utf-8 -*-
import NXOpen
import os

import NXOpen.Gateway

def main():
    session = NXOpen.Session.GetSession()
    ui = NXOpen.UI.GetUI()
    lw = session.ListingWindow
    lw.Open()
    
    part = session.Parts.Work
    if part is None:
        lw.WriteLine("No part is open.")
        return

    display_part = session.Parts.Display
    workPart = session.Parts.Work
    base_dir = r"C:\\Users\\iftdev\\Desktop\\Dhananjay Sharma\\autoscript_POC.py\\autoscript.py\\2D_images"
    part_name = part.Name
    output_dir = os.path.join(base_dir, part_name)
    os.makedirs(output_dir, exist_ok=True)

    view = display_part.Views.WorkView
    
    views_to_export = ["Top", "Front", "Right", "Back", "Left", "Bottom", "Isometric", "Trimetric"]
    count = 0

    for view_name in views_to_export:
        try:
            view.Orient(view_name, NXOpen.View.ScaleAdjustment.Fit)
            view.Fit()
            
            builder = workPart.Views.CreateImageExportBuilder()
            builder.FileName = os.path.join(output_dir, f"{view_name}.tif")
            builder.FileFormat = NXOpen.Gateway.ImageExportBuilder.FileFormats.Tiff
            builder.DeviceWidth = 1920
            builder.DeviceHeight = 1080
            builder.SetCustomBackgroundColor([0.0,0.0,0.0])
            builder.Commit()
            builder.Destroy()

            lw.WriteLine(f"Exported: {view_name}")
            count += 1
        except Exception as e:
            lw.WriteLine(f"Could not export {view_name}: {str(e)}")

    lw.WriteLine(f"Done. Exported {count} views to: {output_dir}")

def GetUnloadOption():
    return NXOpen.Session.LibraryUnloadOption.AtTermination

def UnloadLibrary():
    pass

if __name__ == "__main__":
    main()
