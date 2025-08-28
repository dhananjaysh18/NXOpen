## This script is saving images with Blue circle may be that is origin marker(which i do not want).
## The saved images are not correct positions the i way i want, as the front view is ok but the object is in 90° vertical.
## I do not know how to set logic here to get camera parameters input like sensor size, working distance of real camera (that i change in the json file) 

## Setting brightness, scale or output image, dimensions 2472x2064, or background color from json file 
# changable lighting in TrueStudio if available, 
## In the end i need high quality.
## this script is using config.json 

import os
import json
import math
import NXOpen
import NXOpen.Display
import time


def main():
    the_session = NXOpen.Session.GetSession()
    work_part = the_session.Parts.Work
    
    config_file = "C:\\Users\\iftdev\\Desktop\\Dhananjay Sharma\\autoscript_POC\\config.json"
    
    with open(config_file, 'r') as jsonfile:
        config_data = json.load(jsonfile)
        camera_configs = config_data.get('camera_configurations', [])
        global_settings = config_data.get('settings', {})
        camera_specs = config_data.get('real_camera_specs', {})
    
    output_directory = global_settings.get("output_directory")
    os.makedirs(output_directory, exist_ok=True)
    
    setup_true_studio_rendering(the_session, work_part)
    
    for i, config in enumerate(camera_configs):
        process_camera(the_session, work_part, config, camera_specs, output_directory, global_settings)


def setup_true_studio_rendering(the_session, work_part):
    """Setup TrueStudio rendering for non-interactive sessions"""
    markId1 = the_session.SetUndoMark(NXOpen.Session.MarkVisibility.Invisible, "Setup TrueStudio")
    
    # Create TrueStudioBuilder (works in non-interactive mode)
    trueStudioBuilder = work_part.TrueStudioObjs.CreateTrueStudioBuilder(NXOpen.Display.TrueStudio.Null)
    
    # Enable TrueStudio mode
    trueStudioBuilder.ModeToggle = True
    
    # Set render method (for better quality)
    # Available options: Interactive, Production, Balanced
    trueStudioBuilder.RenderMethodType = NXOpen.Display.TrueStudioBuilder.RenderMethod.FullRender #I want use best image output render method
    
    # Set global material type (default material when none applied to objects)

    trueStudioBuilder.GlobalMaterialType = NXOpen.Display.TrueStudioBuilder.GlobalMaterial.ShinyMetalColorwash # I want also change this later according to requirements

    # Apply the TrueStudio settings
    nXObject = trueStudioBuilder.Commit()
    trueStudioBuilder.Destroy()
    
    # Set the view rendering style to Studio (this works with TrueStudio)
    work_part.ModelingViews.WorkView.RenderingStyle = NXOpen.View.RenderingStyleType.Studio
    
    
def create_camera_matrix(camera_pos, target_pos):
    """
    Create camera matrix for NX coordinate system
    NX uses: +X = Right, +Y = Up, +Z = Toward viewer
    """
    # Calculate view direction (from camera to target)
    view_dir = [
        target_pos[0] - camera_pos[0],
        target_pos[1] - camera_pos[1],
        target_pos[2] - camera_pos[2]
    ]
    
    # Normalize view direction
    view_length = math.sqrt(view_dir[0]**2 + view_dir[1]**2 + view_dir[2]**2)
    view_dir = [view_dir[0]/view_length, view_dir[1]/view_length, view_dir[2]/view_length] if view_length > 0 else [0, 0, -1]
    
    # Determine up vector based on view direction
    # For views primarily along Y axis (top/bottom), use Z as up
    # For all other views, use Y as up
    if abs(view_dir[1]) > 0.9:  # Looking along Y axis (top/bottom views)
        up_vector = [0, 0, 1]  # Z up
    else:  # All other views
        up_vector = [1, 0, 0]  # x up
    
    # Calculate right vector (cross product of view_dir and up)
    right_vector = [
        view_dir[1] * up_vector[2] - view_dir[2] * up_vector[1],
        view_dir[2] * up_vector[0] - view_dir[0] * up_vector[2],
        view_dir[0] * up_vector[1] - view_dir[1] * up_vector[0]
    ]
    
    # Normalize right vector
    right_length = math.sqrt(right_vector[0]**2 + right_vector[1]**2 + right_vector[2]**2)
    right_vector = [right_vector[0]/right_length, right_vector[1]/right_length, right_vector[2]/right_length] if right_length > 0 else [1, 0, 0]
    
    # Recalculate up vector (cross product of right and view_dir)
    up_vector = [
        right_vector[1] * view_dir[2] - right_vector[2] * view_dir[1],
        right_vector[2] * view_dir[0] - right_vector[0] * view_dir[2],
        right_vector[0] * view_dir[1] - right_vector[1] * view_dir[0]
    ]
    
    # Create the camera matrix
    camera_matrix = NXOpen.Matrix3x3()
    camera_matrix.Xx = right_vector[0]; camera_matrix.Xy = up_vector[0]; camera_matrix.Xz = -view_dir[0]
    camera_matrix.Yx = right_vector[1]; camera_matrix.Yy = up_vector[1]; camera_matrix.Yz = -view_dir[1]
    camera_matrix.Zx = right_vector[2]; camera_matrix.Zy = up_vector[2]; camera_matrix.Zz = -view_dir[2]
    
    return camera_matrix


