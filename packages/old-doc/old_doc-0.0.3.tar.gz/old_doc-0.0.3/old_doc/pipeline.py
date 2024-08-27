import numpy as np
import random
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from typing import List, Tuple, Optional
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

class TextBlock:
    def __init__(self, content: str, 
                 block_type: str = "text",
                 font_size: int = 20,
                 font_file: str = "Arial.ttf",
                 font_color: Tuple[int, int, int] = (0, 0, 0),
                 curve_amount: float = 0.0,
                 drop_cap_probability: float = 0.0,
                 drop_cap_font_size: int = 40,
                 drop_cap_offset: Tuple[int, int] = (0, 0),  # Changed to a tuple for x and y offset
                 drop_cap_font_file: str = "Arial.ttf",
                 drop_cap_font_color: Tuple[int, int, int] = (0, 0, 0),
                 gradient_effect: bool = False,
                 word_spacing: float = 1.0,
                 char_spacing: float = 1.0):
        self.content = content
        self.block_type = block_type
        self.font_size = font_size
        self.font_file = font_file
        self.font_color = font_color
        self.curve_amount = curve_amount
        self.drop_cap_probability = drop_cap_probability
        self.drop_cap_font_size = drop_cap_font_size
        self.drop_cap_offset = drop_cap_offset
        self.drop_cap_font_file = drop_cap_font_file
        self.drop_cap_font_color = drop_cap_font_color
        self.gradient_effect = gradient_effect
        self.word_spacing = word_spacing
        self.char_spacing = char_spacing
        self.polygon = []

class Column:
    def __init__(self, text_blocks: List[TextBlock], width: int):
        self.text_blocks = text_blocks
        self.width = width

class Row:
    def __init__(self, columns: List[Column], height: int):
        self.columns = columns
        self.height = height

