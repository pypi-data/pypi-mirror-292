
import numpy as np
import pandas as pd
import seaborn as sns

# for visualizing data
import matplotlib.pyplot as plt
import seaborn as sns

# To check model performance
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# import functions for model evaluation
from jlm_tech_ds_ml_ba_toolkit.ds_preprocessing_utils import adj_r2_score, mape_score

# To get diferent metric scores for logistic regression model
from sklearn.metrics import (
    f1_score,
    accuracy_score,
    recall_score,
    precision_score,
    confusion_matrix
)

# libraries to build logistic regression
from sklearn.linear_model import LogisticRegression

# Libraries to build decision tree classifier
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree

# To tune different models
from sklearn.model_selection import GridSearchCV

from sklearn.ensemble import BaggingClassifier
from sklearn.ensemble import RandomForestClassifier

# Libraries to import decision tree classifier and different ensemble classifiers
from sklearn.ensemble import AdaBoostClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.ensemble import StackingClassifier

# import support vector machine
from sklearn.svm import SVC

# To tune model, get different metric scores and split data
from sklearn.model_selection import StratifiedKFold, cross_val_score

# used for model evaluation
from sklearn import metrics

# To be used for tuning the model
from sklearn.model_selection import RandomizedSearchCV

# to compute distances
from scipy.spatial.distance import cdist

# to perform k-means clustering and compute silhouette scores
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# to compute distances
from scipy.spatial.distance import pdist, squareform

# to perform hierarchical clustering, compute cophenetic correlation, and create dendrograms
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import linkage, cophenet

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

# this will print the conclusion based on the p-value vs alpha(level of significance) for each test
def test_pvalue_with_alpha(p_value, alpha):
    # print the conclusion based on p-value
    if p_value < alpha:
        print(f'As the p-value {p_value} is less than the level of significance, we reject the null hypothesis.')
    else:
        print(f'As the p-value {p_value} is greater than the level of significance, we fail to reject the null hypothesis.')

    print()

# function to compute different metrics to check performance of a regression model
def model_performance_regression(model, predictors, target):

    # predicting using the independent variables
    pred = model.predict(predictors)

    r2 = r2_score(target, pred)  # to compute R-squared
    adjr2 = adj_r2_score(predictors, target, pred)  # to compute adjusted R-squared
    mse = mean_squared_error(target, pred) # to compute MSE
    rmse = np.sqrt(mse)  # to compute RMSE
    mae = mean_absolute_error(target, pred)  # to compute MAE
    mape = mape_score(target, pred)  # to compute MAPE

    # creating a dataframe of metrics
    df_perf = pd.DataFrame(
        {
            "MSE" : mse,
            "RMSE": rmse,
            "MAE": mae,
            "R-squared": r2,
            "Adj. R-squared": adjr2,
            "MAPE": mape,
        },
        index=[0],
    )

    return df_perf

# function to test for linearity, independence, normality and homoscedasticity
def test_for_linearity_and_independence_and_normality_and_homoscedasticity(x_train, y_train, model, alpha=0.05):
    
    # let us create a dataframe with actual, fitted and residual values
    df_pred = pd.DataFrame();

    df_pred["Actual Values"] = y_train;  # actual values
    df_pred["Fitted Values"] = model.fittedvalues;  # predicted values
    df_pred["Residuals"] = model.resid;  # residuals
    print(df_pred.head());
    
    # let's plot the fitted values vs residuals
    sns.residplot(
        data=df_pred, x="Fitted Values", y="Residuals", color="purple", lowess=True
    );
    
    plt.xlabel("Fitted Values");
    plt.ylabel("Residuals");
    plt.title("Fitted vs Residual plot");
    plt.show();
    
    # test for normality
    # histogram plot with kde for normality
    sns.histplot(data=df_pred, x="Residuals", kde=True);
    plt.title("Normality of residuals");
    plt.show();
    
    # Q-Q plot
    stats.probplot(df_pred["Residuals"], dist="norm", plot=pylab);
    plt.show();
    
    # run shapiro-wilks test on the residuals.
    stat, p_value = stats.shapiro(df_pred["Residuals"]);

    print("shapiro-wilks, stat:", stat);
    print("shapiro-wilks, p_value:", p_value);
    print();

    # check if we pass/fail H0 test for the shapiro-wilk test
    test_pvalue_with_alpha(p_value, alpha);
    print();

    # test for homoscedasticity
    # run goldfeldquandt test on df residuals with predictor df
    f_stats, p_value, status_str = sms.het_goldfeldquandt(df_pred["Residuals"], x_train);

    # print data from goldfeldquandt test
    print("goldfeldquandt, f_stat:", f_stats);
    print("goldfeldquandt, p_value:", p_value);
    print("goldfeldquandt, status_str", status_str);
    print();

    # check if we pass/fail H0 test goldfeldquandt test
    test_pvalue_with_alpha(p_value, alpha);

