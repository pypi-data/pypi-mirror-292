import pandas as pd

class Shortcuts:
    class EDA:
        def describe(DataFrame):
            summary = pd.DataFrame()
            # Data Type
            summary['Data Type'] = DataFrame.dtypes
            
            # The Number of Missing Values
            summary['# of NAs'] = DataFrame.isna().sum()
            
            # The Percentage of Missing Values
            summary['% of NAs'] = round((DataFrame.isna().sum() / DataFrame.shape[0]) * 100, 2)
            
            # The Number of Unique Values
            summary['# of Unique'] = DataFrame.apply(lambda x: x.nunique())
            
            # Values
            summary['Count'] = DataFrame.count()
            summary['Min'] = DataFrame.apply(lambda x: x.min() if pd.api.types.is_numeric_dtype(x) else '-')
            summary['Max'] = DataFrame.apply(lambda x: x.max() if pd.api.types.is_numeric_dtype(x) else '-')
            
            # Quartiles
            summary['75%'] = DataFrame.apply(lambda x: x.quantile(0.75) if pd.api.types.is_numeric_dtype(x) else '-')
            summary['50%'] = DataFrame.apply(lambda x: x.quantile(0.50) if pd.api.types.is_numeric_dtype(x) else '-')
            summary['25%'] = DataFrame.apply(lambda x: x.quantile(0.25) if pd.api.types.is_numeric_dtype(x) else '-')
            
            # Measures of Central Tendency: Mean, Median, Mode 
            summary['Mean'] = DataFrame.apply(lambda x: round(x.mean(), 2) if pd.api.types.is_numeric_dtype(x) else '-')
            summary['Median'] = DataFrame.apply(lambda x: x.median() if pd.api.types.is_numeric_dtype(x) else '-')
            summary['Mode'] = DataFrame.apply(lambda x: x.mode().iloc[0] if not x.mode().empty else '-')
            summary['Freq'] = DataFrame.apply(lambda x: x.value_counts().iloc[0] if not x.mode().empty else '-')
            summary["%Freq"] = DataFrame.apply(lambda x: round(100 * x.value_counts().iloc[0] / len(x), 2) if not x.value_counts().empty else '-')
            
            # Measures of Dispersion: Range, Variance, Standard Deviation
            summary['Range'] = DataFrame.apply(lambda x: x.max() - x.min() if pd.api.types.is_numeric_dtype(x) else '-')
            summary['Variance'] = DataFrame.apply(lambda x: x.var() if pd.api.types.is_numeric_dtype(x) else '-')
            
            
            return summary
        
        def corrCheck(df, columns):
            
            def get_redundant_pairs(df):
                pairs_to_drop = set()
                cols = df.columns
                for i in range(0, df.shape[1]):
                    for j in range(0, i+1):
                        pairs_to_drop.add((cols[i], cols[j]))
                return pairs_to_drop

            def get_top_abs_correlations(df, n=5):
                au_corr = df.corr().abs().unstack()
                labels_to_drop = get_redundant_pairs(df)
                au_corr = au_corr.drop(labels=labels_to_drop).sort_values(ascending=False)
                return au_corr[0:n]

            print("Top Absolute Correlations")
            print(get_top_abs_correlations(df[columns], 50)) #выведем топ 50 коррелирующих пар
        
    class NAN:
        # заполнить средним
        def NANmean(data, colums):
            mean = data[colums].mean()
            data[colums].fillna(mean)
            return data
            
        # Заполнить пропуски самым популярным классом
        def NANpopularCat(data, colums):
            popular_category = data[colums].value_counts().index[0]
            data[colums] = data[colums].fillna(popular_category)
            return data
        
        # Заполнить пропуски новой категорией
        def NANnewCat(data, colums, new_cat):
            data[colums] = data[colums].fillna(new_cat)
            return data
            
        # Заполнить пропуски, ориентируясь на похожие объекты
        def NANnearest(data, colums_1, colums_2):
            grouped_means = data.groupby(colums_1)[colums_2].transform("mean")
            data[colums_2] = data[colums_2].fillna(grouped_means)
            return data
        
    class Action:
        
        def correlation(dataset, threshold):
            col_corr = set() # Set of all the names of deleted columns
            corr_matrix = dataset.corr()
            for i in range(len(corr_matrix.columns)):
                for j in range(i):
                    if (corr_matrix.iloc[i, j] >= threshold) and (corr_matrix.columns[j] not in col_corr):
                        colname = corr_matrix.columns[i] # getting the name of column
                        col_corr.add(colname)
                        if colname in dataset.columns:
                            del dataset[colname] # deleting the column from the dataset
            return dataset