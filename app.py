import pickle
from flask import Flask, request, jsonify,render_template
import pandas as pd
import numpy as np
import json
import os
import sys
# from sklearn.datasets import load_iris
# from sklearn.ensemble import RandomForestClassifier

# iris = load_iris()
# X = iris.data
# y = iris.target
# clf = RandomForestClassifier(n_estimators=100, max_depth=2,random_state=0)
# clf.fit(X, y)
# # save the model to disk
# filename = 'model.pkl'
# pickle.dump(clf, open(filename, 'wb'))
model = pickle.load(open('model.pkl', 'rb'))
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/predict',methods=['POST'])
def predict():
    int_features = [int(x) for x in request.form.values()]
    final_features = [np.array(int_features)]
    prediction = model.predict(final_features)

    output = round(prediction[0], 2)
    if output == 0:
        output = 'setosa'
    elif output == 1:
        output = 'versicolor'
    else:
        output = 'virginica'
    return render_template('index.html', prediction_text='According to ml ml model should be {}'.format(output))

if __name__ == "__main__":
    app.run(debug=True)
#index.html
# Path: templates/index.html

