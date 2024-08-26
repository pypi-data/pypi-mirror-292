# -*- coding:utf-8 -*-
from skimage.io import imread
from skimage import color
import matplotlib.pyplot as plt
from skimage.filters import threshold_otsu,gaussian
from skimage.transform import resize
from numpy import asarray
from skimage.metrics import structural_similarity
from skimage import measure
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
import joblib
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
import os
from natsort import natsorted
from sklearn import linear_model, tree, ensemble
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
import cv2
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import re

def crop_top_four_leads(image):
    """ 提取图片2/3的区域""" 
    height, width = image.shape[:2]
    crop_region = (0, 0, width, int(height * 2 / 3))
    cropped_image = image[crop_region[1]:crop_region[3], crop_region[0]:crop_region[2]]

    return cropped_image    

def divide_into_leads(image):
    """将图片分割为12个短导联和1个长导联"""
    leads = []#创建导联集合
    lead_width = image.shape[1] // 4#得到图片的宽度/4
    lead_height = image.shape[0] // 4#得到图片的高度/4
    #划分出四行，将前三行的每一行划分为4个导联
    for i in range(3):
        for j in range(4):
            leads.append(image[i * lead_height:(i + 1) * lead_height, j * lead_width:(j + 1) * lead_width])
    #划分出最后一行，将最后一行的每一列划分为1个长导联
    leads.append(image[3 * lead_height:image.shape[0], :])

    return leads

# 绘制分段数据的图形
def plot_segment(segment_df, filename):
    # 读取分段数据
    segment_data = pd.read_csv(filename)
    
    # 绘制图形
    plt.figure()
    plt.plot(segment_data['X'], label='Segment Data')
    plt.gca().invert_yaxis()
    plt.title(f'Plot for {filename}')
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.legend()
    
    # Save the plot
    save_filename = filename.replace('.csv', '.png')
    plt.savefig(save_filename)
    plt.show()
    print(f"Segment plot saved as {save_filename}")

