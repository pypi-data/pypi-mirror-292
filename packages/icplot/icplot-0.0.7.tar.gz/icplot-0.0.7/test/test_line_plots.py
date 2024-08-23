from pathlib import Path

from icplot.graph import LinePlot, LinePlotSeries


def test_line_plot():
    
    plot = LinePlot(title="test",
                    x_label="test_x",
                    y_label="test_y",
                    legend_label="test_legend")

    data = [([0, 5, 10], [1, 2, 3]),
            ([0, 5, 10], [3, 6, 9]),
            ([0, 5, 10], [4, 8, 12])]

    for idx, [x, y] in enumerate(data):
        plot.series.append(LinePlotSeries(x, y,  label=f"Series {idx}"))
        
    plot.set_x_ticks(0, 10, 5)

    output_path = Path() / "output.svg"
    plot.plot(output_path)

    assert output_path.exists()
    output_path.unlink()
