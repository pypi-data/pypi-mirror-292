# To help with reading and manipulating data
import pandas as pd
import numpy as np
import json

# To help with model building
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
    BaggingClassifier,
)

from xgboost import XGBClassifier

# To oversample and undersample data
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler

# To define maximum number of columns to be displayed in a dataframe
pd.set_option("display.max_columns", None)

# To supress scientific notations for a dataframe
pd.set_option("display.float_format", lambda x: "%.3f" % x)

# To supress warnings
import warnings
warnings.filterwarnings("ignore")

#import the required function
from scipy.stats import chi2_contingency

# # import bayes search cv
# # !pip install scikit-optimize
# from skopt import BayesSearchCV

# # import support vector machine
# from sklearn.svm import SVC

# #!pip install scikit-learn-intelex
# from sklearnex import patch_sklearn 
# patch_sklearn()

# using jlm_tech_ds_ml_ba_toolkit
from jlm_tech_ds_ml_ba_toolkit.stats_and_plots import (
    getStatisticsAndInfoOnDataSets,
    display_outliers,
)

from jlm_tech_ds_ml_ba_toolkit.ds_preprocessing_utils import (
    create_train_test_sets,
    treat_outliers,
    knn_imputation_processing
)

from jlm_tech_ds_ml_ba_toolkit.ml_performance_utils import (
    model_building_with_cross_validation_classifier,
    test_pvalue_with_alpha
)

from jlm_tech_ds_ml_ba_toolkit.ml_utils import (
    shape_and_perct_classes,
    create_json_obj_and_data_frame_from_csv
)