# defining a function to compute different metrics to check performance
# this handles either logistic regression/decision trees
# y_pred_option=1(logistic_regression), y_pred_option=2(decision_tree)
def model_performance_classification_summary(model, predictors, target, y_pred_option, threshold=0.5):

    # use threshold value to get y_pred
    if(y_pred_option == 1):

        # checking which probabilities are greater than threshold
        pred_temp = model.predict(predictors) > threshold
        
        # rounding off the above values to get classes
        pred = np.round(pred_temp)

    # get y_pred w/o threshold
    elif(y_pred_option == 2):

        # predicting using the independent variables
        pred = model.predict(predictors)

    # to compute Accuracy
    acc = accuracy_score(target, pred)
    
    # to compute Recall
    recall = recall_score(target, pred)
    
    # to compute Precision
    precision = precision_score(target, pred)
    
    # to compute F1-score
    f1 = f1_score(target, pred)

    # creating a dataframe of metrics
    df_perf = pd.DataFrame(
        {"Accuracy": acc, "Recall": recall, "Precision": precision, "F1": f1,},
        index=[0],
    )

    return df_perf

# To plot the confusion_matrix with percentages and labels for FP, FN, TP, and TN.
# y_pred_option=1(logistic_regression), y_pred_option=2(decision_tree)
def confusion_matrix_model_plot(model, predictors, target, y_pred_option, threshold=0.5):
    
    # use threshold value to get y_pred
    if(y_pred_option == 1):
        # checking which probabilities are greater than threshold
        y_pred = model.predict(predictors) > threshold

    # get y_pred w/o threshold
    elif(y_pred_option == 2):
        y_pred = model.predict(predictors)
    
    # create the confusion matrix for the predicted values
    cm = confusion_matrix(target, y_pred)

    # Define labels
    labels = np.asarray([
        [f"TN: {cm[0, 0]}\n{cm[0, 0] / cm.sum():.2%}", f"FP: {cm[0, 1]}\n{cm[0, 1] / cm.sum():.2%}"],
        [f"FN: {cm[1, 0]}\n{cm[1, 0] / cm.sum():.2%}", f"TP: {cm[1, 1]}\n{cm[1, 1] / cm.sum():.2%}"]
    ]).reshape(2, 2)

    # plot the confusion matrix with labels for FP, FN, TP, and TN
    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=labels, fmt="", cmap="Blues", annot_kws={"size": 12})
    plt.ylabel("True label")
    plt.xlabel("Predicted label")
    plt.title("Confusion Matrix with FP, FN, TP, and TN")
    plt.show()

# Converting coefficients from log(odds) and to find the odds, we have to take the exponential of the coefficients
# return a dataframe back
def convert_coefficient_to_odds_ratio(model, x_train):
    
    # get the corresponding coefficients from the model and the intercept
    coef_df = pd.DataFrame(
        np.append(model.coef_, model.intercept_),
        index=x_train.columns.tolist() + ["Intercept"],
        columns=["Coefficients"]
    )

    print(coef_df.T)
    print("-------------------")
    print()
    
    # converting coefficients to odds
    odds = np.exp(model.coef_[0])

    # finding the percentage change
    perc_change_odds = (np.exp(model.coef_[0]) - 1) * 100

    # adding the odds to a dataframe
    df_tmp = pd.DataFrame({"Odds": odds, "Change_odd%": perc_change_odds}, index=x_train.columns).T
    
    print("Log odds and Log odds perct:\n", df_tmp)
    print("-------------------")
    print()

# this will aggregate all models into 1 data frame for train/test review
def model_comparison(train_list_model_perfomance, test_list_model_perfomance, list_model_name_performance, print_result=False):
    
    # training performance comparison
    models_train_comp_df = pd.concat(train_list_model_perfomance, axis=1)
    models_train_comp_df.columns = list_model_name_performance
    
    # testing performance comparison
    models_test_comp_df = pd.concat(test_list_model_perfomance, axis=1)
    models_test_comp_df.columns = list_model_name_performance
    
    if(print_result):
        print("Training performance comparison:")
        print(models_train_comp_df.T)
        print()
        
        print("Test set performance comparison:")
        print(models_test_comp_df.T)
        print()
    
    return models_train_comp_df, models_test_comp_df

