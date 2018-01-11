import numpy
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot
import matplotlib.cm
import cartopy
import cartopy.crs
import cartopy.io.img_tiles

class SEA_plot(object):
    TITLE_TEXT_WIDTH = 40
    PRESSURE_LEVELS_HPA = range(980,1030,2)
    def __init__(self, datasets, po1,figname, plot_var, conf1, reg1):
        self.main_plot = None
        self.current_time = 0
        self.plot_options = po1
        self.datasets = datasets
        self.figure_name = figname
        self.current_var = plot_var
        self.current_config = conf1
        self.current_region = reg1
        self.data_bounds = region_dict[self.current_region]
        self.plot_description = self.datasets[self.current_config]['model_name']
        self.show_colorbar = True
        self.setup_plot_funcs()
        self.setup_pressure_labels()
    
    def setup_pressure_labels(self):
        self.mslp_contour_label_dict = {}
        for pressure1 in SEA_plot.PRESSURE_LEVELS_HPA:
            self.mslp_contour_label_dict[pressure1] = '{0:d}hPa'.format(int(pressure1))    

    
    def setup_plot_funcs(self):
        self.plot_funcs = {'precipitation' : self.plot_precip,
                           'wind_vectors' : self.plot_wind_vectors,
                           'wind_mslp' : self.plot_wind_mslp,
                           'wind_streams' : self.plot_wind_streams,
                           'mslp' : self.plot_mslp,
                           'air_temperature' : self.plot_air_temp,
                           'cloud_fraction' :self.plot_cloud,
                          }
        self.update_funcs =  {'precipitation' : self.update_precip,
                           'wind_vectors' : self.update_wind_vectors,
                           'wind_mslp' : self.update_wind_mslp,
                              'wind_streams' : self.update_wind_streams,
                           'mslp' : self.update_mslp,
                           'air_temperature' : self.update_air_temp,
                           'cloud_fraction' :self.update_cloud,
                          }
        
    def update_coords(self, data_cube):
        self.coords_lat = data_cube.coords('latitude')[0].points
        self.coords_long = data_cube.coords('longitude')[0].points
        
    def update_precip(self):
        data_cube = self.datasets[self.current_config][self.current_var]
        array_for_update = data_cube[self.current_time].data[:-1,:-1].ravel()
        self.main_plot.set_array(array_for_update)
        self.update_title(data_cube)
        
    def plot_precip(self):
        data_cube = self.datasets[self.current_config][self.current_var]

        self.update_coords(data_cube)
        self.current_axes.coastlines(resolution='110m')
        self.main_plot = self.current_axes.pcolormesh(self.coords_long, 
                                     self.coords_lat, 
                                     data_cube[self.current_time].data, 
                                     cmap=self.plot_options[self.current_var]['cmap'],
                                     norm=self.plot_options[self.current_var]['norm'],
                                     transform=cartopy.crs.PlateCarree())
        self.update_title(data_cube)

    def update_wind_vectors(self):
        wind_speed_cube = self.datasets[self.current_config]['wind_speed']
        array_for_update = wind_speed_cube[self.current_time].data[:-1,:-1].ravel()
        self.main_plot.set_array(array_for_update)
        self.update_title(wind_speed_cube)
       
        self.quiver_plot.set_UVC(self.datasets[self.current_config]['wv_U'][self.current_time],
                                 self.datasets[self.current_config]['wv_V'][self.current_time],
                                )
    
    def plot_wind_vectors(self):
        wind_speed_cube = self.datasets[self.current_config]['wind_speed']
        self.update_coords(wind_speed_cube)
        self.main_plot = self.current_axes.pcolormesh(self.coords_long, 
                                                      self.coords_lat, 
                                                      wind_speed_cube[self.current_time].data,
                                                      cmap=self.plot_options[self.current_var]['cmap'],
                                                      norm=self.plot_options[self.current_var]['norm']
                                                     )

        # Add coastlines to the map created by contourf.
        coastline_50m = cartopy.feature.NaturalEarthFeature('physical', 
                                                            'coastline', 
                                                            '50m', 
                                                            edgecolor='0.5', 
                                                            facecolor = 'none')
        self.current_axes.add_feature(coastline_50m)
        
        #print(data_wv['xs'])
        self.quiver_plot = self.current_axes.quiver(self.datasets[self.current_config]['wv_X'],
                                               self.datasets[self.current_config]['wv_Y'],
                                               self.datasets[self.current_config]['wv_U'][self.current_time],
                                               self.datasets[self.current_config]['wv_V'][self.current_time],
                                               units='height')
        qk = self.current_axes.quiverkey(self.quiver_plot,
                                             0.9, 
                                             0.9, 
                                             2, 
                                             r'$2 \frac{m}{s}$', 
                                             labelpos='E',
                                             coordinates='figure')    
        self.update_title(wind_speed_cube)
     
    def update_wind_mslp(self):
        wind_speed_cube = self.datasets[self.current_config]['wind_speed']
        array_for_update = wind_speed_cube[self.current_time].data[:-1,:-1].ravel()
        self.main_plot.set_array(array_for_update)
        # to update contours, remove old elements and generate new contours
        for c1 in self.mslp_contour.collections:
            self.current_axes.collections.remove(c1)
            
        ap_cube = self.datasets[self.current_config]['mslp']            
        self.mslp_contour = self.current_axes.contour(self.long_grid_mslp,
                                                      self.lat_grid_mslp,
                                                      ap_cube[self.current_time].data,
                                                      levels=SEA_plot.PRESSURE_LEVELS_HPA,
                                                      colors='k')
        self.current_axes.clabel(self.mslp_contour, 
                                 inline=False, 
                                 fmt=self.mslp_contour_label_dict)        
        
        self.update_title(wind_speed_cube)

        
    def plot_wind_mslp(self):
        wind_speed_cube = self.datasets[self.current_config]['wind_speed']
        self.update_coords(wind_speed_cube)
        self.main_plot = self.current_axes.pcolormesh(self.coords_long, 
                                                      self.coords_lat, 
                                                      wind_speed_cube[self.current_time].data,
                                                      cmap=self.plot_options[self.current_var]['cmap'],
                                                      norm=self.plot_options[self.current_var]['norm']
                                                     )
        
        ap_cube = self.datasets[self.current_config]['mslp']
        lat_mslp = ap_cube.coords('latitude')[0].points
        long_mslp = ap_cube.coords('longitude')[0].points
        self.long_grid_mslp, self.lat_grid_mslp = numpy.meshgrid(long_mslp, lat_mslp)
        self.mslp_contour = self.current_axes.contour(self.long_grid_mslp,
                                                      self.lat_grid_mslp,
                                                      ap_cube[self.current_time].data,
                                                      levels=SEA_plot.PRESSURE_LEVELS_HPA,
                                                      colors='k')
        self.current_axes.clabel(self.mslp_contour, 
                                 inline=False, 
                                 fmt=self.mslp_contour_label_dict)


        # Add coastlines to the map created by contourf.
        coastline_50m = cartopy.feature.NaturalEarthFeature('physical', 
                                                            'coastline', 
                                                            '50m', 
                                                            edgecolor='0.5', 
                                                            facecolor = 'none')
        
        self.current_axes.add_feature(coastline_50m)    
        self.update_title(wind_speed_cube)

    def update_wind_streams(self):
        wind_speed_cube = self.datasets[self.current_config]['wind_speed']
        array_for_update = wind_speed_cube[self.current_time].data[:-1,:-1].ravel()
        self.main_plot.set_array(array_for_update)
        self.update_title(wind_speed_cube)
        
        # remove old plot elements if they are still present
        self.current_axes.collections.remove(self.wind_stream_plot.lines)
        for p1 in self.wind_stream_patches:
            self.current_axes.patches.remove(p1)
        
        pl1 = list(self.current_axes.patches)    
        self.wind_stream_plot = self.current_axes.streamplot(self.datasets[self.current_config]['wv_X_grid'],
                                      self.datasets[self.current_config]['wv_Y_grid'],
                                      self.datasets[self.current_config]['wv_U'][self.current_time],
                                      self.datasets[self.current_config]['wv_V'][self.current_time],
                                      color='k',
                                      density=[0.5,1.0])   
        # we need to manually keep track of arrows so they can be removed when the plot is updated
        pl2 = list(self.current_axes.patches)
        self.wind_stream_patches = [p1 for p1 in pl2 if p1 not in pl1]
        
        
       
    def plot_wind_streams(self):
        wind_speed_cube = self.datasets[self.current_config]['wind_speed']
        self.update_coords(wind_speed_cube)
        self.main_plot = self.current_axes.pcolormesh(self.coords_long, 
                                                      self.coords_lat, 
                                                      wind_speed_cube[self.current_time].data,
                                                      cmap=self.plot_options[self.current_var]['cmap'],
                                                      norm=self.plot_options[self.current_var]['norm']
                                                     )
        pl1 = list(self.current_axes.patches)
        self.wind_stream_plot = self.current_axes.streamplot(self.datasets[self.current_config]['wv_X_grid'],
                                      self.datasets[self.current_config]['wv_Y_grid'],
                                      self.datasets[self.current_config]['wv_U'][self.current_time],
                                      self.datasets[self.current_config]['wv_V'][self.current_time],
                                      color='k',
                                      density=[0.5,1.0])
        
        
        # we need to manually keep track of arrows so they can be removed when the plot is updated
        pl2 = list(self.current_axes.patches)
        self.wind_stream_patches = [p1 for p1 in pl2 if p1 not in pl1]

        # Add coastlines to the map created by contourf.
        coastline_50m = cartopy.feature.NaturalEarthFeature('physical', 
                                                            'coastline', 
                                                            '50m', 
                                                            edgecolor='0.5', 
                                                            facecolor = 'none')
        self.current_axes.add_feature(coastline_50m)    
        self.update_title(wind_speed_cube)        

    def update_air_temp(self):
        at_cube = self.datasets[self.current_config][self.current_var]
        array_for_update = at_cube[self.current_time].data[:-1,:-1].ravel()
        self.main_plot.set_array(array_for_update)
        self.update_title(at_cube)
        
    def plot_air_temp(self):
        at_cube = self.datasets[self.current_config][self.current_var]
        self.update_coords(at_cube)
        self.main_plot = matplotlib.pyplot.pcolormesh(self.coords_long, 
                                                      self.coords_lat, 
                                                      at_cube[self.current_time].data,
                                                      cmap=self.plot_options[self.current_var]['cmap'],
                                                      norm=self.plot_options[self.current_var]['norm']
                                                     )

        # Add coastlines to the map created by contourf.
        coastline_50m = cartopy.feature.NaturalEarthFeature('physical', 
                                                            'coastline', 
                                                            '50m', 
                                                            edgecolor='0.5', 
                                                            facecolor = 'none')
        self.current_axes.add_feature(coastline_50m)    
        self.update_title(at_cube)

    def update_mslp(self):
        ap_cube = self.datasets[self.current_config][self.current_var]
        array_for_update = ap_cube[self.current_time].data[:-1,:-1].ravel()
        self.main_plot.set_array(array_for_update)
        self.update_title(ap_cube)
    
    def plot_mslp(self):
        ap_cube = self.datasets[self.current_config][self.current_var]
        self.update_coords(ap_cube)
        self.main_plot = matplotlib.pyplot.pcolormesh(self.coords_long, 
                                                      self.coords_lat, 
                                                      ap_cube[self.current_time].data,
                                                      cmap=self.plot_options[self.current_var]['cmap'],
                                                      norm=self.plot_options[self.current_var]['norm']
                                                     )

        # Add coastlines to the map created by contourf.
        coastline_50m = cartopy.feature.NaturalEarthFeature('physical', 
                                                            'coastline', 
                                                            '50m', 
                                                            edgecolor='0.5', 
                                                            facecolor = 'none')
        self.current_axes.add_feature(coastline_50m)    
        self.update_title(ap_cube)
        

    def update_cloud(self):
        cloud_cube = self.datasets[self.current_config][self.current_var]
        array_for_update = cloud_cube[self.current_time].data[:-1,:-1].ravel()
        self.main_plot.set_array(array_for_update)
        self.update_title(cloud_cube)
    
    def plot_cloud(self):
        cloud_cube = self.datasets[self.current_config][self.current_var]
        self.update_coords(cloud_cube)
        self.main_plot = matplotlib.pyplot.pcolormesh(self.coords_long, 
                                                      self.coords_lat, 
                                                      cloud_cube[self.current_time].data,
                                                      cmap=self.plot_options[self.current_var]['cmap'],
                                                      norm=self.plot_options[self.current_var]['norm']
                                                     )

        # Add coastlines to the map created by contourf.
        coastline_50m = cartopy.feature.NaturalEarthFeature('physical', 
                                                            'coastline', 
                                                            '50m', 
                                                            edgecolor='0.5', 
                                                            facecolor = 'none')
        self.current_axes.add_feature(coastline_50m)   
        self.update_title(cloud_cube)
 
    def update_title(self, current_cube):
        datestr1 = lib_sea.get_time_str(current_cube.dim_coords[0].points[self.current_time])
        
        str1 = '{plot_desc} {var_name} at {fcst_time}'.format(var_name=self.current_var,
                                                              fcst_time=datestr1,
                                                              plot_desc=self.plot_description,
                                                             )
        self.current_title = '\n'.join(textwrap.wrap(str1, 
                                                     SEA_plot.TITLE_TEXT_WIDTH)) 
        
    def create_plot(self):
        
        self.current_figure = matplotlib.pyplot.figure(self.figure_name, dpi=200,
                                      figsize=matplotlib.pyplot.figaspect(1.0))
        self.current_figure.clf()
        self.current_axes = self.current_figure.add_subplot(111, projection=cartopy.crs.PlateCarree())

        self.plot_funcs[self.current_var]()
        self.current_axes.set_title(self.current_title)
        self.current_axes.set_xlim(self.data_bounds[2], self.data_bounds[3])
        self.current_axes.set_ylim(self.data_bounds[0], self.data_bounds[1])
        self.current_axes.xaxis.set_visible(True)
        self.current_axes.yaxis.set_visible(True)
        if self.show_colorbar:
            self.current_figure.colorbar(self.main_plot,
                                         orientation='horizontal')

        self.current_figure.tight_layout()
        #matplotlib.pyplot.show()
        return self.main_plot

    def update_plot(self):
        # do relevant update
        self.update_funcs[self.current_var]()
        self.current_axes.set_title(self.current_title)
        self.current_figure.canvas.draw_idle()
        
    def share_axes(self, axes_list):
        self.current_axes.get_shared_x_axes().join(self.current_axes, *axes_list)
        self.current_axes.get_shared_y_axes().join(self.current_axes, *axes_list)

        
    def on_data_time_change(self, event1):
        self.current_time = event1['new']
        self.update_plot()
        #self.create_plot()
        
    def on_var_change(self, event1):
        self.current_var = event1['new']
        self.create_plot()
        
    def on_region_change(self, event1):
        self.current_region = event1['new']
        self.data_bounds = region_dict[self.current_region]
        self.create_plot()
    
    def on_config_change(self, event1):
        self.current_config = event1['new']
        self.plot_description = self.datasets[self.current_config]['model_name']
        self.create_plot()


