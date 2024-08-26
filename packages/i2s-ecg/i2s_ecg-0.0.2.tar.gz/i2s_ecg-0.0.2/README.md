# ecg_i2s
the way to transform ECG image to signal
you can use this code to transform ECG image to signal, which is a 1D signal.
First,you need to create your own conda environment 
second,install the required packages, which are:
    scikit-learn==1.24.0
    scikit-image
    unzip
    joblib
    pandas
    matplotlib
    natsort
    streamlit

you can alos use requirements.txt to install the required packages by pip install -r requirements.txt

then, you can run the code by:
```
streamlit run app.py
```

if you can't open the webpage, you can update the streamlit version==1.37.0.


if you run the code with AxiosError: Request failed with status code 403, you can use the following command to run the code:

```
streamlit run app.py --server.enableXsrfProtection=false
```