# evaluate the model performance by using StratifiedKFold and cross_val_score
# K-Folds cross-validation provides dataset indices to split data into train/validation sets. 
# Split dataset into k consecutive stratified folds (without shuffling by default).
# Each fold is then used once as validation while the k - 1 remaining folds form the training set.
def kfold_cross_validation(model, x_dataset, y_dataset, scoring_type, num_splits=5, shuffle=True, random_state=1):

    # we want to use stratified kfold to also keep the dist when we do the cross validation
    kfold = StratifiedKFold(n_splits=num_splits, shuffle=shuffle, random_state=random_state)

    # get the cross validation score, and use all available cores
    cv_result_bfr = cross_val_score(estimator=model, X=x_dataset, y=y_dataset, scoring=scoring_type, cv=kfold, n_jobs=-1)

    print("Cross Validation Scores: ", cv_result_bfr)
    
    # Plotting boxplots for CV scores of model defined above
    plt.boxplot(cv_result_bfr)
    plt.show()

# find the highest cophenetic correlation with its distance metric and linkage methods
def find_max_cophenetic_correlation(distance_metrics, linkage_methods, scaled_df):

    # track highest cophenet value
    high_cophenet_corr = 0

    # track which distance measure and linkage method provides highest cophenet
    high_dm_lm = [0, 0]

    # nested for loop to loop over each distance metric and for each metric
    # attempt each linkage method and get the cophenet values
    for dm in distance_metrics:
        for lm in linkage_methods:

            # create linkage for each distance/linkage method combo
            Z = linkage(scaled_df, metric=dm, method=lm)

            # get the cophenet corr metric and their distances
            c, coph_dists = cophenet(Z, pdist(scaled_df))
            print("Cophenetic correlation for {} distance and {} linkage is {}.".format(dm.capitalize(), lm, c))

            # save the max value cophenetic correlation of all the runs
            if c > high_cophenet_corr:
                high_cophenet_corr = c
                high_dm_lm[0] = dm
                high_dm_lm[1] = lm

    # printing the combination of distance metric and linkage method with the highest cophenetic correlation
    print()
    print("highest cophenetic correlation value",high_cophenet_corr, "with distance/linkage combo", high_dm_lm)

# calculate the distortion and silhouette score for different number of clusters
# also plot the distortion values and silhouette scores
def calc_kmeans_distortion_and_silhoutte_score_and_plot(scaled_df, max_clusters, dist_metric="euclidean"):
    
    # setup range of clusters from [2,max_clusters])
    # always start with 2 clusters
    clusters_range = range(2, max_clusters)
    
    # track the average distortion
    meanDistortions = []
    
    # list to track the silhouette scores
    sil_scores = []

    # loop over the range of clusters
    for n_clusters in clusters_range:
        
        # create kmeans model with number of clusters
        model = KMeans(n_clusters=n_clusters, random_state=1)
        
        # fit and predict the scaled dataset
        preds = model.fit_predict(scaled_df)

        # get the distortion for the model for each number of clusters
        # this will be used to determine the optimal number of clusters
        # this is using the sum of squared distances to the closest cluster center(euclidean) distance
        # its gonna take diff from each subset to the cluster center and sum them and divide by number of rows
        distortion = (
            sum(
                np.min(cdist(scaled_df, model.cluster_centers_, dist_metric), axis=1)
            )
            / scaled_df.shape[0]
        )
        
        # get the silhouette score using the predictions
        score = silhouette_score(scaled_df, preds, random_state=1)

        # append the distortion value to the list
        meanDistortions.append(distortion)
        
        # append the silhouette score to the list
        sil_scores.append(score)

        # print("Number of Clusters:", n_clusters, "\tAverage Distortion:", distortion)
        print("Number of Clusters = {}, \tAverage Distortion = {})".format(n_clusters, distortion))
        print("Number of Clusters = {}, \tthe silhouette score = {})".format(n_clusters, score))
        print("-" * 100)
        
    # plot the elbow curve using the number of clusters as x axis and the distortion as y axis
    plt.plot(clusters_range, meanDistortions, "bx-")
    plt.xlabel("k number of clusters")
    plt.ylabel("Average distortion")
    plt.title("Selecting k with the Elbow Method")
    plt.show()

    # plot the silhouette scores using the number of clusters as x axis and the silhouette score as y axis
    plt.xlabel("k number of clusters")
    plt.ylabel("Silhouette Scores")
    plt.title("Silhouette Scores vs Number of Clusters")
    plt.plot(clusters_range, sil_scores)
    plt.show()
    
    # return mean distortions and silhouette scores and the range of clusters
    return (meanDistortions, sil_scores, clusters_range)

