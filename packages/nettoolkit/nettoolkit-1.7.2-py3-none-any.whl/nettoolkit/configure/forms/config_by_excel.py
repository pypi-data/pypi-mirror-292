
from nettoolkit.nettoolkit.forms.formitems import *
from nettoolkit.configure import ConfigureByExcel
from pprint import pprint

def config_by_excel_exec(obj, i):

	auth = {'un': i['cred_un'] ,'pw': i['cred_pw'], 'en': i['cred_en']}
	files = obj.var_dict['lb_config_excel_files_sequenced'] 
	captures_folder = i['configuration_log_folder'] if i['configuration_log_folder'] else ""
	# ==============================================
	C = ConfigureByExcel(auth,
		files=files,                         ## str-filenane, list - list of file names
		# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
		tab_sort_order=i['combo_config_tab_sort_order'],
		log_folder=captures_folder,
		config_log=i['cb_config_log'],
		exec_log=i['cb_exec_log'],
		exec_display=i['cb_exec_display'],
		configure=not i['cb_config_test'],                    ## Default False for test , True to configure
		# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
	)
	C()
	# ==============================================
	sg.Popup("Configuration Task(s) Complete..")
	return True

def update_lb_config_excel_files(obj, i):
	if obj.var_dict.get('lb_config_excel_files'):
		new_list = obj.var_dict['lb_config_excel_files'] + i['config_excel_files'].split(";")
	else:
		new_list = i['config_excel_files'].split(";")
	if i['config_excel_files'] != '':
		obj.event_update_element(lb_config_excel_files={'values': new_list})
		obj.event_update_element(lb_config_excel_files_sequenced={'values': []})
	obj.var_dict['lb_config_excel_files'] = new_list
	obj.var_dict['lb_config_excel_files_sequenced'] = []
	return True

def add_to_lb_config_excel_files_sequenced(obj, i, event):
	return add_remove_lb_config_excel_files_sequenced('add', obj, i, event)

def remove_from_lb_config_excel_files_sequenced(obj, i, event):
	return add_remove_lb_config_excel_files_sequenced('remove', obj, i, event)

def update_cache_cit_op1_folder(i): 
	update_cache(CACHE_FILE, configuration_log_folder=i['configuration_log_folder'])
	return True




def exec_config_by_excel_frame():
	"""tab display - Inputs

	Returns:
		sg.Frame: Frame with filter selection components
	"""    		
	return sg.Frame(title=None, 
					relief=sg.RELIEF_SUNKEN, 
					layout=[

		[sg.Text('Configure Device(s) using Excel Template', font='Bold', text_color="black") ],

		[sg.Text('Provide Excel configuration File(s):', text_color="black"), 
			sg.InputText('', disabled=True, key='config_excel_files', change_submits=True,),
			sg.FilesBrowse(),
		],
		[sg.Listbox([], key='lb_config_excel_files', change_submits=False, size=(80,5), horizontal_scroll=True, bind_return_key=True)],

		[sg.Text('Arrange in execution Sequence below V:', text_color="black")], 
		[sg.Listbox([], key='lb_config_excel_files_sequenced',  change_submits=False, size=(80,5),horizontal_scroll=True , bind_return_key=True )],

		under_line(80),
		[sg.Text('Options', font='Bold', text_color="black") ],

		[sg.Text('Provide Log folder:', text_color="yellow"), 
			sg.InputText(get_cache(CACHE_FILE, 'configuration_log_folder'), key='configuration_log_folder', change_submits=True),  
			sg.FolderBrowse(),
		],
		[sg.Checkbox('Write Configuration Logs', key='cb_config_log', default=True, text_color='black')],

		[sg.Checkbox('Write Execution Logs', key='cb_exec_log', default=True, text_color='black'),
		 sg.Checkbox('Execution display on screen', key='cb_exec_display', default=True, text_color='black')],

		[sg.Text('Tabs sorting order: ', text_color="yellow"), 
		 sg.InputCombo(['ascending', 'reversed'], default_value='ascending' , key='combo_config_tab_sort_order', size=(12,1)),],

		under_line(80),

		[sg.Checkbox('Test', key='cb_config_test', default=True, text_color='yellow'),
		 sg.Button("Configure", change_submits=True, key='btn_config_by_excel')],

	])

# ====================================================================================

def add_remove_lb_config_excel_files_sequenced(what, obj, i, event):
	lst1 = obj.var_dict['lb_config_excel_files']
	lst2 = obj.var_dict['lb_config_excel_files_sequenced']
	try:
		item = i[event][0]
	except IndexError:
		print("No Such element")
		return False
	if what == 'add':
		lst2.append(item)
		lst1.remove(item)
	elif what == 'remove':
		lst1.append(item)
		lst2.remove(item)
		lst1 = sorted(lst1)
	obj.event_update_element(lb_config_excel_files={'values': lst1})
	obj.event_update_element(lb_config_excel_files_sequenced={'values': lst2})
	obj.var_dict['lb_config_excel_files'] = lst1
	obj.var_dict['lb_config_excel_files_sequenced'] = lst2
	return True

# ====================================================================================




