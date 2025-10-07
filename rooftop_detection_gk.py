import cv2
import matplotlib.pyplot as plt
import numpy as np
import glob
import sys
import argparse
import os

# ===== CONFIGURATION =====
# Change this path to your desired input image
INPUT_IMAGE_PATH = "testcases/image copy 4.png"

# Change tolerance values for rooftop detection 
# Lower values = more precise detection (fewer false positives)
# Higher values = more inclusive detection (catches more rooftops but may include non-rooftops)
TOLERANCE_VALUES = [3, 2]  # Test these tolerance values (±3, ±2)

# Example configurations:
# TOLERANCE_VALUES = [5, 4, 3]  # More inclusive - for images with varied rooftop colors
# TOLERANCE_VALUES = [2, 1]     # Very precise - for images with consistent rooftop colors  
# TOLERANCE_VALUES = [4]        # Single tolerance - faster processing
# TOLERANCE_VALUES = [6, 5, 4, 3, 2]  # Comprehensive test - slower but thorough
# =========================


def detect_rooftops_targeted(image, target_colors, tolerance=12):
    """
    Targeted rooftop detection using your specific colors with fine-tuned parameters
    """
    print(f"TARGETED ROOFTOP DETECTION")
    print(f"Target colors: {target_colors}")
    print(f"Tolerance: ±{tolerance}")
    
    # Convert BGR to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Create combined mask for all target colors
    combined_mask = np.zeros(image_rgb.shape[:2], dtype=np.uint8)
    
    for i, (r, g, b) in enumerate(target_colors):
        # Create color range
        lower = np.array([max(0, r-tolerance), max(0, g-tolerance), max(0, b-tolerance)])
        upper = np.array([min(255, r+tolerance), min(255, g+tolerance), min(255, b+tolerance)])
        
        # Get mask for this color
        color_mask = cv2.inRange(image_rgb, lower, upper)
        combined_mask = cv2.bitwise_or(combined_mask, color_mask)
        
        pixels_found = np.sum(color_mask == 255)
        print(f"Color {i+1} RGB({r},{g},{b}): {pixels_found} pixels")
    
    total_detected = np.sum(combined_mask == 255)
    print(f"Total pixels detected: {total_detected}")
    
    # Morphological operations to clean up
    kernel = np.ones((4, 4), np.uint8)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)  # Remove noise
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)  # Fill gaps
    
    # Filter by contour area and shape
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create final mask with only building-like areas (more inclusive)
    final_mask = np.zeros_like(combined_mask)
    valid_areas = 0
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # More inclusive area filter for better coverage
        if 150 < area < 50000:  # Lower minimum for smaller rooftop sections
            
            # Check if shape is somewhat rectangular (buildings are rectangular)
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            
            # More relaxed aspect ratios
            if 0.1 <= aspect_ratio <= 10.0:
                
                # More relaxed solidity requirement
                hull = cv2.convexHull(contour)
                hull_area = cv2.contourArea(hull)
                solidity = area / hull_area if hull_area > 0 else 0
                
                if solidity > 0.4:  # Reduced from 0.6 to 0.4 for more inclusion
                    cv2.fillPoly(final_mask, [contour], 255)
                    valid_areas += 1
    
    final_pixels = np.sum(final_mask == 255)
    print(f"After filtering: {valid_areas} areas, {final_pixels} pixels")
    
    return final_mask


