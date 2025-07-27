import os
import json
import NXOpen
import NXOpen.Display
import time


def main():
    """
    Camera automation that loads all settings from camera_config.json.
    """
    
    the_session = NXOpen.Session.GetSession()
    work_part = the_session.Parts.Work
    display_part = the_session.Parts.Display
    
    if work_part is None:
        return
    
    # =================================================================================
    # LOAD CONFIGURATION FROM JSON
    # =================================================================================
    
    config_file = "C:\\Users\\iftdev\\Desktop\\Dhananjay Sharma\\autoscript_POC\\config2.json"
    
    if not os.path.exists(config_file):
        return
        
    try:
        with open(config_file, 'r') as jsonfile:
            config_data = json.load(jsonfile)
            camera_configs = config_data.get('camera_configurations', [])
            global_settings = config_data.get('settings', {})
            camera_specs = config_data.get('camera_specs', {})
            
            if not camera_configs:
                return
                
    except Exception as e:
        return
    
    output_directory = global_settings.get("output_directory")
    if output_directory:
        os.makedirs(output_directory, exist_ok=True)
    
    # Setup Advanced Studio
    setup_advanced_studio_centered(the_session, work_part)
    
    # =================================================================================
    # CAMERA PROCESSING
    # =================================================================================
    
    successful_renders = 0
    failed_renders = 0
    
    for i, config in enumerate(camera_configs):
        try:
            success = process_camera_with_true_raytracing(
                the_session, work_part, config, camera_specs, 
                output_directory, global_settings, i+1
            )
            
            if success:
                successful_renders += 1
            else:
                failed_renders += 1
            
        except Exception as e:
            failed_renders += 1
            continue
    
    


def setup_advanced_studio_centered(the_session, work_part):
    """Setup Advanced Studio for centered object rendering."""
    
    markId1 = the_session.SetUndoMark(NXOpen.Session.MarkVisibility.Invisible, "Setup Centered Studio")
    
    trueStudioBuilder1 = work_part.TrueStudioObjs.CreateTrueStudioBuilder(NXOpen.Display.TrueStudio.Null)
    trueStudioBuilder1.ModeToggle = True
    work_part.ModelingViews.WorkView.RenderingStyle = NXOpen.View.RenderingStyleType.Studio
    
    nXObject1 = trueStudioBuilder1.Commit()
    trueStudioBuilder1.Destroy()
    
    return True
    


def center_object_in_view(work_view, global_settings):
    """
    CENTER THE OBJECT in the view for consistent positioning.
    """
   
    centering_method = global_settings.get('centering_method', 'fit_center')
    
    if centering_method == "fit_center":
        work_view.Fit()
        
    elif centering_method == "origin":
        work_view.Fit()  
        
    else:
        work_view.Fit()
    
    
    # Apply margin factor for breathing room
    margin_factor = global_settings.get('margin_factor', 0.9)
    if margin_factor != 1.0:
        scaleAboutPoint = NXOpen.Point3d(0.0, 0.0, 0.0)
        viewCenter = NXOpen.Point3d(0.0, 0.0, 0.0)
        work_view.ZoomAboutPoint(margin_factor, scaleAboutPoint, viewCenter)
    return True
    


def apply_view_specific_adjustment(work_view, view_type, global_settings):
    """
    Apply view-specific margin adjustments after centering.
    """
    try:
        view_specific_margins = global_settings.get('view_specific_margins', {})
        
        # Check for view-specific margin
        margin = None
        if view_type in view_specific_margins:
            margin = view_specific_margins[view_type]
        elif view_type.startswith('Perspective') and 'Perspective' in view_specific_margins:
            margin = view_specific_margins['Perspective']
        
        if margin and margin != 1.0:
            scaleAboutPoint = NXOpen.Point3d(0.0, 0.0, 0.0)
            viewCenter = NXOpen.Point3d(0.0, 0.0, 0.0)
            work_view.ZoomAboutPoint(margin, scaleAboutPoint, viewCenter)
            
        return True
        
    except Exception as e:
        return False