def main():
    
    path = "PATH TO YOUR DIRECTORY WHERE THE CSV FILES ARE STORED"
    
    # full path to csv
    csv_fname = "Train_set_(1)_(1).csv"
    
    # full path to json config
    base_config_fname = "base_config_obj.json"
    
    # full path to new json config
    final_config_fname = "hackathon_config_obj.json"
    
    # create json config/data frame from csv    
    create_json_obj_and_data_frame_from_csv(
        path,
        csv_fname,
        base_config_fname,
        final_config_fname        
    )

    # read the dataset
    df_original_df = pd.read_csv(path+csv_fname)
    
    # Opening JSON file for configuration
    json_file = open(path+final_config_fname)
    
    # load json file and return a py dictionary obj
    config_object = json.load(json_file)
    
    # close json file
    json_file.close()

    # make a copy of the original dataframe
    df = df_original_df.copy()
    print(df.shape)
    print(df.head())

    # load the test set
    original_test_df = pd.read_csv(path+"Test_set_(1)_(2).csv")
    print(original_test_df.shape)
    print(original_test_df.head())
    
    # convert all obj type to category since its more memory efficient
    for col_name in df.select_dtypes(include=np.object_).columns:
        df[col_name] = df[col_name].astype("category")
            
    # output text summary stats
    config_object["enable_stats_processing"] = True
    config_object["enable_1D_plot_processing"] = False
    config_object["enable_2D_plot_processing"] = False
    config_object["enable_numeric_processing"] = False

    # get statistics and info on data set as well as plot numerous variables univariate and bivariate/multivariate
    # save the statistics to an output file for later review
    getStatisticsAndInfoOnDataSets(
        data_frame=df, 
        file_name="NBFC_Load_Default_Dataset-Analysis-V1.txt",
        config_object=config_object
    )
    
    # visualize the counts of rows by state
    # this will show num of applicants by state
    print(df.groupby("state_code")["state_code"].count())
    
    # we are doing some feature engineering here to reduce the num of cols for the model to care about
    # and combine cat_vals where it makes sense to also reduce the num cols when we use get_dummies

    # home_ownership(other,none)
    # we want to replace from this "none" to this "other"
    df['home_ownership'] = df['home_ownership'].replace('NONE', 'OTHER')

    # income_verfication_status(source_verified, verified)
    # we want to replace from this "source_verified" to this "verified"
    df['income_verification_status'] = df['income_verification_status'].replace('Source Verified', 'Verified')

    # Create a new column 'application_level_cnt' in the dataframe df that categorizes the 'state_code' based 
    # on its frequency. The frequency is determined by the value_counts() function, 
    # which returns a series with the count of each unique 'state_code'
    # The pd.cut function is then used to categorize the counts into different bins, with labels 
    # 'low_application_cnt', 'medium_application_cnt', and 'high_application_cnt'
    # The bins are defined as [0, 1000), [1000, 5000), and [5000, infinity), 
    # where 0-1000 is 'low_application_cnt', 1001-5000 is 'medium_application_cnt', 5001-Inf is 'high_application_cnt'
    # where the first bin includes 0 and the last bin includes infinity
    df['application_level_cnt'] = pd.cut(df['state_code'].map(df['state_code'].value_counts()), 
                                    bins=[0, 3000, 6000, float('inf')], 
                                    labels=['low_application', 'medium_application', 'high_application'])

    # state_code is unique for each candidate and wont add value to modeling and we grouped it based on low/med/high
    # applications cnt based on  state
    df = df.drop(["state_code"], axis=1)
    
    # NOTE: after feature engineering its good to do EDA again
    # get statistics and info on data set as well as plot numerous variables univariate and bivariate/multivariate
    # save the statistics to an output file for later review
    getStatisticsAndInfoOnDataSets(
        data_frame=df, 
        file_name="NBFC_Load_Default_Dataset-Analysis-V2.txt",
        config_object=config_object
    )
    
    # create the contingency table showing the distribution of two categorical variables
    contingency_table = pd.crosstab(df['loan_grade'], df['loan_subgrade'])
    print(contingency_table)
    
    # use chi2_contingency() to find the p-value
    chi_2, p_value, dof, exp_freq = chi2_contingency(contingency_table)
    
    # print the conclusion based on p-value, with alpha = 0.05
    test_pvalue_with_alpha(p_value, 0.05)
    
    # loan_grade id dependent on loan_subgrade and we care more about loan_subgrade
    df = df.drop(["loan_grade"], axis=1)
    
    # NOTE: after feature engineering its good to do EDA again
    # get statistics and info on data set as well as plot numerous variables univariate and bivariate/multivariate
    # save the statistics to an output file for later review
    getStatisticsAndInfoOnDataSets(
        data_frame=df, 
        file_name="NBFC_Load_Default_Dataset-Analysis-V3.txt",
        config_object=config_object
    )
    
    x_axis_num = 15
    y_axis_num = 12
    num_cols = 4
    
    # selecting numerical columns
    num_col = df.select_dtypes(include=np.number).columns.tolist()
    
    # display outliers
    display_outliers(df, num_cols, x_axis_num, y_axis_num)

    # get df with just num cols and drop the default col since we dont want to drop outliers here
    df_num_outliers = df[num_col]
    print(df_num_outliers.columns)
    
    # skip these cols from treating outliers
    skip_cols = ["default", "delinq_2yrs","public_records", "interest_rate","last_week_pay"]

    # remove outliers
    df = treat_outliers(df, skip_cols)

    num_cols = 4
    
    # display outliers
    display_outliers(df, num_cols, x_axis_num, y_axis_num)

    # create train test sets    
    x_train, x_test, y_train, y_test, x, y = create_train_test_sets(
        df, 
        "default", 
        add_y_intercept=False, 
        add_dummy_cols=False
    )

    # display shape and percentage of classes
    shape_and_perct_classes(x_train, x_test, y_train, y_test, y)

    # we need to pass numerical values for each categorical column for KNN imputation so we will label encode them
    job_experience = {"<5 Years": 0, "10+ years": 1, "6-10 years": 2}
    x_train["job_experience"] = x_train["job_experience"].map(job_experience)
    x_test["job_experience"] = x_test["job_experience"].map(job_experience)

    # defining a list with names of columns that will be used for imputation
    reqd_col_for_impute = [
        "job_experience",
        "annual_income",
        "delinq_2yrs",
        "public_records",
        "total_acc",
        "last_week_pay",
        "total_current_balance",
        "total_revolving_limit",
        
    ]
    
    # KNN imputation with KNNImputer and reverse encoding train set
    knn_imputation_processing(
        x_train, 
        reqd_col_for_impute,
        job_experience,
        "job_experience",
        n_neighbors=5
    )
    
    # KNN imputation with KNNImputer and reverse encoding test set
    knn_imputation_processing(
        x_test, 
        reqd_col_for_impute,
        job_experience,
        "job_experience",
        n_neighbors=5
    )
    
    # display shape and percentage of classes
    shape_and_perct_classes(x_train, x_test, y_train, y_test, y)
    
    # creating dummy variables train set
    x_train = pd.get_dummies(
        x_train,
        columns=x_train.select_dtypes(include=["object", "category"]).columns.tolist(),
        drop_first=True,
    )

    # creating dummy variables test set
    x_test = pd.get_dummies(
        x_test,
        columns=x_test.select_dtypes(include=["object", "category"]).columns.tolist(),
        drop_first=True,
    )
    
    # remove any non approved char from the cols names before we do model training
    x_train.columns = x_train.columns.str.replace('[', '').str.replace(']', '').str.replace('<', 'less_than_')
    x_test.columns = x_test.columns.str.replace('[', '').str.replace(']', '').str.replace('<', 'less_than_')
    
    # use these models for cross validation
    model_name_list = []
    # model_name_list.append("LogisticRegression")
    # model_name_list.append("DecisionTree")
    # model_name_list.append("RandomForest")
    # model_name_list.append("Bagging")
    # model_name_list.append("GBM")
    # model_name_list.append("Adaboost")
    # model_name_list.append("SVM")
    model_name_list.append("Xgboost")

    # init num splits for cross validation and setup random state to 1 any where we can to have reproducible results
    n_splits = 5
    random_state = 1
    metric_type = "accuracy"

    # --- original data set cross validation ---

    # peform cross validation using the model list and use recall as a metric and plot using a boxplot
    original_train_score_df, original_val_score_df =  model_building_with_cross_validation_classifier(
        metric_type, model_name_list, x_train, y_train, x_test, y_test, "Original", n_splits=n_splits)

    # --- original data set cross validation ---

    # --- SMOTE data set cross validation ---

    # Synthetic Minority Over Sampling Technique
    sm = SMOTE(sampling_strategy=1, k_neighbors=5, random_state=random_state)
    x_train_over, y_train_over = sm.fit_resample(x_train, y_train)

    print("After Oversampling, the shape of train_X: {}".format(x_train_over.shape))
    print("After Oversampling, the shape of train_y: {} \n".format(y_train_over.shape))

    smote_train_score_df, smote_val_score_df =  model_building_with_cross_validation_classifier(
        metric_type, model_name_list, x_train_over, y_train_over, x_test, y_test, "SMOTE", n_splits=n_splits)

    # --- SMOTE data set cross validation ---

    # --- undersamplng data set cross validation ---

    # Random undersampler for under sampling the data
    rus = RandomUnderSampler(random_state=random_state, sampling_strategy=1)
    x_train_under, y_train_under = rus.fit_resample(x_train, y_train)

    print("After UnderSampling, the shape of train_X: {}".format(x_train_under.shape))
    print("After UnderSampling, the shape of train_y: {} \n".format(y_train_under.shape))

    undersampling_train_score_df, undersampling_val_score_df =  model_building_with_cross_validation_classifier(
        metric_type, model_name_list, x_train_under, y_train_under, x_test, y_test, "UnderSampling", n_splits=n_splits)

    # --- undersamplng data set cross validation ---

    print()

    # training performance comparison
    models_train_comp_df = pd.concat(
        [
            original_train_score_df["Model"],
            original_train_score_df["Train Original CV Mean Score"],
            smote_train_score_df["Train SMOTE CV Mean Score"],
            undersampling_train_score_df["Train UnderSampling CV Mean Score"]
        ],
        axis=1
    )

    print("Training performance comparison:")
    print(models_train_comp_df)
    print("**" * 50)
    print()

    # Validation performance comparison
    models_val_comp_df = pd.concat(
        [
            original_val_score_df["Model"],
            original_val_score_df["Validation Original CV Mean Score"],
            smote_val_score_df["Validation SMOTE CV Mean Score"],
            undersampling_val_score_df["Validation UnderSampling CV Mean Score"]
        ],
        axis=1
    )

    print("Validation performance comparison:")
    print(models_val_comp_df)
    print("**" * 50)
    print()

# run the main    
main()