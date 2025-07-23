import NXOpen

# Enum mappings for cleaner config
ENUM_MAPPINGS = {
    "type": {
        "Perspective": NXOpen.Display.CameraBuilder.Types.Perspective,
        "Parallel": NXOpen.Display.CameraBuilder.Types.Parallel
    },
    "lens_angle_type": {
        "Stock": NXOpen.Display.CameraBuilder.LensAngle.Stock,
        "Fov": NXOpen.Display.CameraBuilder.LensAngle.Fov,
        "Magnification": NXOpen.Display.CameraBuilder.LensAngle.Magnification
    },
    "fov_measured": {
        "Horizontally": NXOpen.Display.CameraBuilder.FovMeasured.Horizontally,
        "Vertically": NXOpen.Display.CameraBuilder.FovMeasured.Vertically
    },
    "aperture": {
        "F28": NXOpen.Display.CameraBuilder.Aperture.F28,
        "F56": NXOpen.Display.CameraBuilder.Aperture.F56,
        "F8": NXOpen.Display.CameraBuilder.Aperture.F8,
        "F11": NXOpen.Display.CameraBuilder.Aperture.F11,
        "F16": NXOpen.Display.CameraBuilder.Aperture.F16,
        "F22": NXOpen.Display.CameraBuilder.Aperture.F22
    }
}

def set_camera_property(camera_builder, key, value):
    """Set camera property with proper enum conversion"""
    if key in ENUM_MAPPINGS and isinstance(value, str):
        value = ENUM_MAPPINGS[key].get(value, value)
    
    # Handle special property names
    property_map = {
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
    
    actual_property = property_map.get(key, key)
    if hasattr(camera_builder, actual_property):
        setattr(camera_builder, actual_property, value)