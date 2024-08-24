from .rtp import rtpplot
from .result import ResultSet

def plot(results: ResultSet, indicator: Union[str, Indicator, None]=None):
    number_of_algorithms = len(results.algorithms)
    number_of_problems = len(results.problems)
    n_number_of_objectives = 0
    n_number_of_variables = 0
    number_of_indicators = 0

    if number_of_algorithms == 1:
        pass
        ## Give up for now, later raw performance data

    if n_number_of_variables > 1 and n_number_of_objectives > 1:
        pass
        ## Grid of nv x no rtpplots
    if n_number_of_variables == 1 and n_number_of_objectives > 1:
        pass
        ## row of rtpplots
    if n_number_of_variables > 1 and n_number_of_objectives == 1:
        pass
        ## column of rtpplots
    if number_of_problems == 1:
        rtpplot(results)
    else:
        pass
        
    return None