def process_camera(the_session, work_part, config, camera_specs, output_directory, global_settings):
    work_view = work_part.ModelingViews.WorkView
    
    # Hide all display elements to remove origin marker and coordinate system
    work_view.TriadVisibility = False
    work_view.WcsVisibility = False
    
    work_view.ChangePerspective(True)
    
    # Get camera parameters from config - NO TRANSFORMATION
    camera_pos = [config.get('pos_x', 0.0), config.get('pos_y', 0.0), config.get('pos_z', 0.0)]
    target_pos = [config.get('target_x', 0.0), config.get('target_y', 0.0), config.get('target_z', 0.0)]
    
    # Create and apply camera matrix
    camera_matrix = create_camera_matrix(camera_pos, target_pos)
    work_view.Orient(camera_matrix)
    work_view.Fit()
    
    # Apply margin factor
    margin_factor = global_settings.get('margin_factor', 0.8)
    work_view.ZoomAboutPoint(margin_factor, NXOpen.Point3d(0.0, 0.0, 0.0), NXOpen.Point3d(0.0, 0.0, 0.0))
    
    work_view.UpdateDisplay()
    time.sleep(0.5)
    
    save_image(the_session, work_part, config, camera_specs, output_directory, global_settings)


def save_image(the_session, work_part, config, camera_specs, output_directory, global_settings):
    camera_name = config.get('camera_name', 'unknown')
    image_format = global_settings.get('image_format', 'png')
    output_filename = os.path.join(output_directory, f"{camera_name}.{image_format}")
    
    the_session.BeginTaskEnvironment()
    
    studioImageCaptureBuilder = work_part.Views.CreateStudioImageCaptureBuilder()
    studioImageCaptureBuilder.NativeFileBrowser = output_filename
    studioImageCaptureBuilder.DrawingSizeEnum = NXOpen.Display.StudioImageCaptureBuilder.DrawingSizeEnumType.Custom
    
    # Set higher DPI for better quality
    studioImageCaptureBuilder.DpiEnum = NXOpen.Display.StudioImageCaptureBuilder.DPIEnumType.Dpi400
    
    # Get dimensions from camera specs
    width = camera_specs.get('output_width_pixels', 2472)
    height = camera_specs.get('output_height_pixels', 2064)
    
    # Set custom dimensions (Note: NX expects [height, width] format)
    studioImageCaptureBuilder.SetImageDimensionsInteger([height, width])
    
    
    studioImageCaptureBuilder.BackgroundColor = NXOpen.Display.Color.White
    
    nXObject_export = studioImageCaptureBuilder.Commit()
    studioImageCaptureBuilder.Destroy()
    the_session.EndTaskEnvironment()
    
    print(f"Image saved: {output_filename}")


if __name__ == '__main__':
    main()