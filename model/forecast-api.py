import pickle
from flask import Flask
from flask import request
from flask import jsonify
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow import keras
import json

# Create a flask
app = Flask(__name__)

# Create an API end point
@app.route('/forecast', methods=['POST'])
def get_prediction():

    req = json.loads(request.json)
    data = np.asarray(req['data'])
    xdim = data.shape[2]
    
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data[0])
    
    # Load saved model
    model = keras.models.load_model("model")

    # Predict next hour
    output = model.predict(np.stack([scaled_data]))
    to_inverse = np.repeat(output, xdim, axis=-1)
    predicted_load = scaler.inverse_transform(to_inverse)[:,0]


    # Return a json object with predicted load
    return json.dumps({'predicted load':predicted_load.tolist()})

if __name__ == '__main__':
    app.run(host='0.0.0.0')