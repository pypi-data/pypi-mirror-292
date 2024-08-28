import xarray as xr
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import shutil
import math
from scipy import stats
import warnings
import rasterio
import yaml
import geopandas as gpd
from shapely.geometry import Point  
import os
import tqdm


warnings.filterwarnings("ignore")


def sort_files_by_date(source_dir):  
    """  
    Sorts .nc files in the specified directory by date and moves them into folders named with the dates.  

    Parameters:  
    - source_dir: The path to the source directory containing the .nc files.  
    """  
    # Iterate through all files and folders in the source directory  
    for filename in os.listdir(source_dir):  
        
        if filename.endswith('.nc'):  
            
            start_date_str = filename[12:20]   

            # Create the target directory (if it doesn't exist)  
            target_dir = os.path.join(source_dir, start_date_str)  
            if not os.path.exists(target_dir):  
                os.makedirs(target_dir)  

            
            source_path = os.path.join(source_dir, filename)  
            target_path = os.path.join(target_dir, filename)  

            
            shutil.move(source_path, target_path)  

    print(f"Files in the source directory {source_dir} have been sorted and moved into folders by date.")  


def read_data(f_list: str):

    """  
    Read multiple NetCDF files into a single xarray Dataset.   

    Parameters:  
    - f_list: Files path pointing to the NetCDF files to be read.  

    Returns:  
    - ds (xarray.Dataset): A single xarray Dataset containing the concatenated data from  
    the input files.  
    """  
    # print('The input parameter is the data path: ~\path\*.nc')
    
    ds = xr.open_mfdataset(f_list, concat_dim="sample", combine="nested",
                data_vars='minimal', coords='minimal', compat='override')
    
    return ds



def _check_quality_flags(quality_flags,bit_values_str,bit_list):  
      
    binary_str = format(int(quality_flags), '031b')  
     
    qf_str = ''.join(binary_str[index] for index in bit_list)  
      
    return qf_str == bit_values_str 



def quality_control_default(df_original: pd.DataFrame, ds: xr.Dataset) -> pd.DataFrame:  
    
    if df_original.empty:  
        raise ValueError("Your DataFrame is empty")
    
    
    output_info = """The quality control criteria adopted for this function are as follows: 
                    1. quality_flags: s_band_powered_up, large_sc_attitude_err, black_body_ddm, ddm_is_test_pattern,  
                    direct_signal_in_ddm, low_confidence_gps_eirp_estimate, and sp_over_land 
                    2. sp_inc_angle: less than 65 degrees   
                    3. sp_rx_gain: greater than or equal to 0 
                    4. ddm_snr: greater than or equal to 2  
                    5. brcs_ddm_peak_bin_delay_row: between 4 and 15th """
    print(output_info)

    df = df_original.copy()

    original_columns = df.columns.to_list()
    required_columns = ['quality_flags', 'sp_inc_angle', 'sp_rx_gain', 'ddm_snr', 'brcs_ddm_peak_bin_delay_row']  
    missing_columns = set(required_columns) - set(original_columns)  
    
 
    for col in missing_columns:  
        if col in ds:  
            df[col] = ds[col].values.flatten()  
        else:  
            raise ValueError(f"Dataset {ds} does not contain the required column: {col}")  
  
    df['quality_check'] = df['quality_flags'].apply(lambda x: _check_quality_flags(x,'0000100',[-2,-4,-5,-8,-11,-16,-17]))  
  
      
    df_filtered = df[  
        (df['quality_check'] == True) &  
        (df['sp_inc_angle'] <= 65) &  
        (df['sp_rx_gain'] >= 0) &  
        (df['ddm_snr'] >= 2) &  
        (df['brcs_ddm_peak_bin_delay_row'] >= 4) &  
        (df['brcs_ddm_peak_bin_delay_row'] <= 15)  
    ]  
  
    df_filtered = df_filtered[original_columns]
    print('The number of sampling points before and after quality control is:', len(df_original),'and', len(df_filtered),'respectively.')
    return df_filtered