# create a cluster profile dataframe with cluster labels
def create_cluster_profile_df_with_cluster_labels(df, subset_scaled_df, cluster_model, col_name, cluster_segment, cluster_segment_count):
    
    # adding cluster_model labels to the original and scaled dataframes
    # by adding new columns to the original dataframe and the scaled dataframe
    df[cluster_segment] = cluster_model.labels_
    subset_scaled_df[cluster_segment] = cluster_model.labels_
    
    # create a cluster profile dataframe using groupby on cluster_segment in the original dataframe by the cluster labels
    # and calculating the mean of the numeric columns in the original dataframe
    cluster_profile = df.groupby(cluster_segment).mean(numeric_only=True)
    
    # groupby cluster_segment and get the count in each cluster based on the col_name passed in
    # store in this cluster count in cluster_segment_count column
    cluster_profile[cluster_segment_count] = df.groupby(cluster_segment)[col_name].count().values
    
    return (cluster_profile, df, subset_scaled_df)

# This function performs hierarchical clustering using different distance metrics and linkage methods.
# It calculates silhouette scores to determine the quality of clustering for different combinations,
# and plots the best silhouette scores.
def calc_hierarchical_silhouette_scores_and_plot(scaled_df, max_clusters, distance_metrics, linkage_methods):
    
    # Range of cluster numbers to evaluate, starting from 2 to max_clusters
    clusters_range = range(2, max_clusters + 1)
    
    # Variables to track the best silhouette score and corresponding parameters
    # Init the vars to a default value
    max_sil_score = -1
    best_dm = None
    best_lm = None
    best_sil_scores = []
    
    # Loop over each combination of distance metrics and linkage methods
    for dm in distance_metrics:
        for lm in linkage_methods:
            if lm == 'ward' and dm != 'euclidean':
                # Skip the combination if linkage is 'ward' and distance metric is not 'euclidean'
                # Ward's method only works with Euclidean distances
                continue

            try:
                # Reset silhouette scores for each combination
                sil_scores = []
                
                # Loop over the range of clusters
                for n_clusters in clusters_range:
                    if dm == 'mahalanobis':
                        
                        #---Calculate the Mahalanobis distance matrix manually for the scaled data---
                        
                        # Compute the covariance matrix of the dataset
                        covariance_matrix = np.cov(scaled_df.T)
                        
                        # Compute pairwise Mahalanobis distances
                        pairwise_dists = pdist(scaled_df, metric=dm, VI=np.linalg.inv(covariance_matrix))
                        
                        # Convert the pairwise distances into a distance matrix
                        distance_matrix = squareform(pairwise_dists)
                        
                        #---Calculate the Mahalanobis distance matrix manually for the scaled data---
                        
                        # Initialize AgglomerativeClustering with precomputed distances
                        model = AgglomerativeClustering(n_clusters=n_clusters, metric='precomputed', linkage=lm)
                        
                        # Fit the model and predict cluster labels
                        cluster_labels = model.fit_predict(distance_matrix)
                    else:
                        # For other distance metrics, directly use the specified metric
                        
                        # Initialize the AgglomerativeClustering model
                        model = AgglomerativeClustering(n_clusters=n_clusters, metric=dm, linkage=lm)
                        
                        # Fit the model and predict cluster labels
                        cluster_labels = model.fit_predict(scaled_df)
                    
                    # Calculate the silhouette score using the corresponding distance metric
                    silhouette_avg = silhouette_score(scaled_df, cluster_labels, metric=dm, random_state=1)
                    
                    # Store silhouette score for the current combination by appending to current list
                    sil_scores.append(silhouette_avg)
                    
                    # Print the current configuration and its silhouette score
                    print(f"Metric = {dm}, Linkage = {lm}, Number of Clusters = {n_clusters}, Silhouette Score = {silhouette_avg:.4f}")
                
                # Determine if this is the best silhouette score so far from the sil_scores list
                # by getting the max value from the list
                max_current_sil = max(sil_scores)
                
                # Update the best silhouette score and corresponding parameters if the current is better
                if max_current_sil > max_sil_score:
                    
                    # Update the maximum silhouette score, dm, lm
                    max_sil_score = max_current_sil
                    best_dm = dm
                    best_lm = lm
                    
                    # if we have a winning max silhouette score then we want to save the
                    # current list of silhouette scores for this max score silhouette scores
                    # so we copy the silhouette scores for the best combination
                    best_sil_scores = sil_scores.copy()
                    
            except Exception as e:
                # If an exception occurs, print the error and skip the current combination
                print(f"Skipping combination (Metric: {dm}, Linkage: {lm}) due to error: {e}")
    
    # Plot the best results using the silhouette scores
    plt.figure(figsize=(12, 8))
    plt.plot(clusters_range, best_sil_scores, label=f'Best Metric: {best_dm}, Linkage: {best_lm}')
    
    plt.xlabel("Number of clusters")
    plt.ylabel("Silhouette Score")
    plt.title("Best Silhouette Scores vs Number of Clusters for Hierarchical Clustering\nBest Metric and Linkage Method")
    plt.legend(loc='best')
    plt.show()
    
    # Print the best silhouette score and corresponding parameters
    print(f"The best silhouette score is {max_sil_score:.4f} with Metric: {best_dm} and Linkage: {best_lm}")

