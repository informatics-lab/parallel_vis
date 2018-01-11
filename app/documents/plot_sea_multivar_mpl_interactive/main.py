import os
import time
import sys
import urllib.request
import textwrap
import numpy
import iris
import IPython
import ipywidgets
import lib_sea
from sea_plot import SEA_plot

iris.FUTURE.netcdf_promote = True

try:
    get_ipython
    is_notbook = True
except:
    is_notebook = False


# Extract and Load
bucket_name = 'stephen-sea-public-london'
server_address = 'https://s3.eu-west-2.amazonaws.com'

fcast_time = '20171210T0000Z'

N1280_GA6_KEY = 'n1280_ga6'
KM4P4_RA1T_KEY = 'km4p4_ra1t'
KM1P5_INDO_RA1T_KEY = 'indon2km1p5_ra1t'
KM1P5_MAL_RA1T_KEY = 'mal2km1p5_ra1t'
KM1P5_PHI_RA1T_KEY = 'phi2km1p5_ra1t'

datasets = {N1280_GA6_KEY:{'model_name':'N1280 GA6 LAM Model'},
            KM4P4_RA1T_KEY:{'model_name':'SE Asia 4.4KM RA1-T '},
            # KM1P5_INDO_RA1T_KEY:{'model_name':'Indonesia 1.5KM RA1-T'},
            # KM1P5_MAL_RA1T_KEY:{'model_name':'Malaysia 1.5KM RA1-T'},
            # KM1P5_PHI_RA1T_KEY:{'model_name':'Philipines 1.5KM RA1-T'},
           }

s3_base = '{server}/{bucket}/model_data/'.format(server=server_address,
                                                 bucket=bucket_name)
s3_local_base = os.path.join(os.sep,'s3',bucket_name, 'model_data')

for ds_name in datasets.keys():
    fname1 = 'SEA_{conf}_{fct}.nc'.format(conf=ds_name,
                                         fct=fcast_time)
    datasets[ds_name]['fname'] = fname1
    datasets[ds_name]['s3_url'] = os.path.join(s3_base, fname1)
    datasets[ds_name]['s3_local_path'] = os.path.join(s3_local_base, fname1)
    datasets[ds_name]['data'] = None


fname_key = 's3_local_path'


for ds_name in datasets:
    datasets[ds_name]['data'] = iris.load(datasets[ds_name][fname_key])





#set up datasets dictionary

plot_names = ['precipitation',
              'air_temperature',
              'wind_vectors'
            #    'wind_mslp',
            #   'wind_streams',
            #   'mslp',
            #   'cloud_fraction',
            #   ''
             ]

var_names = ['precipitation',
             'air_temperature',
             'wind_speed',
             'wind_vectors',
            #  'cloud_fraction',
            #  'mslp',
            ]

datasets[N1280_GA6_KEY]['var_lookup'] = {'precipitation':'precipitation_flux',
                                 'cloud_fraction': 'cloud_area_fraction_assuming_maximum_random_overlap',
                                 'air_temperature':'air_temperature',
                                 'x_wind':'x_wind',
                                 'y_wind':'y_wind',
                                 'mslp':'air_pressure_at_sea_level',
                                }
datasets[N1280_GA6_KEY]['units'] = {'precipitation':'kg-m-2-hour^-1',
                                 'cloud_fraction': None,
                                 'air_temperature':'celsius',
                                 'x_wind':'miles-hour^-1',
                                 'y_wind':'miles-hour^-1',
                                 'mslp':'hectopascals',
                                }
datasets[KM4P4_RA1T_KEY]['var_lookup'] = {'precipitation':'stratiform_rainfall_rate',
                                  'cloud_fraction': 'cloud_area_fraction_assuming_maximum_random_overlap',
                                  'air_temperature':'air_temperature',
                                  'x_wind':'x_wind',
                                  'y_wind':'y_wind',
                                  'mslp':'air_pressure_at_sea_level',
                                 }
