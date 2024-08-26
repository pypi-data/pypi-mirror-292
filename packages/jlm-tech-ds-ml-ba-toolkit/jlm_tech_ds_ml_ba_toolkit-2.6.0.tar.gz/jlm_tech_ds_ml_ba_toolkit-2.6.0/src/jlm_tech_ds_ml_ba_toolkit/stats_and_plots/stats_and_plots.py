
from jlm_tech_ds_ml_ba_toolkit.ml_utils import send_to_output
import numpy as np
import pandas as pd
import seaborn as sns
from dateutil.parser import parse

# for visualizing data
import matplotlib.pyplot as plt
import seaborn as sns

# check if a column is numeric
from pandas.api.types import is_numeric_dtype

# To get diferent metric scores for logistic regression model
from sklearn.metrics import (
    roc_auc_score,
    precision_recall_curve,
    roc_curve
)

from sklearn import tree

# to compute distances
from scipy.spatial.distance import pdist

# to perform hierarchical clustering, compute cophenetic correlation, and create dendrograms
from scipy.cluster.hierarchy import dendrogram, linkage, cophenet

# to perform t-SNE
from sklearn.manifold import TSNE

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

# function to create labeled barplots for categorical variables for either percentage or count
def bar_plot_helper(data_frame, col_name, use_x_axis, x_axis_num, y_axis_num, perc=False):
    
    # length of the column and the number of unique values
    total = len(data_frame[col_name])
    
    plt.figure(figsize=(x_axis_num, y_axis_num))
    plt.xticks(rotation=90)
    
    if(use_x_axis == True):
        ax = sns.countplot(
            data=data_frame,
            x=col_name,
            palette="Paired",
            order=data_frame[col_name].value_counts().index[:None],
        )
    else:
        ax = sns.countplot(
            data=data_frame,
            y=col_name,
            palette="Paired",
            order=data_frame[col_name].value_counts().index[:None],
        )

    for p in ax.patches:
        
        # percentage of each class of the category
        if perc == True:
            label = "{:.1f}%".format(
                100 * p.get_height() / total
            )
        else:
            # count of each level of the category
            label = p.get_height()

        # width of the plot
        x = p.get_x() + p.get_width() / 2
        
        # height of the plot
        y = p.get_height()

        # annotate the percentage
        ax.annotate(
            label,
            (x, y),
            ha="center",
            va="center",
            size=12,
            xytext=(0, 5),
            textcoords="offset points",
        )

    # show the plot
    plt.show()

