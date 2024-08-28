
from nettoolkit.nettoolkit.forms.formitems import *
from nettoolkit.capture_it import quick_display


def btn_quick_show_exec(i):
	ip = i['quick_show_device_ip']
	auth = {
		'un': i['quick_sh_cred_un'],
		'pw': i['quick_sh_cred_pw'],
		'en': i['quick_sh_cred_en'] if i['quick_sh_cred_en'] else i['quick_sh_cred_pw'], 
	}
	cmds = i['quick_show_cmds'].split("\n")
	wait =  i['quick_sh_delay'] if i['quick_sh_delay'] else 1
	quick_display(ip, auth, cmds, wait=wait)
	return True

def exec_quick_show_output_frame():
	"""tab display - quick show command outputs

	Returns:
		sg.Frame: Frame with filter selection components
	"""    		
	return sg.Frame(title=None, 
					relief=sg.RELIEF_SUNKEN, 
					layout=[

		[sg.Text('Quick Show Commands Output', font='Bold', text_color="black") ],

		[sg.Text('Device IP:', text_color="yellow"),
		sg.InputText("", key='quick_show_device_ip', disabled=False),
		],
		[sg.Text('List of cisco show commands:', text_color="yellow"),
		sg.Multiline("", key='quick_show_cmds', autoscroll=True, size=(50,5), disabled=False),
		],
		under_line(80),

		[sg.Text("Username:", text_color="yellow"),sg.InputText(get_cache(CACHE_FILE, 'username'), key='quick_sh_cred_un', size=(10,1), change_submits=True),],
		[sg.Text("Password:", text_color="yellow"),sg.InputText("", key='quick_sh_cred_pw', password_char='*', size=(32,1),),],
		[sg.Text("Enable:", text_color="black"),sg.InputText("", key='quick_sh_cred_en',  password_char='*', size=(32,1)),],
		under_line(80),

		[sg.Text("Delay Factor:", text_color="black"),
		sg.InputCombo([1,2,3,4,5,6,7,8,9,10], default_value=1, key='quick_sh_delay', size=(5,1) ),
		],
		under_line(80),

		[sg.Button("Quick Show", change_submits=True, key='btn_quick_show')],

		])

def update_quick_sh_cred_un(i):
	update_cache(CACHE_FILE, username=i['quick_sh_cred_un'])
	return True