# this function will build the model with cross validation
# it will also provide a model summary as a data frame for comparison
# it will also use a boxplot to show the distribution of CV scores
def model_building_with_cross_validation_classifier(metric_type, model_name_list, x_train, y_train, x_val, y_val, data_set_name, n_splits=5):
    
    # Empty list to store all the models
    models = []
    random_state = 1

    # Type of scoring used to compare parameter combinations
    if(metric_type == "recall"):
        scorer = metrics.make_scorer(metrics.recall_score)
        
    elif (metric_type == "precision"):
        scorer = metrics.make_scorer(metrics.precision_score)
        
    elif (metric_type == "accuracy"):
        scorer = metrics.make_scorer(metrics.accuracy_score)       
        
    elif (metric_type == "f1_score"):
        scorer = metrics.make_scorer(metrics.f1_score)
        
    else:
        print("Invalid metric type")
        return
    
    # Appending models into the list by model name
    for model_name in model_name_list:
        
        # adding tuple to the list, with name/model object and its default parameters and random state
        if(model_name == "LogisticRegression"):
            models.append((model_name, LogisticRegression(solver="liblinear", random_state=random_state)))
            
        elif(model_name == "DecisionTree"):
            models.append((model_name, DecisionTreeClassifier(random_state=random_state)))
            
        elif(model_name == "RandomForest"):
            models.append((model_name, RandomForestClassifier(random_state=random_state)))
            
        elif(model_name == "Bagging"):  
            models.append((model_name, BaggingClassifier(random_state=random_state)))
            
        elif(model_name == "GBM"):
            models.append((model_name, GradientBoostingClassifier(random_state=random_state)))
            
        elif(model_name == "Adaboost"):
            models.append((model_name, AdaBoostClassifier(random_state=random_state)))
            
        elif(model_name == "Xgboost"):
            models.append((model_name, XGBClassifier(random_state=random_state, eval_metric="logloss")))
        
        elif(model_name == "SVM"):
            models.append((model_name, SVC(random_state=random_state, kernel='linear')))
            
        else:
            print("Invalid model name")
            return

    # Empty list to store all model's train CV scores
    train_results = []
    
    # Empty list to store all train model's mean CV scores
    train_scores = []
    
    # Empty list to store name of the models
    model_names = []

    # loop through all models to get the mean cross validated score
    print("\n" "Cross-Validation performance on "+data_set_name+" training dataset:" "\n")

    # loop over all models and get the mean cv score
    for name, model in models:
        
        # Setting number of splits equal to 5
        # The folds are made by preserving the percentage of samples for each class.
        kfold = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
        
        # perform cross val score on train_set for each model and get the cv result and use all processors
        cv_result = cross_val_score(estimator=model, X=x_train, y=y_train, scoring=scorer, cv=kfold, n_jobs=-1)
        
        # store the cv result in a list and the name of the model corresponding to that result
        train_results.append(cv_result)
        train_scores.append(cv_result.mean())
        model_names.append(name)

    train_score_df = pd.DataFrame({"Model": model_names, "Train "+data_set_name+" CV Mean Score": train_scores})
    print(train_score_df)
    print()

    print("\n" "Validation Performance:" "\n")

    # Empty list to store all model's val set CV scores
    val_scores = []

    # loop over all the models and check metrics against validation_set for the recall metric
    for name, model in models:
        
        # fit model with the train_set
        model.fit(x_train, y_train)
        
        if(metric_type == "recall"):
            scores = recall_score(y_val, model.predict(x_val))
            
        elif (metric_type == "precision"):
            scores = precision_score(y_val, model.predict(x_val))
            
        elif (metric_type == "accuracy"):
            scores = accuracy_score(y_val, model.predict(x_val))
            
        elif (metric_type == "f1_score"):
            scores = f1_score(y_val, model.predict(x_val))
            
        else:
            print("Invalid metric type")
            return
        
        # store the val score in a list and the name of the model corresponding to that score
        val_scores.append(scores)

    # create a dataframe of all the models and their val scores
    val_score_df = pd.DataFrame({"Model": model_names, "Validation "+data_set_name+" CV Mean Score": val_scores})
    print(val_score_df)

    # keep a copy of df for original data
    copy_of_train_score_df = train_score_df.copy()
    copy_of_val_score_df = val_score_df.copy()

    #---Plotting boxplots for CV scores of all models defined above---
    
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.suptitle("Algorithm Comparison - "+data_set_name+" Data")
    sns.boxplot(data=train_results, ax=ax)
    ax.set_xticklabels(model_names)
    plt.show()
    
    #---Plotting boxplots for CV scores of all models defined above---

    # return both dataframes
    return copy_of_train_score_df, copy_of_val_score_df