# function to perform stats processing
def perform_stats_processing(file_name, data_frame, tmp_col_list, include_col_name_list):
    
    print("perform_stats_processing")
    
    # Open a file to save statistics to
    fo = open(file_name, "w")
    
    # convert all the object type columns to category types
    # to save on memory since catergories don't take much space compared to object
    for col_name in data_frame.select_dtypes(include=np.object_).columns:
        data_frame[col_name] = data_frame[col_name].astype("category")

    send_to_output("---Statistical Summary of the Data frame provided---\n\n", fo)
    send_to_output("---first 5 rows of the data frame---\n", fo)
    send_to_output(data_frame.head().to_string()+"\n", fo)
    send_to_output("\n\n", fo)
    fo.flush()
    
    send_to_output("---last 5 rows of the data frame---\n", fo)
    send_to_output(data_frame.tail().to_string()+"\n", fo)
    send_to_output("\n\n", fo)
    fo.flush()
    
    send_to_output("---row/col dimensions of data frame---\n", fo)
    shape_str = "rows = " + str(data_frame.shape[0])+ ' and cols = '+ str(data_frame.shape[1]) +"\n"
    send_to_output(shape_str, fo)
    send_to_output("\n\n", fo)
    fo.flush()
    
    send_to_output("---info about data frame---\n", fo)
    data_frame.info(buf=fo)
    data_frame.info()
    send_to_output("\n\n", fo)
    fo.flush()
    
    # view the data the vertical with cols as stats and rows as data frame cols for numeric
    send_to_output("---box plot statistics about data frame numeric cols---\n", fo)
    send_to_output(data_frame.describe(include=np.number).T.to_string()+"\n", fo)
    send_to_output("\n\n", fo)
    fo.flush()
    
    # view the data the vertical with cols as stats and rows as data frame cols for non numeric
    send_to_output("---box plot statistics about data frame categorical cols---\n", fo)
    send_to_output(data_frame.describe(exclude=np.number).T.to_string()+"\n", fo)
    send_to_output("\n\n", fo)
    fo.flush()
    
    send_to_output("---list of cols for this data frame---\n", fo)
    send_to_output(str(data_frame.columns)+"\n", fo)
    send_to_output("\n\n", fo)
    fo.flush()
    
    # view all unique data items for each col and the count of data items in the cols
    send_to_output("---unique and nunique items info about data frame per col---\n", fo)
    
    for col_name in tmp_col_list:
        for config_col in include_col_name_list:
            
            # only process the cols we want to use
            if(col_name == config_col):
                send_to_output("unique col = " + config_col + "\n", fo)
                send_to_output(str(data_frame[config_col].unique()), fo)
                send_to_output("\n\n", fo)
                fo.flush()
                
                send_to_output("nunique col = " + config_col + "\n", fo)
                send_to_output(str(data_frame[config_col].nunique()), fo)
                send_to_output("\n\n", fo)
                fo.flush()
    
    # check for how much data is null.
    send_to_output("---display any null data summary for all the cols in df---\n", fo)
    send_to_output(data_frame.isnull().sum().to_string()+"\n", fo)
    send_to_output("\n\n", fo)
    fo.flush()
    
    send_to_output("---display any null data summary for only null cols in df---\n", fo)
    # let's check for missing values in the data and only display cols where null sum > 0
    nullseries = data_frame.isna().sum()
    
    # convert series to string for only the cols with null values count > 0
    nullseries_str = str(nullseries[nullseries > 0])
    send_to_output(nullseries_str+"\n", fo)
    send_to_output("\n\n", fo)
    fo.flush()
    
    # check for duplicated data entries
    send_to_output("---duplicate data summary---\n", fo)
    send_to_output(str(data_frame.duplicated().sum())+"\n", fo)
    send_to_output("\n\n", fo)
    fo.flush()
    
    # create dictionary for null data based on %
    send_to_output("---create statistics on null data for potential imputation---\n", fo)
    send_to_output(
        pd.DataFrame
        (
            {
                'Count':data_frame.isnull().sum()[data_frame.isnull().sum()>0],
                'Percentage':(data_frame.isnull().sum()[data_frame.isnull().sum()>0]/data_frame.shape[0])*100
            }
        ).to_string()+"\n", fo
    )
    
    send_to_output("\n\n", fo)
    fo.flush()

    # Close opened file
    fo.close()
    
