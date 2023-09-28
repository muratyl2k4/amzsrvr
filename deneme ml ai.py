import pandas as pd





s_info = pd.read_excel('salesinfo.xlsx')
ml_test = pd.read_excel('ml_test.xlsx')


data_start = pd.merge(s_info,ml_test,how='inner',on=["ASIN" , 'ASIN'])[['Sales Rank: Current','Sales Rank: 30 days avg.','Sales Rank: 90 days avg.','Sales Rank: 180 days avg.','Sales Rank: Lowest','Sales Rank: Highest','Sales Rank: Drops last 30 days','Sales Rank: Drops last 90 days','Sales Rank: Drops last 180 days','Reviews: Review Count','Reviews: Review Count - 30 days avg.','Reviews: Review Count - 90 days avg.','Reviews: Review Count - 180 days avg.','ASIN','Satis']].dropna()



import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import mglearn

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
import random
from sklearn.tree import DecisionTreeRegressor

#X, y = mglearn.datasets.make_wave(n_samples=60)

poly = PolynomialFeatures(degree=1, include_bias=False)

temp_x = np.random.randint(1,300,150)
temp_y = np.random.randint(1,300,150)
temp_z = (temp_x**2+temp_y**2)

#196780	178578	185112	157296	-7769	189011	36396	380606	1	2	7	2775	2754	2667	2544	B00NAK3URM	


X = data_start[['Sales Rank: Drops last 30 days','Sales Rank: Drops last 90 days','Sales Rank: Drops last 180 days','Reviews: Review Count','Reviews: Review Count - 30 days avg.','Reviews: Review Count - 90 days avg.','Reviews: Review Count - 180 days avg.']]
y = data_start['Satis']

poly.fit(X)
X_poly = poly.transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_poly, y, random_state=42)
lr = LinearRegression().fit(X_poly, y)

#print("lr.coef_: {}".format(lr.coef_))
#print("lr.intercept_: {}".format(lr.intercept_))


tree = DecisionTreeRegressor().fit(X_train, y_train)
print("Training set score: {:.2f}".format(tree.score(X_train, y_train)))
print("Test set score: {:.2f}".format(tree.score(X_test, y_test)))
print("Total set score: {:.2f}".format(tree.score(X_poly, y)))


test_excel =  pd.read_excel('testtest.xlsx')[['Sales Rank: Drops last 30 days','Sales Rank: Drops last 90 days','Sales Rank: Drops last 180 days','Reviews: Review Count','Reviews: Review Count - 30 days avg.','Reviews: Review Count - 90 days avg.','Reviews: Review Count - 180 days avg.','ASIN']].dropna()
XX = test_excel[['Sales Rank: Drops last 30 days','Sales Rank: Drops last 90 days','Sales Rank: Drops last 180 days','Reviews: Review Count','Reviews: Review Count - 30 days avg.','Reviews: Review Count - 90 days avg.','Reviews: Review Count - 180 days avg.']]
XX = [[7,11,11,2608,2588,2568,2507]]
poly.fit(XX)
XX_poly = poly.transform(XX)
print('predict : ' , lr.predict(XX_poly))
#print('predict : ' , tree.predict(XX_poly))

"""
X = pd.DataFrame({'x' : temp_x,
                  'y' : temp_y})
y = pd.DataFrame({'z' : temp_z})




poly.fit(X)
X_poly = poly.transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_poly, y, random_state=42)
lr = LinearRegression().fit(X_poly, y)

print("lr.coef_: {}".format(lr.coef_))
print("lr.intercept_: {}".format(lr.intercept_))

print("Training set score: {:.2f}".format(lr.score(X_train, y_train)))
print("Test set score: {:.2f}".format(lr.score(X_test, y_test)))

poly.fit(XX)
XX_poly = poly.transform(XX)

print(XX_poly)
print('predict : ' , lr.predict(XX_poly))

print((XX['x']**2 + XX['y']**2))

"""