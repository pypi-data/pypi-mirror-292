from JIMG.functions import jimg as jg
import cv2
from stardist.plot import render_label
from csbdeep.utils import normalize
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from stardist.models import StarDist2D
import copy
from tqdm import tqdm
import skimage
from skimage import measure
from collections import Counter
from IPython.display import display, HTML
import mpld3
import tempfile
import webbrowser
import os
import glob
import pickle
import json
import re


class image_tools:
    
    def load_JIMG_project(self, project_path):
            
        if '.pjm' in project_path:
            with open(project_path, 'rb') as file:
                app_metadata_tmp = pickle.load(file)
                
            return app_metadata_tmp
        
        else:
            print('\nProvide path to the project metadata file with *.pjm extension!!!')
            
    def ajd_mask_size(self, image, mask):
        try:
            mask = cv2.resize(mask, (image.shape[2], image.shape[1]))
        except:
            mask = cv2.resize(mask, (image.shape[1], image.shape[0]))
        
        return mask
    
    def load_image(self, path_to_image):
        image = jg.load_image(path_to_image)
        return image
    
    def load_3D_tiff(self, path_to_image):
        image = jg.load_tiff(path_to_image)
        return image
    
    def load_mask(self, path_to_mask):
        mask = cv2.imread(path_to_mask, cv2.IMREAD_GRAYSCALE)
        return mask
    
    def save(self, image, file_name):
        cv2.imwrite(filename = file_name, img = image)
        
        
    def drop_dict(self, dictionary, key, var, action = None):
    
        dictionary = copy.deepcopy(dictionary)
        indices_to_drop = []
        for i, dr in enumerate(dictionary[key]):
    
            if isinstance(dr, np.ndarray):
                dr = np.mean(dr)
                
            if action == '<=':
                if var <= dr:
                    indices_to_drop.append(i)
            elif action == '>=':
                if var >= dr:
                    indices_to_drop.append(i)
            elif action == '==':
                if var == dr:
                    indices_to_drop.append(i)
            elif action == '<':
                if var < dr:
                    indices_to_drop.append(i)
            elif action == '>':
                if var > dr:
                    indices_to_drop.append(i)
            else:
                print('\nWrong action!')
                return None
                
    
        for key, value in dictionary.items():
            dictionary[key] = [v for i, v in enumerate(value) if i not in indices_to_drop]
    
        return dictionary
    
    
    def create_mask(self, dictionary, image):
        image_mask = np.zeros(image.shape)
        
        arrays_list = copy.deepcopy(dictionary['coords'])
    
        for arr in tqdm(arrays_list):
            image_mask[arr[:,0], arr[:,1]] = 2**16-1
            
            
        return image_mask.astype('uint16')
    
    
    
    def min_max_histograme(self, image):
        q = []
        val = []
        perc = []
        
        max_val = image.shape[0] * image.shape[1]
        
        for n in range(0, 100, 5):
            q.append(n)
            val.append(np.quantile(image,n/100))
            sum_val = np.sum(image < np.quantile(image,n/100))
            pr = sum_val/max_val
            perc.append(pr)
                
        
        df = pd.DataFrame({'q':q, 'val':val, 'perc':perc})
        
        
        min_val = 0
        for i in df.index:
            if df['val'][i] != 0 and min_val == 0:
                min_val = df['perc'][i]
                
                
        max_val = 0
        df = df[df['perc'] > 0]
        df = df.sort_values('q',ascending=False).reset_index(drop=True)
    
        for i in df.index:       
            if i > 1 and df['val'][i]*1.5 > df['val'][i-1]:
                max_val = df['perc'][i]
                break
            elif i == len(df.index)-1:
                max_val = df['perc'][i]
                
        return min_val, max_val, df
    
        
    

