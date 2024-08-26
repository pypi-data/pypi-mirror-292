
import numpy as np
import pandas as pd
import seaborn as sns
from dateutil.parser import parse

# for visualizing data
import seaborn as sns

# For randomized data splitting
from sklearn.model_selection import train_test_split

# To build linear regression_model
import statsmodels.api as sm

# To check model performance
from sklearn.metrics import r2_score

# to test for multicollinearity
from statsmodels.stats.outliers_influence import variance_inflation_factor

# To get diferent metric scores for logistic regression model
from sklearn.metrics import roc_curve

# To impute missing values
from sklearn.impute import KNNImputer

# remove warnings
import warnings
warnings.filterwarnings("ignore")

from statsmodels.tools.sm_exceptions import ConvergenceWarning
warnings.simplefilter("ignore", ConvergenceWarning)

# To supress scientific notations for a dataframe
pd.set_option("display.float_format", lambda x: "%.3f" % x)

# sets the theme for all the plots
sns.set_theme()

# Removes the limit for the number of displayed columns
pd.set_option("display.max_columns", None)

# Sets the limit for the number of displayed rows
pd.set_option("display.max_rows", None)

# this function is used to impute missing values based on the inpute_method and the group_by_cols and impute_cols
def impute_missing_values(data_frame, group_by_cols, impute_cols, replace_value=np.nan, impute_method="median"):

    print("---count/percentage of null values before imputation on df")
    print(pd.DataFrame({'Count':data_frame.isnull().sum()[data_frame.isnull().sum()>0],
                        'Percentage':(data_frame.isnull().sum()[data_frame.isnull().sum()>0]/data_frame.shape[0])*100}).to_string(), "\n")

    # print null data
    print("---before imputation with median values for their respective cols---\n", data_frame.isnull().sum())

    # loop through each col and impute missing values using mean, median or mode
    # if the group_by_cols are > 0 then impute the missing values based on the group_by_cols
    # otherwise impute the missing values based on the col_name
    for col_name in impute_cols:
        
        if(impute_method == "mean"):
            with_value = data_frame[col_name].mean()
        elif(impute_method == "median"):
            with_value = data_frame[col_name].median()
        elif(impute_method == "mode"):
            with_value = data_frame[col_name].mode()[0]
        
        if(len(group_by_cols) > 0):
            data_frame[col_name] = data_frame.groupby(group_by_cols, group_keys=False)[col_name].loc[data_frame[col_name] == replace_value] = with_value
        else:
            data_frame[col_name].loc[data_frame[col_name] == replace_value] = data_frame[col_name].median()
                
    print()
    print("---count/percentage of null values after imputation on df")
    print(pd.DataFrame({'Count':data_frame.isnull().sum()[data_frame.isnull().sum()>0],
                        'Percentage':(data_frame.isnull().sum()[data_frame.isnull().sum()>0]/data_frame.shape[0])*100}).to_string(), "\n")

    # print current summary of the data and the null values sums
    print("---after imputation with median values for their respective cols---\n", data_frame.isnull().sum())

    return data_frame

# function to compute adjusted R-squared
def adj_r2_score(predictors, targets, predictions):
    r2 = r2_score(targets, predictions)
    n = predictors.shape[0]
    k = predictors.shape[1]
    return 1 - ((1 - r2) * (n - 1) / (n - k - 1))

# function to compute MAPE
def mape_score(targets, predictions):
    return np.mean(np.abs(targets - predictions) / targets) * 100

