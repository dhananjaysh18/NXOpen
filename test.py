import NXOpen
import NXOpen.Display

def main():
    session = NXOpen.Session.GetSession()
    work_part = session.Parts.Work
    display_Part = session.Parts.Display

    work_view = work_part.Views.WorkView
    work_view.Orient(NXOpen.View.Canned.Isometric, NXOpen.View.ScaleAdjustment.Fit)
    work_view.UpdateDisplay()


    
    rayTracedStudioBuilder = work_part.Views.CreateRayTracedStudioBuilder()
    markId3 = session.SetUndoMark(NXOpen.Session.MarkVisibility.Visible, "Ray Traced Studio Dialog")
    rayTracedStudioBuilder.StationaryQuality = NXOpen.Display.RayTracedStudioBuilder.StationaryDisplayQualityType.High
    rayTracedStudioBuilder.StopRayTracedDisplay()
    
    rayTracedStudioBuilder.RayTracedRenderingStart()
    
    rayTracedStudioBuilder.StopRayTracedDisplay()
    rayTracedStudioBuilder.RayTracedRenderingSave()
    markId4 = session.SetUndoMark(NXOpen.Session.MarkVisibility.Visible, "Start")

    save_builder = work_part.Views.CreateSaveImageFileBrowserBuilder()
    save_builder.NativeImageFileBrowser = "C:\\Users\\iftdev\\Desktop\\Dhananjay Sharma\\autoscript_POC\\2D_images\\single.png"
    save_builder.FileFormat = NXOpen.Display.SaveImageFileBrowserBuilder.FileFormats.Png
    save_builder.UseTransparentBackground = False

    session.SetUndoMarkName(markId4, "Save Image Dialog")
    nXObject1 = save_builder.Commit()
    session.SetUndoMarkName(markId4, "Save Image")
    save_builder.Destroy()
    session.CleanUpFacetedFacesAndEdges()
    session.DeleteUndoMark(markId3, "Ray Traced Studio Dialog")
    rayTracedStudioBuilder.Destroy()
    

if __name__ == "__main__":
    main()







