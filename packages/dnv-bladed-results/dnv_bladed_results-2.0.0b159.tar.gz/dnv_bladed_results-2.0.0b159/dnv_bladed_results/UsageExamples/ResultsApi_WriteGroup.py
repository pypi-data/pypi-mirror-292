from dnv_bladed_results import *
from dnv_bladed_results import UsageExamples
import os
import tempfile

############   Bladed Results API: Write output group   ############

# Demonstrates how to write output groups containing:
# - 1D variables (dependent variables with one independent variable)
# - 2D variables (dependent variables with two independent variables)

# Demonstrates population of variable data using a NumPy array.


def write_1d_output_group_basic(output_directory, output_run_name):

    group_path = r"{0}\{1}.%999".format(output_directory, output_run_name)

    ############################
    #  Create 1D output group  #
    ############################

    # Create axis
    independent_variable = IndependentVariable("Independent variable", "Unit", 0.0, 1.0)

    # Create group
    output_group_1d = OutputGroup1D_Float32(group_path, "TestGroup_Basic", "UserDefined", "Config", independent_variable)

    #############################
    #  Add variables with data  #
    #############################

    variable_data = np.array((1.0, 2.0, 3.0, 4.0, 5.0))
    user_variable_name = "User variable"
    output_group_1d.add_variable_with_data(user_variable_name, "SI unit", variable_data)

    #################
    #  Write group  #
    #################
    
    success = ResultsApi.write_output(output_group_1d)

    if success:
        print("Successfully created 1D output group:", group_path)
    else:
        print("Failed to create 1D output group:", group_path)

    #####################
    #  Prove roundtrip  #
    #####################
    
    prove_1d_roundtrip(variable_data, user_variable_name, output_directory, output_run_name)


def write_2d_output_group_basic(output_directory, output_run_name):

    group_path = r"{0}\{1}.%999".format(output_directory, output_run_name)
    
    ############################
    #  Create 2D output group  #
    ############################
    
    # Create axes
    primary_independent_variable = IndependentVariable("Independent variable 1", "Unit", 0.0, 1.0)
    secondary_axis_intervals = ["Label 1", "Label 2", "Label 3"]
    secondary_independent_variable = IndependentVariable("Independent variable 2", "Unit", secondary_axis_intervals)

    # Create group
    output_group_2d = OutputGroup2D_Float32(group_path, "TestGroup_Basic", "UserDefined", "Config", primary_independent_variable, secondary_independent_variable)

    ######################
    #  Create some data  #
    ######################

    num_points = 10
    num_secondary_axis_values = len(secondary_axis_intervals)
    variable_data = np.zeros([num_secondary_axis_values, num_points])
    for secondary_axis_value_index in range(0, num_secondary_axis_values - 1, 1):
        for point_index in range(0, num_points - 1, 1):
            variable_data[secondary_axis_value_index][point_index] = np.float32((secondary_axis_value_index + 1) * (point_index + 1))

    #############################
    #  Add variables with data  #
    #############################

    user_variable_name = "User variable - Tower Mx"
    output_group_2d.add_variable_with_data(user_variable_name, "SI unit", variable_data)

    #################
    #  Write group  #
    #################
    
    success = ResultsApi.write_output(output_group_2d)

    if success:
        print("Successfully created 2D output group:", group_path)
    else:
        print("Failed to create 2D output group:", group_path)

    #####################
    #  Prove roundtrip  #
    #####################

    prove_2d_roundtrip(variable_data, user_variable_name, output_directory, output_run_name)


def write_1d_output_group_extended(source_run_directory, source_run_name, output_directory, output_run_name):

    group_path = r"{0}\{1}.%999".format(output_directory, output_run_name)

    ############################
    #  Create 1D output group  #
    ############################

    independent_variable = IndependentVariable("Independent variable", "Unit", 0.0, 1.0)
    output_group_1d = OutputGroup1D_Float32(group_path, "TestGroup_Extended", "UserDefined", "Config", independent_variable)

    ######################
    #  Create some data  #
    ######################
    
    control_variable_name = "Rotating hub Mx"
    variable = ResultsApi.get_run(source_run_directory, source_run_name).get_variable_1d(control_variable_name)

    # Read data as NumPy array
    data_original = variable.get_data()
    factor = 2.0
    data_modified = create_1d_variable_data(data_original, factor)
                                                     
    #############################
    #  Add variables with data  #
    #############################

    user_variable_name = "User variable - Rotating hub Mx"
    output_group_1d.add_variable_with_data(user_variable_name, "SI unit", data_modified)

    #################
    #  Write group  #
    #################
    
    success = ResultsApi.write_output(output_group_1d)

    if success:
        print("Successfully created 1D output group:", group_path)
    else:
        print("Failed to create 1D output group:", group_path)

    #####################
    #  Prove roundtrip  #
    #####################
    
    prove_1d_roundtrip(data_original, user_variable_name, output_directory, output_run_name, factor)


