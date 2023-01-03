import time
import re
import pandas as pd
import numpy as np
import jellyfish as jf
from fuzzywuzzy import fuzz, process
from xgboost import XGBClassifier
from sklearn.dummy import DummyClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_auc_score
from csv import DictWriter
import os
from dotenv import load_dotenv
def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn


def loadData():
    df_original = pd.read_csv('./data/dataset.csv')
    df_correct = df_original[['title', 'internal_name', 'category', 'match']].copy()
    df_correct.rename(columns={'title': 'external_name', }, inplace=True)

    # checking data
    #print(df_correct.head(5))
    #print (df_correct.category.unique())
    #print (df_correct.internal_name.unique())
    return df_correct


def createFalseData(df, iterations):
    df_output = df
    i = 0

    while i < iterations:
        df_s = df[['external_name', 'internal_name', 'category']].copy()

        # create columns and shuffle the values
        df_s['shuffled_internal_name'] = df_s['internal_name']
        df_s['shuffled_internal_name'] = df_s.groupby(
            'category')['internal_name'].transform(np.random.permutation)

        #check values
        df_s['match'] = np.where(df_s['internal_name'] == df_s['shuffled_internal_name'] , 1, 0)
        df_s['internal_name'] = np.where(df_s['shuffled_internal_name'] != '',
                                        df_s['shuffled_internal_name'],
                                        df_s['internal_name'])

        df_output = df_output.append(df_s)
        df_output = df_output.drop(columns=['shuffled_internal_name'])
        i += 1
    return df_output


def matchingNumbers(external_name, internal_name):
    external_numbers = set(re.findall(r'[0-9]+', external_name))
    internal_numbers = set(re.findall(r'[0-9]+', internal_name))
    union = external_numbers.union(internal_numbers)
    intersection = external_numbers.intersection(internal_numbers)

    if len(external_numbers) == 0 and len(internal_numbers) == 0:
        return 1
    else:
        return (len(intersection) / len(union))


def computeFeatures(df):
    df['internal_name'] = df['internal_name'].str.lower()
    df['external_name'] = df['external_name'].str.lower()

    df['levenshtein_distance'] = df.apply(
        lambda x: jf.levenshtein_distance(x['external_name'], x['internal_name']), axis=1)

    df['damerau_levenshtein_distance'] = df.apply(
        lambda x: jf.damerau_levenshtein_distance(x['external_name'], x['internal_name']), axis=1)

    df['hamming_distance'] = df.apply(
        lambda x: jf.hamming_distance(x['external_name'], x['internal_name']), axis=1)

    df['jaro_similarity'] = df.apply(
        lambda x: jf.jaro_similarity(x['external_name'], x['internal_name']), axis=1)

    df['jaro_winkler_similarity'] = df.apply(
        lambda x: jf.jaro_winkler_similarity(x['external_name'], x['internal_name']), axis=1)

    df['match_rating_comparison'] = df.apply(
        lambda x: jf.match_rating_comparison(x['external_name'], x['internal_name']), axis=1).fillna(0).astype(int)

    df['ratio'] = df.apply(
        lambda x: fuzz.ratio(x['external_name'], x['internal_name']), axis=1)

    df['partial_ratio'] = df.apply(
        lambda x: fuzz.partial_ratio(x['external_name'], x['internal_name']), axis=1)

    df['token_sort_ratio'] = df.apply(
        lambda x: fuzz.token_sort_ratio(x['external_name'], x['internal_name']), axis=1)

    df['token_set_ratio'] = df.apply(
        lambda x: fuzz.token_set_ratio(x['external_name'], x['internal_name']), axis=1)

    df['w_ratio'] = df.apply(
        lambda x: fuzz.WRatio(x['external_name'], x['internal_name']), axis=1)

    df['uq_ratio'] = df.apply(
        lambda x: fuzz.UQRatio(x['external_name'], x['internal_name']), axis=1)

    df['q_ratio'] = df.apply(
        lambda x: fuzz.QRatio(x['external_name'], x['internal_name']), axis=1)

    df['matching_numbers'] = df.apply(
        lambda x: matchingNumbers(x['external_name'], x['internal_name']), axis=1)

    df['matching_numbers_log'] = (df['matching_numbers']+1).apply(np.log)

    df['log_fuzz_score'] = (df['ratio'] + df['partial_ratio'] + df['token_sort_ratio'] + df['token_set_ratio']).apply(np.log)

    df['log_fuzz_score_numbers'] = df['log_fuzz_score'] + (df['matching_numbers']).apply(np.log)

    # replace wrong values by nan then 0
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna(value=0, inplace=True)

    return df

def get_confusion_matrix_values(y_test, y_pred):
    cm = confusion_matrix(y_test, y_pred)
    return(cm[0][0], cm[0][1], cm[1][0], cm[1][1])