def segment_data(filename):
    df = pd.read_csv(filename)
    match = re.search(r'Normalized_Scaled_X_\d+\.csv', filename)
    match=match.group()
    print(match)
    match=match.replace('.csv','')
    print(match)

    fig6, ax6 = plt.subplots()
    plt.gca().invert_yaxis()
    ax6.plot(df, linewidth=1, color='black', linestyle='solid')

    peaks, _ = find_peaks(-df['X'])
    local_minima = df.iloc[peaks]
    local_minima_sorted = local_minima.sort_values(by='X')
    top_four_indexes = local_minima_sorted.head(6).index.tolist()
    min_value = df['X'].min()
    local_minima_filtered = [index for index in top_four_indexes if df.at[index, 'X'] < (min_value +0.1)]
    sorted_indexes = sorted(local_minima_filtered)
    print("Top  local minima indexes (sorted and filtered):", sorted_indexes)
    if len(sorted_indexes)<=1:
        return
    for index in sorted_indexes:
        ax6.axvline(x=index, color='red', linestyle=':')

    l1 = sorted_indexes[0] if sorted_indexes else None
    l2 = sorted_indexes[1] if len(sorted_indexes) > 1 else None
    l3 = sorted_indexes[2] if len(sorted_indexes) > 2 else None
    r1 = sorted_indexes[3] if len(sorted_indexes)>3 else None
    r2 = sorted_indexes[4] if len(sorted_indexes)>4 else None
    r3 =sorted_indexes[5] if len(sorted_indexes)>5 else None


    dis=sorted_indexes[1]-sorted_indexes[0] if len(sorted_indexes)>1 else 0
    for index in sorted_indexes:
        ax6.axvline(x=index, color='red', linestyle='--')
        if index-dis//3+1>0:
            ax6.axvline(x=index-dis//3, color='blue', linestyle='--')

    save_filename = f'final_{match}.png'
    plt.savefig(save_filename)
    plt.show()
    print(f"Segment plot saved as {save_filename}")

    segment_case = df.loc[sorted_indexes[0]-dis//3+1:sorted_indexes[0]+dis*2//3]
    segment_case_filename = f'{match}_segment.csv'
    segment_case.to_csv(segment_case_filename, index=False)
    plot_segment(segment_case, segment_case_filename)

class ECG:
    def  getImage(self,image):
        """
        作用：读取图片
        返回值：图片数组
        """
        self.image = imread(image)
        return self.image
    
    def GrayImage(self):
        """
        作用：图片灰度化
        返回值：灰度化后的图片数组
        """
        self.gray_image = color.rgb2gray(self.image)
        return self.gray_image
    
    def DividingLeads(self):
        """
		作用：调用函数crop_top_four_leads()和divide_into_leads()，将图片分割为12个短导联和1个长导联
		返回值：分割后的导联数组
		"""
        #得到leads数组
        self.image_resize=crop_top_four_leads(self.image)
        self.leads = divide_into_leads(self.image_resize)

        #创建整个12个短导联的图像窗口
        fig , ax = plt.subplots(4,3)
        fig.set_size_inches(10, 10)#设置整个窗口大小
        x_counter=0
        y_counter=0
        #创建12个导联的子图并保存最终图片
        for x,y in enumerate(self.leads[:len(self.leads)-1]):
            if (x+1)%3==0:#每3个导联换行
                ax[x_counter][y_counter].imshow(y)
                ax[x_counter][y_counter].axis('off')#关闭坐标轴
                ax[x_counter][y_counter].set_title("leads {}".format(x+1))#命名导联
                x_counter+=1
                y_counter=0
            else:
                ax[x_counter][y_counter].imshow(y)
                ax[x_counter][y_counter].axis('off')
                ax[x_counter][y_counter].set_title("leads {}".format(x+1))
                y_counter+=1
        fig.savefig('Leads_1-12_figure.jpg')

        #创建长导联的窗口并保存最终图片
        fig1 , ax1 = plt.subplots()
        fig1.set_size_inches(10, 10)
        ax1.imshow(self.leads[12])
        ax1.set_title("Leads 13")
        ax1.axis('off')
        fig1.savefig('Long_Lead_13_figure.jpg')

        return self.leads
    
    def PreprocessingLeads(self):
        """
		作用：对导联预处理：灰度化、高斯滤波、全局阈值二值化
		"""
        #创建整个12个短导联的图像窗口
        fig2 , ax2 = plt.subplots(4,3)
        fig2.set_size_inches(10, 10)
        x_counter=0
        y_counter=0

        for x,y in enumerate(self.leads[:len(self.leads)-1]):
            grayscale = color.rgb2gray(y)#灰度化
            blurred_image = gaussian(grayscale, sigma=1)#高斯滤波，用于平滑图像，减少噪声
            global_thresh = threshold_otsu(blurred_image)#使用Otsu方法计算全局阈值
            binary_global = blurred_image < global_thresh#二值化处理
			#resize image
            # binary_global = resize(binary_global, (300, 450))
            if (x+1)%3==0:
                ax2[x_counter][y_counter].imshow(binary_global,cmap="gray")
                ax2[x_counter][y_counter].axis('off')
                ax2[x_counter][y_counter].set_title("pre-processed Leads {} image".format(x+1))
                x_counter+=1
                y_counter=0
            else:
                ax2[x_counter][y_counter].imshow(binary_global,cmap="gray")
                ax2[x_counter][y_counter].axis('off')
                ax2[x_counter][y_counter].set_title("pre-processed Leads {} image".format(x+1))
                y_counter+=1
        fig2.savefig('Preprossed_Leads_1-12_figure.png')

        #创建长导联的窗口并保存最终图片
        fig3 , ax3 = plt.subplots()
        fig3.set_size_inches(10, 10)
        grayscale = color.rgb2gray(self.leads[-1])
        blurred_image = gaussian(grayscale, sigma=1)
        global_thresh = threshold_otsu(blurred_image)
        print(global_thresh)
        binary_global = blurred_image < global_thresh
        ax3.imshow(binary_global,cmap='gray')
        ax3.set_title("Leads 13")
        ax3.axis('off')
        fig3.savefig('Preprossed_Leads_13_figure.png')

    def SignalExtraction_Scaling(self):
        """
		作用：查找轮廓并提取信号，并对信号进行归一化
		"""
        fig4 , ax4 = plt.subplots(4,3)
		#fig4.set_size_inches(10, 10)
        x_counter=0
        y_counter=0
        for x,y in enumerate(self.leads[:len(self.leads)-1]):
            #预处理
            grayscale = color.rgb2gray(y)
            blurred_image = gaussian(grayscale, sigma=0.7)
            global_thresh = threshold_otsu(blurred_image)
            binary_global = blurred_image < global_thresh
			# #resize image
            # binary_global = resize(binary_global, (300, 450))

			#寻找轮廓
            contours = measure.find_contours(binary_global,0.8)
            contours_shape = sorted([x.shape for x in contours])[::-1][0:1]#按形状进行排序，选择前1个最大的轮廓形状
            for contour in contours:#遍历所有轮廓，调整大小到 (255, 2)
                if contour.shape in contours_shape:
                    test = resize(contour, (255, 2))
            if (x+1)%3==0:
                ax4[x_counter][y_counter].invert_yaxis()
                ax4[x_counter][y_counter].plot(test[:, 1], test[:, 0],linewidth=1,color='black')
                ax4[x_counter][y_counter].axis('image')
                ax4[x_counter][y_counter].set_title("Contour {} image".format(x+1))
                x_counter+=1
                y_counter=0
            else:
                ax4[x_counter][y_counter].invert_yaxis()
                ax4[x_counter][y_counter].plot(test[:, 1], test[:, 0],linewidth=1,color='black')
                ax4[x_counter][y_counter].axis('image')
                ax4[x_counter][y_counter].set_title("Contour {} image".format(x+1))
                y_counter+=1
        
        #信号提取和信号缩放
            lead_no=x
            scaler = MinMaxScaler()#归一化工具
            fit_transform_data = scaler.fit_transform(test)#对 test 数据进行归一化
            Normalized_Scaled=pd.DataFrame(fit_transform_data[:,0], columns = ['X'])#将归一化后的数据转换为一个 DataFrame
            Normalized_Scaled=Normalized_Scaled.T#转置
			#保存归一化数据到 CSV 文件
            if (os.path.isfile('scaled_data_1D_{lead_no}.csv'.format(lead_no=lead_no+1))):
                Normalized_Scaled.to_csv('Scaled_1DLead_{lead_no}.csv'.format(lead_no=lead_no+1), mode='a',index=False)
            else:
                Normalized_Scaled.to_csv('Scaled_1DLead_{lead_no}.csv'.format(lead_no=lead_no+1),index=False)
	      	# Save original data to CSV in a separate folder
		
        fig4.savefig('Contour_Leads_1-12_figure.png')

    def Extractheart_period(self):
        """
        作用：提取心跳周期
        """
        for i in range(1, 13):
            print(i)
            filename = f'Scaled_1DLead_{i}.csv'
            print(filename)
            df1 = pd.read_csv(filename)
            df1_t = df1.T
            df1_t.columns = ['X']
            output_path = f'/old_home/lyt/zxj_workplaces/Cardiovascular-Detection-using-ECG-images-main/Normalized_pic/Normalized_Scaled_X_{i}.csv'
            df1_t.to_csv(output_path, index=False)
            segment_data(output_path)


    def CombineConvert1Dsignal(self):
        """
		作用：将所有导联的 1D 信号合并为一个 DataFrame
		"""
        test_final=pd.read_csv('Scaled_1DLead_1.csv')
        location= os.getcwd()
        print(location)
		#loop over all the 11 remaining leads and combine as one dataset using pandas concat
        for files in natsorted(os.listdir(location)):
            if files.endswith(".csv") and files.startswith("Scaled_1DLead_"):
            	if files!='Scaled_1DLead_1.csv':
                    df=pd.read_csv('{}'.format(files))
                    test_final=pd.concat([test_final,df],axis=1,ignore_index=True)
         # 检查 test_final 是否只有一行，如果不是，则只保留第一行数据
        if test_final.shape[0] > 1:
            test_final = test_final.iloc[[0]]

        return test_final    
    
    def DimensionalReduciton(self,test_final):
        """
		作用：使用 PCA 对数据进行降维
        """
		#first load the trained pca
        pca_loaded_model = joblib.load(r'/old_home/lyt/zxj_workplaces/Cardiovascular-Detection-using-ECG-images-main/model_pkl/PCA_ECG (1).pkl')
        result = pca_loaded_model.transform(test_final)
        final_df = pd.DataFrame(result)
        return final_df
    
    def ModelLoad_predict(self, final_df):
    # 加载模型
        loaded_model = joblib.load(r'/old_home/lyt/zxj_workplaces/Cardiovascular-Detection-using-ECG-images-main/model_pkl/Heart_Disease_Prediction_using_ECG (4).pkl')
    # 使用模型进行预测并获取概率
        probabilities = loaded_model.predict_proba(final_df)
        result = np.argmax(probabilities, axis=1)  # 获取预测类别
    # 预测类别和对应的概率
        prediction = result[0]
        probability = probabilities[0][prediction]
        
        return prediction , probability