def process_camera_with_true_raytracing(the_session, work_part, config, camera_specs, 
                                       output_directory, global_settings, camera_number):
    """
    Process camera with OBJECT CENTERING and TRUE RAY TRACING.
    """
    
    # =================================================================
    # SET VIEW ORIENTATION AND HIDE UI ELEMENTS
    # =================================================================
    
    work_view = work_part.ModelingViews.WorkView
    view_type = config.get('view_type', 'Isometric')
    
    # HIDE COORDINATE TRIAD AND WCS FOR CLEAN IMAGES
    work_view.TriadVisibility = False
    work_view.WcsVisibility = False
    
    # Set basic view orientation BEFORE centering
    if view_type == 'Top':
        work_view.Orient(NXOpen.View.Canned.Top, NXOpen.View.ScaleAdjustment.Fit)
    elif view_type == 'Front':
        work_view.Orient(NXOpen.View.Canned.Front, NXOpen.View.ScaleAdjustment.Fit)
    elif view_type == 'Right':
        work_view.Orient(NXOpen.View.Canned.Right, NXOpen.View.ScaleAdjustment.Fit)
    elif view_type == 'Back':
        work_view.Orient(NXOpen.View.Canned.Back, NXOpen.View.ScaleAdjustment.Fit)
    elif view_type == 'Left':
        work_view.Orient(NXOpen.View.Canned.Left, NXOpen.View.ScaleAdjustment.Fit)
    elif view_type == 'Bottom':
        work_view.Orient(NXOpen.View.Canned.Bottom, NXOpen.View.ScaleAdjustment.Fit)
    elif view_type == 'Trimetric':
        work_view.Orient(NXOpen.View.Canned.Trimetric, NXOpen.View.ScaleAdjustment.Fit)
    else:
        work_view.Orient(NXOpen.View.Canned.Isometric, NXOpen.View.ScaleAdjustment.Fit)
    
    # =================================================================
    # CENTER THE OBJECT
    # =================================================================
    
    if global_settings.get('center_object_first', True):
        center_object_in_view(work_view, global_settings)
    
    # =================================================================
    # APPLY VIEW-SPECIFIC ADJUSTMENTS
    # =================================================================
    
    apply_view_specific_adjustment(work_view, view_type, global_settings)
    
    # =================================================================
    # FINAL ZOOM ADJUSTMENT
    # =================================================================
    
    zoom_after_center = global_settings.get('zoom_after_center', 1.1)
    if zoom_after_center != 1.0:
        scaleAboutPoint = NXOpen.Point3d(0.0, 0.0, 0.0)
        viewCenter = NXOpen.Point3d(0.0, 0.0, 0.0)
        work_view.ZoomAboutPoint(zoom_after_center, scaleAboutPoint, viewCenter)
    
    # =================================================================
    # RAY TRACING + STUDIO EXPORT
    # =================================================================
    
    # Enter task environment for studio operations
    the_session.BeginTaskEnvironment()
    
    # Create ray traced studio builder for ray tracing
    rayTracedStudioBuilder = work_part.Views.CreateRayTracedStudioBuilder()
    rayTracedStudioBuilder.StopRayTracedDisplay()
    
    rayTracedStudioBuilder.RayTracedRenderingStart()
    rayTracedStudioBuilder.StopRayTracedDisplay()
    rayTracedStudioBuilder.RayTracedRenderingSave()
    
    # =================================================================
    # STUDIO IMAGE CAPTURE
    # =================================================================
    
    # Create studio image capture builder
    studioImageCaptureBuilder = work_part.Views.CreateStudioImageCaptureBuilder()
    studioImageCaptureBuilder.DrawingSizeEnum = NXOpen.Display.StudioImageCaptureBuilder.DrawingSizeEnumType.Custom
    studioImageCaptureBuilder.DpiEnum = NXOpen.Display.StudioImageCaptureBuilder.DPIEnumType.Dpi400
    
    image_format = global_settings.get("image_format", "tif")
    output_filename = os.path.join(output_directory, f"{config['camera_name']}.{image_format}")
    studioImageCaptureBuilder.NativeFileBrowser = output_filename
    
    image_width = global_settings.get("image_width", camera_specs.get("pixel_width", 2048))
    image_height = global_settings.get("image_height", camera_specs.get("pixel_height", 2448))
    
    imagedimensionsdouble = [None] * 2
    imagedimensionsdouble[0] = float(image_width)
    imagedimensionsdouble[1] = float(image_height)
    studioImageCaptureBuilder.SetImageDimensionsDouble(imagedimensionsdouble)
    
    imagedimensionsinteger = [None] * 2
    imagedimensionsinteger[0] = image_width
    imagedimensionsinteger[1] = image_height
    studioImageCaptureBuilder.SetImageDimensionsInteger(imagedimensionsinteger)
    
    nXObject_export = studioImageCaptureBuilder.Commit()
    studioImageCaptureBuilder.Destroy()
    
    # =================================================================
    # CLEANUP
    # =================================================================
    
    rayTracedStudioBuilder.StopRayTracedDisplay()
    rayTracedStudioBuilder.Destroy()
    the_session.EndTaskEnvironment()
        


if __name__ == '__main__':
    main()