# univariate analysis for 1D plots
def display_1D_plots(data_frame, include_plot_list, tmp_col_list, exclude_list_numeric, exclude_list_categorical, numeric_cols, categorical_cols,x_axis_num, y_axis_num):
    
    print("display_1D_plots")

    """
    univariate analysis => view freq and basic statistics of the data use per col of data frame using
                    [
                        histogram, (numeric)
                        boxplot    (numeric)
                        distplot   (numeric)
                        countplot[barplot]  (categorical)
                    ]
    """    
    for plot_obj in include_plot_list:

        plot_name = plot_obj["plot_name"]
        use_col_name_list_pref = plot_obj["use_col_name_list_pref"]

        # dynamic plotting of histogram, boxplot
        for col_name in tmp_col_list:
            for config_col in use_col_name_list_pref:
                
                # only process the cols we want to use
                if(col_name == config_col["col_name"]):
            
                    # skip if we are in the exclusion list for numeric or categorical
                    if( (col_name in exclude_list_numeric) or (col_name in exclude_list_categorical) ):
                        continue
            
                    # display histogram from this col
                    if("histogram" == plot_name and col_name in numeric_cols):
                        
                        if(config_col["use_x_axis"] == True):
                            plt.figure(figsize=(x_axis_num, y_axis_num))
                            sns.histplot(data=data_frame, x=col_name, kde=True)
                            
                            # if the col is numeric then add the mean and median lines to plot
                            if(is_numeric_dtype(data_frame[col_name])):
                                plt.axvline(data_frame[col_name].mean(), color='green', linestyle='--')
                                plt.axvline(data_frame[col_name].median(), color="black", linestyle="-")
                            
                            plt.xticks(rotation=90)
                            plt.xlabel(col_name)
                            plt.ylabel('Frequency')
                            plt.title("Histogram: "+str(col_name))
                            plt.tight_layout()
                            plt.show()
                        else:
                            plt.figure(figsize=(y_axis_num, x_axis_num))
                            sns.histplot(data=data_frame, y=col_name, kde=True)
                            
                            # if the col is numeric then add the mean and median lines to plot
                            if(is_numeric_dtype(data_frame[col_name])):
                                plt.axvline(data_frame[col_name].mean(), color='green', linestyle='--')
                                plt.axvline(data_frame[col_name].median(), color="black", linestyle="-")

                            # plt.xticks(rotation=90)
                            plt.xlabel('Frequency')
                            plt.ylabel(col_name)
                            plt.title("Histogram: "+str(col_name))
                            plt.tight_layout()
                            plt.show()
                        
                    # display box plot for this col
                    elif("boxplot" == plot_name and col_name in numeric_cols):
                        
                        if(config_col["use_x_axis"] == True):
                            plt.figure(figsize=(x_axis_num, y_axis_num))
                            sns.boxplot(data=data_frame, x=col_name, showmeans=True, color="violet")
                            plt.xticks(rotation=90)
                            plt.xlabel(col_name)
                            plt.title("BoxPlot: "+str(col_name))
                            plt.tight_layout()
                            plt.show()
                        else:
                            plt.figure(figsize=(y_axis_num, x_axis_num))
                            sns.boxplot(data=data_frame, y=col_name, showmeans=True, color="violet")
                            # plt.xticks(rotation=90)
                            plt.ylabel(col_name)
                            plt.title("BoxPlot: "+str(col_name))
                            plt.tight_layout()
                            plt.show()
                            
                    # display distributionplot for this col
                    elif("displot" == plot_name and col_name in numeric_cols):
                        
                        if(config_col["use_x_axis"] == True):
                            plt.figure(figsize=(x_axis_num, y_axis_num))
                            sns.displot(data=data_frame, x=col_name, kde=True)
                            plt.xticks(rotation=90)
                            plt.xlabel(col_name)
                            plt.title("DisPlot: "+str(col_name))
                            plt.tight_layout()
                            plt.show()
                        else:
                            plt.figure(figsize=(y_axis_num, x_axis_num))
                            sns.displot(data=data_frame, y=col_name, kde=True)
                            # plt.xticks(rotation=90)
                            plt.ylabel(col_name)
                            plt.title("DisPlot: "+str(col_name))
                            plt.tight_layout()
                            plt.show()
                        
                    # display count plot for this col
                    if("countplot" == plot_name and (col_name in categorical_cols or col_name in numeric_cols)):
                        
                        # bar plot helper to display percentage for each category
                        bar_plot_helper(data_frame, col_name, config_col["use_x_axis"], x_axis_num, y_axis_num, perc=True)    