class nucli_finder(image_tools):
    
    
    def __init__(self, image = None, 
                test_results=None, 
                hyperparameter_nucli={'nms':0.8, 'prob':0.4, 'max_size':1000, 'min_size':200, 
                                      'circularity':.3, 'ratio':.1, 'intensity_mean':(2**16-1)/5
                                      }, 
                
            
                hyperparameter_chromatization={'max_size':100, 'min_size':2, 'ratio':.1 , 'cut_point':4
                                      }, 
                
                img_adj_par_chrom ={'gamma':1, 'contrast':1, 'brightness':1000 ,
                                      }, 
                
                img_adj_par ={'gamma':1, 'contrast':1, 'brightness':1000 ,
                                      }, 
                
                show_plots = True,
                nuclei_results={'nuclei':None, 'nuclei_reduced':None, 'nuclei_chromatization':None},
                images={'nuclei':None, 'nuclei_reduced':None, 'nuclei_chromatization':None}):
       
       
       self.image = image
       self.test_results = test_results
       self.hyperparameter_nucli = hyperparameter_nucli
       self.nuclei_results = nuclei_results
       self.images = images
       self.show_plots = show_plots
       self.hyperparameter_chromatization = hyperparameter_chromatization
       self.img_adj_par_chrom = img_adj_par_chrom
       self.img_adj_par = img_adj_par


       
       
       
    def set_nms(self, nms:float):
        self.hyperparameter_nucli['nms'] = nms
    
    
    def set_prob(self, prob:float):
        self.hyperparameter_nucli['prob'] = prob
        
        
    def set_nucli_circularity(self, circ:float):
        self.hyperparameter_nucli['circularity'] = circ      
        
    
         
    def set_nucli_yx_len_min_ratio(self, ratio:float):
        self.hyperparameter_nucli['ratio'] = ratio        
        
        
        
    def set_nucli_size(self, size:tuple):
        self.hyperparameter_nucli['min_size'] = size[0]
        self.hyperparameter_nucli['max_size'] = size[1]
        
             
    def set_nucli_min_mean_intensity(self, intensity:int):
        self.hyperparameter_nucli['intensity_mean'] = intensity
        
        
    def set_chromatization_size(self, size:tuple):
        self.hyperparameter_chromatization['min_size'] = size[0]
        self.hyperparameter_chromatization['max_size'] = size[1]
   
    
    def set_chromatization_ratio(self, ratio:int):
        self.hyperparameter_chromatization['ratio'] = ratio
             
        
    def set_chromatization_cut_point(self, cut_point:int):
        self.hyperparameter_chromatization['cut_point'] = cut_point

    
    #
    
    def set_adj_image_gamma(self, gamma:float):
        self.img_adj_par['gamma'] = gamma
        
    def set_adj_image_contrast(self, contrast:float):
        self.img_adj_par['contrast'] = contrast
        
    def set_adj_image_brightness(self, brightness:float):
        self.img_adj_par['brightness'] = brightness
        
    #
    
    def set_adj_chrom_gamma(self, gamma:float):
        self.img_adj_par_chrom['gamma'] = gamma
        
    def set_adj_chrom_contrast(self, contrast:float):
        self.img_adj_par_chrom['contrast'] = contrast
        
    def set_adj_chrom_brightness(self, brightness:float):
        self.img_adj_par_chrom['brightness'] = brightness
             
         
    
    @property
    def current_parameters_nucli(self):
        print(self.hyperparameter_nucli)
        return self.hyperparameter_nucli
    
    
    @property
    def current_parameters_chromatizatio(self):
        print(self.hyperparameter_chromatization)
        return self.hyperparameter_chromatization
    
    @property
    def current_parameters_img_adj(self):
        print(self.img_adj_par)
        return self.img_adj_par
    
    
    @property
    def current_parameters_img_adj_chro(self):
        print(self.img_adj_par_chrom)
        return self.img_adj_par_chrom


    @property
    def get_results_nucli(self):
        
        if self.show_plots == True:
            jg.display_preview(self.images['nuclei'])   
        return self.nuclei_results['nuclei'], self.images['nuclei']
    
    
    @property   
    def get_results_nucli_selected(self):
        
        if self.show_plots == True:
            jg.display_preview(self.images['nuclei_reduced'])   
        return self.nuclei_results['nuclei_reduced'], self.images['nuclei_reduced']
    

    @property   
    def get_results_nuclei_chromatization(self):
        
        if self.show_plots == True:
            jg.display_preview(self.images['nuclei_chromatization'])   
        return self.nuclei_results['nuclei_chromatization'], self.images['nuclei_chromatization']


        
    def add_test(self, plots):
        self.test_results = plots
       
        
    def input_image(self, img):
        self.image = img
        self.add_test(None)
        
        
        
    def get_features(self, model_out, image):

        features = {'label':[],
                    'area':[],
                    'area_bbox':[],
                    'area_convex':[],
                    'area_filled':[],
                    'axis_major_length':[],
                    'axis_minor_length':[],
                    'eccentricity':[],
                    'equivalent_diameter_area':[],
                    'extent':[],
                    'feret_diameter_max':[],
                    'solidity':[],
                    'orientation':[],
                    'perimeter':[],
                    'perimeter_crofton':[],
                    'circularity':[],
                    'intensity_max':[],
                    'intensity_mean':[],
                    'intensity_min':[],
                    'ratio':[],
                    'coords':[]

                    }
                   
        
        
        for region in skimage.measure.regionprops(model_out, intensity_image=image):
            # Compute circularity
            circularity = 4 * np.pi * region.area / (region.perimeter ** 2)
            
            
            features['area'].append(region.area)
            features['area_bbox'].append(region.area_bbox)
            features['area_convex'].append(region.area_convex)
            features['area_filled'].append(region.area_filled)
            features['axis_major_length'].append(region.axis_major_length)
            features['axis_minor_length'].append(region.axis_minor_length)
            features['eccentricity'].append(region.eccentricity)
            features['equivalent_diameter_area'].append(region.equivalent_diameter_area)
            features['feret_diameter_max'].append(region.feret_diameter_max)
            features['solidity'].append(region.solidity)
            features['orientation'].append(region.orientation)
            features['perimeter'].append(region.perimeter)
            features['perimeter_crofton'].append(region.perimeter_crofton)
            features['label'].append(region.label)
            features['coords'].append(region.coords)
            features['circularity'].append(circularity)
            features['intensity_max'].append(np.max(region.intensity_max))
            features['intensity_min'].append(np.max(region.intensity_min))
            features['intensity_mean'].append(np.max(region.intensity_mean))


           
            
        ratios = []  

        # Calculate the ratio for each pair of values
        for min_len, max_len in zip(features['axis_minor_length'], features['axis_major_length']):
            if max_len != 0:
                ratio = min_len / max_len
                ratios.append(ratio)
            else:
                ratios.append(float(0.0))  
                
        features['ratio'] = ratios


            
        return features
     
     
     
     
    def nucli_finder_test(self):
        
        StarDist2D.from_pretrained()
        model = StarDist2D.from_pretrained('2D_versatile_fluo')
        
        nmst = [0,.2,.4,.6,.8]
        probt = [.1,.3,.5,.7]
        
        try:
            img = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        except:
            img = self.image
    
        plot = []
        
        fig = plt.figure(dpi=300)
        plt.imshow(img)
        plt.axis("off")
        plt.title("Original", fontsize = 25)
        
        if self.show_plots == True:
            plt.show()
    
        
        plot.append(fig)
        
        for n in tqdm(nmst):
            for t in probt:
                
                img = jg.adjust_img_16bit(img, brightness = self.img_adj_par['brightness'], contrast = self.img_adj_par['contrast'], gamma = self.img_adj_par['gamma'])
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                labels, _ = model.predict_instances(normalize(img), nms_thresh=n, prob_thresh=t)
                
                tmp = self.get_features(model_out = labels, image = img)
                
                
                fig = plt.figure(dpi=300)
                plt.imshow(render_label(labels, img=img))
                plt.axis("off")
                plt.title(f"nms {n} & prob {t} \n detected nuc: {len(tmp['area'])} \n var: {int(np.array(tmp['area']).var())}", fontsize=25)
                
                if self.show_plots == True:
                    plt.show()
            
                
                plot.append(fig)
                
                
        self.add_test(plot)
      
    
     

    
    def find_nucli(self):
        
        if isinstance(self.image, np.ndarray):
            StarDist2D.from_pretrained()
            model = StarDist2D.from_pretrained('2D_versatile_fluo')
            
            try:
                img = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            except:
                img = self.image    
            
            img = jg.adjust_img_16bit(img, brightness = self.img_adj_par['brightness'], contrast = self.img_adj_par['contrast'], gamma = self.img_adj_par['gamma'])
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            labels, _ = model.predict_instances(normalize(img), nms_thresh=self.hyperparameter_nucli['nms'], prob_thresh=self.hyperparameter_nucli['prob'])
             
            
            self.nuclei_results['nuclei'] = self.get_features(model_out = labels, image = img)     
            
            nucli_mask = jg.adjust_img_16bit(cv2.cvtColor(self.create_mask(self.nuclei_results['nuclei'] , self.image), cv2.COLOR_BGR2GRAY), color='blue')
            # nucli_mask = jg.adjust_img_16bit(cv2.cvtColor(finder.create_mask(finder.nuclei_results['nuclei'] , finder.image), cv2.COLOR_BGR2GRAY), color='blue')

            position = (int(nucli_mask.shape[0]/5), int(nucli_mask.shape[1]/15))  # Position where you want the text to be placed
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 2
            font_color = (0, 0, 2**16-1)  # White color in BGR
            thickness = 2
            
            nucli_mask = cv2.putText(nucli_mask, 'Estimated nucleus', position, font, font_scale, font_color, thickness)

            oryginal = jg.adjust_img_16bit(img, color='gray')
            oryginal = cv2.putText(oryginal, 'Original image', position, font, font_scale, font_color, thickness)

            concatenated_image = cv2.hconcat([oryginal, nucli_mask])
            concatenated_image = jg.resize_to_screen_img(concatenated_image)
            
                 
            self.images['nuclei'] = concatenated_image

            
            if self.show_plots == True:
                jg.display_preview(self.images['nuclei'])   

        
        else:
            print('\nAdd image firstly!')
        
        
       
    
    
    def select_nuclei(self):
        
        input_in = copy.deepcopy(self.nuclei_results['nuclei'])
        
        nucli_dictionary = self.drop_dict(input_in, key = 'area', var = self.hyperparameter_nucli['min_size'], action = '>')
        nucli_dictionary = self.drop_dict(nucli_dictionary, key = 'area', var =  self.hyperparameter_nucli['max_size'], action = '<')
        # nucli_dictionary = self.drop_dict(nucli_dictionary, key = 'eccentricity', var = np.mean(input_in['eccentricity'])*.75, action = '>')
        # nucli_dictionary = self.drop_dict(nucli_dictionary, key = 'eccentricity', var = np.mean(input_in['eccentricity'])*2, action = '<')
        nucli_dictionary = self.drop_dict(nucli_dictionary, key = 'circularity', var = self.hyperparameter_nucli['circularity'], action = '>')
        nucli_dictionary = self.drop_dict(nucli_dictionary, key = 'ratio', var =  self.hyperparameter_nucli['ratio'], action = '>')
        nucli_dictionary = self.drop_dict(nucli_dictionary, key = 'intensity_mean', var =  self.hyperparameter_nucli['intensity_mean'], action = '>')
    
        self.nuclei_results['nuclei_reduced'] = nucli_dictionary
        
        
        nucli_mask = jg.adjust_img_16bit(cv2.cvtColor(self.create_mask(self.nuclei_results['nuclei_reduced'] , self.image), cv2.COLOR_BGR2GRAY), color='blue')
        # nucli_mask = jg.adjust_img_16bit(cv2.cvtColor(finder.create_mask(finder.nuclei_results['nuclei'] , finder.image), cv2.COLOR_BGR2GRAY), color='blue')

        try:
            img = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        except:
            img = self.image    
             
             
        position = (int(nucli_mask.shape[0]/5), int(nucli_mask.shape[1]/15))  # Position where you want the text to be placed
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2
        font_color = (0, 0, 2**16-1)  # White color in BGR
        thickness = 2
        
        nucli_mask = cv2.putText(nucli_mask, 'Estimated nucleus', position, font, font_scale, font_color, thickness)

        oryginal = jg.adjust_img_16bit(img, color='gray')
        oryginal = cv2.putText(oryginal, 'Original image', position, font, font_scale, font_color, thickness)

        concatenated_image = cv2.hconcat([oryginal, nucli_mask])
        concatenated_image = jg.resize_to_screen_img(concatenated_image)
        
        
        self.images['nuclei_reduced'] = concatenated_image
        
        
        
        if self.show_plots == True:
            jg.display_preview(self.images['nuclei_reduced'])   
            


          
    
    def nuclei_chromatization(self):
        
        def is_list_in_llist(lst, llist):
            return any(sub_lst == lst for sub_lst in llist)
    
        def add_lists(f, g):
            result = []
            max_length = max(len(f), len(g))
           
            for i in range(max_length):
                f_elem = f[i] if i < len(f) else ""
                g_elem = g[i] if i < len(g) else ""
                result.append(f_elem + g_elem)
           
            return result
        
            
        def reverse_coords(image, x, y):
            
            
            zero = np.zeros(image.shape)
            
            zero[x, y] = 2**16
    
            zero_indices = np.where(zero == 0)
            
            return zero_indices[0], zero_indices[1]
            
        
        
        
         
        if isinstance(self.nuclei_results['nuclei_reduced'], dict):
            nucli_dictionary = self.nuclei_results['nuclei_reduced']
        else:
            nucli_dictionary = self.nuclei_results['nuclei']

         
        
        arrays_list = copy.deepcopy(nucli_dictionary['coords'])
    
        
        
        x = []
        y = []
        for arr in arrays_list:
            x = x + list(arr[:,0])
            y = y + list(arr[:,1])
    
                    
    
        x1, y1 = reverse_coords(self.image, x, y)
                
        
        regions_chro2 = self.image.copy()
    
        regions_chro2 = regions_chro2.astype('uint64')
    
        regions_chro2[x1, y1] = 0
        
        spot = np.quantile(regions_chro2[x, y], .9)
        
        
         
        for arr in arrays_list:
            xt = list(arr[:,0])
            yt = list(arr[:,1])
            
            
            regions_chro2[xt, yt] = (regions_chro2[xt, yt] / np.mean(regions_chro2[xt, yt])) * spot
    
        
        spot = np.quantile(regions_chro2[x, y], .9)
    
        
        regions_chro2[regions_chro2 > 2**16-1] = 2**16-1
        
        regions_chro2 = np.clip(regions_chro2, 0, 2**16-1)
    
        regions_chro2 = regions_chro2.astype('uint16')
        
        try:
            regions_chro2 = cv2.cvtColor(regions_chro2, cv2.COLOR_BGR2GRAY)
        except:
            pass
    
        regions_chro2 = jg.clahe_16bit(regions_chro2)
        regions_chro2 = jg.adjust_img_16bit(regions_chro2, brightness = self.img_adj_par_chrom['brightness'], contrast = self.img_adj_par_chrom['contrast'], gamma = self.img_adj_par_chrom['gamma'])
        regions_chro2 = cv2.cvtColor(regions_chro2, cv2.COLOR_BGR2GRAY)
        
        if self.show_plots == True:
            jg.display_preview(regions_chro2)   
        
    
    
        chromatione = regions_chro2 > np.max(regions_chro2) * self.hyperparameter_chromatization['cut_point']/10
    
    
        labeled_cells = measure.label(chromatione)
        regions = measure.regionprops(labeled_cells)
        regions = measure.regionprops(labeled_cells, intensity_image=regions_chro2)
    
    
        chromatione_info = {
            
                    'area':[],
                    'area_bbox':[],
                    'area_convex':[],
                    'area_filled':[],
                    'axis_major_length':[],
                    'axis_minor_length':[],
                    'eccentricity':[],
                    'equivalent_diameter_area':[],
                    'feret_diameter_max':[],
                    'solidity':[],
                    'orientation':[],
                    'perimeter':[],
                    'perimeter_crofton':[],
                    'coords':[]

                    }
        
        
        for region in regions:
            
            chromatione_info['area'].append(region.area)
            chromatione_info['area_bbox'].append(region.area_bbox)
            chromatione_info['area_convex'].append(region.area_convex)
            chromatione_info['area_filled'].append(region.area_filled)
            chromatione_info['axis_major_length'].append(region.axis_major_length)
            chromatione_info['axis_minor_length'].append(region.axis_minor_length)
            chromatione_info['eccentricity'].append(region.eccentricity)
            chromatione_info['equivalent_diameter_area'].append(region.equivalent_diameter_area)
            chromatione_info['feret_diameter_max'].append(region.feret_diameter_max)
            chromatione_info['solidity'].append(region.solidity)
            chromatione_info['orientation'].append(region.orientation)
            chromatione_info['perimeter'].append(region.perimeter)
            chromatione_info['perimeter_crofton'].append(region.perimeter_crofton)
            chromatione_info['coords'].append(region.coords)

            
    
    
        ratios = []  
        
        
        for min_len, max_len in zip(chromatione_info['axis_minor_length'], chromatione_info['axis_major_length']):
            if max_len != 0:
                ratio = min_len / max_len
                ratios.append(ratio)
            else:
                ratios.append(float(0.0))  
                
                
        chromatione_info['ratio'] = ratios
        
    
        chromation_dic = self.drop_dict(chromatione_info, key = 'area', var = self.hyperparameter_chromatization['min_size'], action = '>')
        chromation_dic = self.drop_dict(chromation_dic, key = 'area', var = self.hyperparameter_chromatization['max_size'], action = '<')
        chromation_dic = self.drop_dict(chromation_dic, key = 'ratio', var = self.hyperparameter_chromatization['ratio'], action = '>')
    

        arrays_list2 = copy.deepcopy(chromation_dic['coords'])
        
        nucli_dictionary['spot_size_area'] = []
        nucli_dictionary['spot_size_area_bbox'] = []
        nucli_dictionary['spot_size_area_convex'] = []
        nucli_dictionary['spot_size_area_filled'] = []
        nucli_dictionary['spot_axis_major_length'] = []
        nucli_dictionary['spot_axis_minor_length'] = []
        nucli_dictionary['spot_eccentricity'] = []
        nucli_dictionary['spot_size_equivalent_diameter_area'] = []
        nucli_dictionary['spot_feret_diameter_max'] = []
        nucli_dictionary['spot_orientation'] = []
        nucli_dictionary['spot_perimeter'] = []
        nucli_dictionary['spot_perimeter_crofton'] = []



        
        for i, arr in enumerate(tqdm(arrays_list)):
            
            spot_size_area = []
            spot_size_area_bbox = []
            spot_size_area_convex = []
            spot_size_area_convex = []
            spot_size_area_filled = []
            spot_axis_major_length = []
            spot_axis_minor_length = []
            spot_eccentricity = []
            spot_size_equivalent_diameter_area = []
            spot_feret_diameter_max = []
            spot_orientation = []
            spot_perimeter = []
            spot_perimeter_crofton = []


            # Flatten the array,
            df_tmp = pd.DataFrame(arr)
            df_tmp['duplicates'] = add_lists([str(x) for x in df_tmp[0]], [str(y) for y in df_tmp[1]])
            
            counter_tmp = Counter(df_tmp['duplicates'])
            
    
            for j, arr2 in enumerate(arrays_list2):
                df_tmp2 = pd.DataFrame(arr2)
                df_tmp2['duplicates'] = add_lists([str(x) for x in df_tmp2[0]], [str(y) for y in df_tmp2[1]])
                
                counter_tmp2 = Counter(df_tmp2['duplicates'])
                intersection_length = len(counter_tmp.keys() & counter_tmp2.keys())
                min_length = min(len(counter_tmp), len(counter_tmp2))
                
                if intersection_length >= 0.8 * min_length:
                    
    
                    if (len(list(df_tmp2['duplicates']))/len(list(df_tmp['duplicates']))) >= 0.025 and (len(list(df_tmp2['duplicates']))/len(list(df_tmp['duplicates']))) <= 0.5:
                        spot_size_area.append(chromation_dic['area'][j])
                        spot_size_area_bbox.append(chromation_dic['area_bbox'][j])
                        spot_size_area_convex.append(chromation_dic['area_convex'][j])
                        spot_size_area_filled.append(chromation_dic['area_filled'][j])
                        spot_axis_major_length.append(chromation_dic['axis_major_length'][j])
                        spot_axis_minor_length.append(chromation_dic['axis_minor_length'][j])
                        spot_eccentricity.append(chromation_dic['eccentricity'][j])
                        spot_size_equivalent_diameter_area.append(chromation_dic['equivalent_diameter_area'][j])
                        spot_feret_diameter_max.append(chromation_dic['feret_diameter_max'][j])
                        spot_orientation.append(chromation_dic['orientation'][j])
                        spot_perimeter.append(chromation_dic['perimeter'][j])
                        spot_perimeter_crofton.append(chromation_dic['perimeter_crofton'][j])
                        
                        
                        
                        
            nucli_dictionary['spot_size_area'].append(spot_size_area)
            nucli_dictionary['spot_size_area_bbox'].append(spot_size_area_bbox)
            nucli_dictionary['spot_size_area_convex'].append(spot_size_area_convex)
            nucli_dictionary['spot_size_area_filled'].append(spot_size_area_filled)
            nucli_dictionary['spot_axis_major_length'].append(spot_axis_major_length)
            nucli_dictionary['spot_axis_minor_length'].append(spot_axis_minor_length)
            nucli_dictionary['spot_eccentricity'].append(spot_eccentricity)
            nucli_dictionary['spot_size_equivalent_diameter_area'].append(spot_size_equivalent_diameter_area)
            nucli_dictionary['spot_feret_diameter_max'].append(spot_feret_diameter_max)
            nucli_dictionary['spot_orientation'].append(spot_orientation)
            nucli_dictionary['spot_perimeter'].append(spot_perimeter)
            nucli_dictionary['spot_perimeter_crofton'].append(spot_perimeter_crofton)
            
            
        
        self.nuclei_results['chromatization'] = chromation_dic
        self.nuclei_results['nuclei_chromatization'] = nucli_dictionary
        
        self.images['nuclei_chromatization'] = self.create_mask(chromation_dic, self.image)
        
        img_chrom = jg.adjust_img_16bit(cv2.cvtColor(self.create_mask(self.nuclei_results['chromatization'] , self.image), cv2.COLOR_BGR2GRAY), color='yellow')        
        
        
        if isinstance(self.nuclei_results['nuclei_reduced'], dict):
            nucli_mask = jg.adjust_img_16bit(cv2.cvtColor(self.create_mask(self.nuclei_results['nuclei_reduced'] , self.image), cv2.COLOR_BGR2GRAY), color='blue')
        else:
            nucli_mask = jg.adjust_img_16bit(cv2.cvtColor(self.create_mask(self.nuclei_results['nuclei'] , self.image), cv2.COLOR_BGR2GRAY), color='blue')


        nucli_mask = jg.merge_images([nucli_mask, img_chrom], [1, 1])


        try:
            img = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        except:
            img = self.image    
             
             
        position = (int(nucli_mask.shape[0]/5), int(nucli_mask.shape[1]/15)) 
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2
        font_color = (0, 0, 2**16-1)  
        thickness = 2
        
        nucli_mask = cv2.putText(nucli_mask, 'Estimated nucleus', position, font, font_scale, font_color, thickness)

        oryginal = jg.adjust_img_16bit(img, color='gray')
        oryginal = cv2.putText(oryginal, 'Original image', position, font, font_scale, font_color, thickness)

        concatenated_image = cv2.hconcat([oryginal, nucli_mask])
        concatenated_image = jg.resize_to_screen_img(concatenated_image)
        

        self.images['nuclei_chromatization'] = concatenated_image
        
        
        if self.show_plots == True:
            jg.display_preview(self.images['nuclei_chromatization'])   
            



    def broswere_test(self):
        html_content = ""

        # Iterate through the test results and concatenate HTML representations
        for f in self.test_results:
            html_content += mpld3.fig_to_html(f)

        # Write the HTML content to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as tmp_file:
            tmp_file.write(html_content)
            tmp_filename = tmp_file.name

        # Open the temporary HTML file in a web browser
        webbrowser.open_new_tab(tmp_filename)



    def series_analysis_chromatization(self, path_to_images, file_extension = 'tiff'):
        
        
        results_dict = {}

        files = glob.glob(os.path.join(path_to_images, "*." + file_extension))


        for file in files:
            
            print(file)
            
            self.show_plots = False
            
            image = self.load_image(file)
    
            self.input_image(image)
            
            self.find_nucli()
    
            self.select_nuclei()
    
            self.nuclei_chromatization()
            
            results_dict[str(os.path.basename(file))] = self.get_results_nuclei_chromatization
            
            self.show_plots = True

            
        
        return results_dict
    
    
    def series_analysis_nuclei(self, path_to_images, file_extension = 'tiff'):
        
        
        results_dict = {}

        files = glob.glob(os.path.join(path_to_images, "*." + file_extension))


        for file in files:
            
            print(file)
            
            self.show_plots = False
            
            image = self.load_image(file)
    
            self.input_image(image)
            
            self.find_nucli()
    
            self.select_nuclei()
                
            results_dict[str(os.path.basename(file))] = self.get_results_nucli_selected
            
            self.show_plots = True

            
        
        return results_dict

            
        
        
        