# this function will perform hyperparameter tuning on the classifier
# for different combinations of parameters and different search algorithms
def hyperparameter_tuning_classifier(
    metric_type, model_name, random_state, param_grid, x_train, y_train, search_type="random", cv=5, n_iter=10):
    
    # Type of scoring used to compare parameter combinations
    if(metric_type == "recall"):
        scorer = metrics.make_scorer(metrics.recall_score)
        
    elif (metric_type == "precision"):
        scorer = metrics.make_scorer(metrics.precision_score)
        
    elif (metric_type == "accuracy"):
        scorer = metrics.make_scorer(metrics.accuracy_score)       
        
    elif (metric_type == "f1_score"):
        scorer = metrics.make_scorer(metrics.f1_score)
        
    else:
        print("Invalid metric type")
        return

    # adding tuple to the list, with name/model object and its default parameters and random state
    if(model_name == "LogisticRegression"):
        model = LogisticRegression(solver="liblinear", random_state=random_state)
        
    elif(model_name == "DecisionTree"):
        model = DecisionTreeClassifier(random_state=random_state)
        
    elif(model_name == "RandomForest"):
        model = RandomForestClassifier(random_state=random_state)
        
    elif(model_name == "Bagging"):  
        model = BaggingClassifier(random_state=random_state)
        
    elif(model_name == "GBM"):
        model = GradientBoostingClassifier(random_state=random_state)
        
    elif(model_name == "Adaboost"):
        model = AdaBoostClassifier(random_state=random_state)
        
    elif(model_name == "Xgboost"):
        model = XGBClassifier(random_state=random_state, eval_metric="logloss")
    
    elif(model_name == "SVM"):
        model = SVC(random_state=random_state, kernel='linear')
        
    else:
        print("Invalid model name")
        return

    if(search_type == "random"):
        
        # Calling RandomizedSearchCV
        search_cv = RandomizedSearchCV(
            estimator=model,
            param_distributions=param_grid,
            n_iter=n_iter,
            n_jobs = -1,
            scoring=scorer,
            cv=cv,
            random_state=random_state
        )
    
    elif(search_type == "grid"):
        
        # Calling GridSearchCV
        search_cv = GridSearchCV(
            estimator=model,
            param_grid=param_grid,
            n_jobs = -1,
            scoring=scorer,
            cv=5
        )
    
    else:
        print("Invalid search type")
        return
    
    # Fitting parameters in search algm
    search_cv.fit(x_train, y_train)

    # printing best parameters and best score
    print("Search Algorithm={}, Best parameters are={}, with CV score={}" .format(search_type, search_cv.best_params_, search_cv.best_score_))