# bivariate analysis with diff types of 2D plots
def display_2D_plots(data_frame, numeric_cols, exclude_list_numeric, include_plot_list, tmp_col_list, categorical_cols, exclude_list_categorical,  x_axis_num, y_axis_num):
    
    print("display_2D_plots")

    """
    bivariate analysis => to view correlation between 2 vars in data use
                        [
                            jointplot (numeric(x) vs numeric(y)),
                            lmplot (numeric(x) vs numeric(y))
                        ]
    """
    
    # used to remove combination of cols for optimal performance
    # only allowing permutations of 2 cols
    hash_table = {}
    
    for col_name_x in numeric_cols:
        
        # skip if we are in the exclusion list
        if(col_name_x in exclude_list_numeric):
            continue
            
        for col_name_y in numeric_cols:
            
            # skip if we are in the exclusion list
            if(col_name_y in exclude_list_numeric):
                continue
            
            # skip if the same col name is on that iteration for outer/inner loops
            if(col_name_x == col_name_y):
                continue
            
            for plot_obj in include_plot_list:
                plot_name = plot_obj["plot_name"]
                use_col_name_list_pref = plot_obj["use_col_name_list_pref"]
                
                for config_col in use_col_name_list_pref:
                
                    # only process the cols we want to use
                    if(col_name_x == config_col["col_name"]):
            
                        # create key1/2
                        key1 = col_name_x.strip() + col_name_y.strip() + plot_name.strip()
                        key2 = col_name_y.strip() + col_name_x.strip()+ plot_name.strip()
                        
                        # if we have the key in the hash table then skip the plot for either key
                        if( (key1 in hash_table) or (key2 in hash_table) ):
                            continue
                        else:
                            # update the HT to show that we have processed this key
                            hash_table[key1] = 1
                            hash_table[key2] = 1
                        
                        # only display if the plot is in the plot list
                        if("jointplot" == plot_name):
                            sns.jointplot(data=data_frame, x=col_name_x, y=col_name_y, kind="reg")
                            plt.title("JointPlot")
                            plt.tight_layout()
                            plt.show()
                            break
                        
                        # only display if the plot is in the plot list
                        elif("lmplot" == plot_name):
                            sns.lmplot(data=data_frame, x=col_name_x, y=col_name_y)
                            plt.title("LmPlot")
                            plt.tight_layout()
                            plt.show()
                            break

    # clear the hash table
    hash_table.clear()

    """
    if we ever need to specify the specific x axis use these processing
    bivariate analysis => to view correlation between 2 vars in data use
                        [
                            lineplot (numeric(x) vs numeric(y))
                        ]
    """
    
    # loop over the plot list
    for plot_obj in include_plot_list:
        
        # get the plot name
        plot_name = plot_obj["plot_name"]
        use_col_name_list_pref = plot_obj["use_col_name_list_pref"]

        if("lineplot" == plot_name):
            
            for col_name in tmp_col_list:
                for config_col in use_col_name_list_pref:

                    # only process the cols we want to use
                    if(col_name == config_col["col_name"]):
            
                        # get the x axis col list
                        x_axis_col_list = plot_obj["x_axis_col_list"]
                        
                        # loop over the x axis col list
                        for x_axis_col in x_axis_col_list:
                                
                            # skip if we are in the exclusion list
                            if( (col_name in exclude_list_numeric) or (col_name in exclude_list_categorical) ):
                                continue
                            
                            # skip if the same col name is on that iteration loop
                            elif (x_axis_col == col_name):
                                continue
                            
                            # create key1/2
                            key1 = x_axis_col.strip() + col_name.strip() + plot_name.strip()
                            key2 = col_name.strip() + x_axis_col.strip()+ plot_name.strip()
                            
                            # if we have the key in the hash table then skip the plot for either key
                            if( (key1 in hash_table) or (key2 in hash_table) ):
                                continue
                            else:
                                # update the HT to show that we have processed this key
                                hash_table[key1] = 1
                                hash_table[key2] = 1
                            
                            # plot the line plot
                            sns.lineplot(data = data_frame , x = x_axis_col , y = col_name, ci = False)
                            plt.xlabel(x_axis_col)
                            plt.ylabel(col_name)
                            plt.title("LinePlot")
                            plt.tight_layout()
                            plt.show()
                            break
    
    # clear the hash table
    hash_table.clear()
        
    """
    bivariate analysis => to view correlation between 2 vars in data use
                        [
                            stackbarchart (categorical(x) vs categorical(y))
                        ]
    """
    for col_name_x in categorical_cols:
        
        # skip if we are in the exclusion list
        if(col_name_x in exclude_list_categorical):
            continue
        
        for col_name_y in categorical_cols:
            
            # skip if we are in the exclusion list
            if(col_name_y in exclude_list_categorical):
                continue
            
            # skip if the same col name is on that iteration for outer/inner loops
            if(col_name_x == col_name_y):
                continue
                            
            for plot_obj in include_plot_list:
                plot_name = plot_obj["plot_name"]
                
                if("stackbarchart" == plot_name):
                    
                    use_col_name_list_pref = plot_obj["use_col_name_list_pref"]
                    for col_name_obj in use_col_name_list_pref:
                        
                        # only allow for the col_name in the list
                        if(col_name_x == col_name_obj["col_name"]):
                            
                            # if we want to skip the col_name for y(hue) then check for it
                            if(col_name_y == col_name_obj["skip_y"]):
                                continue
                            
                            else:
                                
                                # create key1/2
                                key1 = col_name_x.strip() + col_name_y.strip() + plot_name.strip()
                                key2 = col_name_y.strip() + col_name_x.strip()+ plot_name.strip()
                                
                                # if we have the key in the hash table then skip the plot for either key
                                if( (key1 in hash_table) or (key2 in hash_table) ):
                                    continue
                                else:
                                    # update the HT to show that we have processed this key
                                    hash_table[key1] = 1
                                    hash_table[key2] = 1
                                
                                # only display if the plot is in the plot list
                                pd.crosstab(data_frame[col_name_x], data_frame[col_name_y], normalize="index").plot(kind='bar',stacked=True)
                                plt.title("StackBarChart")
                                plt.tight_layout()
                                plt.show()
                                break
    
    # clear the hash table
    hash_table.clear()
                
    """
    bivariate analysis => to view correlation between 2 vars in data use
                        [
                            catplot         (categorical(x) vs numeric(y))
                            boxplot         (categorical(x) vs numeric(y))
                        ]
    """
    for col_name_x in categorical_cols:
        
        # # skip the displaying if the col is in the exclusion list
        if(col_name_x in exclude_list_categorical):
            continue
        
        for col_name_y in numeric_cols:
            
            # skip if the same col name is on that iteration for outer/inner loops
            if(col_name_y in exclude_list_numeric):
                continue
            
            for plot_obj in include_plot_list:
                plot_name = plot_obj["plot_name"]
                use_col_name_list_pref = plot_obj["use_col_name_list_pref"]
            
                # create key1/2
                key1 = col_name_x.strip() + col_name_y.strip() + plot_name.strip()
                key2 = col_name_y.strip() + col_name_x.strip()+ plot_name.strip()
                
                # if we have the key in the hash table then skip the plot for either key
                if( (key1 in hash_table) or (key2 in hash_table) ):
                    continue
                else:
                    # update the HT to show that we have processed this key
                    hash_table[key1] = 1
                    hash_table[key2] = 1
            
                if("catplot" == plot_name):
                    for config_col in use_col_name_list_pref:
                
                        # only process the cols we want to use
                        if(col_name_x == config_col["col_name"]):
                            if(config_col["use_x_axis_2D"] == True):
                                sns.catplot(data=data_frame, x=col_name_x, y=col_name_y)
                                plt.title("CatPlot")
                                plt.xticks(rotation=90)
                                plt.tight_layout()
                                plt.show()
                                
                            else:
                                sns.catplot(data=data_frame, x=col_name_y, y=col_name_x)
                                plt.title("CatPlot")
                                # plt.xticks(rotation=90)
                                plt.tight_layout()
                                plt.show()
                
                elif("boxplot2D" == plot_name):
                    for config_col in use_col_name_list_pref:
                
                        # only process the cols we want to use
                        if(col_name_x == config_col["col_name"]):
                            if(config_col["use_x_axis_2D"] == True):
                                plt.figure(figsize=(x_axis_num, y_axis_num))
                                sns.boxplot(data=data_frame, x=col_name_x, y=col_name_y, showmeans=True, color="violet")
                                # plt.xticks(rotation=90)
                                plt.xlabel(col_name_x)
                                plt.ylabel(col_name_y)
                                plt.title("2D BoxPlot")
                                plt.tight_layout()
                                plt.show()
                                
                            else:
                                plt.figure(figsize=(x_axis_num, y_axis_num))
                                sns.boxplot(data=data_frame, x=col_name_y, y=col_name_x, showmeans=True, color="violet")
                                # plt.xticks(rotation=90)
                                plt.xlabel(col_name_y)
                                plt.ylabel(col_name_x)
                                plt.title("2D BoxPlot")
                                plt.tight_layout()
                                plt.show()
    
