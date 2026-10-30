from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.util import Inches

from app.engine.coordinates import (
    CONTENT_LEFT,
    CONTENT_TOP,
    CONTENT_WIDTH,
    CONTENT_HEIGHT,
)
from app.engine.layouts.base import BaseLayoutBuilder
from app.engine.theme import parse_hex_color
from app.schemas.deck import ChartSlide

CHART_TYPE_MAP = {
    "column_clustered": XL_CHART_TYPE.COLUMN_CLUSTERED,
    "column": XL_CHART_TYPE.COLUMN_CLUSTERED,
    "bar_clustered": XL_CHART_TYPE.BAR_CLUSTERED,
    "bar": XL_CHART_TYPE.BAR_CLUSTERED,
    "line": XL_CHART_TYPE.LINE,
    "pie": XL_CHART_TYPE.PIE,
    "area": XL_CHART_TYPE.AREA,
}


class ChartLayoutBuilder(BaseLayoutBuilder):
    """Layout builder for native PowerPoint OpenXML charts."""

    def render(self, slide_model: ChartSlide):
        slide, _, text_color, muted_color = self.create_blank_slide(slide_model)

        self.render_header(
            slide=slide,
            kicker=slide_model.kicker,
            title=slide_model.title,
            subtitle=slide_model.subtitle,
            text_color=text_color,
            muted_color=muted_color,
        )

        chart_data_model = slide_model.chart

        # 1. Build in-memory CategoryChartData
        chart_data = CategoryChartData()
        chart_data.categories = chart_data_model.categories
        for s in chart_data_model.series:
            chart_data.add_series(s.name, tuple(s.values))

        # 2. Resolve chart type
        chart_type = CHART_TYPE_MAP.get(
            chart_data_model.chart_type, XL_CHART_TYPE.COLUMN_CLUSTERED
        )

        # 3. Add chart shape in standard content bounds
        chart_shape = slide.shapes.add_chart(
            chart_type,
            Inches(CONTENT_LEFT),
            Inches(CONTENT_TOP),
            Inches(CONTENT_WIDTH),
            Inches(CONTENT_HEIGHT),
            chart_data,
        )
        chart = chart_shape.chart

        # 4. Legend configuration
        chart.has_legend = chart_data_model.show_legend
        if chart.has_legend:
            chart.legend.position = XL_LEGEND_POSITION.TOP
            chart.legend.include_in_layout = False

        # 5. Data labels configuration
        if chart_data_model.show_data_labels and chart.plots:
            chart.plots[0].has_data_labels = True

        # 6. Apply series colors
        default_palette = [self.theme.primary, self.theme.accent]
        for idx, s_model in enumerate(chart_data_model.series):
            if idx < len(chart.series):
                series = chart.series[idx]
                color = (
                    parse_hex_color(s_model.color)
                    if s_model.color
                    else default_palette[idx % len(default_palette)]
                )
                try:
                    if chart_type == XL_CHART_TYPE.LINE:
                        series.format.line.color.rgb = color
                    elif chart_type != XL_CHART_TYPE.PIE:
                        series.format.fill.solid()
                        series.format.fill.fore_color.rgb = color
                except Exception:
                    pass

        return slide

