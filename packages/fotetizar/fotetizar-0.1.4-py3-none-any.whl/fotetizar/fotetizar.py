import os
from PIL import Image, ImageDraw, ImageFont
import argparse

# Define color themes
THEMES = {
    "monokai": {"background": (39, 40, 34), "text": (248, 248, 242), "line_number": (128, 128, 128)},
    "blackandwhite": {"background": (255, 255, 255), "text": (0, 0, 0), "line_number": (128, 128, 128)},
    "solarized": {"background": (0, 43, 54), "text": (131, 148, 150), "line_number": (108, 113, 122)},
    "gruvbox": {"background": (40, 40, 40), "text": (235, 219, 178), "line_number": (160, 113, 24)},
    "nord": {"background": (46, 52, 64), "text": (216, 222, 233), "line_number": (136, 192, 208)},
    "dracula": {"background": (40, 42, 54), "text": (248, 248, 242), "line_number": (98, 114, 164)},
    "github": {"background": (255, 255, 255), "text": (36, 41, 46), "line_number": (199, 199, 199)},
    "one_dark": {"background": (40, 44, 52), "text": (171, 178, 191), "line_number": (106, 115, 125)},
    "atom": {"background": (33, 37, 43), "text": (171, 178, 191), "line_number": (109, 130, 143)},
    "vscode": {"background": (30, 30, 30), "text": (212, 212, 212), "line_number": (128, 128, 128)},
    "commodore64": {"background": (66, 77, 72), "text": (152, 219, 160), "line_number": (255, 255, 255)},  # Custom theme for Commodore64 mode
}

def draw_editor(d, img, lines, font, line_number_font, text_color, line_number_color):
    # Draw the mac-style window header
    header_height = 30
    d.rectangle([0, 0, img.width, header_height], fill=(60, 60, 60))
    
    # Draw the window control icons
    icon_radius = 10
    icon_spacing = 15
    icon_colors = [(255, 0, 0), (255, 255, 0), (0, 255, 0)]  # Red, Yellow, Green
    for i, color in enumerate(icon_colors):
        d.ellipse((icon_spacing + i * (2 * icon_radius + icon_spacing), 5, 
                  icon_spacing + (i + 1) * (2 * icon_radius) + i * icon_spacing, 5 + 2 * icon_radius),
                  fill=color)
    
    # Draw the file content
    line_number_width = 30  # Width reserved for line numbers
    x_text = line_number_width + 10  # Padding after line numbers
    for i, line in enumerate(lines):
        # Draw line number
        line_number_text = f"{i + 1}"
        d.text((10, header_height + 10 + i * 18), line_number_text, font=line_number_font, fill=line_number_color)
        
        # Draw code text
        d.text((x_text, header_height + 10 + i * 18), line, font=font, fill=text_color)

def draw_console(d, img, lines, font, text_color, file_name):
    linux_prompt = "user@hostname:~$"
    # Console theme colors
    console_bg_color = (0, 0, 0)  # Black background
    prompt_color = (0, 255, 0)    # Green color for the prompt and text
    
    # Draw the old-style console background
    d.rectangle([0, 0, img.width, img.height], fill=console_bg_color)

    # Set up prompt text and spacing
    prompt_font = ImageFont.truetype(font.path, size=18)
    prompt_text = f"{linux_prompt} cat {file_name}"
    prompt_y = 10

    # Draw the Linux prompt and file content
    d.text((10, prompt_y), prompt_text, font=prompt_font, fill=prompt_color)
    
    # Draw file content below the prompt
    content_y = prompt_y + 30  # Leave space below the prompt
    for i, line in enumerate(lines):
        d.text((10, content_y + i * 18), line, font=font, fill=prompt_color)
    
    # Draw the end of the file content prompt
    end_prompt_text = f"{linux_prompt}"
    end_prompt_y = content_y + len(lines) * 18 + 10  # Space after content
    d.text((10, end_prompt_y), end_prompt_text, font=prompt_font, fill=prompt_color)

def render_image(input_file, theme, font_path=None, mode="editor"):
    # Determine the default font directory and default font path
    default_font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    default_font_path = os.path.join(default_font_dir, 'UbuntuMono-Regular.ttf')

    # Use the provided font or fallback to the default font
    try:
        font = ImageFont.truetype(font_path or default_font_path, size=14)  # Adjust size as needed
    except OSError:
        print(f"Warning: Unable to open font file '{font_path or default_font_path}'. Using default font.")
        font = ImageFont.load_default()  # Load a default font

    line_number_font = font  # Use the same font for line numbers

    # Load the input file
    with open(input_file, 'r') as f:
        code = f.read()

    # Get the selected theme colors
    theme_colors = THEMES.get(theme, THEMES["monokai"])
    text_color = theme_colors["text"]
    line_number_color = theme_colors["line_number"]

    # Calculate the image size
    lines = code.split('\n')
    max_line_length = max([len(line) for line in lines])
    image_width = max_line_length * 10 + 40  # 10 is an approximate character width in pixels
    image_height = len(lines) * 18 + 40  # 18 is an approximate line height in pixels

    img = Image.new('RGB', (image_width, image_height), color=theme_colors["background"])
    d = ImageDraw.Draw(img)

    if mode == "editor":
        draw_editor(d, img, lines, font, line_number_font, text_color, line_number_color)
    elif mode == "console":
        draw_console(d, img, lines, font, text_color, os.path.basename(input_file))

    # Save the image
    mode_suffix = "_console" if mode == "console" else ""
    output_file = f"{os.path.splitext(os.path.basename(input_file))[0]}_{theme}{mode_suffix}.png"
    img.save(output_file)
    print(f"Image saved as {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate images from code with different themes.")
    parser.add_argument("input_file", help="Path to the input file")
    parser.add_argument("theme", help="Theme to use for rendering")
    parser.add_argument("--font", help="Optional custom font file to use", default=None)
    parser.add_argument("--mode", help="Scenario type (console or editor)", default="editor")

    args = parser.parse_args()

    render_image(args.input_file, args.theme, args.font, args.mode)

if __name__ == "__main__":
    main()