# display correlation plots for bivariate analysis
def display_correlation_matrix(data_frame, exclude_list_numeric):
    
    print("display_correlation_matrix")
    
    # drop not needed cols to be used in pair plot and heat map
    data_frame = data_frame.drop(exclude_list_numeric, axis=1)
    
    # get numeric cols from new data frame w/o the excluded cols
    numeric_cols_dropped_df = data_frame.select_dtypes(include=np.number)

    # view all numeric type cols as a pair plot. only view lower diagonal of plot
    sns.pairplot(data=data_frame, diag_kind='kde', vars=numeric_cols_dropped_df, corner=True)
    # sns.pairplot(data=data_frame, vars=numeric_cols_dropped_df)
    plt.show()
            
    # view all numeric type cols as a heatmap
    # specify size of heatmap
    heatmap_x_axis_num = 15
    heatmap_y_axis_num = 10
    heatmap_linewidths = .3
    
    # applying mask to just view diagonal of heat map
    mask = np.triu(np.ones_like(numeric_cols_dropped_df.corr()))
    
    fig, ax = plt.subplots(figsize=(heatmap_x_axis_num, heatmap_y_axis_num))
    sns.heatmap(data=numeric_cols_dropped_df.corr(numeric_only=True), vmin=-1,vmax=1, annot=True, linewidths=heatmap_linewidths, mask=mask)
    plt.title("HeatMap")
    plt.show()
    
