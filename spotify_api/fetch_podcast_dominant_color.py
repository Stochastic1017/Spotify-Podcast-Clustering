
import pandas as pd
import requests
from io import BytesIO
from PIL import Image
from tqdm import tqdm
import numpy as np
import colorsys

def is_white_dominated(image):
    """
    Check if the image is predominantly white.
    
    Args:
    image (PIL.Image): Loaded image object.
    
    Returns:
    bool: True if image is predominantly white, False otherwise.
    """
    # Convert image to numpy array
    img_array = np.array(image)
    
    # Calculate the percentage of white pixels
    white_threshold = 230  # RGB values close to white
    white_pixels = np.sum(np.all(img_array >= white_threshold, axis=2))
    total_pixels = img_array.shape[0] * img_array.shape[1]
    
    # Consider it white-dominated if over 60% of pixels are white
    return white_pixels / total_pixels > 0.6

def color_dominance_score(color, max_color_freq, threshold_multiplier=0.2):
    """
    Calculate a dominance score for a color.
    
    Args:
    color (tuple): RGB color tuple.
    max_color_freq (dict): Dictionary of color frequencies.
    threshold_multiplier (float): Multiplier for determining significant colors.
    
    Returns:
    float: Dominance score.
    """
    # Calculate the frequency of the color
    freq = max_color_freq.get(color, 0)
    
    # Calculate the total number of sampled pixels
    total_samples = sum(max_color_freq.values())
    
    # Compute dominance score
    return freq / total_samples

def is_muted_color(rgb_color, threshold=50):
    """
    Check if a color is grey, black, or too close to neutral.
    
    Args:
    rgb_color (tuple): RGB color as a tuple (R, G, B).
    threshold (int): Threshold for color variation and intensity.
    
    Returns:
    bool: True if the color is muted, False otherwise.
    """
    r, g, b = rgb_color
    
    # Check if color is too dark or close to black
    if r + g + b < threshold * 3:
        return True
    
    # Check color variance
    color_variance = max(r, g, b) - min(r, g, b)
    
    # Check if colors are too similar (grey-like)
    return color_variance < threshold

def get_comprehensive_dominant_color(image_url):
    """
    Get the most representative color from the image with comprehensive analysis.
    
    Args:
    image_url (str): URL of the image.
    
    Returns:
    str: RGB color string or None if no suitable color found.
    """
    try:
        response = requests.get(image_url, timeout=30)
        if response.status_code == 200:
            # Open image and convert to RGB
            image = Image.open(BytesIO(response.content)).convert('RGB')
            
            # Handle white-dominated images
            if is_white_dominated(image):
                return "rgb(255, 255, 255)"
            
            # Get image dimensions
            width, height = image.size
            
            # Create a color frequency dictionary
            color_freq = {}
            
            # Comprehensive sampling with more sophisticated approach
            sample_step_x = max(1, width // 100)
            sample_step_y = max(1, height // 100)
            
            for x in range(0, width, sample_step_x):
                for y in range(0, height, sample_step_y):
                    pixel = image.getpixel((x, y))
                    
                    # Skip very muted colors
                    if not is_muted_color(pixel):
                        color_freq[pixel] = color_freq.get(pixel, 0) + 1
            
            # If no colors found, return None
            if not color_freq:
                return None
            
            # Find most frequent colors
            sorted_colors = sorted(color_freq.items(), key=lambda x: x[1], reverse=True)
            
            # Calculate dominance scores
            max_color_freq = dict(color_freq)
            dominant_colors = [
                color for color, freq in sorted_colors 
                if color_dominance_score(color, max_color_freq) > 0.05
            ]
            
            # If no dominant colors found, fall back to most frequent color
            if not dominant_colors:
                best_color = sorted_colors[0][0]
            else:
                # Select the most representative color
                best_color = max(dominant_colors, key=lambda c: color_freq[c])
            
            return f"rgb({best_color[0]}, {best_color[1]}, {best_color[2]})"
        
        else:
            print(f"Failed to fetch image: {image_url} (HTTP {response.status_code})")
    except Exception as e:
        print(f"Error processing image {image_url}: {e}")
    return None

def append_dominant_colors_to_csv(input_csv, output_csv):
    """
    Append the dominant color for each podcast's image to the CSV.
    
    Args:
    input_csv (str): Path to the input CSV file.
    output_csv (str): Path to save the updated CSV file.
    """
    df = pd.read_csv(input_csv)
    dominant_colors = []
    print("Extracting dominant colors for podcast images...")
    
    for image_url in tqdm(df["podcast_image_url"], desc="Processing Images"):
        if pd.isna(image_url):
            dominant_colors.append(None)
        else:
            dominant_colors.append(get_comprehensive_dominant_color(image_url))
    
    df["podcast_dominant_color"] = dominant_colors
    df.to_csv(output_csv, index=False)
    print(f"Updated CSV saved to {output_csv}")
    
# Example usage
if __name__ == "__main__":
    input_csv = "data/cleaned_podcast_details.csv"
    output_csv = "data/cleaned_podcast_details.csv"
    append_dominant_colors_to_csv(input_csv, output_csv)