datasets[KM4P4_RA1T_KEY]['units'] = {'precipitation':'kg-m-2-hour^-1',
                                 'cloud_fraction': None,
                                 'air_temperature':'celsius',
                                 'x_wind':'miles-hour^-1',
                                 'y_wind':'miles-hour^-1',
                                 'mslp':'hectopascals',
                                }

# datasets[KM1P5_INDO_RA1T_KEY]['units'] = dict(datasets[KM4P4_RA1T_KEY]['units'])
# datasets[KM1P5_MAL_RA1T_KEY]['units'] = dict(datasets[KM4P4_RA1T_KEY]['units'])
# datasets[KM1P5_PHI_RA1T_KEY]['units'] = dict(datasets[KM4P4_RA1T_KEY]['units'])

# datasets[KM1P5_INDO_RA1T_KEY]['var_lookup'] = dict(datasets[KM4P4_RA1T_KEY]['var_lookup'])
# datasets[KM1P5_MAL_RA1T_KEY]['var_lookup'] = dict(datasets[KM4P4_RA1T_KEY]['var_lookup'])
# datasets[KM1P5_PHI_RA1T_KEY]['var_lookup'] = dict(datasets[KM4P4_RA1T_KEY]['var_lookup'])




for ds_name in datasets:
    print('loading dataset {0}'.format(ds_name))
    for var1 in datasets[ds_name]['var_lookup']:
        print('    loading var {0}'.format(var1))
        datasets[ds_name][var1] = iris.load_cube(datasets[ds_name][fname_key], 
                                                 datasets[ds_name]['var_lookup'][var1])
        if datasets[ds_name]['units'][var1]:
            datasets[ds_name][var1].convert_units(datasets[ds_name]['units'][var1])


# process wind cubes to calculate wind speed
WIND_SPEED_NAME = 'wind_speed'
cube_pow = iris.analysis.maths.exponentiate
for ds_name in datasets:
    print('calculating wind speed for {0}'.format(ds_name))
    cube_x_wind = datasets[ds_name]['x_wind']
    cube_y_wind = datasets[ds_name]['y_wind']
    datasets[ds_name]['wind_speed'] = cube_pow( cube_pow(cube_x_wind, 2.0) +
                                                  cube_pow(cube_y_wind, 2.0),
                                                 0.5 )
    datasets[ds_name]['wind_speed'].rename(WIND_SPEED_NAME)


for ds_name in datasets:
    datasets[ds_name].update(lib_sea.calc_wind_vectors(datasets[ds_name]['x_wind'], 
                                               datasets[ds_name]['y_wind'],
                                               10))

# create regions
region_dict = {'indonesia': [-15.1, 1.0865, 99.875, 120.111],
               'malaysia': [-2.75, 10.7365, 95.25, 108.737],
               'phillipines': [3.1375, 21.349, 115.8, 131.987],
               'se_asia': [-18.0, 29.96, 90.0, 153.96],
              }

#Setup and display plots
plot_opts = lib_sea.create_colour_opts(plot_names)





init_time = 4
init_var = plot_names[-1]
init_region = 'se_asia'
init_model_left = N1280_GA6_KEY # KM4P4_RA1T_KEY
init_model_right = KM4P4_RA1T_KEY # N1280_GA6_KEY


plot_obj_left = SEA_plot(datasets,
                         plot_opts,
                         'plot_sea_left',
                         init_var,
                         init_model_left,
                         init_region,
                        )

plot_obj_left.current_time = init_time
_ = plot_obj_left.create_plot()

plot_obj_right = SEA_plot(datasets,
                    plot_opts,
                    'plot_sea_right',
                    init_var,
                    init_model_right,
                    init_region,
                    )

plot_obj_right.current_time = init_time
_ = plot_obj_right.create_plot()



# Share axes between plots to enable linked zooming and panning
#plot_obj_left.share_axes([plot_obj_right.current_axes])



left = figure_to_object(plot_obj_left.current_figure)
right = figure_to_object(plot_obj_right.current_figure, left)
if not is_notebook:
    curdoc().add_root(row(
        left,
        right
    ))
