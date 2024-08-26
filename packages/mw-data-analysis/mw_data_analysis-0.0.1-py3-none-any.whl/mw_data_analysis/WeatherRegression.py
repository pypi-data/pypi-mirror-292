class WeatherRegression: 
    def __init__(self, filepath, disease_data: str, analyze_data):
        import pandas as pd
        self.disease_data = disease_data
        self.df = pd.read_csv(filepath)
        self.analyze_data = analyze_data
    
    def stacking(self, forcast_data):
        import pandas as pd
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, GradientBoostingRegressor
        from sklearn.ensemble import StackingRegressor
        import matplotlib.pyplot as plt
        import warnings
        warnings.simplefilter('ignore')

        list_stk = self.analyze_data + [self.disease_data]
        df_stk = self.df[list_stk]
        df_stk = df_stk.dropna()

        x = df_stk[self.analyze_data]
        y = df_stk[self.disease_data]
        disease_average = y.mean()
        #print(f'The dataset\'s average {self.disease_data} is {disease_average}')
        train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.1)
        #print(train_x.values)
        rgr1 = RandomForestRegressor(criterion='squared_error', n_estimators=50, random_state=0,
                                     n_jobs=2, max_depth=10, max_features='log2', 
                                     min_samples_split=30, max_leaf_nodes=100, bootstrap=False)
        rgr2 = ExtraTreesRegressor(criterion='squared_error', n_estimators=100, random_state=0,
                                    n_jobs=2, max_depth=10, max_features='log2',
                                    min_samples_split=30, bootstrap=False)
        fe = GradientBoostingRegressor(n_estimators=25, subsample=0.7, min_samples_split=30,
                                       max_features='log2', random_state=200)
        stk = StackingRegressor(estimators=[('rfr', rgr1), ('etr', rgr2)], final_estimator=fe)
        stk = stk.fit(train_x.values, train_y)
        print('stacking regressor score:', stk.score(test_x, test_y))

        pred_y = stk.predict(test_x)
        mse = mean_squared_error(test_y, pred_y)
        mae = mean_absolute_error(test_y, pred_y)
        r2 = r2_score(test_y, pred_y)
        print(f'MSE: {mse}\nMAE: {mae}\nr2 score: {r2}')
        
        predict = stk.predict(forcast_data)
        '''if predict > disease_average:
            print(f'\nSemtimental...\nThe model predicts that\nthe mental disease incidence will be {predict}\nis higher than dataset\'s average {disease_average}...')
        else:
            print(f'\nHappy :)\nThe model predicts that\nthe mental disease incidence will be {predict}\nis lower than dataset\'s average {disease_average} :)')
        '''
        rgr1 = rgr1.fit(train_x.values, train_y)
        feature_importance_1 = pd.Series(rgr1.feature_importances_, index=train_x.columns).sort_values(ascending=False)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12,4))
        
        ax1.bar(feature_importance_1.index, feature_importance_1)
        ax1.set_title('RandomForestRegressor')
        ax1.set_ylabel('Feature Importance')

        rgr2 = rgr2.fit(train_x.values, train_y)
        feature_importance_2 = pd.Series(rgr2.feature_importances_, index=train_x.columns).sort_values(ascending=False)
        ax2.bar(feature_importance_2.index, feature_importance_2)
        ax2.set_title('ExtraTreesRegressor')
        ax2.set_ylabel('Feature Importance')
        plt.show()
        return predict
    
    def stacking_app(self, forcast_data):
        import pandas as pd
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, GradientBoostingRegressor
        from sklearn.ensemble import StackingRegressor
        import matplotlib.pyplot as plt
        import warnings
        warnings.simplefilter('ignore')

        list_stk = self.analyze_data + [self.disease_data]
        df_stk = self.df[list_stk]
        df_stk = df_stk.dropna()

        x = df_stk[self.analyze_data]
        y = df_stk[self.disease_data]
        disease_average = y.mean()
        #print(f'The dataset\'s average {self.disease_data} is {disease_average}')
        train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.1)
        #print(train_x.values)
        rgr1 = RandomForestRegressor(criterion='squared_error', n_estimators=50, random_state=0,
                                     n_jobs=2, max_depth=10, max_features='log2', 
                                     min_samples_split=30, max_leaf_nodes=100, bootstrap=False)
        rgr2 = ExtraTreesRegressor(criterion='squared_error', n_estimators=100, random_state=0,
                                    n_jobs=2, max_depth=10, max_features='log2',
                                    min_samples_split=30, bootstrap=False)
        fe = GradientBoostingRegressor(n_estimators=25, subsample=0.7, min_samples_split=30,
                                       max_features='log2', random_state=200)
        stk = StackingRegressor(estimators=[('rfr', rgr1), ('etr', rgr2)], final_estimator=fe)
        stk = stk.fit(train_x.values, train_y)

        pred_y = stk.predict(test_x)
        mse = mean_squared_error(test_y, pred_y)
        mae = mean_absolute_error(test_y, pred_y)
        r2 = r2_score(test_y, pred_y)
        
        predict = stk.predict(forcast_data)
        
        return predict, disease_average, r2
'''
import pandas as pd
filepath = 'informations_2.csv'
df = pd.read_csv(filepath)
test = WeatherRegression(df, 'Incidence', ['tavg', 'prcp', 'snow', 'pres', 'wspd'], True)
test.stacking([[30, 0, 10]])
'''