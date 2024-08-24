from dnv_bladed_results import *
from dnv_bladed_results import UsageExamples
import os

############   Bladed Results API: Get run metadata   ############

# Finds runs according to search criteria and displays run metadata.


def display_run_metadata(run_directory):

    ##########################################################################
    #  Get a set of runs, excluding those with unsupported calculation type  #
    ##########################################################################

    ResultsApi_SearchSettings.set_include_unsupported_calculations(False)
    runs = ResultsApi.get_runs(run_directory, SEARCH_SCOPE_RECURSIVE_SEARCH)
    print("\nFound " + str(runs.size) + " runs")

    ##########################
    #  Display run metadata  #
    ##########################
    
    run: Run
    for run in runs:
        print("\nDisplaying information for run: " + run.get_directory() + run.get_name())
        print("Calculation name:", run.get_calculation_descriptive_name())
        if run.is_turbine_simulation():
            print("\nRun is a turbine simulation")
        if run.is_post_processing_calculation():
            print("\nRun is a post-processing calculation")
        if run.is_supporting_calculation():
            print("\nRun is a supporting calculation")
        if run.was_successful():
            print("Run was successful")
        else:
            print("Run was not successful")
        print("Run date:", run.get_timestamp())
        try:
            print("Run execution duration (s):", str(run.get_execution_duration_seconds()))
        except RuntimeError as e:
            print("Cannot get run execution duration")
        try:
            print("\nRun message file ($ME) content:\n", run.get_message_file_content())
        except RuntimeError as e:
            print("Cannot get run message file ($ME) content")
        
    print()
    
    # Revert default search setting
    ResultsApi_SearchSettings.set_include_unsupported_calculations(True)


run_directory = os.path.join(UsageExamples.__path__[0], "Runs/demo")
display_run_metadata(run_directory)
