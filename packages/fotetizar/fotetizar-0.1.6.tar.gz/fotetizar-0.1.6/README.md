
---

# Because Your Code Deserves to Shine!

Tired of your code looking plain and boring? It's time to give it the spotlight it deserves! With `fotetizar`, you can transform your code into stunning, themed images. Whether you’re looking to share your code with style or need a cool visual for your portfolio, `fotetizar` has you covered.

## Installation

To get started with `fotetizar`, you'll need Python and Poetry. If you don’t have Poetry installed, follow the installation guide [here](https://python-poetry.org/docs/#installation).

### 1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/fotetizar.git
   cd fotetizar
   ```

### 2. **Install Dependencies**

   Install all required dependencies with Poetry:

   ```bash
   poetry install
   ```

### 3. **Install the Package**

   If you want to install the package locally for development purposes:

   ```bash
   poetry install --editable .
   ```
### 4. **Install with pip**

   If you want to install the package with pip. 

   ```bash
    pip install fotetizar
   ```
## Usage

`fotetizar` can be used both in code and from the command line.

### In Code

Here’s a quick example of how to use `fotetizar` programmatically:

```python
from fotetizar import render_image

input_file = 'your_code_file.py'  # Replace with your actual file
theme = 'dracula'
font_path = 'path/to/custom/font.ttf'  # Replace with your actual font path
mode = 'editor'

render_image(input_file, theme, font_path, mode)
```

This will generate an image of the code in `your_code_file.py` using the "dracula" theme, with the specified font, in "editor" mode.

### In Console

To use `fotetizar` from the command line, run the following command:

```bash
fotetizar your_code_file.py dracula --mode editor
```

This command generates an image of `your_code_file.py` using the "dracula" theme in "editor" mode.

## Options / Arguments

Here are the available options and arguments for `fotetizar`:

- **`input_file`** (required): The path to the input file you want to render. This should be a Python script or any text file containing code.
  - Example: `your_code_file.py`

- **`theme`** (required): The color theme to use for rendering.
  - Available themes:
    - `monokai`
    - `blackandwhite`
    - `solarized`
    - `gruvbox`
    - `nord`
    - `dracula`
    - `github`
    - `one_dark`
    - `atom`
    - `vscode`
    - `commodore64`
  - Example: `dracula`

- **`--font`** (optional): Path to a custom font file to use for rendering.
  - Example: `path/to/custom/font.ttf`

- **`--mode`** (optional): The rendering mode, either "editor" or "console".
  - Example: `editor`

### Examples

1. **Generate an image with the "dracula" theme and "editor" mode**:

   ```bash
   fotetizar your_code_file.py dracula --mode editor
   ```

2. **Generate an image with a custom font and "console" mode**:

   ```bash
   fotetizar your_code_file.py nord --font path/to/custom/font.ttf --mode console
   ```

3. **Use the "commodore64" theme with default settings**:

   ```bash
   fotetizar your_code_file.py commodore64
   ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