# this func will save the statistics to an output file and plot numerous variables across 1D and 2D
# plots as well as correlation matrix info
def getStatisticsAndInfoOnDataSets(
    data_frame, 
    file_name="tmp_statistics.txt",
    config_object=None
    ):
    
    # list of cols from data frame
    tmp_col_list = data_frame.columns
    
    # get the data for the cols and prefs
    include_col_name_list = config_object["include_col_name_list"]
    
    # cols thats are either int/floats and only get the cols names
    numeric_cols = data_frame.select_dtypes(include=np.number).columns
    
    # cols that are of type object(string..etc) and only get the cols names
    # categorical_cols = data_frame.select_dtypes([np.object_, np.category]).columns
    categorical_cols = data_frame.select_dtypes(include=["object", "category"]).columns
    
    # used for sizing of plot on screen
    x_axis_num = 20
    y_axis_num = 7
    
    # list of objs that contain the main grp of plots with cols to plot    
    include_plot_list = config_object["include_plot_list"]
    
    # 2 lists that help with excluding numeric or catergorical cols as needed from config obj
    exclude_list_categorical = config_object["exclude_list_categorical"]
    exclude_list_numeric = config_object["exclude_list_numeric"]

    # get vars to enable or disable processing
    enable_stats_processing = config_object["enable_stats_processing"]
    if(enable_stats_processing == True):

        # perform stats processing
        perform_stats_processing(file_name, data_frame, tmp_col_list, include_col_name_list)

    enable_1D_plot_processing = config_object["enable_1D_plot_processing"]
    if(enable_1D_plot_processing == True):

        # display 1D plots processing
        display_1D_plots(data_frame, include_plot_list, tmp_col_list, exclude_list_numeric, exclude_list_categorical, numeric_cols, categorical_cols,x_axis_num, y_axis_num)
    
    enable_2D_plot_processing = config_object["enable_2D_plot_processing"]    
    if(enable_2D_plot_processing == True):

        # display 2D plots processing
        display_2D_plots(data_frame, numeric_cols, exclude_list_numeric, include_plot_list, tmp_col_list, categorical_cols, exclude_list_categorical,  x_axis_num, y_axis_num)
    
    enable_numeric_processing = config_object["enable_numeric_processing"]
    if(enable_numeric_processing == True):
        
        # display correlation plots
        display_correlation_matrix(data_frame, exclude_list_numeric)

# this function is used to display outliers
def display_outliers(data_frame, num_cols, x_axis_num, y_axis_num):
    
    # get only numeric type cols
    num_cols_list = data_frame.select_dtypes(include=np.number).columns
    
    # calculate number of rows
    num_rows = int(len(num_cols_list) / num_cols + 1)

    # used for sizing of plot on screen
    plt.figure(figsize=(x_axis_num, y_axis_num))

    # display boxplots before treatment
    for i, variable in enumerate(num_cols_list):

        plt.subplot(num_rows, num_cols, i + 1)
        sns.boxplot(data=data_frame, x=variable, showmeans=True, color="violet")
        plt.tight_layout()

    plt.show()

