# -*- coding:utf-8 -*-
import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper
from ecg import ECG
import numpy as np

ecg = ECG()#创建ecg对象
st.title("心跳周期提取和ECG图像的数值信号转换")
st.markdown("帮助进行心跳周期的提取和ECG图像的数值信号转换:sunglasses:")
# 上传图片
uploaded_file = st.file_uploader("选择一张图片...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # If a new image is uploaded, reset session state variables
    if 'uploaded_file' not in st.session_state or st.session_state['uploaded_file'] != uploaded_file:
        st.session_state['rotation_angle'] = 0
        st.session_state['crop_done'] = False
        st.session_state['edited_image'] = None
        st.session_state['uploaded_file'] = uploaded_file
    
    image = Image.open(uploaded_file)

    # Rotate and crop image
    if not st.session_state['crop_done']:
        st.write("Rotate the image")
        rotate_angle = st.selectbox("Rotate Angle", [-180, -90, 0, 90, 180], index=2)
        st.session_state['rotation_angle'] = rotate_angle
        rotated_img = image.rotate(st.session_state['rotation_angle'], expand=True)
        st.image(rotated_img, caption='Rotated Image', use_column_width=True)

        with st.expander("Edit Image", expanded=True):
            st.write("Crop and Rotate Image")
            aspect_ratio = (16, 9)
            box_color = st.color_picker("Box Color", "#0000FF")

            # Cropping
            cropped_img = st_cropper(rotated_img, realtime_update=True, box_color=box_color, aspect_ratio=aspect_ratio)
            st.write("Cropped Image")
            st.image(cropped_img, use_column_width=True)
            # Save cropped image to disk
            if st.button("Save and Close"):
                # Adjust image size
                cropped_img.thumbnail((1024, 1024), Image.LANCZOS)
                # Save cropped image to disk
                
                st.session_state['edited_image'] = cropped_img
                st.session_state['crop_done'] = True
                st.experimental_rerun()
                cropped_img.save("cropped_image.jpg")
    else:
        st.write("Edited Image (Resized to 1024x1024)")
        st.image(st.session_state['edited_image'], use_column_width=True)
        # Save cropped image to disk
        cropped_img = st.session_state['edited_image']
        cropped_img.save("cropped_image.jpg")

    if cropped_img is not None:
        """下载图片"""
        ecg_user_image = ecg.getImage('cropped_image.jpg')
        # 展示图片
        st.image(ecg_user_image)

        """分割导联"""
        # Call the Divide leads method
        dividing_leads = ecg.DividingLeads()
        my_expander1 = st.expander(label='分割导联')
        with my_expander1:
            st.image('Leads_1-12_figure.jpg')
            st.image('Long_Lead_13_figure.jpg')

        """导联预处理"""
        ecg_preprocessed_leads = ecg.PreprocessingLeads()

        my_expander2 = st.expander(label='导联预处理')
        with my_expander2:
            st.image('Preprossed_Leads_1-12_figure.png')
            st.image('Preprossed_Leads_13_figure.png')   
        
        """数值转换(1-12)"""
        # Call the signal extraction method
        ec_signal_extraction = ecg.SignalExtraction_Scaling()
        my_expander3 = st.expander(label='绘制导联（1-12）轮廓')
        with my_expander3:
            st.image('Contour_Leads_1-12_figure.png')
        
        """提取心跳周期"""
        # Call the heart beat detection method
        ecg_heart_beat = ecg.Extractheart_period()
        my_expander4 = st.expander(label='心跳周期')
        with my_expander4:
            st.image('final_Normalized_Scaled_X_1.png')
            st.image('Normalized_Scaled_X_1_segment.png')
        

        """转换为1D信号"""
        # Call the combine and convert to 1D signal method
        ecg_1dsignal = ecg.CombineConvert1Dsignal()
        my_expander5 = st.expander(label='1D信号')
        with my_expander5:
            st.write(ecg_1dsignal)
        
        """数据降维"""
        # Call the dimensionality reduction function
        ecg_final = ecg.DimensionalReduciton(ecg_1dsignal)
        my_expander6 = st.expander(label='数据降维')
        with my_expander6:
            st.write(ecg_final)
        
        """机器学习预测"""
        # Call the pretrained ML model for prediction
        ecg_model ,ecg_probability = ecg.ModelLoad_predict(ecg_final)
        my_expander7 = st.expander(label='预测')
        with my_expander7:
            if ecg_model == 0:
                st.write("Your ECG corresponds to Abnormal Heartbeat\n您的心电图显示心律异常")
            elif ecg_model == 1:
                st.write("Your ECG corresponds to Myocardial Infarction\n您的心电图显示心肌梗死")
            elif ecg_model == 2:
                st.write("Your ECG is Normal\n您的心电图正常")
            else:
                st.write("Your ECG corresponds to History of Myocardial Infarction\n您的心电图显示出心肌梗死的历史记录") 
            st.write(f"Prediction Probability: {ecg_probability:.2%}")