# treats outliers for a feature/col based on IQR method
# if we have items in the skip cols list, those cols will not be treated
def treat_outliers(data_frame, skip_col_list=[]):

    # represents all numeric types.
    numerical_col = data_frame.select_dtypes(include=np.number).columns.tolist()

    # loop over the col_list and for each col, get the IQR and upper and lower whiskers
    # and then apply the IQR method by using the clip function of NumPy to cap the outliers
    for col_name in numerical_col:
        
        # skip over this col if it is in the skip_col_list
        if(col_name in skip_col_list):
            continue
        
        # 25th quantile/ 1st quartile
        Q1 = data_frame[col_name].quantile(0.25)
        
        # 75th quantile/ 3rd quartile
        Q3 = data_frame[col_name].quantile(0.75)
        
        # Inter Quantile Range (75th perentile - 25th percentile)
        IQR = Q3 - Q1
        
        # Generally, a value of 1.5 * IQR is taken to cap the values of outliers to upper and lower whiskers 
        # but any number (example 0.5, 2, 3, etc) other than 1.5 can be chosen.
        lower_whisker = Q1 - 1.5 * IQR
        upper_whisker = Q3 + 1.5 * IQR

        # all the values smaller than lower_whisker will be assigned the value of lower_whisker
        # all the values greater than upper_whisker will be assigned the value of upper_whisker
        # the assignment will be done by using the clip function of NumPy
        data_frame[col_name] = np.clip(data_frame[col_name], lower_whisker, upper_whisker)

    # return the dataframe
    return data_frame

# creates train/test or train/validation/test data sets using the different percentage splits for train, validation and test
# also adds an intercept col if the user wants and dummy cols if the user wants
# if also creates dummy vars if needed
# return the train/test or train/validation/test dataframes to caller
def create_train_test_sets(
    data_frame, 
    dependent_col_name, 
    add_y_intercept=True, 
    add_dummy_cols=True, 
    train_test_type="train_test", 
    temp_test_split=0.20, 
    train_validation_split=0.25, 
    random_state=1):
    
    # specifying the independent and dependent variables
    x = data_frame.drop([dependent_col_name], axis=1)
    y = data_frame[dependent_col_name]

    # only if we want to add an intercept
    if(add_y_intercept):
        # adding a constant to the independent variables
        x = sm.add_constant(x)

    # only if we want to add dummy cols
    if(add_dummy_cols):
        # creating dummy variables for categorical with 1 hot enconding approach
        # this will grab any cols types that are object or category types and create dummy cols for them and 
        # drop the first col from that 1 hot encoding based on alphabetical order.
        x = pd.get_dummies(
                x,
                columns=x.select_dtypes(include=["object", "category"]).columns.tolist(),
                drop_first=True,
                dtype='int' # convert all the dummy boolean(T/F) cols to int(1/0) cols
        )

    if(train_test_type == "train_test"):
        
        # Splitting data into training and test set:

        # first we split data into 2 parts, say train and test
        # we also want to keep the same distrubution of classes in y, so we use stratify with the y var for the split        
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=temp_test_split, random_state=random_state, stratify=y)
        
        # print shape of train and test data sets, and confirm that all the classes are balanced after the split
        print(x_train.shape, x_test.shape)

        # return the train and test sets
        return x_train, x_test, y_train, y_test, x, y
        
    elif(train_test_type == "train_validation_test"):
        
        # Splitting data into training, validation and test set:

        # first we split data into 2 parts, say temporary and test
        # we also want to keep the same distrubution of classes in y, so we use stratify with the y var for the split
        x_temp, x_test, y_temp, y_test = train_test_split(x, y, test_size=temp_test_split, random_state=random_state, stratify=y)

        # then we split the temporary set into train and validation
        # to keep the same distribution as temp y set, we use statify to be y_temp
        x_train, x_val, y_train, y_val = train_test_split(x_temp, y_temp, test_size=train_validation_split, random_state=random_state, stratify=y_temp)

        # print shape of train, validation and test data sets, and confirm that all the classes are balanced after the split
        print(x_train.shape, x_val.shape, x_test.shape)

        # return the train and test sets
        return x_train, x_val, x_test, y_train, y_val, y_test, x, y

# we will define a function to check VIF
def checking_vif(predictors):
    
    vif = pd.DataFrame()
    vif["feature"] = predictors.columns

    # calculating VIF for each feature
    vif["VIF"] = [
        variance_inflation_factor(predictors.values, i)
        for i in range(len(predictors.columns))
    ]
    
    return vif

