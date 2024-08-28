
# ---------------------------------------------------------------------------------------
from collections import OrderedDict
from .var_frames import (
	MINITOOLS_FRAMES, IPSCANNER_FRAMES, CAPTUREIT_FRAMES, FACTSFINDER_FRAMES, J2CONFIG_FRAMES, PYVIG_FRAMES,
	CONFIGURE_FRAMES
)
# ---------------------------------------------------------------------------------------
#   ADD ANY NEW SERVICE BUTTON HERE 
# ---------------------------------------------------------------------------------------
BUTTUN_PALLETE_NAMES = OrderedDict()
BUTTUN_PALLETE_NAMES["Minitools"] = 'btn_minitools'
BUTTUN_PALLETE_NAMES["Addressing"] = 'btn_ipscanner'
BUTTUN_PALLETE_NAMES["Capture-IT"] = 'btn_captureit'
BUTTUN_PALLETE_NAMES["Facts Gen"] = 'btn_factsfinder'
BUTTUN_PALLETE_NAMES["Configure"] = 'btn_configure'	
BUTTUN_PALLETE_NAMES["Config Gen"] = 'btn_j2config'
BUTTUN_PALLETE_NAMES["Drawing Gen"] = 'btn_pyvig'
TAB_EVENT_UPDATERS = set(BUTTUN_PALLETE_NAMES.values())
#
# ---------------------------------------------------------------------------------------
ALL_TABS = set()
ALL_TABS = ALL_TABS.union(IPSCANNER_FRAMES.keys())
ALL_TABS = ALL_TABS.union(MINITOOLS_FRAMES.keys())
ALL_TABS = ALL_TABS.union(CAPTUREIT_FRAMES.keys())
ALL_TABS = ALL_TABS.union(FACTSFINDER_FRAMES.keys())
ALL_TABS = ALL_TABS.union(J2CONFIG_FRAMES.keys())
ALL_TABS = ALL_TABS.union(PYVIG_FRAMES.keys())
ALL_TABS = ALL_TABS.union(CONFIGURE_FRAMES.keys())

# ---------------------------------------------------------------------------------------

def enable_disable(obj, * , group, group_frames, all_tabs, event_updaters):
	"""enable/disable provided object frames

	Args:
		obj (NGui): NGui class instance object
		group (str): button group key, which is to enabled.
		group_frames (list): list of frames to be enabled
		all_tabs (set): set of all frames keys
		event_updaters (set): set of Button pallet names button keys
	"""	
	tabs_to_disable = all_tabs.difference(group_frames)
	buttons_to_rev = event_updaters.difference(group)
	for tab in tabs_to_disable:
		d = {tab: {'visible':False}}
		obj.event_update_element(**d)	
	for i, tab in enumerate(group_frames):
		e = {tab: {'visible':True}}
		obj.event_update_element(**e)
		if i ==0: obj.w[tab].select()
	if group:
		for tab in buttons_to_rev:
			e = {tab: {'button_color': 'gray'}}
			obj.event_update_element(**e)
		e = {group: {'button_color': 'blue'}}
		obj.event_update_element(**e)



# ---------------------------------------------------------------------------------------
#  ADD / EDIT FRAMES UPDATE HERE
#

def btn_ipscanner_exec(obj):
	"""executor function to switch and enable ipscanner tabs

	Args:
		obj (Nettoolkit): Nettoolkit class instance object

	Returns:
		True: when succeded
	"""	
	enable_disable(obj, group_frames=IPSCANNER_FRAMES.keys(), group='btn_ipscanner', all_tabs=ALL_TABS, event_updaters=TAB_EVENT_UPDATERS)
	return True

def btn_minitools_exec(obj):
	"""executor function to switch and enable minitools tabs

	Args:
		obj (Nettoolkit): Nettoolkit class instance object

	Returns:
		True: when succeded
	"""	
	enable_disable(obj, group_frames=MINITOOLS_FRAMES.keys(), group='btn_minitools', all_tabs=ALL_TABS, event_updaters=TAB_EVENT_UPDATERS)
	return True

def btn_captureit_exec(obj):
	"""executor function to switch and enable captureit tabs

	Args:
		obj (Nettoolkit): Nettoolkit class instance object

	Returns:
		True: when succeded
	"""	
	enable_disable(obj, group_frames=CAPTUREIT_FRAMES.keys(), group='btn_captureit', all_tabs=ALL_TABS, event_updaters=TAB_EVENT_UPDATERS)
	return True

def btn_factsfinder_exec(obj):
	"""executor function to switch and enable factsfinder tabs

	Args:
		obj (Nettoolkit): Nettoolkit class instance object

	Returns:
		True: when succeded
	"""	
	enable_disable(obj, group_frames=FACTSFINDER_FRAMES.keys(), group='btn_factsfinder', all_tabs=ALL_TABS, event_updaters=TAB_EVENT_UPDATERS)
	return True

def btn_j2config_exec(obj):
	"""executor function to switch and enable j2config tabs

	Args:
		obj (Nettoolkit): Nettoolkit class instance object

	Returns:
		True: when succeded
	"""	
	enable_disable(obj, group_frames=J2CONFIG_FRAMES.keys(), group='btn_j2config', all_tabs=ALL_TABS, event_updaters=TAB_EVENT_UPDATERS)
	return True

def btn_pyvig_exec(obj):
	"""executor function to switch and enable pyvig tabs

	Args:
		obj (Nettoolkit): Nettoolkit class instance object

	Returns:
		True: when succeded
	"""	
	enable_disable(obj, group_frames=PYVIG_FRAMES.keys(), group='btn_pyvig', all_tabs=ALL_TABS, event_updaters=TAB_EVENT_UPDATERS)
	return True

def btn_configure_exec(obj):
	"""executor function to switch and enable configure tabs

	Args:
		obj (Nettoolkit): Nettoolkit class instance object

	Returns:
		True: when succeded
	"""	
	enable_disable(obj, group_frames=CONFIGURE_FRAMES.keys(), group='btn_configure', all_tabs=ALL_TABS, event_updaters=TAB_EVENT_UPDATERS)
	return True

# ---------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Main Function
# ------------------------------------------------------------------------------
if __name__ == '__main__':
	pass
# ------------------------------------------------------------------------------