def quality_control_custom(df_original: pd.DataFrame,ds: xr.Dataset,config_file: str) -> pd.DataFrame:

    df = df_original.copy()

    if df.empty:  
        raise ValueError("Your DataFrame is empty")

    with open(config_file, 'r') as file:  
        
        config = yaml.safe_load(file)

        required_columns = list(config.keys())[:-1]  
        missing_columns = set(required_columns) - set(df.columns)  
       

        if missing_columns:  
                
            for col in missing_columns:  
                if col in ds:  
                    df[col] = ds[col].values.flatten() 
            
                else:  
                    raise ValueError(f"Dataset {ds} does not contain the variable: {col}")  
                

        qc_list = config['CYGNSS L1 V3.1 quality_flags lookup table'] 
        qc_dict = {item['name']: -int(item['bit']) for item in qc_list} # CYGNSS L1 V3.1 质量标签和对应的索引
     

        quality_flags = config['quality_flags'] #用户自定义的质量标签
        bit_values_list = [value for dict_ in quality_flags for value in dict_.values()] #用户自定义的质量标签对应的值列表
        bit_values_str = ''.join([str(value) for value in bit_values_list]) #用户自定义的质量标签对应的值列表字符串
        

        bit_list = [] #用户自定义的质量标签对应的索引
        #根据用户自定的质量标签获取对应的索引
        for flag in quality_flags:
        
            keys_str = ''.join(flag.keys())
            
            if keys_str in qc_dict:
            
                bit_list.append(qc_dict[keys_str])
            else:
                raise ValueError(f"The quality flag {keys_str} is not in the CYGNSS L1 V3.1 quality_flags lookup table")

           
        df['quality_check'] = df['quality_flags'].apply(lambda x: _check_quality_flags(x,bit_values_str,bit_list))

        quality_check_condition = 'quality_check'  
        empirical_qc = [(col, op) for col, op in config.items() if col not in ['CYGNSS L1 V3.1 quality_flags lookup table', 'quality_flags']]
        
        
        query_str = f"{quality_check_condition} & {' & '.join([    
            f'({col} {op.split(',')[0].strip()})' if ',' not in op else    
            f'(({col} {op.split(',')[0].strip()}) & ({col} {op.split(',')[1].strip()}))'    
            for col, op in empirical_qc    
        ])}" 
        

        df_filtered = df.query(query_str)[df_original.columns]
        print('The number of sampling points before and after quality control is:', len(df_original),'and', len(df_filtered),'respectively.')
        return df_filtered
      


def extract_obs(ds: xr.Dataset, obs_list: list, quality_control: bool = False, quality_control_method: str = 'default',config_file: str = None) -> pd.DataFrame:  
    """  
    Extract and flatten specified variables from an xarray.Dataset into a pandas.DataFrame.  

    Parameters:  
    - ds (xarray.Dataset): The xarray Dataset containing the variables to be extracted.  
    - obs_list (List[str]): A list of strings specifying the names of the variables to extract.  

    Returns:  
    - pd.DataFrame: A pandas DataFrame where each column corresponds to a variable from obs_list,  
                    and the data is flattened (converted to a 1D array) from the original shape.   
    """  
    
    if not obs_list or not all(isinstance(obs, str) for obs in obs_list):  
        raise ValueError("obs_list must be a non-empty list of strings")


    df = pd.DataFrame()  


    for obs in tqdm(obs_list, desc="Processing variables"):  
        if obs in ds:  
            # Check the dimensions of the variable  
            dims = ds[obs].dims  

            if 'delay' in dims and 'doppler' in dims:  
                # Perform max reduction over 'delay' and 'doppler'  
                flattened_data = ds[obs].max(('delay', 'doppler')).values.flatten()  
                print(f"Info: Variable '{obs}' applies a maximum reduction along the 'delay' and 'doppler' dimensions.")  
            else:  
                # For variables without 'delay' and 'doppler', just flatten  
                flattened_data = ds[obs].values.flatten()     

            df[obs] = flattened_data  
        
        else:  
            print(f"Warning: Variable '{obs}' not found in the Dataset.")  
    
    if 'sp_lon' in df.columns:  
        df.loc[df['sp_lon'] > 180, 'sp_lon'] -= 360  

    if quality_control:  
        if quality_control_method == 'default':  
            df = quality_control_default(df, ds)  
        elif quality_control_method == 'custom':    
            df = quality_control_custom(config_file,df,ds)  
        else:  
            raise ValueError("Unsupported quality control method. Choose 'default' or 'custom'.") 


    return df



