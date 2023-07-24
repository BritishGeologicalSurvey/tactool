from tactool.table_model import AnalysisPoint


def reset_id(analysis_point: AnalysisPoint) -> AnalysisPoint:
    """
    Resed the ID value of a given Analysis Point.
    """
    analysis_point.id = None
    return analysis_point
