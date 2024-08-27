from .cli_analysis import add_analysis_parser
from .cli_convert import add_convert_parser
from .cli_notebook import add_notebook_parser
from .cli_graph_sorting import add_graph_sorting_parser

parsers = [add_analysis_parser, add_convert_parser, add_notebook_parser, add_graph_sorting_parser]