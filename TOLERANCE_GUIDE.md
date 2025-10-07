# TOLERANCE CONFIGURATION EXAMPLES FOR ROOFTOP DETECTION

# The tolerance values are now at the top of rooftop_detection_gk.py for easy modification

# ===== CURRENT CONFIGURATION =====
TOLERANCE_VALUES = [3, 2]  # Default: precise detection

# ===== ALTERNATIVE CONFIGURATIONS =====

# 1. MORE INCLUSIVE DETECTION (for varied rooftop colors)
# TOLERANCE_VALUES = [5, 4, 3]
# Use this when: Your image has rooftops with many different colors/shades

# 2. VERY PRECISE DETECTION (for consistent rooftop colors)  
# TOLERANCE_VALUES = [2, 1]
# Use this when: Rooftops are very similar in color, avoid false positives

# 3. SINGLE TOLERANCE (faster processing)
# TOLERANCE_VALUES = [4]
# Use this when: You know which tolerance works best, want quick results

# 4. COMPREHENSIVE TEST (thorough but slower)
# TOLERANCE_VALUES = [6, 5, 4, 3, 2]
# Use this when: Testing new images, want to see all options

# 5. HIGH TOLERANCE (very inclusive)
# TOLERANCE_VALUES = [8, 6, 4]
# Use this when: Image has poor quality or very varied lighting

# ===== HOW TO USE =====
# 1. Edit line 14 in rooftop_detection_gk.py
# 2. Change TOLERANCE_VALUES to your desired configuration
# 3. Run: python rooftop_detection_gk.py
# 4. Script will test all your specified tolerance values and pick the best result

# ===== UNDERSTANDING TOLERANCE =====
# Tolerance ±3 means: RGB(79,60,66) will match colors from RGB(76,57,63) to RGB(82,63,69)
# Lower tolerance = more strict color matching = fewer rooftops detected = more precise
# Higher tolerance = looser color matching = more rooftops detected = less precise