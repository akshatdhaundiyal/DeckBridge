# Standard Widescreen (16:9) PowerPoint Dimensions in Inches
SLIDE_WIDTH = 13.333
SLIDE_HEIGHT = 7.5

# Standard Header Canvas Bounds
HEADER_LEFT = 1.0
HEADER_TOP = 0.75
HEADER_WIDTH = 11.333
HEADER_HEIGHT = 1.3

# Standard Content Canvas Bounds
CONTENT_LEFT = 1.0
CONTENT_TOP = 2.15
CONTENT_WIDTH = 11.333
CONTENT_HEIGHT = 4.65


def get_column_bounds(
    total_cols: int,
    left: float = 1.0,
    total_width: float = 11.333,
    gap: float = 0.35,
) -> tuple[list[float], float]:
    """Calculate column left positions and uniform width.

    NEVER use hardcoded coordinate numbers inside layout loops.
    """
    if total_cols <= 0:
        raise ValueError("total_cols must be at least 1")
    col_w = (total_width - (gap * (total_cols - 1))) / total_cols
    left_positions = [left + i * (col_w + gap) for i in range(total_cols)]
    return left_positions, col_w


def get_row_bounds(
    total_rows: int,
    top: float = 2.2,
    total_height: float = 4.6,
    gap: float = 0.3,
) -> tuple[list[float], float]:
    """Calculate row top positions and uniform height."""
    if total_rows <= 0:
        raise ValueError("total_rows must be at least 1")
    row_h = (total_height - (gap * (total_rows - 1))) / total_rows
    top_positions = [top + i * (row_h + gap) for i in range(total_rows)]
    return top_positions, row_h