def place_solar_panels_optimal(image, rooftop_mask):
    """
    Optimally place solar panels on detected rooftops with improved coverage
    """
    result_image = image.copy()
    rows, cols = rooftop_mask.shape
    
    # Improved panel specifications for better coverage
    panel_width = 14    # Slightly smaller panels for better fit
    panel_height = 10   # Smaller height too
    gap = 1            # Minimal gap between panels
    min_coverage = 0.70  # Reduced from 85% to 70% for more placements
    
    panel_count = 0
    
    print(f"PANEL PLACEMENT")
    print(f"Panel size: {panel_width}x{panel_height}")
    print(f"Gap: {gap}px")
    print(f"Coverage required: {min_coverage*100}%")
    
    # First pass: Standard grid placement
    for y in range(0, rows - panel_height, panel_height + gap):
        for x in range(0, cols - panel_width, panel_width + gap):
            
            # Check the panel area
            panel_roi = rooftop_mask[y:y+panel_height, x:x+panel_width]
            
            if panel_roi.size > 0:
                rooftop_pixels = np.sum(panel_roi == 255)
                total_pixels = panel_roi.size
                coverage = rooftop_pixels / total_pixels
                
                # Place panel if coverage is sufficient
                if coverage >= min_coverage:
                    # Draw blue panel with black border
                    cv2.rectangle(result_image, (x, y), (x + panel_width, y + panel_height), (255, 0, 0), -1)
                    cv2.rectangle(result_image, (x, y), (x + panel_width, y + panel_height), (0, 0, 0), 1)
                    panel_count += 1
    
    # Second pass: Fill gaps with smaller panels
    small_panel_width = 10
    small_panel_height = 8
    min_coverage_small = 0.60  # Even lower threshold for gap filling
    
    print(f"Gap filling with {small_panel_width}x{small_panel_height} panels, {min_coverage_small*100}% threshold")
    
    for y in range(0, rows - small_panel_height, small_panel_height + gap):
        for x in range(0, cols - small_panel_width, small_panel_width + gap):
            
            # Check if this area is already covered by a panel
            center_x, center_y = x + small_panel_width//2, y + small_panel_height//2
            current_pixel = result_image[center_y, center_x]
            
            # If not already blue (no existing panel)
            if not (current_pixel[0] > 200 and current_pixel[1] < 50 and current_pixel[2] < 50):
                
                panel_roi = rooftop_mask[y:y+small_panel_height, x:x+small_panel_width]
                
                if panel_roi.size > 0:
                    rooftop_pixels = np.sum(panel_roi == 255)
                    total_pixels = panel_roi.size
                    coverage = rooftop_pixels / total_pixels
                    
                    if coverage >= min_coverage_small:
                        # Draw smaller panel
                        cv2.rectangle(result_image, (x, y), (x + small_panel_width, y + small_panel_height), (255, 0, 0), -1)
                        cv2.rectangle(result_image, (x, y), (x + small_panel_width, y + small_panel_height), (0, 0, 0), 1)
                        panel_count += 1
    
    print(f"Placed {panel_count} solar panels")
    return result_image, panel_count


def place_solar_panels_double_density(image, rooftop_mask):
    """
    Place solar panels with DOUBLE DENSITY for maximum coverage
    """
    result_image = image.copy()
    rows, cols = rooftop_mask.shape
    
    # Double density specifications - smaller panels, no gaps
    panel_width = 8     # Much smaller panels
    panel_height = 6    # Much smaller height
    gap = 0            # NO gap between panels for maximum density
    min_coverage = 0.50  # Lower threshold for more placement
    
    panel_count = 0
    
    print(f"DOUBLE DENSITY PANEL PLACEMENT")
    print(f"Panel size: {panel_width}x{panel_height}")
    print(f"Gap: {gap}px (no gaps)")
    print(f"Coverage required: {min_coverage*100}%")
    
    # Dense grid placement with overlapping coverage
    for y in range(0, rows - panel_height, panel_height + gap + 1):
        for x in range(0, cols - panel_width, panel_width + gap + 1):
            
            # Check the panel area
            panel_roi = rooftop_mask[y:y+panel_height, x:x+panel_width]
            
            if panel_roi.size > 0:
                rooftop_pixels = np.sum(panel_roi == 255)
                total_pixels = panel_roi.size
                coverage = rooftop_pixels / total_pixels
                
                # Place panel if coverage is sufficient
                if coverage >= min_coverage:
                    # Draw red panel for double density (different color)
                    cv2.rectangle(result_image, (x, y), (x + panel_width, y + panel_height), (0, 0, 255), -1)
                    cv2.rectangle(result_image, (x, y), (x + panel_width, y + panel_height), (0, 0, 0), 1)
                    panel_count += 1
    
    # Fill any remaining gaps with micro panels
    micro_panel_width = 6
    micro_panel_height = 4
    min_coverage_micro = 0.40  # Very low threshold for micro panels
    
    print(f"Micro-panel filling with {micro_panel_width}x{micro_panel_height} panels, {min_coverage_micro*100}% threshold")
    
    for y in range(0, rows - micro_panel_height, micro_panel_height + 1):
        for x in range(0, cols - micro_panel_width, micro_panel_width + 1):
            
            # Check if this area is already covered by a panel
            center_x, center_y = x + micro_panel_width//2, y + micro_panel_height//2
            current_pixel = result_image[center_y, center_x]
            
            # If not already covered by red panels
            if not (current_pixel[2] > 200 and current_pixel[0] < 50 and current_pixel[1] < 50):
                
                panel_roi = rooftop_mask[y:y+micro_panel_height, x:x+micro_panel_width]
                
                if panel_roi.size > 0:
                    rooftop_pixels = np.sum(panel_roi == 255)
                    total_pixels = panel_roi.size
                    coverage = rooftop_pixels / total_pixels
                    
                    if coverage >= min_coverage_micro:
                        # Draw micro panel in orange
                        cv2.rectangle(result_image, (x, y), (x + micro_panel_width, y + micro_panel_height), (0, 165, 255), -1)
                        cv2.rectangle(result_image, (x, y), (x + micro_panel_width, y + micro_panel_height), (0, 0, 0), 1)
                        panel_count += 1
    
    print(f"Placed {panel_count} solar panels (DOUBLE DENSITY)")
    return result_image, panel_count