def write_2d_output_group_extended(source_run_directory, source_run_name, output_directory, output_run_name):

    group_path = r"{0}\{1}.%999".format(output_directory, output_run_name)
    
    ############################
    #  Create 2D output group  #
    ############################

    control_variable_name = "Tower Mx"
    variable = ResultsApi.get_run(source_run_directory, source_run_name).get_variable_2d(control_variable_name)
    
    # Create primary independent variable (interval axis)
    primary_independent_variable = IndependentVariable("Independent variable 1", "Unit", 0.0, 1.0)

    # Create secondary independent variable (axis with string labels)
    num_secondary_axis_intervals = variable.get_independent_variable(INDEPENDENT_VARIABLE_ID_SECONDARY_INDEPENDENT_VARIABLE).get_number_of_values()
    secondary_axis_intervals = np.empty(num_secondary_axis_intervals, dtype=object)
    for i in range(0, num_secondary_axis_intervals):
        secondary_axis_intervals[i] = "Label " + str(i + 1)
    
    secondary_independent_variable = IndependentVariable("Independent variable 2", "Unit", secondary_axis_intervals)

    # Create group
    output_group_2d = OutputGroup2D_Float32(group_path, "TestGroup_Extended", "UserDefined", "Config", primary_independent_variable, secondary_independent_variable)

    ######################
    #  Create some data  #
    ######################

    # Read data as NumPy array
    data_original = variable.get_data_for_all_independent_variable_values()
    factor = 2.0
    data_modified = create_2d_variable_data(data_original, factor)

    #############################
    #  Add variables with data  #
    #############################

    user_variable_name = "User variable - Tower Mx"
    output_group_2d.add_variable_with_data(user_variable_name, "SI unit", data_modified)

    #################
    #  Write group  #
    #################
    
    success = ResultsApi.write_output(output_group_2d)

    if success:
        print("Successfully created 2D output group:", group_path)
    else:
        print("Failed to create 2D output group:", group_path)

    #####################
    #  Prove roundtrip  #
    #####################

    prove_2d_roundtrip(data_original, user_variable_name, output_directory, output_run_name, factor)


def create_1d_variable_data(data_original, factor):
   
    num_points = len(data_original)

    # Copy original array, and multiply every value by 2
    data_modified = np.array(data_original, copy=True)

    for point_index in range(0, num_points, 1):
        data_modified[point_index] = data_original[point_index] * factor

    return data_modified


def prove_1d_roundtrip(data_original, user_variable_name, output_directory, output_run_name, factor=1.0):

    run = ResultsApi.get_run(output_directory, output_run_name)
    assert run.get_calculation_type() == CALCULATION_TYPE_USER_DEFINED

    data_roundtrip = run.get_variable_1d(user_variable_name).get_data()

    point_index = 0
    for val in data_original:
        assert (val * factor) == data_roundtrip[point_index], "Expected value equality on data roundtrip: array index = " + str(point_index)
        point_index = point_index + 1

    print("Roundtrip successful for 1D array containing", str(point_index), "values\n")


def create_2d_variable_data(data_original, factor):

    num_secondary_axis_vals = len(data_original)
    num_points = len(data_original[0])

    # Copy original array, and multiply every value by 2
    data_modified = np.array(data_original, copy=True)

    for secondary_axis_value_index in range(0, num_secondary_axis_vals, 1):
        for point_index in range(0, num_points, 1):
            data_modified[secondary_axis_value_index][point_index] = data_original[secondary_axis_value_index][point_index] * factor

    return data_modified


def prove_2d_roundtrip(data_original, user_variable_name, output_directory, output_run_name, factor=1.0):

    num_secondary_axis_vals = len(data_original)
    num_points = 0
    if num_secondary_axis_vals > 0:
        num_points = len(data_original[0])

    run = ResultsApi.get_run(output_directory, output_run_name)
    assert run.get_calculation_type() == CALCULATION_TYPE_USER_DEFINED

    data_roundtrip = run.get_variable_2d(user_variable_name).get_data_for_all_independent_variable_values()

    point_index = 0
    for secondary_axis_value_index in range(0, num_secondary_axis_vals, 1):
        for val in data_original[secondary_axis_value_index]:
            assert (val * factor) == (data_roundtrip[secondary_axis_value_index][point_index]), "Expected value equality on data roundtrip: secondary axis index = {0} point index = {1}".format(str(secondary_axis_value_index), str(point_index))
            point_index = point_index + 1
        point_index = 0

    print("Roundtrip successful for 2D array containing {0} secondary axis values and {1} points\n".format(str(num_secondary_axis_vals), str(num_points)))


output_directory = os.path.join(UsageExamples.__path__[0], "Runs/output")
source_run_directory = os.path.join(UsageExamples.__path__[0], "Runs/demo/powprod5MW")
source_run_name = "powprod5MW"

# Write a one-dimensional Bladed output group (a group containing only 1D variables) using hard-coded data
write_1d_output_group_basic(output_directory, "UserGroup1DTest_Basic")

# Write a two-dimensional Bladed output group (a group containing only 2D variables) using hard-coded data
write_2d_output_group_basic(output_directory, "UserGroup2DTest_Basic")

# Write a one-dimensional Bladed output group (a group containing only 1D variables) using data extracted and transformed from an existing output group
write_1d_output_group_extended(source_run_directory, source_run_name, output_directory, "UserGroup1DTest_Extended")

# Write a two-dimensional Bladed output group (a group containing only 2D variables) using data extracted and transformed from an existing output group
write_2d_output_group_extended(source_run_directory, source_run_name, output_directory, "UserGroup2DTest_Extended")

# Long path test, where the Bladed output group path length exceeds Windows _MAX_PATH limit
output_run_name = "test_output_group_showing_the_new_results_api_handles_paths_that_are_longer_than_the_piffling_two_hundred_and_sixty_character_limit_on_windows"
output_directory_temp = tempfile.gettempdir() + "/BladedResultsAPI/Output/PathWithMoreCharactersThanMaxPath/PathWithMoreCharactersThanMaxPath/PathWithMoreCharactersThanMaxPath/PathWithMoreCharactersThanMaxPath/PathWithMoreCharactersThanMaxPath/PathWithMoreCharactersThanMaxPath/PathWithMoreCharactersThanMaxPath/PathWithMoreCharactersThanMaxPath"
write_1d_output_group_extended(source_run_directory, source_run_name, output_directory_temp, output_run_name)
