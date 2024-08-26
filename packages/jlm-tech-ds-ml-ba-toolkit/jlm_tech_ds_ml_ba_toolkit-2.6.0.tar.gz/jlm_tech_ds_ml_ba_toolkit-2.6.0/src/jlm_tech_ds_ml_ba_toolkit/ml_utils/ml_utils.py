
import pandas as pd
import seaborn as sns
import json

# to import csv
import csv

# for visualizing data
import seaborn as sns

# remove warnings
import warnings
warnings.filterwarnings("ignore")

from statsmodels.tools.sm_exceptions import ConvergenceWarning
warnings.simplefilter("ignore", ConvergenceWarning)

# Removes the limit for the number of displayed columns
pd.set_option("display.max_columns", None)

# Sets the limit for the number of displayed rows
pd.set_option("display.max_rows", None)

# To supress scientific notations for a dataframe
pd.set_option("display.float_format", lambda x: "%.3f" % x)

# sets the theme for all the plots
sns.set_theme()

# this will read a csv file and a base json file and create a json config file
# using the header cols from the csv file to fill in the base json file and create
# a new json file with filled in cols.
def create_json_config_from_csv(csv_path, base_config_obj_path, config_obj_path):
    
    print(f"Creating json config file from {csv_path} to {base_config_obj_path}")
    
    # Opening CSV file and read first line as the header
    # this will also close the file automatically
    with open(csv_path, 'r') as file:
        reader = csv.reader(file)
        header_line = next(reader)
        header_line_str = str(header_line)
    
    # remove white spaces from the header line    
    # header_line = str(header_line).strip()
    print(f"Header line: {header_line_str}")
    
    # remove white spaces from the fields in the header line
    header_line_list = [field.strip() for field in header_line]
    
    # Opening base JSON file 
    base_json_config_file = open(base_config_obj_path)
    
    # load json file and return a py dictionary obj
    base_json_config_object = json.load(base_json_config_file)

    # set the include_col_name_list in the json config object
    base_json_config_object["include_col_name_list"] = header_line_list

    # Dynamically create new objects in the include_plot_list based on the 
    # header_line_list and the template object.
    for plot_config in base_json_config_object["include_plot_list"]:
        if "use_col_name_list_pref" in plot_config:
            # Retrieve the first object in the use_col_name_list_pref list as a template
            template = plot_config["use_col_name_list_pref"][0]
            
            # Create a new list of objects by iterating over each col_name in the header_line_list
            plot_config["use_col_name_list_pref"] = [
                # Merge the template object with the col_name using the ** operator
                {**template, "col_name": col_name} 
                for col_name in header_line_list 
            ]
    
    # open a new file
    json_config_file = open(config_obj_path, 'w')
    
    # dump the json config object to this new file
    json.dump(base_json_config_object, json_config_file, indent=3)
    
    # close json file
    base_json_config_file.close()
    
    # close this json file with the new json config object
    json_config_file.close()

# simple func to help with file or sysout of data
def send_to_output(dat_str, file_obj, command="FILE_SYSOUT"):
    
    if(command == "FILE_SYSOUT"):
        file_obj.write(dat_str)
        print(dat_str)
        
    elif(command == "FILE"):
        file_obj.write(dat_str)
        
    elif(command == "SYSOUT"):
        print(dat_str)
        
    else:
        print("Invalid command for sending to output.")

# display shape and percentage of classes
def shape_and_perct_classes(x_train, x_test, y_train, y_test, y):
    print("Shape of Training set : ", x_train.shape)
    print("Shape of test set : ", x_test.shape)
    print()

    print("Shape of Training set : ", y_train.shape)
    print("Shape of test set : ", y_test.shape)
    print()

    print("Percentage of classes in Y set:")
    print(y.value_counts(normalize=True))
    print()

    print("Percentage of classes in training set:")
    print(y_train.value_counts(normalize=True))
    print()

    print("Percentage of classes in test set:")
    print(y_test.value_counts(normalize=True))
    print()
    
    # Checking that no column has missing values in train, validation or test sets
    print(x_train.isna().sum())
    print("-" * 30)
    print()
    print(x_test.isna().sum())
    print("-" * 30)
    print()

# create json obj and config file from csv and return the dataframe and config object
def create_json_obj_and_data_frame_from_csv(path, train_set_fname, base_config_fname, final_config_fname, return_data=False):
    
    # full path to csv
    csv_path = path+train_set_fname
    
    # full path to json config
    base_config_obj_path = path+base_config_fname
    
    # full path to new json config
    config_obj_path = path+final_config_fname
    
    # create json config from csv
    create_json_config_from_csv(csv_path, base_config_obj_path, config_obj_path)
    
    print("Path to config file: ", config_obj_path)
    
    # return the dataframe and config object only if we set this to true
    if(return_data == True):
    
        # read the dataset
        df_original_df = pd.read_csv(csv_path)
        
        # Opening JSON file for configuration
        json_file = open(config_obj_path)
        
        # load json file and return a py dictionary obj
        config_object = json.load(json_file)
        
        # close json file
        json_file.close()
        
        return config_object, df_original_df

# print the linear regression equation
def print_linear_regression_summary_equation(str_dep_var, x_train, olsmodel):
    
    # Let us write the equation of linear regression to see what it looks like for prediction purposes
    Equation = str_dep_var+ " =";
    print(Equation, end=" ");
    for i in range(len(x_train.columns)):
        if i == 0:
            
            print(olsmodel.params[i], "+", end=" ");
            
        elif i != len(x_train.columns) - 1:
            
            print(
                olsmodel.params[i],
                "* (",
                x_train.columns[i],
                ")",
                "+",
                end="  ",
            );
            
        else:
            print(olsmodel.params[i], "* (", x_train.columns[i], ")");