def get_closest_matches(external_name, df):

    unique_internal_names = df['internal_name'].unique().tolist()
    closest_matches = process.extract(external_name, 
                unique_internal_names, 
                scorer=fuzz.token_set_ratio)

    return closest_matches

def prepare_data(external_name, df):

    closest_matches = get_closest_matches(external_name, df)

    df = pd.DataFrame(columns=['external_name', 'internal_name'])

    for match in closest_matches:
        row = {'external_name': external_name, 'internal_name': match[0]}
        df = df.append(row, ignore_index=True)

    return df

def buildModel (df):
    df = createFalseData(df, 10)
    df = computeFeatures(df)

    X = df[['levenshtein_distance', 'damerau_levenshtein_distance', 'hamming_distance',
       'jaro_similarity','jaro_winkler_similarity','matching_numbers_log',
       'matching_numbers','token_set_ratio','token_sort_ratio','partial_ratio',
       'ratio','log_fuzz_score','log_fuzz_score_numbers','match_rating_comparison',
       'q_ratio','uq_ratio','w_ratio']].values
    y = df['match'].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1, stratify=y)
    classifiers = {
    "DummyClassifier_stratified":DummyClassifier(strategy='stratified', random_state=0),    
    "KNeighborsClassifier":KNeighborsClassifier(3),
    "XGBClassifier":XGBClassifier(n_estimators=1000, learning_rate=0.1),
    "DecisionTreeClassifier":DecisionTreeClassifier(),
    "RandomForestClassifier":RandomForestClassifier(),
    "GradientBoostingClassifier":GradientBoostingClassifier(),
    "XGBClassifer tuned": XGBClassifier(colsample_bytree=0.8,
                      gamma=0.9,
                      max_depth=20,
                      min_child_weight=1,
                      scale_pos_weight=12,
                      subsample=0.9,
                      n_estimators=50, 
                      learning_rate=0.1)
}

    df_results = pd.DataFrame(columns=['model', 'accuracy', 'mae', 'precision',
                                    'recall','f1','roc','run_time','tp','fp',
                                    'tn','fn'])

    for key in classifiers:

        start_time = time.time()
        classifier = classifiers[key]
        model = classifier.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        roc = roc_auc_score(y_test, y_pred)
        run_time = format(round((time.time() - start_time)/60,2))
        tp, fp, fn, tn = get_confusion_matrix_values(y_test, y_pred)

        row = {'model': key,
            'accuracy': accuracy,
            'mae': mae,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'roc': roc,
            'run_time': run_time,
            'tp': tp,
            'fp': fp,
            'tn': tn,
            'fn': fn,
            }
        df_results = df_results.append(row, ignore_index=True)

    # get best classifier and use it
    best_classifier = df_results[df_results.accuracy == df_results['accuracy'].max()].iloc[0].model
    classifier = classifiers[best_classifier]
    model = classifier.fit(X_train, y_train)

    return model, df

def findMatch(product, df, model):

    closest_data = prepare_data(product['title'], df)
    data = computeFeatures(closest_data)
    data = data[['levenshtein_distance', 'damerau_levenshtein_distance', 'hamming_distance',
       'jaro_similarity','jaro_winkler_similarity','matching_numbers_log',
       'matching_numbers','token_set_ratio','token_sort_ratio','partial_ratio',
       'ratio','log_fuzz_score','log_fuzz_score_numbers','match_rating_comparison',
       'q_ratio','uq_ratio','w_ratio']]
    y_pred = model.predict_proba(data)[:,1]
    data = data.assign(prediction=y_pred)
    data = data.merge(closest_data)
    if y_pred[0] >= 0.95 :
        return data[['external_name','internal_name','prediction']].iloc[0].internal_name
    else :
        title_matched = data[['external_name','internal_name','prediction']].iloc[0].external_name
        category = ''
        if 'album' in title_matched:
            category = 'album'
        elif any (x in title_matched for x in ['photobook', 'monograph', 'dfesta']):
            category = 'photbook'
        elif any (x in title_matched for x in ['dvd', 'blueray']):
            category = 'concert'
        else:
            category = 'autre'
        column_names = ['image_url','price','title','url','internal_name','category','match']
        dict_to_add = {'image_url': product['image_url'],
                    'price': product['price'], 
                    'title': product['title'],
                    'url': product['url'], 
                    'internal_name': title_matched,
                    'category': category,
                    'match':1}
        load_dotenv()
        PROJECT_PATH = os.getenv('PROJECT_PATH')
        with open(PROJECT_PATH + f'/data/dataset.csv', 'a') as f:
            dictwriter_object = DictWriter(f, fieldnames=column_names)
            dictwriter_object.writerow(dict_to_add)
        f.close()
        return title_matched
