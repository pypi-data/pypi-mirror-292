
# ---------------------------------------------------------------------------------------
try:
	import PySimpleGUI as sg
except:
	pass

from dataclasses import dataclass, field
import nettoolkit as nt
#
from .forms.gui_template import GuiTemplate
from .forms.formitems import *

### -- For Nettoolkit() class
from .forms.tab_event_funcs import BUTTUN_PALLETE_NAMES, TAB_EVENT_UPDATERS
from .forms.tab_event_funcs import btn_minitools_exec as initial_frames_load
from .forms.var_frames import FRAMES
from .forms.var_event_funcs import EVENT_FUNCTIONS
from .forms.var_event_updators import EVENT_UPDATORS
from .forms.var_event_item_updators import EVENT_ITEM_UPDATORS
from .forms.var_retractables import RETRACTABLES
from nettoolkit.addressing.forms.subnet_scanner import count_ips
# ---------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Generalized Class to Prepare GUI UserForm using template 
# -----------------------------------------------------------------------------

class NGui(GuiTemplate):

	def __init__(self, * ,
		header="Set Your private Header",
		banner="Set Your private Banner",
		form_width=1440,
		form_height=700,
		frames_dict={},
		event_catchers={},
		event_updaters=set(),
		event_item_updaters=set(),
		retractables=set(),
		button_pallete_dic={},
		):
		super().__init__(
			header, banner, form_width, form_height,
			frames_dict, event_catchers, event_updaters, 
			event_item_updaters, retractables, button_pallete_dic,
		)
		self.tab_updaters = set(self.button_pallete_dic.values())

	def __call__(self, initial_frame=None):
		super().__call__(initial_frame)

	def update_set(self, name, value):
		if self.__dict__.get(name): 
			self.__dict__[name] = self.__dict__[name].union(value)
		else:
			self.__dict__[name] = value


	def update_dict(self, name, value):
		if self.__dict__.get(name): 
			self.__dict__[name].update(value)
		else:
			self.__dict__[name] = value

	@property
	def cleanup_fields(self):
		return self.retractables


# ---------- ---------- ---------- ---------- ---------- ---------- ---------- ---------- ---------- 

# -----------------------------------------------------------------------------
# Class to initiate Nettoolkit UserForm
# -----------------------------------------------------------------------------


class Nettoolkit(NGui):
	'''Minitools UserForm asking user inputs.	'''

	# Object Initializer
	def __init__(self):
		banner = f'Nettoolkit: v{nt.__version__} - GuiTemplate: v{super().version}'
		header = f'{nt.__doc__}'
		#
		self.initialize_custom_variables()
		self.NG = NGui(
			header = header,
			banner = banner,
			frames_dict = FRAMES,
			event_catchers = EVENT_FUNCTIONS,
			event_updaters = EVENT_UPDATORS,
			event_item_updaters = EVENT_ITEM_UPDATORS,
			retractables = RETRACTABLES,
			button_pallete_dic = BUTTUN_PALLETE_NAMES,
			form_width = 800,
			# form_height = 700,
		)	

	def __call__(self):
		self.NG(initial_frames_load)

	def initialize_custom_variables(self):
		"""Initialize all custom variables
		"""		
		self.custom_dynamic_cmd_class = None      # custom dynamic commands execution class
		self.custom_ff_class = None  # custom facts-finder class
		self.custom_fk = {}          # custom facts-finder foreign keys

	def user_events(self, i, event):
		"""specific event catchers

		Args:
			i (dict): dictionary of GUI fields variables
			event (str): event
		"""		
		if event == 'file_md5_hash_check':
			self.event_update_element(file_md5_hash_value={'value': ""})
		if event == 'go_count_ips':
			self.event_update_element(ss_ip_counts={'value': count_ips(i['pfxs'], i['till'])})

# ---------- ---------- ---------- ---------- ---------- ---------- ---------- ---------- ---------- 


# ------------------------------------------------------------------------------
# Main Function
# ------------------------------------------------------------------------------
if __name__ == '__main__':
	pass
# ------------------------------------------------------------------------------