# this will plot ROC curve and ROC AUC using auc_score and roc_curve(fpr,tpr)
def plot_roc_curve_and_roc_auc(model, predictors, target):
    
    logit_roc_auc_train = roc_auc_score(target, model.predict(predictors))
    fpr, tpr, thresholds = roc_curve(target, model.predict(predictors))
    
    plt.figure(figsize=(7, 5))
    plt.plot(fpr, tpr, label="Logistic Regression (area = %0.2f)" % logit_roc_auc_train)
    plt.plot([0, 1], [0, 1], "r--")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Receiver operating characteristic")
    plt.legend(loc="lower right")
    plt.show()

# plot the precision and recall curve
def precision_recall_curve_plot(model, predictors, target):
    
    # get predicted score using the model
    y_scores = model.predict(predictors)
    
    # get the precisions, recalls, thresholds for the precision recall curve
    precisions, recalls, thresholds = precision_recall_curve(target, y_scores)

    # plot the precision and recall curve
    plt.plot(thresholds, precisions[:-1], "b--", label="precision")
    plt.plot(thresholds, recalls[:-1], "g--", label="recall")
    plt.xlabel("Threshold")
    plt.legend(loc="upper left")
    plt.ylim([0, 1])
    plt.figure(figsize=(10, 7))
    plt.show()

def plot_tree_and_bar_chart_for_feature_importance(model, x_train, plot_tree=False):
    
    # create feature names list from train cols
    feature_names = x_train.columns
    
    # finding the importance of each feature
    importances = model.feature_importances_
    
    # sorting the features based on their importance
    indices = np.argsort(importances)
    
    if(plot_tree == True):
        
        # set the figure size
        plt.figure(figsize=(20, 30))

        # plot the decision tree
        out = tree.plot_tree(
            model,
            feature_names=feature_names,
            filled=True,
            fontsize=9,
            node_ids=True,
            class_names=True,
        )
        
        # set border color of nodes to black
        for o in out:
            arrow = o.arrow_patch
            if arrow is not None:
                arrow.set_edgecolor("black")
                arrow.set_linewidth(1)
                
        plt.show()
    
        # Text report showing the rules of a decision tree
        print(tree.export_text(model, feature_names=feature_names, show_weights=True))
        print()
    
    # importance of features in the tree building
    # (The importance of a feature is computed as the (normalized) total reduction of the 
    # 'criterion' brought by that feature. It is also known as the Gini importance)
    print(pd.DataFrame(importances, columns=["Imp"], index=x_train.columns).sort_values(by="Imp", ascending=False))
    print()

    # sort feature importance in descending order
    # plot the feature importance
    plt.figure(figsize=(12, 30))
    plt.title("Feature Importances")
    plt.barh(range(len(indices)), importances[indices], color="violet", align="center")
    plt.yticks(range(len(indices)), [feature_names[i] for i in indices])
    plt.xlabel("Relative Importance")
    plt.show()

# display boxplots for each cluster for the scaled data set
def display_boxplot_for_each_cluster(data_frame, num_col, df_name, cluster_col_name):
    
    # we are doing a boxplot with x being cluster val and y being cols to view stats on these clusters
    plt.figure(figsize=(10, 30))
    plt.suptitle("Boxplot of "+df_name+" numerical variables for each cluster", fontsize=15)
    
    num_cols = 2
    num_rows = int(len(num_col)/num_cols)+1
    
    # create box plots for each cluster
    for i, variable in enumerate(num_col):
        plt.subplot(num_rows, num_cols, i + 1)
        sns.boxplot(data=data_frame, x=cluster_col_name, y=variable, showmeans=True, color="violet")

    plt.tight_layout(pad=2.0)
    plt.show()
    
