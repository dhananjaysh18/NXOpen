import json
import NXOpen
import NXOpen.Display
import NXOpen.Gateway

# Enum mappings embedded in main file
CAMERA_PROPERTY_MAP = {
    "type": "Type",
    "lens_angle_type": "LensAngleType",
    "fov_angle": "FieldOfViewAngle",
    "fov_measured": "FieldOfViewMeasured",
    "aspect_ratio_type": "AspectRatioType",
    "aspect_ratio_width": "AspectRatioWidth",
    "aspect_ratio_height": "AspectRatioHeight",
    "aperture": "ApertureType",
    "depth_of_field": "DepthOfFieldToggle",
    "use_target_point": "UseTargetPoint"
}

def get_enum_value(enum_type, string_value):
    """Convert string to NXOpen enum value"""
    enum_mappings = {
        "CameraType": NXOpen.Display.CameraBuilder.Types,
        "LensAngleType": NXOpen.Display.CameraBuilder.LensAngle,
        "FovMeasured": NXOpen.Display.CameraBuilder.FovMeasured,
        "AspectRatioType": NXOpen.Display.CameraBuilder.AspectRatio,
        "ApertureType": NXOpen.Display.CameraBuilder.Aperture
    }
    
    # Determine enum class from property
    if enum_type in ["Type", "CameraType"]:
        return getattr(NXOpen.Display.CameraBuilder.Types, string_value)
    elif enum_type == "LensAngleType":
        return getattr(NXOpen.Display.CameraBuilder.LensAngle, string_value)
    elif enum_type == "FovMeasured":
        return getattr(NXOpen.Display.CameraBuilder.FovMeasured, string_value)
    elif enum_type == "AspectRatioType":
        return getattr(NXOpen.Display.CameraBuilder.AspectRatio, string_value)
    elif enum_type == "ApertureType":
        return getattr(NXOpen.Display.CameraBuilder.Aperture, string_value)
    
    return string_value

def apply_camera_settings(camera_builder, defaults, position_config):
    """Apply all camera settings from configuration"""
    # Apply defaults
    for key, value in defaults.items():
        prop_name = CAMERA_PROPERTY_MAP.get(key, key)
        if hasattr(camera_builder, prop_name):
            # Convert string enums if needed
            if isinstance(value, str) and prop_name in ["Type", "LensAngleType", "FieldOfViewMeasured", "AspectRatioType", "ApertureType"]:
                value = get_enum_value(prop_name, value)
            setattr(camera_builder, prop_name, value)
    
    # Apply position and target
    pos = position_config["position"]
    camera_builder.CameraPosition = NXOpen.Point3d(pos["x"], pos["y"], pos["z"])
    
    tgt = position_config["target"]
    camera_builder.TargetPosition = NXOpen.Point3d(tgt["x"], tgt["y"], tgt["z"])
    
    camera_builder.FocalDistance = position_config["focal_distance"]
    
    # Apply custom settings
    for key, value in position_config.get("custom_settings", {}).items():
        prop_name = CAMERA_PROPERTY_MAP.get(key, key)
        if hasattr(camera_builder, prop_name):
            if isinstance(value, str) and prop_name in ["Type", "LensAngleType", "FieldOfViewMeasured", "AspectRatioType", "ApertureType"]:
                value = get_enum_value(prop_name, value)
            setattr(camera_builder, prop_name, value)

def load_config(config_path):
    """Load camera configuration from JSON file"""
    with open(config_path, 'r') as f:
        return json.load(f)
    
def capture_view(work_part, camera_config, output_path):
    """Capture image with specified camera configuration"""
    # Create image export builder
    export_builder = work_part.Views.CreateImageExportBuilder()
    
    # Apply export settings
    defaults = camera_config["image_export_defaults"]
    export_builder.FileName = output_path
    export_builder.DeviceWidth = defaults["width"]
    export_builder.DeviceHeight = defaults["height"]
    
    # Use string values from config and convert to enums
    format_enum = getattr(NXOpen.Gateway.ImageExportBuilder.FileFormats, defaults["file_format"])
    export_builder.FileFormat = format_enum
    
    bg_enum = getattr(NXOpen.Gateway.ImageExportBuilder.BackgroundOptions, defaults["background"])
    export_builder.BackgroundOption = bg_enum
    
    # Capture
    export_builder.Commit()
    export_builder.Destroy()

def main():
    # Initialize
    session = NXOpen.Session.GetSession()
    work_part = session.Parts.Work
    
    # Load configuration
    config = load_config("C:\\Users\\iftdev\\Desktop\\Dhananjay Sharma\\autoscript_POC\\camera_configration.json")
    
    # Enable Advanced Studio
    studio_builder = work_part.TrueStudios.CreateTrueStudioBuilder(None)
    studio_builder.ModeToggle = True
    studio_builder.RenderMethodType = NXOpen.Display.TrueStudioBuilder.RenderMethod.FullRender
    studio_builder.Commit()
    studio_builder.Destroy()
    
    # Process each camera position
    for cam_pos in config["camera_positions"]:
        # Create camera
        camera_builder = work_part.Cameras.CreateCameraBuilder(None)
        
        # Apply settings from config
        apply_camera_settings(camera_builder, config["camera_defaults"], cam_pos)
        
        # Commit camera
        camera = camera_builder.Commit()
        camera_builder.Destroy()
        
        # Apply to view
        work_view = work_part.Views.WorkView
        camera.ApplyToView(work_view)
        
        # Capture image
        output_file = f"output/{cam_pos['name']}.png"
        capture_view(work_part, config, output_file)
        
        print(f"Captured: {output_file}")

if __name__ == "__main__":
    main()