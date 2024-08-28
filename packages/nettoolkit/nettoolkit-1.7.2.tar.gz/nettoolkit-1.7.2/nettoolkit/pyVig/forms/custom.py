
# ---------------------------------------------------------------------------------------
from pathlib import *
import sys

from nettoolkit.nettoolkit.forms.formitems import *
# ---------------------------------------------------------------------------------------




def pv_custom_data_frame():
	"""pyVig  - input data

	Returns:
		sg.Frame: Frame with filter selection components
	"""    		
	return sg.Frame(title=None, 
					relief=sg.RELIEF_SUNKEN, 
					layout=[

		[sg.Text('Customize your data', font='Bold', text_color="black") ],
		under_line(80),

		[sg.Text('select custom pyVig support package file:', text_color='yellow'), 
			sg.InputText(get_cache(CACHE_FILE, 'pyvig_custom_pkg_module'), key='pv_custom_pkg', change_submits=True), 
			sg.FileBrowse(key='pv_custom_pkg_button'),
		],

		[sg.Text('Update Mandatory custom functions below to identify item (device) hierarchical order series and item type series ', text_color='yellow')],
		[sg.Multiline(get_cache(CACHE_FILE, 'pyvig_custom_mandatory_functions'),  
			key='pv_custom_mandatory_fns', text_color='blue', size=(80,5), change_submits=True),], 

		[sg.Text('Add Optional custom var functions below (if any)', text_color='black'),], 
		[sg.Multiline(get_cache(CACHE_FILE, 'pyvig_custom_optional_functions'),  
			key='pv_custom_opt_var_fns', text_color='black', size=(80,5), change_submits=True),], 

		[sg.Text('Add Sheet Filters (if any) - in python dictionary format', text_color='black'),], 
		[sg.Multiline("""{\n}""", 
			key='pv_custom_sheet_filters', text_color='black', size=(40,5)),], 



		])

# ---------------------------------------------------------------------------------------


def update_cache_pv_custom_pkg(i):
	update_cache(CACHE_FILE, pyvig_custom_pkg_module=i['pv_custom_pkg'])
	return True

def update_cache_pv_custom_mandatory_fns(i):
	update_cache(CACHE_FILE, pyvig_custom_mandatory_functions=i['pv_custom_mandatory_fns'])
	return True

def update_cache_pv_custom_opt_var_fns(i):
	update_cache(CACHE_FILE, pyvig_custom_optional_functions=i['pv_custom_opt_var_fns'])
	return True


