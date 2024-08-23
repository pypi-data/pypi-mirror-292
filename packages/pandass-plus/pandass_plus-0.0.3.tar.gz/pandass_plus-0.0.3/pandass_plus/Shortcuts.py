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
            # Count of Values
            summary['Count'] = DataFrame.count()
            # Max
            summary['Max'] = DataFrame.apply(lambda x: x.max() if pd.api.types.is_numeric_dtype(x) else '-')
            # Min
            summary['Min'] = DataFrame.apply(lambda x: x.min() if pd.api.types.is_numeric_dtype(x) else '-')
            # Measures of Central Tendency: Mean, Median, Mode 
            summary['Mean'] = DataFrame.apply(lambda x: round(x.mean(), 2) if pd.api.types.is_numeric_dtype(x) else '-')
            summary['Median'] = DataFrame.apply(lambda x: x.median() if pd.api.types.is_numeric_dtype(x) else '-')
            summary['Mode'] = DataFrame.apply(lambda x: x.mode().iloc[0] if not x.mode().empty else '-')
            
            # Measures of Dispersion: Range, Variance, Standard Deviation
            summary['Range'] = DataFrame.apply(lambda x: x.max() - x.min() if pd.api.types.is_numeric_dtype(x) else '-')
            summary['Variance'] = DataFrame.apply(lambda x: x.var() if pd.api.types.is_numeric_dtype(x) else '-')
            summary['Standard Deviation'] = DataFrame.apply(lambda x: x.std() if pd.api.types.is_numeric_dtype(x) else '-')
            
            # Quartiles
            summary['25%'] = DataFrame.apply(lambda x: x.quantile(0.25) if pd.api.types.is_numeric_dtype(x) else '-')
            summary['50%'] = DataFrame.apply(lambda x: x.quantile(0.50) if pd.api.types.is_numeric_dtype(x) else '-')
            summary['75%'] = DataFrame.apply(lambda x: x.quantile(0.75) if pd.api.types.is_numeric_dtype(x) else '-')
            
            return summary
    
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