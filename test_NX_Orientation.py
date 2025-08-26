# NX 2412 Camera Builder Script with Real Camera Parameters
# This script creates multiple camera views using real camera specifications
# and exports high resolution images based on configuration file

import json
import os
import math
import NXOpen
import NXOpen.Display
import NXOpen.Preferences
import NXOpen
import NXOpen.Gateway

class CameraBuilder:
    def __init__(self, config_file_path):
        """Initialize CameraBuilder with configuration from JSON file"""
        self.session = NXOpen.Session.GetSession()
        self.work_part = self.session.Parts.Work
        self.display_part = self.session.Parts.Display
        self.config = self.load_config(config_file_path)
        self.setup_output_directory()
        
    def load_config(self, config_file_path):
        """Load camera configuration from JSON file"""
        with open(config_file_path, 'r') as f:
            return json.load(f)
    
    def setup_output_directory(self):
        """Create output directory if it doesn't exist"""
        base_dir = self.config['output_settings']['base_directory']
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
            
    def create_camera(self, view_config):
        """Create and configure a camera with real camera parameters"""
        camera_builder = self.work_part.Cameras.CreateCameraBuilder(None)
        
        # Apply real camera sensor settings
        sensor_config = self.config['camera_settings']['sensor']
        lens_config = self.config['camera_settings']['lens']
        
        # Set focal length (converting mm to model units if needed)
        focal_length = lens_config['focal_length_mm']
        camera_builder.SetFocalLength(focal_length)
        
        # Set sensor dimensions for aspect ratio
        sensor_width = sensor_config['width_mm']
        sensor_height = sensor_config['height_mm']
        aspect_ratio = sensor_width / sensor_height
        
        # Configure camera type as perspective
        camera_builder.CameraType = NXOpen.Display.CameraBuilder.Type.Perspective
        
        # Set field of view based on sensor and focal length
        # FOV = 2 * atan(sensor_diagonal / (2 * focal_length))
        sensor_diagonal = sensor_config['diagonal_mm']
        fov_radians = 2 * math.atan(sensor_diagonal / (2 * focal_length))
        fov_degrees = math.degrees(fov_radians)
        camera_builder.LensAngleType = NXOpen.Display.CameraBuilder.LensAngle.Fov
        camera_builder.FieldOfView = fov_degrees
        
        # Set aperture (f-stop)
        aperture = lens_config['aperture_f_stop']
        camera_builder.ApertureType = NXOpen.Display.CameraBuilder.Aperture.UserDefined
        camera_builder.ApertureValue = aperture
        
        # Set aspect ratio
        camera_builder.AspectRatioType = NXOpen.Display.CameraBuilder.AspectRatio.UserDefined
        camera_builder.AspectRatioWidth = sensor_width
        camera_builder.AspectRatioHeight = sensor_height
        
        # Set camera position and orientation
        position = view_config['camera_position']
        target = view_config['target_position']
        up_vector = view_config['up_vector']
        
        camera_builder.SetCameraPosition(position)
        camera_builder.SetTargetPosition(target)
        camera_builder.SetUpVector(up_vector)
        
        # Commit camera creation
        camera = camera_builder.Commit()
        camera_builder.Destroy()
        
        return camera
    
    def setup_view_style(self):
        """Setup display style and preferences"""
        capture_settings = self.config['camera_settings']['capture']
        
        # Set display style to Studio for high quality rendering
        self.work_part.ModelingViews.WorkView.DisplayStyle = NXOpen.View.DisplayStyleType.Studio
        
        # Configure edge display
        self.work_part.ModelingViews.WorkView.VisualizationVisualPreferences.ShadedEdgeStyle = \
            NXOpen.Preferences.ViewVisualizationVisual.ShadedEdgeStyleType.NotSet
    
    def apply_standard_view(self, orientation_name):
        """Apply standard NX view orientations"""
        work_view = self.work_part.ModelingViews.WorkView
        
        # Orient method requires two parameters: view name and scale adjustment
        scale_adjustment = NXOpen.View.ScaleAdjustment.Fit
        
        if orientation_name == "Front":
            work_view.Orient(NXOpen.View.Canned.Front, scale_adjustment)
        elif orientation_name == "Top":
            work_view.Orient(NXOpen.View.Canned.Top, scale_adjustment)
        elif orientation_name == "Bottom":
            work_view.Orient(NXOpen.View.Canned.Bottom, scale_adjustment)
        elif orientation_name == "Back":
            work_view.Orient(NXOpen.View.Canned.Back, scale_adjustment)
        elif orientation_name == "Right":
            work_view.Orient(NXOpen.View.Canned.Right, scale_adjustment)
        elif orientation_name == "Left":
            work_view.Orient(NXOpen.View.Canned.Left, scale_adjustment)
        elif orientation_name == "Isometric":
            work_view.Orient(NXOpen.View.Canned.Isometric, scale_adjustment)
        
        # Apply zoom using SetScale
        if 'zoom_factor' in self.config['camera_settings']['capture']:
            zoom_scale = self.config['camera_settings']['capture']['zoom_factor']
            work_view.SetScale(zoom_scale)
        
        work_view.Regenerate()
    
    def apply_custom_view(self, view_config):
        """Apply custom camera position for non-standard views"""
        work_view = self.work_part.ModelingViews.WorkView
        
        # Create transformation matrix for custom view
        position = view_config['camera_position']
        target = view_config['target_position']
        up_vector = view_config['up_vector']
        
        # Calculate view direction
        view_direction = [
            target[0] - position[0],
            target[1] - position[1],
            target[2] - position[2]
        ]
        
        # Normalize view direction
        length = math.sqrt(sum(x**2 for x in view_direction))
        view_direction = [x/length for x in view_direction]
        
        # Calculate right vector (cross product of view direction and up vector)
        right_vector = [
            view_direction[1] * up_vector[2] - view_direction[2] * up_vector[1],
            view_direction[2] * up_vector[0] - view_direction[0] * up_vector[2],
            view_direction[0] * up_vector[1] - view_direction[1] * up_vector[0]
        ]
        
        # Normalize right vector
        right_length = math.sqrt(sum(x**2 for x in right_vector))
        right_vector = [x/right_length for x in right_vector]
        
        # Recalculate up vector (cross product of right and view direction)
        final_up = [
            right_vector[1] * view_direction[2] - right_vector[2] * view_direction[1],
            right_vector[2] * view_direction[0] - right_vector[0] * view_direction[2],
            right_vector[0] * view_direction[1] - right_vector[1] * view_direction[0]
        ]
        
        # Create rotation matrix
        matrix = NXOpen.Matrix3x3()
        matrix.Xx = right_vector[0]
        matrix.Xy = right_vector[1]
        matrix.Xz = right_vector[2]
        matrix.Yx = final_up[0]
        matrix.Yy = final_up[1]
        matrix.Yz = final_up[2]
        matrix.Zx = -view_direction[0]
        matrix.Zy = -view_direction[1]
        matrix.Zz = -view_direction[2]
        
        # Apply the orientation
        work_view.Orient(matrix)
        
        # Apply zoom using SetScale
        if 'zoom_factor' in self.config['camera_settings']['capture']:
            zoom_scale = self.config['camera_settings']['capture']['zoom_factor']
            work_view.SetScale(zoom_scale)
        
        work_view.Regenerate()
    
    def export_high_resolution_image(self, view_config):
        """Export high resolution image with real camera parameters"""
        capture_settings = self.config['camera_settings']['capture']
        output_settings = self.config['output_settings']
        
        # Create studio image capture builder
        studio_builder = self.work_part.Views.CreateStudioImageCaptureBuilder()
        
        # Set image dimensions (landscape as specified)
        dimensions = capture_settings['dimensions']
        studio_builder.DrawingSizeEnum = NXOpen.Display.StudioImageCaptureBuilder.DrawingSizeEnumType.Custom
        studio_builder.SetImageDimensionsDouble([float(dimensions['width']), float(dimensions['height'])])
        studio_builder.SetImageDimensionsInteger([dimensions['width'], dimensions['height']])
        
        # Set DPI
        studio_builder.DpiEnum = NXOpen.Display.StudioImageCaptureBuilder.DPIEnumType.Dpi400
        
        # Set background color (white)
        bg_color = capture_settings['background_color']
        studio_builder.SetCustomBackgroundColor(bg_color)
        
        # Set edge enhancement
        studio_builder.EnhanceEdges = capture_settings['enhance_edges']
        
        # Build output file path
        base_dir = output_settings['base_directory']
        file_prefix = output_settings['file_prefix']
        view_name = view_config['name']
        file_format = capture_settings['output_format']
        
        # All images go in the base directory
        file_path = os.path.join(base_dir, f"{file_prefix}_{view_name}.{file_format}")
        
        studio_builder.NativeFileBrowser = file_path
        
        # Commit to export the image
        studio_builder.Commit()
        studio_builder.Destroy()
        
        return file_path
    
    def process_all_views(self):
        """Process all views defined in configuration"""
        self.setup_view_style()
        exported_files = []
        
        for view_config in self.config['views']:
            view_name = view_config['name']
            orientation = view_config['orientation']
            
            # Apply view orientation
            if orientation in ["Front", "Top", "Bottom", "Back", "Right", "Left", "Isometric"]:
                self.apply_standard_view(orientation)
            else:
                self.apply_custom_view(view_config)
            
            # Export the image
            file_path = self.export_high_resolution_image(view_config)
            exported_files.append(file_path)
            
        # Clean up
        self.session.CleanUpFacetedFacesAndEdges()
        
        return exported_files
    
    

def main():
    """Main function to execute the camera builder"""
    # Path to configuration file
    config_file = "C:\\Users\\iftdev\\Desktop\\Dhananjay Sharma\\autoscript_POC\\camera_config.json"
    
    # Create camera builder instance
    camera_builder = CameraBuilder(config_file)
    
    # Process all views
    exported_files = camera_builder.process_all_views()
    
    

if __name__ == '__main__':
    main()