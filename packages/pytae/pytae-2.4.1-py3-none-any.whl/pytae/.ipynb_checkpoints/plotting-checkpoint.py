import warnings
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes




class Plotter:
    def __init__(self, mosaic=None,figsize=None):
        if mosaic is not None:
            self.fig, self.axd = plt.subplot_mosaic(mosaic=mosaic,figsize=figsize)
        else:
            self.fig, ax = plt.subplots(figsize=figsize)
            self.axd = {'default': ax}
        self.last_kwargs = {}
        self.df = None
        plt.close()

        

    def data(self, df):
        self.df = df
        self.last_kwargs = {}  # Reset kwargs when new data is provided
        return self

    def plot(self, **kwargs):
        self._update_kwargs(kwargs)
        ax = self._get_target_axis()

        if self.kind == 'scatter':
            self._plot_scatter(ax)
        elif self.kind == 'hexbin':
            self._plot_hexbin(ax)
        elif self.kind in ['line']:
            self._plot_line(ax)
        elif self.kind in ['bin']:
            self._plot_bin(ax)
        elif self.kind in ['kde','density']:
            self._plot_density(ax)
        elif self.kind == 'pie':
            self._plot_pie(ax)
        elif self.kind == 'hist':
            self._plot_hist(ax)
        else:
            self._plot_other(ax)

        return self

    def _update_kwargs(self, kwargs):
        # Extract print_data and clip_data before updating last_kwargs
        self.print_data = kwargs.get('print_data', False)
        self.clip_data = kwargs.get('clip_data', False)
    
        # Store the current kind and check if it has changed
        new_kind = kwargs.get('kind', self.current_kind if hasattr(self, 'current_kind') else 'line')
        
        if hasattr(self, 'current_kind') and self.current_kind != new_kind:
            self.last_kwargs = {}  # Reset kwargs if kind changes
        self.current_kind = new_kind
        
        # Combine kwargs but exclude print_data and clip_data from last_kwargs
        combined_kwargs = {**self.last_kwargs, **kwargs}
        self.last_kwargs = {k: v for k, v in combined_kwargs.items() if k not in ['print_data', 'clip_data']}
        
        self.x = combined_kwargs.get('x', None)
        self.y = combined_kwargs.get('y', None)
        self.by = combined_kwargs.get('by', None)
        self.column = combined_kwargs.get('column', None)
        self.kind = new_kind
        self.aggfunc = combined_kwargs.get('aggfunc', None) if self.kind in ['scatter', 'density', 'kde', 'hist'] else combined_kwargs.get('aggfunc', 'sum')
        self.dropna = combined_kwargs.get('dropna', False)

    

    def _get_target_axis(self):
        ax_key = self.last_kwargs.get('on', 'default')
        return self.axd.get(ax_key, self.axd.get('default'))

            
     

    def _plot_scatter(self,ax):
        plot_dict = self._filter_plot_kwargs([ 'by','aggfunc','dropna','on','print_data','clip_data'])

 
        if 'aggfunc' in self.last_kwargs:
            warnings.warn("Aggregation is not supported for scatter plots. The 'aggfunc' argument will be ignored.")
        if 'dropna' in self.last_kwargs:
            warnings.warn("The 'dropna' argument is not applicable to scatter plots and will be ignored.")
        if 'by' in self.last_kwargs:
            warnings.warn("Use 'c' and 'cmap' to split the scatter plot by a particular column. The 'by' argument will be ignored.")
        k=self.df.copy()

        c = plot_dict.get('c', None) 
        
        if c: #c needs to be categorical
            
            k[c] = k[c].astype('category')
    

        self.ax = k.plot(ax=ax,  **plot_dict)

        
        self._handle_data_output(k)
            
    def _plot_pie(self,ax):
        plot_dict = self._filter_plot_kwargs([ 'x','by','aggfunc','on','print_data','clip_data'])

        self.df=self.df[[self.by,self.y]].groupby(self.by, observed=True,dropna=self.dropna).agg({ self.y: self.aggfunc})

        # Handle color dictionary if provided
        if 'colors' in self.last_kwargs:
            color_dict = self.last_kwargs['colors']
            # Convert the color dictionary to a list based on the categories in self.df.index
            plot_dict['colors'] = [color_dict.get(category, 'grey') for category in self.df.index] #for pie it is colors and not color

        else:
            # If no color dictionary is provided, let pandas handle colors
            pass
        self.ax = self.df.plot(ax=ax,  **plot_dict)

        
        self._handle_data_output(self.df)

    def _plot_hexbin(self,ax):
        plot_dict = self._filter_plot_kwargs([ 'by','aggfunc','dropna','on','print_data','clip_data'])

 
        if 'aggfunc' in self.last_kwargs:
            warnings.warn("Aggregation is not supported for hex plots. Use reduce_C_function instead.")
            
           # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.hexbin.html
        if 'dropna' in self.last_kwargs:
            warnings.warn("The 'dropna' argument is not applicable to hex plots and will be ignored.")
        if 'by' in self.last_kwargs:
            warnings.warn("Use 'c' and 'cmap' to split the hex plot by a particular column. The 'by' argument will be ignored.")
    

        self.ax = self.df.plot(ax=ax,  **plot_dict)

        
        self._handle_data_output(self.df)

            
    def _plot_line(self, ax):
        plot_dict = self._filter_plot_kwargs(['y', 'by', 'aggfunc', 'dropna', 'on','print_data','clip_data'])

        #handle special case for lines
        style = plot_dict.pop('style', None) 
        width = plot_dict.pop('width', None) 

        
        pivot_data = self.get_pivot_data()
        self.ax = pivot_data.plot(ax=ax, **plot_dict)
        

        if style:
            for line, (name, style_value) in zip(self.ax.get_lines(), style.items()):
                line.set_linestyle(style_value)
        if width:
            for line, (name, width_value) in zip(self.ax.get_lines(), width.items()):
                line.set_linewidth(width_value)


        self._handle_data_output(pivot_data)
        

    #bar, barh, area
    def _plot_other(self, ax):
        plot_dict = self._filter_plot_kwargs(['y', 'by', 'aggfunc', 'dropna', 'on','print_data','clip_data'])
        self.ax = self.get_pivot_data().plot(ax=ax, **plot_dict)

        
        self._handle_data_output(self.get_pivot_data())

    #kde,density
    def _plot_density(self, ax):
        plot_dict = self._filter_plot_kwargs(['x','y', 'by', 'aggfunc', 'dropna', 'on','print_data','clip_data'])
        
        if 'aggfunc' in self.last_kwargs:
            warnings.warn("Aggregation is not supported for kde/density plot. The 'aggfunc' argument will be ignored.")
        if 'dropna' in self.last_kwargs:
            warnings.warn("The 'dropna' argument is not applicable to kde/density plots and will be ignored.")

        k = self.df.pivot(columns=self.by, values=self.column) 

            
        self.ax = k.plot(ax=ax, **plot_dict)

        
        self._handle_data_output(k)
        
    #hist
    def _plot_hist(self, ax):
        plot_dict = self._filter_plot_kwargs(['x','y', 'by','aggfunc', 'dropna', 'on','print_data','clip_data','column'])
        #should not be passing 'by' to plot_dict because pandas plot for hist will use by to subplot:)
        
        if 'aggfunc' in self.last_kwargs:
            warnings.warn("Aggregation is not supported for hist plot. The 'aggfunc' argument will be ignored.")
        if 'dropna' in self.last_kwargs:
            warnings.warn("The 'dropna' argument is not applicable to hist plots and will be ignored.")

        k=self.df.copy()
        # by = plot_dict.pop('by', None) #don;t want to pop by because we should be able to access it in next call.

        if self.by:

            k=k[[self.by,self.column]]
            k = k.pivot(columns=self.by, values=self.column) 
        else:
            k=k[[self.column]]

     
            

            
        self.ax = k.plot(ax=ax, **plot_dict)
        self._handle_data_output(k)

    def _filter_plot_kwargs(self, keys_to_remove):
        return {k: v for k, v in self.last_kwargs.items() if k not in keys_to_remove}

    def get_pivot_data(self):
        pivot_table = self.df.pivot_table(index=self.x, columns=self.by, values=self.y,
                                          aggfunc=self.aggfunc, dropna=self.dropna, observed=False).reset_index()
        pivot_table[self.x] = pivot_table[self.x].astype('object')

        pivot_table.columns.name = None


        return pivot_table


    def finalize(self, consolidate_legends=False, bbox_to_anchor=(0.8, -0.05), ncols=10):
        self.consolidate_legends = consolidate_legends
        self.bbox_to_anchor = bbox_to_anchor
        self.ncols = ncols
    
        handles = []
        labels = []
        seen = set()  # To track unique (label, type) combinations
    
        for ax in self.axd.values():
            # ax.customize_spines()
            # ax.spines['left'].set_position(('outward', 5))
            # ax.spines['bottom'].set_position(('outward', 5))
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
                
        
            # Collect handles and labels for the legends
            h, l = ax.get_legend_handles_labels()
            
            for handle, label in zip(h, l):
                # Create a unique identifier for the (label, type) combination
                handle_type = type(handle)
                identifier = (label, handle_type)
                
                if identifier not in seen:
                    handles.append(handle)
                    labels.append(label)
                    seen.add(identifier)  # Mark this (label, type) as seen
    
            # Manage the legend for the current axis
            legend = ax.get_legend()
            if legend and any(len(text.get_text()) > 0 for text in legend.get_texts()):
                if not self.consolidate_legends:
                    ax.legend(frameon=False)  # Keep individual legends if not consolidating
                else:
                    legend.remove()  # Remove individual legend if consolidating
    
        if self.consolidate_legends:
            # Add a single consolidated legend to the figure
            self.fig.legend(handles, labels, bbox_to_anchor=self.bbox_to_anchor, ncol=self.ncols, frameon=False)
    
        # Adjust the layout
        self.fig.tight_layout()
    
        return self
        



    def _handle_data_output(self, data):
        if self.print_data:
            print(data)
        if self.clip_data:
            data.to_clipboard(index=False)
