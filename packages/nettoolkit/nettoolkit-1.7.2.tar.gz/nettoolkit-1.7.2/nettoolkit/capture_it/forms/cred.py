
from nettoolkit.nettoolkit.forms.formitems import *


def cred_pw_exec(obj, i):
	"""executor function

	Args:
		obj (object): frame object 
		i (itemobject): item object of frame

	Returns:
		bool: wheter executor success or not.
	"""	
	# try:
	if i['cred_pw'] != '':
		obj.event_update_element(cred_en={'value': i['cred_pw']})
		return True
	# except:
	# 	return None


def exec_cred_frame():
	"""tab display - Credential inputs

	Returns:
		sg.Frame: Frame with filter selection components
	"""    		
	return sg.Frame(title=None, 
					relief=sg.RELIEF_SUNKEN, 
					layout=[

		[sg.Text('Credentials', font='Bold', text_color="black") ],
		[sg.Text("Username:", text_color="yellow"),sg.InputText(get_cache(CACHE_FILE, 'username'), key='cred_un', size=(10,1), change_submits=True)],
		[sg.Text("Password:", text_color="yellow"),sg.InputText("", key='cred_pw', password_char='*', size=(32,1),),],
		[sg.Text("Enable:", text_color="black"),sg.InputText("", key='cred_en',  password_char='*', size=(32,1)),],
		under_line(80),

		[sg.Text('Output Folder', font='Bold', text_color="black") ],
		[sg.Text('select folder:', text_color="yellow"), 
			sg.InputText(get_cache(CACHE_FILE, 'captures_folder'), key='cit_op_folder', change_submits=True),  
			sg.FolderBrowse(),
		],
		under_line(80),

		])



def update_cache_cred_un(i): 
	update_cache(CACHE_FILE, username=i['cred_un'])
	return True

def update_cache_cit_op_folder(i): 
	update_cache(CACHE_FILE, captures_folder=i['cit_op_folder'])
	return True

