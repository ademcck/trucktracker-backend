import xml.etree.ElementTree as ET
import os
from core.settings.base import BASE_DIR

class SVGCustomizer:
    def __init__(self, svg_template_path):
        self.svg_template_path = svg_template_path
        self.tree, self.root, self.width, self.height = self.load_existing_svg(svg_template_path)
        self.namespaces = {'svg': 'http://www.w3.org/2000/svg'}
        self.register_namespaces()

    def load_existing_svg(self, file_path):
        " Loads an existing SVG file and gets its dimensions. "
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Get SVG dimensions (by default A4: 210x297mm)
        width = root.get('width', '210mm')
        height = root.get('height', '297mm')
        
        # Convert values in mm to numeric values
        if 'mm' in width:
            width = float(width.replace('mm', ''))
        if 'mm' in height:
            height = float(height.replace('mm', ''))
            
        return tree, root, width, height

    def register_namespaces(self):
        " Saves SVG namespaces. "
        for prefix, uri in self.namespaces.items():
            ET.register_namespace(prefix, uri)

    def add_points_to_svg(self, coordinates, task_id, color='red'):
        " Adds coordinates as points to the SVG file. "
        coords_dict = self.parse_coordinates(coordinates)
        
        # Her sayfa için koordinatları yeni bir SVG'ye ekle
        for page, points in coords_dict.items():
            # Her sayfa için yeni bir SVG oluştur
            new_tree, new_root, _, _ = self.load_existing_svg(self.svg_template_path)
            
            group = ET.Element('{http://www.w3.org/2000/svg}g')
            group.set('id', page)
            
            path = ET.Element('{http://www.w3.org/2000/svg}path')
            path_data = f"M {points[0][0]} {points[0][1]}"
            for x, y in points[1:]:
                path_data += f" L {x} {y}"
            path.set('d', path_data)
            path.set('stroke', color)
            path.set('stroke-width', '1')
            path.set('fill', 'none')
            group.append(path)
            
            new_root.append(group)

            os.makedirs(f"{BASE_DIR}/core/utils/temp/{task_id}", exist_ok=True)
            # Sonucu kaydet
            new_tree.write(f"{BASE_DIR}/core/utils/temp/{task_id}/_{page}.svg", encoding='utf-8', xml_declaration=True)
            print(f"Coordinates added to temp/{task_id}/_{page}", end='.svg\n') # debug

    def parse_coordinates(self, coordinates):
        " Processes coordinates and converts them into standard format. "
        coords_dict = coordinates
        # Format validation
        for page, points in coords_dict.items():
            if not isinstance(points, list):
                raise ValueError(f"The coordinates for page {page} should be a list")
            
            for point in points:
                if not isinstance(point, list) or len(point) != 2:
                    raise ValueError(f"Invalid coordinate format for page {page}: {point} should be [x, y]")
        
        return coords_dict

def create_svg_main(coords, task_id):
    svg_customizer = SVGCustomizer(f"{BASE_DIR}/core/utils/template.svg")
    svg_customizer.add_points_to_svg(coords, task_id, color="black")