def cal_sr(ds: xr.Dataset, quality_control: bool = False, quality_control_method: str = 'default',config_file: str = None) -> pd.DataFrame:  
      
    df = pd.DataFrame()  
      
    required_columns = ['power_analog', 'gps_eirp', 'sp_rx_gain', 'rx_to_sp_range', 'tx_to_sp_range', 'sp_lon', 'sp_lat']  
    final_columns = ['sr', 'sp_lat', 'sp_lon']  
      
    for col in required_columns:  
        if col == 'power_analog':  
            df[col] = ds[col].max(('delay', 'doppler')).values.flatten()  
        else:  
            df[col] = ds[col].values.flatten()  
  
    sr = 10*np.log10(df['power_analog'])-10*np.log10(df['gps_eirp'])-10*np.log10(df['sp_rx_gain'])-20*np.log10(0.1904)+20*np.log10(df['rx_to_sp_range']+df['tx_to_sp_range'])+20*np.log10(4*math.pi)  
  
    df['sr'] = sr  
  
    df.loc[df['sp_lon'] > 180, 'sp_lon'] -= 360  
  
    df = df[final_columns]  
  
    if quality_control:  
        if quality_control_method == 'default':  
            df = quality_control_default(df, ds)  
        elif quality_control_method == 'custom':    
            df = quality_control_custom(config_file,df,ds)  
        else:  
            raise ValueError("Unsupported quality control method. Choose 'default' or 'custom'.")  
  
    return df



def filter_data_by_lonlat(df_original: pd.DataFrame, region: list) -> pd.DataFrame:  
    """  
    Filters a DataFrame based on a given longitude and latitude range.  

    Args:  
        df (pd.DataFrame): The DataFrame to be filtered.  
        region (list): A list containing four elements representing the minimum longitude, maximum longitude,  
                    minimum latitude, and maximum latitude respectively, in the order: [lon_min, lon_max, lat_min, lat_max].  

    Returns:  
        pd.DataFrame: The filtered DataFrame containing only the rows that fall within the specified region.  
    """  
    
    if 'sp_lon' not in df_original.columns or 'sp_lat' not in df_original.columns:  
        raise ValueError("DataFrame must contain 'sp_lon' and 'sp_lat' columns.")  

    
    if len(region) != 4:  
        raise ValueError("Region list must contain exactly 4 elements: [lon_min, lon_max, lat_min, lat_max].")  

    
    lon_min, lon_max, lat_min, lat_max = region  


    if lon_min > lon_max or lat_min > lat_max:  
        raise ValueError("Longitude and latitude ranges must be specified in ascending order.")  
    
    
    df = df_original.copy() 

    df_region = df[(df['sp_lon'] >= lon_min) & (df['sp_lon'] <= lon_max) &  
                    (df['sp_lat'] >= lat_min) & (df['sp_lat'] <= lat_max)]  
        
    return  df_region 



def filter_data_by_vector(df: pd.DataFrame, vector_path: str) -> pd.DataFrame: 

    if 'sp_lon' not in df.columns or 'sp_lat' not in df.columns:  
        raise ValueError("DataFrame must contain 'sp_lon' and 'sp_lat' columns.")  
      
    if not os.path.exists(vector_path):  
        raise FileNotFoundError(f"The file {vector_path} does not exist.")  
       
    try:  
        gdf_shp = gpd.read_file(vector_path)  
    except Exception as e:  
        raise ValueError(f"Failed to read the file {vector_path}: {e}")   
     

    geometry = [Point(xy) for xy in zip(df['sp_lon'], df['sp_lat'])]  
    gdf_points = gpd.GeoDataFrame(df, geometry=geometry)  
      
    boundary_union = gdf_shp.unary_union  
    
    is_within = gdf_points.within(boundary_union)  

    result = df[is_within]  
      
    return result 




