from pathlib import Path
from .cairo_interface import CairoInterface
from .geometry import Scene, Color, Rectangle


class GanttChart:

    def __init__(self):
        self.milestones = []
        self.start_date = None
        self.end_date = None
        self.milestone_bar_max_height = 0.1
        self.height = 100
        self.width = 500
        self.milestone_color = Color(0.7, 0, 0)

    def _add_milestone(self, scene, milestone, chart_range, yloc):
        chart_delta = chart_range[1] - chart_range[0]
        start_delta = milestone.start_date - chart_range[0]
        milestone_delta = milestone.due_date - milestone.start_date

        start_frac = float(start_delta / chart_delta)
        milestone_frac = float(milestone_delta / chart_delta)

        w = milestone_frac * self.width
        h = self.milestone_bar_max_height * self.height
        x = start_frac * self.width
        y = yloc

        rect = Rectangle(w, h)
        rect.location = (x, y)
        rect.fill = self.milestone_color
        scene.items.append(rect)

    def _add_milestones(self, scene):

        if not self.milestones:
            return

        milestones = self.milestones
        milestones.sort(key=lambda x: x.start_date, reverse=True)

        start_date = self.start_date
        end_date = self.end_date
        if not start_date:
            start_date = milestones[0].start_date

        if not end_date:
            end_date = max(m.due_date for m in milestones)

        chart_range = (start_date, end_date)
        yloc = 0
        bar_height = self.milestone_bar_max_height * self.height
        for milestone in milestones:
            self._add_milestone(scene, milestone, chart_range, yloc)
            yloc += bar_height

    def plot(self, path: Path):
        scene = Scene()

        self._add_milestones(scene)

        renderer = CairoInterface()
        renderer.draw_svg(scene, path)
