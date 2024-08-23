import os
from pathlib import Path
import cairo

from .geometry import Scene, Rectangle, Color, TextPath


class CairoInterface:

    def __init__(self):
        pass

    def draw_rect(self, cr, rect: Rectangle):
        x0, y0 = rect.location
        x1 = rect.w
        y1 = rect.h
        cr.move_to(x0, y0)
        cr.line_to(x1, y0)
        cr.line_to(x1, y1)
        cr.line_to(x0, y1)
        cr.close_path()

    def draw_shape(self, cr, shape):
        cr.save()
        if shape.shape_type == "rect":
            self.draw_rect(cr, shape)
        else:
            return
        cr.set_source_rgba(shape.fill.r, shape.fill.g, shape.fill.b, shape.fill.a)
        cr.fill_preserve()
        if shape.stroke is not None:
            cr.set_source_rgba(
                shape.stroke.r, shape.stroke.g, shape.stroke.b, shape.stroke.a
            )
            cr.set_line_width(shape.stroke_thickness)
            cr.stroke()

        cr.restore()

    def draw_text(self, cr, text):
        cr.save()

        cr.select_font_face(text.font.family)
        cr.set_font_size(text.font.size)
        cr.move_to(text.location[0], text.location[1])
        cr.show_text(text.content)

        cr.restore()

    def draw_scene(self, cr, scene: Scene):
        for item in scene.items:
            if item.item_type == "shape":
                self.draw_shape(cr, item)
            elif item.item_type == "text":
                self.draw_text(cr, text)

    def draw_svg(self, scene, path):
        with cairo.SVGSurface(path, scene.size[0], scene.size[1]) as surface:
            cr = cairo.Context(surface)
            self.draw_scene(cr, scene)


if __name__ == "__main__":

    cairo_interface = CairoInterface()

    scene = Scene()

    rect = Rectangle(20, 20)
    rect.location = (10, 10)
    rect.fill = Color(0.5, 0.5, 1, 0.5)
    rect.stroke = Color(0.5, 0.0, 0.0, 0.5)
    scene.items.append(rect)

    text = TextPath("Hello World")
    text.location = (5, 5)
    scene.items.append(text)

    output_path = Path(os.getcwd()) / "output.svg"
    cairo_interface.draw_svg(scene, output_path)