def filter_data_by_watermask(tif_path,df_original: pd.DataFrame) -> pd.DataFrame:

    df = df_original.copy()
    
    if 'sp_lon' not in df.columns or 'sp_lat' not in df.columns:  
        raise ValueError("DataFrame must contain 'sp_lon' and 'sp_lat' columns.")  


    if not os.path.exists(tif_path):  
        raise FileNotFoundError(f"The file {tif_path} does not exist.")  

        
    coords = [(x, y) for x, y in zip(df.sp_lon, df.sp_lat)]  

    ds = rasterio.open(tif_path)
    
    
    df['water_id'] = [x[0] for x in ds.sample(coords)]
    
    df = df[~(df['water_id'] >= 1) & (df['water_id'] <= 12)]
    
    df = df.drop('water_id',axis = 1)

    return df 
    


def grid_obs(df: pd.DataFrame, lats: np.ndarray, lons: np.ndarray, obs_list: list):  
    """  
    Grid and compute the mean of gnss-r observations for multiple variables.  
  
    Parameters:  
    - df: Pandas DataFrame containing the observations.  
    - lats: 1D numpy array of latitude bin edges.  
    - lons: 1D numpy array of longitude bin edges.  
    - obs_list: List of column names in `df` to grid and compute means for.  
  
    Returns:  
    - Dictionary containing the gridded and meaned observations for each variable in `obs_list`.   
    """  
      
    if not (lats.ndim == 1 and lons.ndim == 1 and np.all(np.diff(lats) > 0) and np.all(np.diff(lons) > 0)):  
        raise ValueError("Both `lats` and `lons` must be 1D arrays and sorted in ascending order.")  
    
    print('Please check your input data, make sure the second parameter is latitude boundaries and the third parameter is longitude boundaries.')

    required_columns = ['sp_lat', 'sp_lon'] + obs_list  
    missing_columns = [col for col in required_columns if col not in df.columns]  
    if missing_columns:  
        raise ValueError(f"The DataFrame is missing the following required columns: {', '.join(missing_columns)}")  
  
    gridded_results = {}  
  
    for obs in obs_list:  
        statistic, _, _, _ = stats.binned_statistic_2d(  
            df['sp_lat'], df['sp_lon'], values=df[obs], statistic='mean',  
            bins=[lats, lons]  
        )  
        gridded_results[obs] = statistic   
  
    return gridded_results




# def grid_36km(df: pd.DataFrame, obs:str):
#     """  
#     Grid and compute the mean of gnss-r observations..    

#     Notes:  
#     - It is important that the `lats` and `lons` arrays are sorted in ascending order,  
#     as `binned_statistic_2d` expects the bin edges to be in increasing order.  
#     """  
        
#     lats_filepath = 'EASE2_M36km.lats.964x406x1.double'  
#     lons_filepath = 'EASE2_M36km.lons.964x406x1.double'  


#     for filepath in [lats_filepath, lons_filepath]:  
#         if not os.path.exists(filepath):  
#             raise FileNotFoundError(f"EASE-GRID file {filepath} does not exist in the current working path. \n"  
#                                     f"You can download it from [https://code.mpimet.mpg.de/boards/1/topics/9593?r=9596#message-9596].")  

#     required_columns = ['sp_lat', 'sp_lon', obs]  
#     missing_columns = [col for col in required_columns if col not in df.columns]  
#     if missing_columns:  
#         raise ValueError(f"The DataFrame is missing the following required columns: {', '.join(missing_columns)}")  

#     lats = np.fromfile(lats_filepath, dtype=np.float64).reshape((406, 964))  
#     lons = np.fromfile(lons_filepath, dtype=np.float64).reshape((406, 964))  

#     statistic, xedges, yedges, binnumber = stats.binned_statistic_2d(
#     df['sp_lat'], df['sp_lon'], values=df[obs], statistic='mean', 
#     bins=[lats[:,0][::-1], lons[0,:]])
    
#     grid_obs = np.flipud(statistic)

#     return grid_obs



def plot_obs(df: pd.DataFrame):
    pass