class Page:
    def __init__(self, rows: List[Row],
                 cell_padding: int = 10,
                 background_color: Tuple[int, int, int] = (255, 255, 255),
                 background_texture: Optional[str] = None,
                 background_image: Optional[str] = None,
                 noise_factor: float = 0.0):
        self.rows = rows
        self.cell_padding = cell_padding
        self.background_color = background_color
        self.background_texture = background_texture
        self.background_image = background_image
        self.noise_factor = noise_factor
        self.width = max(sum(col.width for col in row.columns) for row in rows)
        self.height = sum(row.height for row in rows)
        self.image = None
        self.alto = None
        self.text_polygons = []

    def generate(self):
        # Create the base image
        if self.background_image:
            self.image = Image.open(self.background_image).resize((self.width, self.height))
        else:
            self.image = Image.new('RGB', (self.width, self.height), color=self.background_color)
        
        # Apply background texture if provided
        if self.background_texture:
            texture = Image.open(self.background_texture).resize((self.width, self.height))
            self.image = Image.blend(self.image, texture, 0.5)
        
        # Apply noise
        if self.noise_factor > 0:
            noise = np.random.normal(0, self.noise_factor, (self.height, self.width, 3)).astype(np.uint8)
            noise_image = Image.fromarray(noise, mode='RGB')
            self.image = Image.blend(self.image, noise_image, 0.5)
        
        draw = ImageDraw.Draw(self.image)
        
        # Initialize ALTO XML structure
        self.alto = ET.Element("alto", xmlns="http://www.loc.gov/standards/alto/ns-v4#")
        layout = ET.SubElement(self.alto, "Layout")
        page = ET.SubElement(layout, "Page", ID="PAGE_0001", PHYSICAL_IMG_NR="1", HEIGHT=str(self.height), WIDTH=str(self.width))
        print_space = ET.SubElement(page, "PrintSpace", ID="PS_0001")
        
        # Process each row and column
        y = 0
        for row_index, row in enumerate(self.rows):
            x = 0
            for col_index, column in enumerate(row.columns):
                # Create TextBlock in ALTO XML
                text_block = ET.SubElement(print_space, "TextBlock", ID=f"TB_{row_index}_{col_index}")
                ET.SubElement(text_block, "Shape")
                ET.SubElement(text_block, "Coords", POINTS=f"{x},{y} {x+column.width},{y} {x+column.width},{y+row.height} {x},{y+row.height}")
                
                # Process text blocks in the column
                for block in column.text_blocks:
                    self.process_text_block(draw, block, x, y, column.width, text_block)
                
                x += column.width
            y += row.height
        
        return self.image, self.alto

    def process_text_block(self, draw, block, x, y, width, alto_block):
        font = ImageFont.truetype(block.font_file, block.font_size)

        if block.block_type == "heading":
            y = self.add_curved_line(draw, block.content, x, y, width, font, alto_block, is_heading=True, text_block=block)
        elif random.random() < block.drop_cap_probability:
            drop_cap_width, drop_cap_height = self.add_drop_cap(draw, block.content[0], x, y, alto_block, text_block=block)
            
            # Calculate the remaining width for text after the drop cap
            remaining_width = width - drop_cap_width - self.cell_padding
            
            # Add text to the right of the drop cap
            text_x = x + drop_cap_width + self.cell_padding
            y = self.add_wrapped_text(draw, block.content[1:], text_x, y, remaining_width, font, alto_block, text_block=block)
            
            # Ensure y is at least as large as drop_cap_height
            y = max(y, y + drop_cap_height)
        else:
            y = self.add_wrapped_text(draw, block.content, x, y, width, font, alto_block, text_block=block)

        return y

    def add_drop_cap(self, draw, char, x, y, alto_block, text_block):
        font = ImageFont.truetype(text_block.drop_cap_font_file, text_block.drop_cap_font_size)
        drop_cap_x = x + text_block.drop_cap_offset[0]
        drop_cap_y = y + text_block.drop_cap_offset[1]
        
        draw.text((drop_cap_x, drop_cap_y), char, fill=text_block.drop_cap_font_color, font=font)

        bbox = draw.textbbox((drop_cap_x, drop_cap_y), char, font=font)
        polygon_points = [
            (bbox[0], bbox[1]),
            (bbox[2], bbox[1]),
            (bbox[2], bbox[3]),
            (bbox[0], bbox[3])
        ]

        self.text_polygons.append((char, polygon_points))

        # Add drop cap to ALTO XML
        text_line = ET.SubElement(alto_block, "TextLine", ID=f"TL_DC_{alto_block.get('ID')}")
        coords = " ".join([f"{int(x)},{int(y)}" for x, y in polygon_points])
        ET.SubElement(text_line, "Coords", POINTS=coords)
        string = ET.SubElement(text_line, "String", CONTENT=char)
        string.set("STYLE", "dropcap")

        # Return the width and height of the drop cap
        return (bbox[2] - bbox[0], bbox[3] - bbox[1])

    def add_wrapped_text(self, draw, text, x, y, max_width, font, alto_block, text_block):
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            line_width = draw.textlength(test_line, font=font)
            if line_width <= max_width - 2 * self.cell_padding:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []

        if current_line:
            lines.append(' '.join(current_line))

        for line in lines:
            y = self.add_curved_line(draw, line, x, y, max_width, font, alto_block, text_block=text_block)

        return y

    def add_curved_line(self, draw, text, x, y, max_width, font, alto_block, is_heading=False, text_block=None):
        bbox = draw.textbbox((x, y), text, font=font)
        line_width = min(bbox[2] - bbox[0], max_width - 2 * self.cell_padding)
        line_height = bbox[3] - bbox[1]

        curve = np.sin(np.linspace(0, np.pi, int(line_width))) * text_block.curve_amount * text_block.font_size

        polygon_points = []
        words = text.split()
        
        # Calculate total width with adjusted spacing
        total_width = sum(draw.textlength(word, font=font) for word in words)
        total_width += text_block.char_spacing * (len(text) - len(words))  # Add char spacing
        total_width += text_block.word_spacing * (len(words) - 1)  # Add word spacing
        scale_factor = line_width / total_width

        current_x = x + self.cell_padding
        for word_index, word in enumerate(words):
            for char_index, char in enumerate(word):
                char_width = draw.textlength(char, font=font) * scale_factor
                char_x = current_x
                char_y = y + self.cell_padding + curve[min(int(current_x - x - self.cell_padding), len(curve) - 1)]

                if text_block.gradient_effect:
                    char_color = self.get_gradient_color(char_y, text_block.font_color, (255, 255, 255), self.height)
                else:
                    char_color = text_block.font_color

                draw.text((char_x, char_y), char, fill=char_color, font=font)
                polygon_points.append((char_x, char_y))

                current_x += char_width
                
                # Add character spacing after each character except the last one in the word
                if char_index < len(word) - 1:
                    current_x += text_block.char_spacing * scale_factor

            # Add word spacing after each word except the last one
            if word_index < len(words) - 1:
                current_x += text_block.word_spacing * scale_factor

        # Ensure the last point is at the end of the line
        last_x = x + self.cell_padding + line_width
        last_y = y + self.cell_padding + curve[-1]
        polygon_points.append((last_x, last_y))

        # Complete the polygon
        for i in range(len(polygon_points) - 1, -1, -1):
            char_x = polygon_points[i][0]
            char_y = polygon_points[i][1] + line_height
            polygon_points.append((char_x, char_y))

        self.text_polygons.append((text, polygon_points))

        # Add line to ALTO XML
        text_line = ET.SubElement(alto_block, "TextLine", ID=f"TL_{alto_block.get('ID')}_{len(alto_block)}")
        coords = " ".join([f"{int(x)},{int(y)}" for x, y in polygon_points])
        ET.SubElement(text_line, "Coords", POINTS=coords)
        string = ET.SubElement(text_line, "String", CONTENT=text)
        if is_heading:
            string.set("STYLE", "heading")

        return y + line_height + self.cell_padding

    def get_gradient_color(self, y_position, start_color, end_color, total_height):
        t = y_position / total_height
        return tuple(int(start + (end - start) * t) for start, end in zip(start_color, end_color))

    def visualize_results(self, show_polygons=True):
        if self.image is None:
            raise ValueError("Image has not been generated yet. Call generate() first.")

        plt.figure(figsize=(15, 20))
        plt.subplot(1, 2, 1)
        plt.imshow(self.image)
        plt.title("Generated Image")
        plt.axis('off')

        if show_polygons:
            plt.subplot(1, 2, 2)
            plt.imshow(self.image)
            for _, polygon in self.text_polygons:
                x, y = zip(*polygon)
                plt.plot(x + x[:1], y + y[:1], 'r-')
            plt.title("Image with Polygons")
            plt.axis('off')

        plt.tight_layout()
        plt.show()

    def save_alto_xml(self, filename: str):
        if self.alto is None:
            raise ValueError("ALTO XML has not been generated yet. Call generate() first.")

        rough_string = ET.tostring(self.alto, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(reparsed.toprettyxml(indent="  "))