# Checking the effect of dropping the columns showing high multicollinearity on model performance (adj. R-squared and RMSE)
def treating_multicollinearity(predictors, target, high_vif_columns):

    # empty lists to store adj. R-squared and RMSE values
    adj_r2 = []
    rmse = []

    # build ols models by dropping one of the high VIF columns at a time
    # store the adjusted R-squared and RMSE in the lists defined previously
    for cols in high_vif_columns:
        
        # defining the new train set
        train = predictors.loc[:, ~predictors.columns.str.startswith(cols)]

        # create the model
        olsmodel = sm.OLS(target, train).fit()

        # adding adj. R-squared and RMSE to the lists
        adj_r2.append(olsmodel.rsquared_adj)
        rmse.append(np.sqrt(olsmodel.mse_resid))

    # creating a dataframe for the results
    temp = pd.DataFrame(
        {
            "col": high_vif_columns,
            "Adj. R-squared after_dropping col": adj_r2,
            "RMSE after dropping col": rmse,
        }
    ).sort_values(by="Adj. R-squared after_dropping col", ascending=False)
    
    temp.reset_index(drop=True, inplace=True)

    return temp

def drop_high_p_values(x_train, y_train):
    
    # initial list of columns
    predictors = x_train.copy()
    cols = predictors.columns.tolist()

    # setting an initial max p-value
    max_p_value = 1

    while len(cols) > 0:
        
        # defining the train set
        x_train_aux = predictors[cols]

        # fitting the model
        model = sm.OLS(y_train, x_train_aux).fit()

        # getting the p-values and the maximum p-value
        p_values = model.pvalues
        max_p_value = max(p_values)

        # name of the variable with maximum p-value
        feature_with_p_max = p_values.idxmax()

        if max_p_value > 0.05:
            cols.remove(feature_with_p_max)
        else:
            break

    selected_features = cols
    print(selected_features)
    
    return selected_features

# get the optimal threshold as per AUC-ROC curve    
def optimal_threshold_using_auc_roc_curve(model, predictors, target):

    # Optimal threshold as per AUC-ROC curve
    fpr, tpr, thresholds = roc_curve(target, model.predict(predictors))

    # The optimal cut off would be where tpr is high and fpr is low
    optimal_idx = np.argmax(tpr - fpr)
    optimal_threshold_auc_roc = thresholds[optimal_idx]
    print("optimal_threshold_auc_roc: ", optimal_threshold_auc_roc)
    
    return optimal_threshold_auc_roc

# KNN Imputation with KNNImputer and reverse encoding
# for this imputer approach we need to encode the categorical data back to its original form
# after imputation
def knn_imputation_processing(data_frame, reqd_col_for_impute, dict_reverse_mapping, col_to_reverse_map, n_neighbors=5):

    # Checking that no column has missing values in train, validation or test sets
    print("---Before Data Frame Imputation KNN---")
    print(data_frame.isna().sum())
    print("-" * 30)
    print()
    
    # defining the KNN imputer
    imputer = KNNImputer(n_neighbors=n_neighbors)

    # Fit and transform the train data
    data_frame[reqd_col_for_impute] = imputer.fit_transform(data_frame[reqd_col_for_impute])
    
    # inverse the encoding
    inv_dict = {v: k for k, v in dict_reverse_mapping.items()}
    data_frame[col_to_reverse_map] = np.round(data_frame[col_to_reverse_map]).map(inv_dict).astype("category")
    
    print("---After Data Frame Imputation KNN---")
    print(data_frame.isna().sum())
    print("-" * 30)
    print()
    
    return data_frame

# feature scaling using passed in scalar obj and return the scaled dataframe using the original dataframe
def feature_scaling(data_frame, scaler_obj):
    
    # selecting numerical columns
    num_col = data_frame.select_dtypes(include=np.number).columns.tolist()

    # scaling the dataset before clustering
    subset = data_frame[num_col].copy()
    subset_scaled = scaler_obj.fit_transform(subset)

    # creating a dataframe of the scaled columns
    subset_scaled_df = pd.DataFrame(subset_scaled, columns=subset.columns)

    # return the scaled dataframe
    return subset_scaled_df, num_col