class feaure_intensity(image_tools):
    
    def __init__(self, input_image = None, 
                image=None,   
                normalized_image_values = None,
                mask = None,
                background_mask = None,
                typ = 'avg',
                size_info = None,
                correction_factor = .1,
                show_plots = True,
                img_type = None,
                scale = None,
                stack_selection = []):
        

       self.input_image = input_image
       self.image = image
       self.normalized_image_values = normalized_image_values
       self.mask = mask
       self.background_mask = background_mask
       self.typ = typ
       self.size_info = size_info
       self.correction_factor = correction_factor
       self.show_plots = show_plots
       self.scale = scale
       self.stack_selection = stack_selection



    @property
    def current_metadata(self):
        print(f'Projection type: {self.typ}') 
        print(f'Correction factor: {self.correction_factor}')
        print(f'Scale (unit/px): {self.scale}')
        print(f'Selected stac to remove: {self.stack_selection}')
        
    def set_projection(self, projection:str):
        t = ['avg', 'median', 'std', 'var', 'max', 'min']
        if projection in t:
            self.typ = projection
        else:
            print(f'\nProvided parameter is incorrect. Avaiable projection types: {t}')
            
    def set_correction_factorn(self, factor:float):
        
        if factor < 1 and factor > 0:
            self.correction_factor = factor
        else:
            print('\nProvided parameter is incorrect. The factor should be a floating-point value within the range of 0 to 1.')
            
    def set_scale(self, scale):
        
        self.scale = scale
       
    def set_selection_list(self, rm_list:list):
        
        self.stack_selection = rm_list
       
        
    def load_JIMG_project_(self, path):
        
        if '.pjm' in path:
            metadata = self.load_JIMG_project(path)
    
            try:
                self.scale = metadata.metadata['X_resolution[um/px]']
            except:
                
                try:
                    self.scale = metadata.images_dict['metadata'][0]['X_resolution[um/px]']
                
                except: 
                    print('/nUnable to set scale on this project! Set scale using "set_scale()"')
                
            self.stack_selection = metadata.removal_list

            
        else:
            print('\nWrong path. The provided path does not point to a JIMG project (*.pjm).')
        
        
       
    def stack_selection_(self):
        if len(self.input_image.shape) == 3:
            if len(self.stack_selection) > 0:
                self.input_image = self.input_image[[x for x in range(self.input_image.shape[0]) if x not in self.stack_selection]]
            else:
                print('\nImages to remove from the stack were not selected!')
       

    def projection(self):
        
        if self.typ == 'avg':
            img = np.mean(self.input_image, axis=0)

        elif self.typ == 'std':
            img = np.std(self.input_image, axis=0)

        elif self.typ == 'median':
            img = np.median(self.input_image, axis=0)

        elif self.typ == 'var':
            img = np.var(self.input_image, axis=0)

        elif self.typ == 'max':
            img = np.max(self.input_image, axis=0)

        elif self.typ == 'min':
            img = np.min(self.input_image, axis=0)
            
        self.image = img
            
     
    def detect_img(self):
        check = len(self.input_image.shape)
        
        if check == 3:
            print('\n3D image detected! Starting processing for 3D image...')
            print(f'Projection - {self.typ}...')
            
            self.stack_selection_()
            self.projection()
            
        elif check == 2:
            print('\n2D image detected! Starting processing for 2D image...')
            
        else:
            print('\nData does not match any image type!')
            
            
    def load_image_(self, path):
        self.input_image = self.load_3D_tiff(path)

        
    def load_mask_(self, path):
        self.mask = self.load_mask(path)
        
        print("\nThis mask was also set as the reverse background mask. If you want a different background mask for normalization, use 'load_normalization_mask()'.")
        self.background_mask = self.load_mask(path)


    def load_normalization_mask_(self, path):
        self.background_mask = self.load_mask(path)

    
    def intensity_calculations(self):
        tmp_mask = self.ajd_mask_size(image = self.image, mask = self.mask)
        tmp_bmask = self.ajd_mask_size(image = self.image, mask = self.background_mask)
        
        selected_values = self.image[tmp_mask == np.max(tmp_mask)]

        threshold = np.mean(self.image[tmp_bmask == np.min(tmp_bmask)])

        final_val = (selected_values - (threshold+(threshold*self.correction_factor)))/threshold

        final_val = final_val[final_val > 0]

        tmp_dict = {'min':np.min(final_val), 
                    'max':np.max(final_val), 
                    'mean':np.mean(final_val),
                    'median':np.median(final_val),
                    'std':np.std(final_val),
                    'var':np.var(final_val),
                    'values':final_val.tolist()}
        
        self.normalized_image_values = tmp_dict
    
    
    
    def size_calculations(self):
        
        tmp_mask = self.ajd_mask_size(image = self.image, mask = self.mask)
        
        size_px = int(len(tmp_mask[tmp_mask > np.min(tmp_mask)]))
        
        
        if self.scale is not None:
            size = float(size_px*self.scale)
        else:
            size = None
            print('\nUnable to calculate real size, scale (unit/px) not provided, use "set_scale()" or load JIMG project .pjm metadata "load_pjm()" to set scale for calculations!')
            
        non_zero_indices = np.where(tmp_mask == np.max(tmp_mask))

        min_y, max_y = np.min(non_zero_indices[0]), np.max(non_zero_indices[0])
        min_x, max_x = np.min(non_zero_indices[1]), np.max(non_zero_indices[1])
        
        max_length_x_axis = int(max_x - min_x + 1)
        max_length_y_axis = int(max_y - min_y + 1)
        


        tmp_val = {'size':size, 
                   'px_size':size_px,
                   'max_length_x_axis':max_length_x_axis,
                   'max_length_y_axis':max_length_y_axis}

        self.size_info = tmp_val


    def run_calculations(self):
        
        if self.input_image is not None:
            
            if self.mask is not None:
                
                print('\nStart...')
                self.detect_img()
                self.intensity_calculations()
                self.size_calculations()
                print('\nCompleted!')
                
                
    def get_results(self):
        
        if self.normalized_image_values is not None and self.size_info is not None:
        
            results = {'intensity':self.normalized_image_values,
                     'size':self.size_info}
        
            return results
        
        else:
            print('/nAnalysis were not conducted. Run analysis "run_calculations()"')
                
            
    def save_results(self, path = '', name = 'results'):
        
        if self.normalized_image_values is not None and self.size_info is not None:
        
            results = {'intensity':self.normalized_image_values,
                     'size':self.size_info}
            
            full_path = os.path.join(path, re.sub('\\.json', '', name) + '.json')
            
            with open(full_path, 'w') as file:
                json.dump(results, file, indent=4)
        
        else:
            print('/nAnalysis were not conducted. Run analysis "run_calculations()"')
                      
    
    
        