# plot dendogram for distance/linkage methods
# capture the cophenetic correlation for different distance/linkage methods
def plot_dendogram_for_distance_linkage_methods(distance_metrics, linkage_methods, scaled_df):
    
    # Track the distance/linkage method and cophenetic correlation as a tuple of 3 items
    compare = []

    # Calculate the total number of plots
    total_plots = len(distance_metrics) * len(linkage_methods)
    
    # Determine the number of rows
    rows = total_plots
    
    # Use 1 column
    cols = 1

    # Increase the figure size to make the dendrograms larger
    # Increase height proportionally
    fig, axes = plt.subplots(rows, cols, figsize=(12, 7 * rows))
    fig.tight_layout(pad=3.0)

    # Add spacing between plots
    plt.subplots_adjust(hspace=0.5)

    # Ensure axes is an array
    if rows == 1:
        axes = [axes]

    plot_num = 0
    
    # Loop over each combination of distance metric and linkage method
    for dm in distance_metrics:
        for lm in linkage_methods:
            
            ax = axes[plot_num]
            plot_num += 1

            # Create linkage
            Z = linkage(scaled_df, metric=dm, method=lm)
            
            # Get the cophenetic correlation
            coph_corr, coph_dists = cophenet(Z, pdist(scaled_df))
            
            # Set plot params for dendogram
            ax.set_title("Distance: {}\nLinkage: {}\nCophenetic: {:.2f}".format(dm.capitalize(), lm.capitalize(), coph_corr))
            ax.set_xlabel('Sample Index')
            ax.set_ylabel('Distance')
            
            # Setup dendogram
            dendrogram(Z, ax=ax, leaf_rotation=90., color_threshold=40, leaf_font_size=8.)
            
            # Append create tuple of distance/linkage method and cophenetic correlation
            compare.append([dm, lm, coph_corr])
    
    plt.show()
    
    # Let's create a dataframe to compare cophenetic correlations for each linkage method
    df_cc = pd.DataFrame(compare, columns=["Distance_Metric", "Linkage_Method", "Cophenetic_Coefficient"])
    print("---Summary of Distance, Linkage, Cophenetic Correlation data frame---\n")
    print(df_cc.head())

# perform t-SNE and plot using different values of perplexity and scaled data frame in 2D
def plot_tsne_in_2D_with_different_perplexity(scaled_df, perplexity, class_type):

    # set figure size
    plt.figure(figsize=(20, 10))
    
    # loopping through different values of perplexity
    for i in range(len(perplexity)):
        
        # n_jobs specifies the number of parallel jobs to run
        # -1 means using all processors
        # -2 means using all processors except one
        tsne = TSNE(n_components=2, perplexity=perplexity[i], n_jobs=-1, random_state=1)
        
        X_red = tsne.fit_transform(scaled_df)
        red_data_df = pd.DataFrame(data=X_red, columns=["Component 1", "Component 2"])

        plt.subplot(2, int(len(perplexity) / 2), i + 1)

        plt.title("perplexity=" + str(perplexity[i]))
        sns.scatterplot(data=red_data_df, x="Component 1", y="Component 2", hue=class_type)
        plt.tight_layout(pad=2)
    
    plt.show()

# Function to plot distributions w.r.t target
def distribution_plot_wrt_target(data, predictor, target):

    fig, axs = plt.subplots(2, 2, figsize=(12, 10))

    target_uniq = data[target].unique()

    axs[0, 0].set_title("Distribution of target for target=" + str(target_uniq[0]))
    sns.histplot(
        data=data[data[target] == target_uniq[0]],
        x=predictor,
        kde=True,
        ax=axs[0, 0],
        color="teal",
    )

    axs[0, 1].set_title("Distribution of target for target=" + str(target_uniq[1]))
    sns.histplot(
        data=data[data[target] == target_uniq[1]],
        x=predictor,
        kde=True,
        ax=axs[0, 1],
        color="orange",
    )

    axs[1, 0].set_title("Boxplot w.r.t target")
    sns.boxplot(data=data, x=target, y=predictor, ax=axs[1, 0], palette="gist_rainbow")

    axs[1, 1].set_title("Boxplot (without outliers) w.r.t target")
    sns.boxplot(
        data=data,
        x=target,
        y=predictor,
        ax=axs[1, 1],
        showfliers=False,
        palette="gist_rainbow",
    )

    plt.tight_layout()
    plt.show()
