# coding: utf-8
# Author: Gauthier Patin
# Licence: GNU GPL v3.0

import os
import pandas as pd
import numpy as np
import colour
from typing import Optional, Union, List, Tuple
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter
from scipy.interpolate import interp1d
import seaborn as sns
import matplotlib.pyplot as plt
from uncertainties import ufloat, ufloat_fromstr, unumpy
from pathlib import Path


class MFT(object):

    def __init__(self, files:list, BWS:Optional[bool] = True, stdev:Optional[bool] = False) -> None:
        """Instantiate a Microfading (MFT) class

        Parameters
        ----------
        files : list
            A list of string, where each string corresponds to the absolute path of text or csv file that contains the data and metadata of a single microfading measurement. The content of the file requires a specific structure, for which an example can be found in .... If the file structure is not respected, the script will not be able to properly read the file and access its content.
        """
        self.files = files
        self.BWS = BWS
        self.stdev = stdev

        if self.BWS == False:
            self.files = [x for x in self.files if 'BW' not in x.name]

       
    def __repr__(self) -> str:
        return f'Microfading data class - Number of files = {len(self.files)}'
    

    def data_points(self, coordinates:Optional[list] = ['dE00'], dose_unit:Optional[str] = 'He', dose_values:Union[int, float, list, tuple] = 1, index:Optional[bool] = False):
        # Retrieve the range light dose values
        doses = {'He':'He_MJ/m2', 'Hv':'Hv_Mlxh', 't': 't_sec'}

        if isinstance(dose_values, (float, int)):
            dose_values = [dose_values]

        elif isinstance(dose_values, tuple):
            dose_values = np.arange(dose_values[0], dose_values[1], dose_values[2])

        elif isinstance(dose_values, list):
            dose_values = dose_values        
           
        # Retrieve the data
        original_data = self.get_data(data='dE')
        
        # Added the delta LabCh values to the data dataframes   
        if original_data[0].columns.nlevels > 1:
            
            delta_coord = [unumpy.uarray(d[coord, 'mean'], d[coord, 'std']) - unumpy.uarray(d[coord, 'mean'], d[coord, 'std'])[0] for coord in ['L*', 'a*', 'b*', 'C*', 'h'] for d in original_data]
            
            delta_means = [unumpy.nominal_values(x) for x in delta_coord]
            delta_stds = [unumpy.std_devs(x) for x in delta_coord]

            delta_coord_mean = [(f'd{coord}', 'mean') for coord in ['L*', 'a*', 'b*', 'C*', 'h']]
            delta_coord_std = [(f'd{coord}', 'std') for coord in ['L*', 'a*', 'b*', 'C*', 'h']]

            # Add the new columns to the dictionary
            data = []

            for d in original_data:
                for coord_mean,delta_mean,coord_std,delta_std in zip(delta_coord_mean,delta_means, delta_coord_std,delta_stds):
                    d[coord_mean] = delta_mean
                    d[coord_std] = delta_std

                data.append(d)

            
            # Select the wanted dose_unit and coordinate        
            wanted_data = [x[[doses[dose_unit]] + coordinates] for x in data]        
            wanted_data = [x.set_index(x.columns[0]) for x in wanted_data]
            
        else:
            data = [d.assign(**{f'd{coord}': d[coord] - d[coord].values[0] for coord in ['L*', 'a*', 'b*', 'C*', 'h']}) for d in original_data]
                
            # Select the wanted dose_unit and coordinate        
            wanted_data = [x[[doses[dose_unit]] + coordinates] for x in data]        
            wanted_data = [x.set_index(x.columns[0]) for x in wanted_data]
            
        # Interpolation function, assuming linear interpolation
        interp_functions = lambda x, y: interp1d(x, y, kind='linear', fill_value="extrapolate")

        # Double comprehension list to interpolate each dataframe in wanted_data
        interpolated_data = [
            pd.DataFrame({
                col: interp_functions(df.index, df[col])(dose_values)
                for col in df.columns
            }, index=dose_values)
            .rename_axis(doses[dose_unit])
            .reset_index()
            for df in wanted_data
        ]

        # Whether to set the index
        if index:
            interpolated_data = [x.set_index(x.columns[0]) for x in interpolated_data]
        
        return interpolated_data       
    
    
    def delta(self, coordinates:Optional[list] = ['dE00'], dose_unit:Optional[list] = ['He'], rate:Optional[bool] = False):
        """Retrieve the CIE delta values for a given set of colorimetric coordinates corresponding to the given microfading analyses.

        Parameters
        ----------
        coordinates : list, optional
            List of colorimetric coordinates, by default ['dE00']
            Any of the following coordinates can be added to the list: 'dE76', 'dE00', 'dR_vis' , 'L*', 'a*', 'b*', 'C*', 'h'.

        dose_unit : list, optional
            List of light energy doses, by default ['He']
            Any of the following units can be added to the list: 'He', 'Hv', 't'. Where 'He' corresponds to radiant energy (MJ/m2), 'Hv' to exposure dose (Mlxh), and 't' to times (sec)

        rate : bool, optional
            Whether to return the first derivative values of the desired coordinates, by default False

        Returns
        -------
        _type_
            Returns a Pandas dataframe where each column corresponds to a desired coordinate or light energy dose.
        """

        doses_dic = {'He': 'He_MJ/m2', 'Hv': 'Hv_Mlxh', 't': 't_sec'} 
        doses_labels = [doses_dic[x] for x in dose_unit]

        wanted_data = []
        

        if self.stdev == False: 
            
            doses = self.get_data(data=doses_labels) 
            data = self.get_data(data=coordinates)        
                        
            
            for el_data,el_dose in zip(data,doses):
                for col in el_data.columns:
                    if col in ['L*','a*','b*','C*','h']:
                        values = el_data[col]
                        values_delta = values - values[0]   

                        el_data[col] = values_delta
                        el_data.rename(columns={col:f'd{col}'}, inplace=True)
                
                if rate:   
                    
                    step_dose = el_dose.iloc[:,0].values[2]-el_dose.iloc[:,0].values[1]

                    el_data = pd.DataFrame(np.gradient(el_data.T.values, step_dose, axis=1).T, columns=el_data.columns)

                wanted_data.append(pd.concat([el_dose, el_data], axis=1))


        else:

            data = self.get_data(data=coordinates)[0] - self.get_data(data=coordinates)[0].iloc[0,:]
            doses = self.get_data(data=doses_labels)
            wanted_data = [pd.concat([doses[0],data], axis=1)]
            
            new_columns = []
            for i in wanted_data:
                for col in i.columns:
                    if col[1] in ['L*','a*','b*','C*','h']:
                        new_columns.append((col[0], f'd{col[1]}'))
                    else:
                        new_columns.append(col)

                i.columns = pd.MultiIndex.from_tuples(new_columns, names=i.columns.names)          
        
        
        return wanted_data


    def fit_data(self, plot:Optional[bool] = False, return_data:Optional[bool] = False, dose_unit:Optional[str] = 'He', coordinate:Optional[str] = 'dE00', equation:Optional[str] = 'c0*(x**c1)', initial_params:Optional[List[float]] = [0.1, 0.0], x_range:Optional[Tuple[int]] = (0, 1001, 1), save: Optional[bool] = False, path_fig: Optional[str] = 'default') -> Union[None, Tuple[np.ndarray, np.ndarray]]:

        # Retrieve the range light dose values
        doses = {'He':'He_MJ/m2', 'Hv':'Hv_Mlxh', 't': 't_sec'}  
        x_values = np.arange(*x_range)
           
        # Retrieve the data
        original_data = self.get_data(data='dE') if self.data_category == 'interim' else self.get_data(data='dE')[0].astype(float)

        # Added the delta LabCh values to the data dataframes
        coordinates = ['L*', 'a*', 'b*', 'C*', 'h']
        data = [d.assign(**{f'd{coord}': d[coord] - d[coord].values[0] for coord in coordinates}) for d in original_data]
                
        # Select the wanted dose_unit and coordinate
        wanted_data = [x[[doses[dose_unit], coordinate]] for x in data]
        wanted_data = [x.set_index(x.columns[0]) for x in wanted_data]
        
        # Define the function to fit
        def fit_function(x, *params):
            param_dict = {f'c{i}': param for i, param in enumerate(params)}
            param_dict['x'] = x
            return eval(equation, globals(), param_dict)
    
        # Define boundaries for the parameters
        #bounds = ([-np.inf] * len(initial_params), [np.inf, 1]) if len(initial_params) == 2 else ([-np.inf] * len(initial_params), [np.inf, 1, np.inf])

        # Create an empty dataframe for the fitted data
        fitted_data = pd.DataFrame(index=pd.Series(x_values))

        # Empty list to store the labels
        fitted_labels = []

        # Emtpy list to store the optimized parameters
        fitted_parameters = []

        for d in wanted_data:
            # retrieve the x(light dose) and y(coordinate) values
            x, y = d.index, d.iloc[:,0]
                  
            # perform the curve fitting
            optimized_params, _ = curve_fit(fit_function, x, y, p0=initial_params, ) # bounds=bounds
            
            # generate fitted y data
            fitted_y = fit_function(x_values, *optimized_params)
            
            # append it to the fitted_data dataframe
            fitted_data = pd.concat([fitted_data, pd.DataFrame(fitted_y, index=pd.Series(x_values))], axis=1)
            
            # Calculate R-squared value
            residuals = y - fit_function(x, *optimized_params)
            ss_res, ss_tot = np.sum(residuals**2), np.sum((y - np.mean(y))**2)        
            r_squared = np.round(1 - (ss_res / ss_tot), 3)

            # Create a string representation of the equation with optimized parameters
            optimized_equation = equation
            for i, param in enumerate(optimized_params):
                optimized_equation = optimized_equation.replace(f'c{i}', str(np.round(param,2)))

            fitted_labels.append(f'{optimized_equation}, $R^2$ = {r_squared}')
            fitted_parameters.append(optimized_params)

        fitted_data.columns = [f'{x.split(".")[-1]}, $y$ = {y}' for x,y in zip(self.meas_ids, fitted_labels)]         
        
        if plot:
            labels_eq = {
                'L*': r'CIE $L^*$',
                'a*': r'CIE $a^*$',
                'b*': r'CIE $b^*$',
                'C*': r'CIE $C^*$',
                'h': r'CIE $h$',
                'dE76': r'$\Delta E^*_{ab}$',
                'dE00': r'$\Delta E^*_{00}$',
                'dR_VIS': r'$\Delta R_{\rm vis}$',
                'dL*': r'CIE $\Delta L^*$',
                'da*': r'CIE $\Delta a^*$',
                'db*': r'CIE $\Delta b^*$',
                'dC*': r'CIE $\Delta C^*$',
                'dh': r'CIE $\Delta h$',
            }

            labels_H = {
                'Hv': 'Exposure dose $H_v$ (Mlxh)',
                'He': 'Radiant Exposure $H_e$ (MJ/m²)',
                't' : 'Exposure duration (seconds)'
            }

            sns.set_theme(context='paper', font='serif', palette='colorblind')
            fig, ax = plt.subplots(1,1, figsize=(10,6))
            fs = 24

            
            pd.concat(wanted_data, axis=1).plot(ax=ax, color='0.7', ls='-', lw=5, legend=False)
            fitted_data.plot(ax=ax, lw=2, ls='--')

            #meas_line, = ax.plot(x,y, ls='-', lw=3)            
            #fitted_line, = ax.plot(x_values,fitted_y, ls='--', lw=2)

            ax.set_xlabel(labels_H[dose_unit], fontsize=fs)
            ax.set_ylabel(labels_eq[coordinate],fontsize=fs)
            
            title = f'Microfading, {self.Id}, data fitting'
            ax.set_title(title, fontsize = fs-4)   
            
            '''
            if coordinate.startswith('d'):                
                ax.set_ylim(0) 
            '''

            ax.set_xlim(0)    

            ax.xaxis.set_tick_params(labelsize=fs)
            ax.yaxis.set_tick_params(labelsize=fs)
        
            #plt.legend([meas_line,fitted_line], ["original data",f"$f(x) = {optimized_equation}$\n$R^2 = {r_squared:.3f}$"],fontsize=fs-6)
            #plt.tight_layout()
            

            if save:

                filename = self.make_filename('dEfit')

                if save:            
                    if path_fig == 'default':
                        path_fig = self.get_folder_figures() / filename

                    if path_fig == 'cwd':
                        path_fig = f'{os.getcwd()}/{filename}' 

                    plt.savefig(path_fig, dpi=300, facecolor='white')

            plt.show()
        
        if return_data:
            return fitted_parameters, fitted_data


    def read_files(self):
        """Read the data files given as argument when defining the instance of the MFT class.

        Returns
        -------
        pandas dataframe
            It returns of the content of the files where the each column relates to a file.
        """
        
        files = []
                
        for file in self.files:
            df_info = pd.read_excel(file, sheet_name='info')
            df_sp = pd.read_excel(file, sheet_name='spectra')
            df_cl = pd.read_excel(file, sheet_name='CIELAB')

            files.append([df_info, df_cl, df_sp])

        return files
     

    def get_data(self, data:Union[str, list] = 'all'):
        """Retrieve the microfading data.

        Parameters
        ----------
        data : str, optional
            Possibility to select the type of data, by default 'all'
            When 'all', it returns all the data (spectral and colorimetric).
            When 'sp', it only returns the spectral data.
            When 'cl', it only return the colorimetric data.            

        Returns
        -------
        pandas dataframe
            It returns the data inside a pandas dataframe where each column corresponds to a single file.
        """

        data_cl = []
        data_sp = []  
        

        for file in self.files:
            

            if type(data) == list:
                dic_doses = {'He': 'He_MJ/m2', 'Hv':'Hv_Mlxh', 't':'t_sec'}
                data = [dic_doses[x] if x in dic_doses.keys() else x for x in data]

                if self.stdev:                    
                    df_sp = pd.read_excel(file, sheet_name='spectra', index_col=0, header=[0,1])
                    df_cl = pd.read_excel(file, sheet_name='CIELAB', header=[0,1])
                    df_cl = df_cl[data]
                
                else:
                    df_sp = pd.read_excel(file, sheet_name='spectra', index_col=0)
                    df_cl = pd.read_excel(file, sheet_name='CIELAB')
                    df_cl = df_cl[data]

            else:
                if self.stdev:
                    df_sp = pd.read_excel(file, sheet_name='spectra', index_col=0, header=[0,1])
                    df_cl = pd.read_excel(file, sheet_name='CIELAB', header=[0,1])
                else:
                    df_sp = pd.read_excel(file, sheet_name='spectra', index_col=0)
                    df_cl = pd.read_excel(file, sheet_name='CIELAB')

            data_cl.append(df_cl)
            data_sp.append(df_sp)        

        if data == 'all':
            return data_sp, data_cl
        
        elif data == 'sp':            
            return data_sp

        elif data == 'cl':
            return data_cl
        
        else:
            return data_cl
           

    def get_metadata(self):
        """Retrieve the metadata.

        Returns
        -------
        pandas dataframe
            It returns the metadata inside a pandas dataframe where each column corresponds to a single file.
        """
        
        df = self.read_files()
        metadata = [x[0] for x in df]

        df_metadata = pd.DataFrame(index = metadata[0].set_index('parameter').index)

        for m in metadata:
            m = m.set_index('parameter')
            Id = m.loc['meas_id']['value']
            
            df_metadata[Id] = m['value']

        return df_metadata
       

    def Lab(self, illuminant:Optional[str] = 'D65', observer:Optional[str] = '10'):
        """
        Retrieve the CIE L*a*b* values.

        Parameters
        ----------
        illuminant : (str, optional)  
            Reference *illuminant* ('D65', or 'D50'). by default 'D65'.
 
        observer : (str|int, optional)
            Reference *observer* in degree ('10' or '2'). by default '10'.

            
        Returns
        -------
        pandas dataframe
            It returns the L*a*b* values inside a dataframe where each column corresponds to a single file.
        """        
        observer = str(observer)

        illuminants = {'D65':colour.SDS_ILLUMINANTS['D65'], 'D50':colour.SDS_ILLUMINANTS['D50']}
        observers = {
            '10': 'cie_10_1964',
            '2' : 'cie_2_1931',
        }
        cmfs_observers = {
            '10': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1964 10 Degree Standard Observer"],
            '2': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1931 2 Degree Standard Observer"] 
            }
        
        ccs_ill = colour.CCS_ILLUMINANTS[observers[observer]][illuminant]

        meas_ids = self.meas_ids

        if self.stdev:
            df_sp = [x['mean'] for x in self.get_data(data='sp')]
        else:
            df_sp = self.get_data(data='sp')

        df_Lab = []
        

        for df, meas_id in zip(df_sp, meas_ids):            
            Lab_values = pd.DataFrame(index=['L*','a*','b*']).T           
            
            for col in df.columns:
                
                sp = df[col]
                wl = df.index
                sd = colour.SpectralDistribution(sp,wl)                

                XYZ = colour.sd_to_XYZ(sd,cmfs_observers[observer], illuminant=illuminants[illuminant])        
                Lab = np.round(colour.XYZ_to_Lab(XYZ/100,ccs_ill),2)               
                Lab_values = pd.concat([Lab_values, pd.DataFrame(Lab, index=['L*','a*','b*']).T], axis=0)
                Lab_values.index = np.arange(0,Lab_values.shape[0])

            Lab_values.columns = pd.MultiIndex.from_product([[meas_id], Lab_values.columns])
            df_Lab.append(Lab_values)

        return pd.concat(df_Lab, axis=1)
    

    @property
    def meas_ids(self):
        info = self.get_metadata()        
        return info.loc['meas_id'].values


    def mean(self, return_data:Optional[bool] = True, path:Optional[str] = 'none', criterion:Optional['str'] = 'group'):

        if len(self.files) < 2:        
            raise RuntimeError('Not enough files. At least two measurement files are required to compute the average values.')
        

        def mean_std_with_nan(arrays):
            '''Compute the mean of several numpy arrays of different shapes.'''
            
            # Find the maximum shape
            max_shape = np.max([arr.shape for arr in arrays], axis=0)
                    
            # Create arrays with NaN values
            nan_arrays = [np.full(max_shape, np.nan) for _ in range(len(arrays))]
                    
            # Fill NaN arrays with actual values
            for i, arr in enumerate(arrays):
                nan_arrays[i][:arr.shape[0], :arr.shape[1]] = arr
                    
            # Calculate mean
            mean_array = np.nanmean(np.stack(nan_arrays), axis=0)

            # Calculate std
            std_array = np.nanstd(np.stack(nan_arrays), axis=0)
                    
            return mean_array, std_array
        
        
        def to_float(x):
            try:
                return float(x)
            except ValueError:
                return x


        ###### SPECTRAL DATA #######

        data_sp = self.get_data(data='sp')

        # Get the energy dose step
        H_values = [x.columns.astype(float) for x in data_sp]       
        step_H = sorted(set([x[2] - x[1] for x in H_values]))[0]
        highest_He = np.max([x[-1] for x in H_values])

        # Average the spectral data
        sp = mean_std_with_nan(data_sp)
        sp_mean = sp[0]
        sp_std = sp[1] 
       

        # Wanted energy dose values          
        wanted_H = np.round(np.arange(0,highest_He+step_H,step_H),1)  

        if len(wanted_H) != sp_mean.shape[1]:            
            wanted_H = np.linspace(0,highest_He,sp_mean.shape[1])

        # Retrieve the wavelength range
        wl = self.wavelength.iloc[:,0]
        

        # Create a multi-index pandas DataFrame
        H_tuples = [(dose, measurement) for dose in wanted_H for measurement in ['mean', 'std']]
        multiindex_cols = pd.MultiIndex.from_tuples(H_tuples, names=['He_MJ/m2', 'Measurement'])
        
        data_df_sp = np.empty((len(wl), len(wanted_H) * 2))       
        data_df_sp[:, 0::2] = sp_mean
        data_df_sp[:, 1::2] = sp_std
        df_sp_final = pd.DataFrame(data_df_sp,columns=multiindex_cols, index=wl)
        df_sp_final.index.name = 'wavelength_nm'
                  
           

        ###### COLORIMETRIC DATA #######

        data_cl = self.get_data(data='dE')
        columns_cl = data_cl[0].columns

        # Average the colorimetric data    
        cl = mean_std_with_nan(data_cl)
        cl_mean = cl[0]
        cl_std = cl[1]

        # Create a multi-index pandas DataFrame
        cl_tuples = [(x, measurement) for x in data_cl[0].columns for measurement in ['mean', 'std']]
        multiindex_cols = pd.MultiIndex.from_tuples(cl_tuples, names=['coordinates', 'Measurement'])
        
        data_df_cl = np.empty((cl_mean.shape[0], cl_mean.shape[1] * 2))       
        data_df_cl[:, 0::2] = cl_mean
        data_df_cl[:, 1::2] = cl_std
        df_cl_final = pd.DataFrame(data_df_cl,columns=multiindex_cols, )
        df_cl_final.drop([('He_MJ/m2','std'), ('Hv_Mlxh','std'), ('t_sec','std')], axis=1, inplace=True)
        
        mapper = {('He_MJ/m2', 'mean'): ('He_MJ/m2', 'value'), ('Hv_Mlxh', 'mean'): ('Hv_Mlxh', 'value'), ('t_sec', 'mean'): ('t_sec', 'value')}
        df_cl_final.columns = pd.MultiIndex.from_tuples([mapper.get(x, x) for x in df_cl_final.columns])
        
    
        cl_cols = df_cl_final.columns
        cl_cols_level1 = [x[0] for x in cl_cols]
        cl_cols_level2 = [x[1] for x in cl_cols]
        df_cl_final.columns = np.arange(0,df_cl_final.shape[1])

        df_cl_final = pd.concat([pd.DataFrame(data=np.array([cl_cols_level2])), df_cl_final])
        df_cl_final.columns = cl_cols_level1
        df_cl_final = df_cl_final.set_index(df_cl_final.columns[0])
        

        ###### INFO #######

        data_info = self.get_metadata().fillna(' ')

        # Select the first column as a template
        df_info = data_info.iloc[:,0]
        

        # Rename title file
        df_info.rename({'[SINGLE MICRO-FADING ANALYSIS]': '[MEAN MICRO-FADING ANALYSES]'}, inplace=True)

        # Date time
        most_recent_dt = max(data_info.loc['date_time'])
        df_info.loc['date_time'] = most_recent_dt

        # Project data info
        df_info.loc['project_id'] = '_'.join(sorted(set(data_info.loc['project_id'].values)))
        df_info.loc['projectleider'] = '_'.join(sorted(set(data_info.loc['projectleider'].values)))
        df_info.loc['meelezer'] = '_'.join(sorted(set(data_info.loc['meelezer'].values)))
        df_info.loc['aanvraagdatum'] = '_'.join(sorted(set(data_info.loc['aanvraagdatum'].values)))
        df_info.loc['uiterste_datum'] = '_'.join(sorted(set(data_info.loc['uiterste_datum'].values)))

        # Object data info
        if len(set([x.split('_')[0] for x in data_info.loc['institution'].values])) > 1:
            df_info.loc['institution'] = '_'.join(sorted(set([x.split('_')[0] for x in data_info.loc['institution'].values])))
        
        df_info.loc['object_id'] = '_'.join(sorted(set(data_info.loc['object_id'].values)))
        df_info.loc['object_category'] = '_'.join(sorted(set(data_info.loc['object_category'].values)))
        df_info.loc['object_type'] = '_'.join(sorted(set(data_info.loc['object_type'].values)))
        df_info.loc['object_technique'] = '_'.join(sorted(set(data_info.loc['object_technique'].values)))
        df_info.loc['object_title'] = '_'.join(sorted(set(data_info.loc['object_title'].values)))
        df_info.loc['object_name'] = '_'.join(sorted(set(data_info.loc['object_name'].values)))
        df_info.loc['object_creator'] = '_'.join(sorted(set(data_info.loc['object_creator'].values)))
        df_info.loc['object_date'] = '_'.join(sorted(set(data_info.loc['object_date'].values)))
        df_info.loc['object_support'] = '_'.join(sorted(set(data_info.loc['object_support'].values)))
        df_info.loc['color'] = '_'.join(sorted(set(data_info.loc['color'].values)))
        df_info.loc['colorants'] = '_'.join(sorted(set(data_info.loc['colorants'].values)))
        df_info.loc['colorants_name'] = '_'.join(sorted(set(data_info.loc['colorants_name'].values)))
        df_info.loc['binding'] = '_'.join(sorted(set(data_info.loc['binding'].values)))
        df_info.loc['ratio'] = '_'.join(sorted(set(data_info.loc['ratio'].values)))
        df_info.loc['thickness_microns'] = '_'.join(sorted(set(data_info.loc['thickness_microns'].values)))
        df_info.loc['status'] = '_'.join(sorted(set(data_info.loc['status'].values)))

        # Device data info
        if len(set(data_info.loc['device'].values)) > 1:
            df_info.loc['device'] = '_'.join(sorted(set([x.split('_')[0] for x in data_info.loc['device'].values])))
        
        df_info.loc['measurement_mode'] = '_'.join(sorted(set(data_info.loc['measurement_mode'].values)))
        df_info.loc['zoom'] = '_'.join(sorted(set(data_info.loc['zoom'].values)))
        df_info.loc['iris'] = '_'.join(sorted(set(str(data_info.loc['iris'].values))))
        df_info.loc['geometry'] = '_'.join(sorted(set(data_info.loc['geometry'].values)))
        df_info.loc['distance_ill_mm'] = '_'.join(sorted(set(str(data_info.loc['distance_ill_mm'].values))))
        df_info.loc['distance_coll_mm'] = '_'.join(sorted(set(str(data_info.loc['distance_coll_mm'].values))))       

        if len(set(data_info.loc['fiber_fading'].values)) > 1:
            df_info.loc['fiber_fading'] = '_'.join(sorted(set([x.split('_')[0] for x in data_info.loc['fiber_fading'].values])))

        if len(set(data_info.loc['fiber_ill'].values)) > 1:
            df_info.loc['fiber_ill'] = '_'.join(sorted(set([x.split('_')[0] for x in data_info.loc['fiber_ill'].values])))

        if len(set(data_info.loc['fiber_coll'].values)) > 1:
            df_info.loc['fiber_coll'] = '_'.join(sorted(set([x.split('_')[0] for x in data_info.loc['fiber_coll'].values])))

        if len(set(data_info.loc['lamp_fading'].values)) > 1:
            df_info.loc['lamp_fading'] = '_'.join(sorted(set([x.split('_')[0] for x in data_info.loc['lamp_fading'].values])))

        if len(set(data_info.loc['lamp_ill'].values)) > 1:
            df_info.loc['lamp_ill'] = '_'.join(sorted(set([x.split('_')[0] for x in data_info.loc['lamp_ill'].values])))

        if len(set(data_info.loc['filter_fading'].values)) > 1:
            df_info.loc['filter_fading'] = '_'.join(sorted(set([x.split('_')[0] for x in data_info.loc['filter_fading'].values])))

        if len(set(data_info.loc['filter_ill'].values)) > 1:
            df_info.loc['filter_ill'] = '_'.join(sorted(set([x.split('_')[0] for x in data_info.loc['filter_ill'].values])))

        if len(set(data_info.loc['white_ref'].values)) > 1:
            df_info.loc['white_ref'] = '_'.join(sorted(set([x.split('_')[0] for x in data_info.loc['white_ref'].values])))
        

        # Analysis data info
        
        criterion_value = df_info.loc[criterion]
        object_id = df_info.loc['object_id']
        if criterion == 'group':            
            df_info.loc['meas_id'] = f'MF.{object_id}.{criterion_value}'
        elif criterion == 'object' or criterion == 'project':
             df_info.loc['meas_id'] = f'MF.{criterion_value}'
        else:
            print('Choose one of the following options for the criterion parameter: ["group", "object", "project"]')

        meas_nbs = '-'.join([x.split('.')[-1] for x in self.meas_ids])
        df_info.loc['group'] = f'{"-".join(sorted(set(data_info.loc["group"].values)))}_{meas_nbs}'    
        df_info.loc['group_description'] = '_'.join(sorted(set(data_info.loc['group_description'].values)))
        df_info.loc['background'] = '_'.join(sorted(set(data_info.loc['background'].values)))  

        if len(set(data_info.loc['specular_component'].values)) > 1:
            df_info.loc['specular_component'] = '_'.join(sorted(set([x.split('_')[0] for x in data_info.loc['specular_component'].values]))) 

        df_info.loc['integration_time_ms'] = '_'.join([str(x) for x in sorted(set(data_info.loc['integration_time_ms'].values))]) 
        df_info.loc['average'] = '_'.join([str(x) for x in sorted(set(data_info.loc['average'].values))]) 
        df_info.loc['duration_min'] = '_'.join([str(x) for x in sorted(set(data_info.loc['duration_min'].values))]) 
        df_info.loc['interval_sec'] = '_'.join([str(x) for x in sorted(set(data_info.loc['interval_sec'].values))])
        df_info.loc['measurements_N'] = '_'.join([str(x) for x in sorted(set(data_info.loc['measurements_N'].values))])
        df_info.loc['illuminant'] = '_'.join(sorted(set(data_info.loc['illuminant'].values)))
        df_info.loc['observer'] = '_'.join(sorted(set(data_info.loc['observer'].values)))


        # Beam data info

        df_info.loc['beam_photo'] = '_'.join(sorted(set(data_info.loc['beam_photo'].values)))
        df_info.loc['resolution_micron/pixel'] = '_'.join(sorted(set(str(data_info.loc['resolution_micron/pixel'].values))))

        fwhm = data_info.loc['FWHM_micron']
        fwhm_avg = np.mean([i for i in [to_float(x) for x in fwhm] if isinstance(i, (int, float))])
        df_info.loc['FWHM_micron'] = fwhm_avg

        power_info = data_info.loc['power_mW']
        power_avg = np.mean([ufloat_fromstr(x.split('_')[1]) for x in power_info])
        power_ids = '-'.join(sorted(set([x.split('_')[0] for x in power_info])))
        df_info.loc['power_mW'] = f'{power_ids}_{power_avg}' 

        try:
            irr = [ufloat_fromstr(x) for x in data_info.loc['irradiance_W/m**2']]
            irr_avg = np.mean(irr)
        except AttributeError:
            irr = [float(x) for x in data_info.loc['irradiance_W/m**2']]
            irr_avg = np.int32(np.mean(irr))
        
        
        df_info.loc['irradiance_W/m**2'] = irr_avg
       
        lm = [x for x in data_info.loc['luminuous_flux_lm'].values]
        lm_avg = np.round(np.mean(lm),3)
        df_info.loc['luminuous_flux_lm'] = lm_avg

        ill = [x for x in data_info.loc['illuminance_Mlx']]
        ill_avg = np.round(np.mean(ill),3)
        df_info.loc['illuminance_Mlx'] = ill_avg

        
        # Results data info
        df_info.loc['totalDose_He_MJ/m**2'] = df_cl_final.index.values[-1]
        df_info.loc['totalDose_Hv_Mlxh'] = df_cl_final['Hv_Mlxh'].values[-1]
        df_info.loc['fittedEqHe_dE00'] = ''
        df_info.loc['fittedEqHv_dE00'] = ''
        df_info.loc['fittedRate_dE00_at_2Mlxh'] = ''
        df_info.loc['fittedRate_dE00_at_20MJ/m**2'] = ''
        df_info.loc['dE00_at_300klxh'] = ''
        df_info.loc['dE00_at_3MJ/m**2'] = ''
        df_info.loc['dEab_final'] = ufloat(df_cl_final['dE76'].values[-1][0], df_cl_final['dE76'].values[-1][1])
        df_info.loc['dE00_final'] = ufloat(df_cl_final['dE00'].values[-1][0], df_cl_final['dE00'].values[-1][1])
        df_info.loc['dR_VIS_final'] = ufloat(df_cl_final['dR_vis'].values[-1][0], df_cl_final['dR_vis'].values[-1][1])
        df_info.loc['Hv_at_1dE00'] = ''
        df_info.loc['BWSE'] = ''

        # Rename the column
        df_info.name = 'value'
                
        
        ###### SAVE THE MEAN DATAFRAMES #######
        
        if path != 'none':

            # create a excel writer object
            if path == 'default':
                first_filename = self.files[0]                
                saving_filename = Path(first_filename.parent) / f'{first_filename.stem}_MEAN{first_filename.suffix}'

            else:
                saving_filename = path            

            
            with pd.ExcelWriter(saving_filename) as writer:

                df_info.to_excel(writer, sheet_name='info', index=True)
                df_cl_final.to_excel(writer, sheet_name="CIELAB", index=True)
                df_sp_final.to_excel(writer, sheet_name='spectra', index=True)
        

        ###### RETURN THE MEAN DATAFRAMES #######
            
        if return_data:
            return df_info, df_cl_final, df_sp_final
  


    def set_illuminant(self, illuminant:Optional[str] = 'D65', observer:Optional[str] = '10'):
        """_summary_

        Parameters
        ----------
        illuminant : Optional[str], optional
            _description_, by default 'D65'
            It can be any value within the following list: ['A', 'B', 'C', 'D50', 'D55', 'D60', 'D65', 'D75', 'E', 'FL1', 'FL2', 'FL3', 'FL4', 'FL5', 'FL6', 'FL7', 'FL8', 'FL9', 'FL10', 'FL11', 'FL12', 'FL3.1', 'FL3.2', 'FL3.3', 'FL3.4', 'FL3.5', 'FL3.6', 'FL3.7', 'FL3.8', 'FL3.9', 'FL3.10', 'FL3.11', 'FL3.12', 'FL3.13', 'FL3.14', 'FL3.15', 'HP1', 'HP2', 'HP3', 'HP4', 'HP5', 'LED-B1', 'LED-B2', 'LED-B3', 'LED-B4', 'LED-B5', 'LED-BH1', 'LED-RGB1', 'LED-V1', 'LED-V2', 'ID65', 'ID50', 'ISO 7589 Photographic Daylight', 'ISO 7589 Sensitometric Daylight', 'ISO 7589 Studio Tungsten', 'ISO 7589 Sensitometric Studio Tungsten', 'ISO 7589 Photoflood', 'ISO 7589 Sensitometric Photoflood', 'ISO 7589 Sensitometric Printer']

        observer : Optional[str], optional
            Standard observer in degree, by default '10'
            It can be either '2' or '10'

        Returns
        -------
        tuple
            It returns a tuple with two set of values: the chromaticity coordinates of the illuminants (CCS) and the spectral distribution of the illuminants (SDS).
        """

        observers = {
            '10': "cie_10_1964",
            '2' : "cie_2_1931"
        }
       
        CCS = colour.CCS_ILLUMINANTS[observers[observer]][illuminant]
        SDS = colour.SDS_ILLUMINANTS[illuminant]

        return CCS, SDS

     
    def set_observer(self, observer:Optional[str] = '10'):

        observers = {
            '10': "CIE 1964 10 Degree Standard Observer",
            '2' : "CIE 1931 2 Degree Standard Observer"
        }

        return colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER[observers[observer]]
    

    def sp_derivation(self):
        """Compute the first derivative values of reflectance spectra.

        Returns
        -------
        pandas dataframe
            It returns the first derivative values of the reflectance spectra inside a dataframe where each column corresponds to a single file.
        """

        sp = self.get_data(data='sp')                    

        sp_derivation = [pd.DataFrame(pd.concat([pd.DataFrame(np.gradient(x.iloc[:,:], axis=0), index=pd.Series(x.index), columns=x.columns)], axis=1),index=pd.Series(x.index), columns=x.columns) for x in sp]

        return sp_derivation
    

    def sRGB(self, illuminant='D65', observer='10'):
        """Compute the sRGB values. 

        Parameters
        ----------
        illuminant : (str, optional)  
            Reference *illuminant* ('D65', or 'D50'). by default 'D65'.
 
        observer : (str|int, optional)
            Reference *observer* in degree ('10' or '2'). by default '10'.

        Returns
        -------
        pandas dataframe
            It returns the sRGB values inside a dataframe where each column corresponds to a single file.
        """
        observer = str(observer)

        illuminants = {'D65':colour.SDS_ILLUMINANTS['D65'], 'D50':colour.SDS_ILLUMINANTS['D50']}
        observers = {
            '10': 'cie_10_1964',
            '2' : 'cie_2_1931',
        }
        cmfs_observers = {
            '10': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1964 10 Degree Standard Observer"],
            '2': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1931 2 Degree Standard Observer"] 
            }
        
        ccs_ill = colour.CCS_ILLUMINANTS[observers[observer]][illuminant]

        meas_ids = self.meas_ids                
        df_sp = self.get_data(data='sp')       
        df_srgb = []
        

        for df, meas_id in zip(df_sp, meas_ids):
            df = df.set_index('wl-nm_He-MJ/m2')
            srgb_values = pd.DataFrame(index=['R','G','B']).T           
            
            for col in df.columns:
                
                sp = df[col]
                wl = df.index
                sd = colour.SpectralDistribution(sp,wl)                

                XYZ = colour.sd_to_XYZ(sd,cmfs_observers[observer], illuminant=illuminants[illuminant]) 
                srgb = colour.XYZ_to_sRGB(XYZ / 100, illuminant=ccs_ill)                          
                srgb_values = pd.concat([srgb_values, pd.DataFrame(srgb, index=['R','G','B']).T], axis=0)
                srgb_values.index = np.arange(0,srgb_values.shape[0])

            srgb_values.columns = pd.MultiIndex.from_product([[meas_id], srgb_values.columns])
            df_srgb.append(srgb_values)

        return pd.concat(df_srgb, axis=1)


    @property
    def wavelength(self):
        data = self.get_data(data='sp')

        wavelengths = pd.concat([pd.Series(x.index.values) for x in data], axis=1)
        wavelengths.columns = self.meas_ids

        return wavelengths


    def XYZ(self, illuminant:Optional[str] = 'D65', observer:Union[str,int] = '10'):
        """Compute the XYZ values. 

        Parameters
        ----------
        illuminant : (str, optional)  
            Reference *illuminant* ('D65', or 'D50'). by default 'D65'.
 
        observer : (str|int, optional)
            Reference *observer* in degree ('10' or '2'). by default '10'.

        Returns
        -------
        pandas dataframe
            It returns the XYZ values inside a dataframe where each column corresponds to a single file.
        """


        observer = str(observer)

        illuminants = {'D65':colour.SDS_ILLUMINANTS['D65'], 'D50':colour.SDS_ILLUMINANTS['D50']}
        observers = {
            '10': 'cie_10_1964',
            '2' : 'cie_2_1931',
        }
        cmfs_observers = {
            '10': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1964 10 Degree Standard Observer"],
            '2': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1931 2 Degree Standard Observer"] 
            }
        
        ccs_ill = colour.CCS_ILLUMINANTS[observers[observer]][illuminant]

        meas_ids = self.meas_ids                
        df_sp = self.get_data(data='sp')       
        df_XYZ = []
        

        for df, meas_id in zip(df_sp, meas_ids):
            df = df.set_index('wl-nm_He-MJ/m2')
            XYZ_values = pd.DataFrame(index=['X','Y','Z']).T           
            
            for col in df.columns:
                
                sp = df[col]
                wl = df.index
                sd = colour.SpectralDistribution(sp,wl)                

                XYZ = np.round(colour.sd_to_XYZ(sd,cmfs_observers[observer], illuminant=illuminants[illuminant]),3)
                XYZ_values = pd.concat([XYZ_values, pd.DataFrame(XYZ, index=['X','Y','Z']).T], axis=0)
                XYZ_values.index = np.arange(0,XYZ_values.shape[0])

            XYZ_values.columns = pd.MultiIndex.from_product([[meas_id], XYZ_values.columns])
            df_XYZ.append(XYZ_values)

        return pd.concat(df_XYZ, axis=1)


    def xy(self, illuminant:Optional[str] = 'D65', observer:Union[str, int] = '10'):
        """Compute the xy values. 

        Parameters
        ----------
        illuminant : (str, optional)  
            Reference *illuminant* ('D65', or 'D50'). by default 'D65'.
 
        observer : (str|int, optional)
            Reference *observer* in degree ('10' or '2'). by default '10'.

        Returns
        -------
        pandas dataframe
            It returns the xy values inside a dataframe where each column corresponds to a single file.
        """


        observer = str(observer)

        illuminants = {'D65':colour.SDS_ILLUMINANTS['D65'], 'D50':colour.SDS_ILLUMINANTS['D50']}
        observers = {
            '10': 'cie_10_1964',
            '2' : 'cie_2_1931',
        }
        cmfs_observers = {
            '10': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1964 10 Degree Standard Observer"],
            '2': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1931 2 Degree Standard Observer"] 
            }
        
        ccs_ill = colour.CCS_ILLUMINANTS[observers[observer]][illuminant]

        meas_ids = self.meas_ids                
        df_sp = self.get_data(data='sp')       
        df_xy = []
        

        for df, meas_id in zip(df_sp, meas_ids):
            df = df.set_index('wl-nm_He-MJ/m2')
            xy_values = pd.DataFrame(index=['x','y']).T           
            
            for col in df.columns:
                
                sp = df[col]
                wl = df.index
                sd = colour.SpectralDistribution(sp,wl)                

                XYZ = np.round(colour.sd_to_XYZ(sd,cmfs_observers[observer], illuminant=illuminants[illuminant]),3)
                xy = np.round(colour.XYZ_to_xy(XYZ),4)
                xy_values = pd.concat([xy_values, pd.DataFrame(xy, index=['x','y']).T], axis=0)
                xy_values.index = np.arange(0,xy_values.shape[0])

            xy_values.columns = pd.MultiIndex.from_product([[meas_id], xy_values.columns])
            df_xy.append(xy_values)

        return pd.concat(df_xy, axis=1)





















        observer = str(observer)

        illuminants = {'D65':colour.SDS_ILLUMINANTS['D65'], 'D50':colour.SDS_ILLUMINANTS['D50']}
        observers = {
            '10': 'cie_10_1964',
            '2' : 'cie_2_1931',
        }
        cmfs_observers = {
            '10': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1964 10 Degree Standard Observer"],
            '2': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1931 2 Degree Standard Observer"] 
            }
        
        df_xy = pd.DataFrame(index=pd.Series(['x','y']))
        df_sp = self.get_data(data='sp')
        wl = df_sp.index
        
        for col in df_sp.columns:
            sp = df_sp[col]
            sd = colour.SpectralDistribution(sp,wl)

            XYZ = colour.sd_to_XYZ(sd,cmfs_observers[observer], illuminant=illuminants[illuminant]) 
            xy = np.round(colour.XYZ_to_xy(XYZ),4)
            
            df_xy[col] = xy

        return df_xy
    




    

    