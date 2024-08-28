
from nettoolkit.nettoolkit.forms.formitems import *


def cred_pw1_exec(obj, i):
	"""executor function

	Args:
		obj (object): frame object 
		i (itemobject): item object of frame

	Returns:
		bool: wheter executor success or not.
	"""	
	try:
		if i['cred_pw1'] != '':
			obj.event_update_element(cred_en1={'value': i['cred_pw1']})
			return True
	except:
		return None

def update_cache_cred1_un(i): 
	update_cache(CACHE_FILE, username1=i['cred_un1'])
	return True


def exec_cred1_frame():
	"""tab display - Credential inputs

	Returns:
		sg.Frame: Frame with filter selection components
	"""    		
	return sg.Frame(title=None, 
					relief=sg.RELIEF_SUNKEN, 
					layout=[

		[sg.Text('Credentials', font='Bold', text_color="black") ],
		[sg.Text("Username:", text_color="yellow"),sg.InputText(get_cache(CACHE_FILE, 'username1'), key='cred_un1', size=(10,1), change_submits=True)],
		[sg.Text("Password:", text_color="yellow"),sg.InputText("", key='cred_pw1', password_char='*', size=(32,1),),],
		[sg.Text("Enable:", text_color="black"),sg.InputText("", key='cred_en1',  password_char='*', size=(32,1)),],
		under_line(80),

		])