def place_solar_panels_custom(image, rooftop_mask, target_count, panel_width=40, panel_height=25):
    """
    Place exactly the specified number of solar panels on rooftops
    Fixed size: 40x25 pixels, Blue color
    """
    print(f"CUSTOM PANEL PLACEMENT")
    print(f"Target panels: {target_count}")
    print(f"Panel size: {panel_width}x{panel_height} (FIXED)")
    print(f"Gap: 3px")
    print(f"Color: Blue")
    
    result_image = image.copy()
    
    # Find all rooftop areas
    contours, _ = cv2.findContours(rooftop_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Sort contours by area (largest first)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    # Generate all possible panel positions
    possible_positions = []
    gap = 3  # Increased gap for larger panels
    
    for contour in contours:
        x_cont, y_cont, w_cont, h_cont = cv2.boundingRect(contour)
        
        # Generate grid positions for this contour
        for y in range(y_cont, y_cont + h_cont - panel_height + 1, panel_height + gap):
            for x in range(x_cont, x_cont + w_cont - panel_width + 1, panel_width + gap):
                # Check if this position has good rooftop coverage
                panel_roi = rooftop_mask[y:y+panel_height, x:x+panel_width]
                
                if panel_roi.size > 0:
                    rooftop_pixels = np.sum(panel_roi == 255)
                    total_pixels = panel_roi.size
                    coverage = rooftop_pixels / total_pixels
                    
                    if coverage >= 0.4:  # Reduced from 60% to 40% minimum coverage
                        possible_positions.append((x, y, coverage))
    
    # Sort positions by coverage quality (best first)
    possible_positions.sort(key=lambda pos: pos[2], reverse=True)
    
    # Place exactly target_count panels
    panels_placed = 0
    used_positions = set()
    
    for x, y, coverage in possible_positions:
        if panels_placed >= target_count:
            break
            
        # Check if this position overlaps with already placed panels
        overlap = False
        for used_x, used_y in used_positions:
            if (abs(x - used_x) < panel_width + gap and 
                abs(y - used_y) < panel_height + gap):
                overlap = True
                break
        
        if not overlap:
            # Draw panel in BLUE color
            cv2.rectangle(result_image, (x, y), (x + panel_width, y + panel_height), (255, 0, 0), -1)
            cv2.rectangle(result_image, (x, y), (x + panel_width, y + panel_height), (0, 0, 0), 2)
            
            # Add panel number text in white with better visibility
            panel_num = panels_placed + 1
            text_x = x + panel_width // 2 - 10
            text_y = y + panel_height // 2 + 5
            # Add black background for better text visibility
            cv2.rectangle(result_image, (text_x-8, text_y-12), (text_x+16, text_y+3), (0, 0, 0), -1)
            cv2.putText(result_image, str(panel_num), (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            used_positions.add((x, y))
            panels_placed += 1
    
    print(f"Successfully placed {panels_placed} out of {target_count} requested panels")
    return result_image, panels_placed


def main(args=None):
    # Your expanded rooftop colors (original + new ones + additional campus colors)
    target_colors = [
        # Original colors
        (60, 49, 55), (55, 40, 45), (72, 53, 55), (81, 59, 64),
        # New colors you provided
        (86, 63, 69), (79, 60, 66), (92, 70, 76), (74, 52, 58),
        (85, 64, 70), (78, 57, 63), (68, 50, 55), (89, 66, 72),
        (82, 61, 66), (58, 45, 51), (96, 73, 79), (70, 52, 57),
        # Additional campus/institutional building colors
        (120, 100, 90), (110, 95, 85), (130, 110, 100), (100, 85, 75),
        (140, 120, 110), (125, 105, 95), (115, 100, 90), (135, 115, 105),
        # Reddish roof colors common in campus buildings
        (150, 120, 100), (160, 130, 110), (140, 110, 90), (155, 125, 105),
        # Concrete/gray roof colors
        (90, 85, 80), (105, 100, 95), (95, 90, 85), (110, 105, 100)
    ]
    
    # Use the predefined image path if no command line arguments
    if args and args.image:
        image_path = args.image
        if not os.path.exists(image_path):
            print(f"❌ Error: Image '{image_path}' not found!")
            return
    else:
        # Use the predefined image path from the top of the file
        image_path = INPUT_IMAGE_PATH
        if not os.path.exists(image_path):
            print(f"❌ Error: Predefined image '{image_path}' not found!")
            print("💡 Please update the INPUT_IMAGE_PATH variable at the top of the script")
            return
    
    # Ask user for number of solar panels if not provided via command line
    if args and args.panels:
        num_panels = args.panels
    else:
        while True:
            try:
                print(f"🔋 SOLAR PANEL PLACEMENT")
                print(f"📸 Input Image: {image_path}")
                print("-" * 50)
                num_panels = int(input("🎯 How many solar panels would you like to place? "))
                if num_panels > 0:
                    break
                else:
                    print("❌ Please enter a positive number!")
            except ValueError:
                print("❌ Please enter a valid number!")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                return
    
    print(f"\n🚀 Processing with {num_panels} solar panels...")
    
    # Process the single image
    images = [image_path]
    
    for fname in images:
        print(f"\n{'='*60}")
        print(f"Processing: {fname}")
        print(f"{'='*60}")
        
        image = cv2.imread(fname)
        if image is None:
            print(f"Could not load {fname}")
            continue
        
        h, w = image.shape[:2]
        print(f"Image size: {w}x{h}")
        
        # Use configurable tolerance levels from the top of the script
        tolerances = TOLERANCE_VALUES
        print(f"Testing tolerance values: ±{tolerances}")
        results = []
        
        for tolerance in tolerances:
            print(f"\n--- Testing Tolerance ±{tolerance} ---")
            
            rooftop_mask = detect_rooftops_targeted(image, target_colors, tolerance)
            
            # Calculate coverage percentage
            total_pixels = h * w
            rooftop_pixels = np.sum(rooftop_mask == 255)
            coverage_pct = (rooftop_pixels / total_pixels) * 100
            
            print(f"Coverage: {coverage_pct:.1f}%")
            
            # Always use custom mode with user-specified panel count
            result_image_custom, panel_count_custom = place_solar_panels_custom(
                image, rooftop_mask, num_panels)
            
            results.append({
                'tolerance': tolerance,
                'coverage': coverage_pct,
                'mask': rooftop_mask,
                'result_custom': result_image_custom,
                'panels_custom': panel_count_custom,
                'mode': 'custom'
            })
        
        # Select best result (reasonable coverage, good panel count)
        best_result = None
        best_score = 0
        
        for result in results:
            # Score based on reasonable coverage (5-20%) and panel count
            coverage_score = 100 if 5 <= result['coverage'] <= 20 else max(0, 50 - abs(result['coverage'] - 12.5))
            
            # For custom mode, score based on how close we got to target
            achieved_panels = result['panels_custom']
            panel_score = max(0, 100 - abs(num_panels - achieved_panels) * 2)
            print(f"Tolerance ±{result['tolerance']}: {result['coverage']:.1f}% coverage, {achieved_panels}/{num_panels} custom panels, Score: {coverage_score + panel_score:.1f}")
            
            total_score = coverage_score + panel_score
            
            if total_score > best_score:
                best_score = total_score
                best_result = result
        
        # Display results
        if best_result:
            print(f"\n🎉 BEST RESULT:")
            print(f"   📊 Tolerance: ±{best_result['tolerance']}")
            print(f"   📈 Coverage: {best_result['coverage']:.1f}%")
            print(f"   🔋 Custom Panels: {best_result['panels_custom']}/{num_panels} (achieved/target)")
            
            # Create visualization - always custom mode
            fig, axes = plt.subplots(1, 3, figsize=(18, 6))
            fig.suptitle(f'Custom Solar Panels - {best_result["panels_custom"]}/{num_panels} panels placed', fontsize=16, fontweight='bold')
            
            # Original Image
            axes[0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            axes[0].set_title('Original Image', fontsize=14, fontweight='bold')
            axes[0].axis('off')
            
            # Detected Rooftops (black and white mask)
            axes[1].imshow(best_result['mask'], cmap='gray')
            axes[1].set_title(f'Detected Rooftops\\n±{best_result["tolerance"]} tolerance', fontsize=14, fontweight='bold')
            axes[1].axis('off')
            
            # Custom Panels with numbers
            axes[2].imshow(cv2.cvtColor(best_result['result_custom'], cv2.COLOR_BGR2RGB))
            axes[2].set_title(f'Custom Panels\\n{best_result["panels_custom"]} placed', fontsize=14, fontweight='bold')
            axes[2].axis('off')
            
            plt.tight_layout()
            plt.show()
            
            # Save results
            output_name = os.path.basename(fname).split('.')[0]
            
            cv2.imwrite(f'final_rooftops_{output_name}.jpg', best_result['mask'])
            cv2.imwrite(f'final_solar_custom_{output_name}.jpg', best_result['result_custom'])
            
            print(f"\n💾 SAVED FILES:")
            print(f"   📁 Rooftops: final_rooftops_{output_name}.jpg")
            print(f"   🔋 Custom Panels: final_solar_custom_{output_name}.jpg")
            
        else:
            print("\n❌ No suitable results found")


if __name__ == "__main__":
    print("🔋 GK HACKS - ROOFTOP DETECTION & SOLAR PANEL PLACEMENT 🏠")
    print("=" * 60)
    
    # Check if command line arguments are provided
    if len(sys.argv) > 1:
        # Parse command line arguments (for backward compatibility)
        parser = argparse.ArgumentParser(description='🔋 GK HACKS - Rooftop Detection and Solar Panel Placement 🏠')
        parser.add_argument('--mode', choices=['normal', 'double', 'both', 'custom'], default='custom',
                           help='Solar panel placement mode (default: custom)')
        parser.add_argument('--image', type=str, help='Specific image file to process (optional)')
        parser.add_argument('--panels', type=int, help='Number of solar panels to place')
        
        args = parser.parse_args()
        
        # Validate custom mode arguments
        if args.mode == 'custom' and args.panels is None:
            print("Error: --panels argument is required for custom mode")
            print("Example: python rooftop_detection_gk.py --mode custom --panels 10")
            sys.exit(1)
        if args.panels and args.panels <= 0:
            print("Error: Number of panels must be positive")
            sys.exit(1)
        
        main(args)
    else:
        # Interactive mode - no command line arguments
        print(f"📁 Using predefined image: {INPUT_IMAGE_PATH}")
        print("💡 To change the image, edit the INPUT_IMAGE_PATH variable at the top of the script")
        print()
        main()