import warnings
warnings.filterwarnings('ignore')

import streamlit as st
import pandas as pd
import joblib
from sklearn.preprocessing import RobustScaler

st.set_page_config(page_icon="🏡", page_title="House Prices Prediction", layout='wide')

st.markdown('<h1 style="text-align:center;">🏡 HOUSE PRICES PREDICTION 🏡</h1>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center;">🔍 based on 1stFlrSF, 2ndFlrSF, LowQualFinSF, GrLivArea, GarageArea, WoodDeckSF, OpenPorchSF, TotalBath, \
             BsmtFullBath, BathRatio, FullBath, HalfBath, BedroomAbvGr, TotRmsAbvGrd 🔍</div>', unsafe_allow_html=True)
st.write('---')


def load_model(file_path):
    try:
        model = joblib.load(file_path)
        return model
    except (OSError, IOError) as e:
        st.error(f"Error loading model file {file_path}: {e}")
        return None
    except joblib.externals.loky.process_executor._RemoteTraceback as e:
        st.error(f"Error unpickling model file {file_path}: {e}")
        return None

def model_predictions(dataset, features):
    l2_model = load_model('models/Linear_Regression_l2Regularizer_model.pkl')
    lr_model = load_model('models/Linear_Regression_model.pkl')
    
    if l2_model is None or lr_model is None:
        return None, None

    rs = RobustScaler()
    rs.fit(dataset.iloc[:,:-1])

    input_data = rs.transform(features)
    
    l2_prediction = l2_model.predict(input_data)
    lr_prediction = lr_model.predict(input_data)
    
    return l2_prediction, lr_prediction

# Function to process uploaded CSV file
def process_uploaded_file(dataset, uploaded_file):
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success('File successfully uploaded and loaded into DataFrame.')

            # Predictions for each row in the uploaded CSV
            l2_predictions = []
            lr_predictions = []

            cols = ['1stFlrSF', '2ndFlrSF', 'LowQualFinSF', 'GrLivArea', 'GarageArea',
                    'WoodDeckSF', 'OpenPorchSF', 'BsmtFullBath', 
                    'FullBath', 'HalfBath', 'BedroomAbvGr', 'TotRmsAbvGrd']
            
            df = df.loc[:, cols]

            df.insert(7, 'TotalBath', df['FullBath'] + (2 * df['HalfBath']))
            df.insert(9, 'BathRatio', ((df['FullBath'] + df['HalfBath']) / df['TotalBath']))


            df = df.ffill()

            rs = RobustScaler()
            rs.fit(dataset.iloc[:,:-1])

            df = rs.transform(df)

            l2_model = load_model('models/Linear_Regression_l2Regularizer_model.pkl')
            lr_model = load_model('models/Linear_Regression_model.pkl')
            
            if l2_model is None or lr_model is None:
                return None, None
            
            l2_predictions.append(l2_model.predict(df))
            lr_predictions.append(lr_model.predict(df))

            st.write(l2_predictions)
            st.write(lr_predictions)

        except Exception as e:
            st.error(f"Error processing uploaded file: {e}")


def main():
    global dataset  

    dataset = pd.read_csv('data/refined_dataset.csv') 

    st.write('👋 Hello! Please fill in the details below or upload a CSV file to predict house prices:')
    
    col1, col2 = st.columns(2)
    
    with col1:
        first_floor_sf = st.number_input('1st Floor Square Feet' , value = 0.0, format = '%f')
        second_floor_sf = st.number_input('2nd Floor Square Feet' , value = 0.0, format = '%f' )    
        low_qual_fin_sf = st.number_input('Low Quality Finished Square Feet' , value = 0.0, format = '%f' )
        gr_liv_area = st.number_input('Above Grade (Ground) Living Area Square Feet' , value = 0.0, format = '%f')
        garage_area = st.number_input('Garage Area' , value = 0.0, format = '%f' )
        wood_deck_sf = st.number_input('Wood Deck Area'  , value = 0.0, format = '%f')
    
    with col2:
        open_porch_sf = st.number_input('Open Porch Area', value = 0.0, format = '%f')
        bsmt_full_bath = st.number_input('Basement Full Bath', value = 0, format='%d' )
        full_bath = st.number_input('Full Bath',value = 0, format='%d' )
        half_bath = st.number_input('Half Bath',value = 0, format='%d' )
        bedroom_abv_gr = st.number_input('Bedrooms Above Grade',value = 0, format='%d' )
        tot_rms_abv_grd = st.number_input('Total Rooms Above Grade',value = 0, format='%d' )
    
    
    total_bath = full_bath + 2 * half_bath
    bath_ratio = (full_bath + half_bath) / (total_bath if total_bath != 0 else 1)
    
    
    features = [
        first_floor_sf, second_floor_sf, low_qual_fin_sf, gr_liv_area, garage_area, wood_deck_sf, 
        open_porch_sf, total_bath, bsmt_full_bath, bath_ratio, full_bath, half_bath, bedroom_abv_gr, tot_rms_abv_grd
    ]
    
    
    submit_button = st.button('Predict Individual 🚀')

    if submit_button:
        l2_prediction, lr_prediction = model_predictions(dataset, [features])
        if l2_prediction is not None and lr_prediction is not None:
            st.write(f'🔮 L2 Regularized Linear Regression Prediction: ${l2_prediction[0]:,.2f}')
            st.write(f'🔮 Linear Regression Prediction: ${lr_prediction[0]:,.2f}')

    st.write('---')

    uploaded_file = st.file_uploader('Upload a CSV file for batch prediction:', type=['csv'])

    if st.button('Predict from File 📁') and uploaded_file is not None:
        print(process_uploaded_file(dataset, uploaded_file))

main()
