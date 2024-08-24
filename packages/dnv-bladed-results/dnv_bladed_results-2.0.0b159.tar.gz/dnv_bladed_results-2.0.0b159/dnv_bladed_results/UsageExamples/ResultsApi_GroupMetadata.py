from dnv_bladed_results import *
from dnv_bladed_results import UsageExamples
import os

############   Bladed Results API: Get output group metadata   ############

# Gets group metadata for 1D and 2D variables
# Prints information about dependent and independent variables


# The following function is needed for rendering special UTF8 chars on the console, e.g. superscript
def fix_encoding_for_terminal_print(unencoded):
    return unencoded.encode('utf-8', 'surrogateescape').decode('ISO-8859-1')


def display_group_metadata(run_directory, run_name):
    
    try:
        
        ################################
        #  Get a specific run by name  #
        ################################

        run = ResultsApi.get_run(run_directory, run_name)

        ##########################
        #  Get a specific Group  #
        ##########################

        group = run.get_group("support structure accelerations")
        print("\n#####   Group name: " + group.get_name() + "   #####")
        print("Calculation name: " + group.get_calculation_short_name() + " (" + group.get_calculation_descriptive_name() + ")")

        ####################
        #  Get all groups  #
        ####################

        print("Displaying metadata for run '" + run.get_name() + "'")
        all_groups = run.get_all_groups()
        print("Run has " + str(all_groups.size) + " output groups")
        
        # Iterate group collection
        group: Group
        for group in all_groups:
            
            print("\n#####   Group name: " + group.get_name() + "   #####")
            
            #########################################
            #  Display some basic calculation info  #
            #########################################

            print("Calculation name: " + group.get_calculation_short_name() + " (" + group.get_calculation_descriptive_name() + ")")
            print("  Group has " + str(group.get_data_point_count()) + " data points per series")
            
            # Full enumeration of calculation types available via CalculationType:
            calc_type = group.get_calculation_type()
            if calc_type == CALCULATION_TYPE_POWER_PRODUCTION_SIMULATION:
                pass
            elif calc_type == CALCULATION_TYPE_PARKED_SIMULATION:
                pass

            ####################################################
            #  Get independent variables and display metadata  #
            ####################################################

            # Print independent variable info (a group always has either 1 or 2 independent variables)
            print("  Group has " + str(group.get_number_of_independent_variables()) + " independent variables:")
            primary_independent_var = group.get_independent_variable(INDEPENDENT_VARIABLE_ID_PRIMARY_INDEPENDENT_VARIABLE)
            print("  - Primary independent variable name: " + primary_independent_var.get_name() + ";\tSI unit: " + fix_encoding_for_terminal_print(primary_independent_var.get_siunit()))
            if group.get_number_of_independent_variables() == 2:
                secondary_independent_var = group.get_independent_variable(INDEPENDENT_VARIABLE_ID_SECONDARY_INDEPENDENT_VARIABLE)
                print("  - Secondary independent variable name: " + secondary_independent_var.get_name() + ";\tSI unit: " + fix_encoding_for_terminal_print(secondary_independent_var.get_siunit()))

            ##################################################
            #  Get dependent variables and display metadata  #
            ##################################################

            if group.get_number_of_independent_variables() == 1:
                all_dependent_vars = group.get_all_variables_1d()
            else:
                all_dependent_vars = group.get_all_variables_2d()

            # Print dependent variable info
            print("  Group has " + str(group.get_number_of_variables()) + " dependent variables:")
            dependent_var: Variable
            for dependent_var in all_dependent_vars:
                print("  - Dependent variable name: " + dependent_var.get_name() + ";\tSI unit: " + fix_encoding_for_terminal_print(dependent_var.get_siunit()))

        print()

    except RuntimeError as e:
        print(e)


run_directory = os.path.join(UsageExamples.__path__[0], "Runs/demo/powprod5MW")
run_name = "powprod5MW"
display_group_metadata(run_directory, run_name)
