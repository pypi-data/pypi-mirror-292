

# ---------------------------------------------------------------------------------------
#
from .tab_event_funcs import *
#
from nettoolkit.pyJuniper.forms.md5_calculator import *
from nettoolkit.pyJuniper.forms.pw_enc_dec import *
from nettoolkit.pyJuniper.forms.juniper_oper import *
#
from nettoolkit.addressing.forms.subnet_scanner import *
from nettoolkit.addressing.forms.compare_scanner_outputs import *
from nettoolkit.addressing.forms.prefixes_oper import *
from nettoolkit.addressing.forms.create_batch import *
#
from nettoolkit.capture_it.forms.cred import *
from nettoolkit.capture_it.forms.options import *
from nettoolkit.capture_it.forms.common_to_all import *
from nettoolkit.capture_it.forms.custom import *
from nettoolkit.capture_it.forms.quick_show import *
#
from nettoolkit.facts_finder.forms.ff_generate import *
from nettoolkit.facts_finder.forms.ff_custom import *
from nettoolkit.facts_finder.forms.ff_custom_cit import *
#
from nettoolkit.pyVig.forms.input_data import *
from nettoolkit.pyVig.forms.custom import *
#
from nettoolkit.j2config.forms.input_data import *
#
from nettoolkit.compare_it.forms.compare_configs import *
#
from nettoolkit.configure.forms.config_by_excel import *
from nettoolkit.configure.forms.cred import *
#
# ---------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------
#   dictionary of event updators v/s its executor functions.
# ---------------------------------------------------------------------------------------

MINITOOLS_EVENT_FUNCS = {
	'quick_sh_cred_un': update_quick_sh_cred_un,
	'go_md5_calculator': md5_calculator_exec,
	'go_pw_enc_cisco': pw_enc_cisco_exec,
	'go_pw_dec_cisco': pw_dec_cisco_exec,
	'go_pw_enc_juniper': pw_enc_juniper_exec,
	'go_pw_dec_juniper': pw_dec_juniper_exec,
	'go_juniper_to_set': juniper_oper_to_jset_exec,
	'go_juniper_remove_remarks': juniper_oper_remove_remarks_exec,
	'go_compare_config_text': go_compare_config_text_exec,
	'go_compare_config_xl': go_compare_config_xl_exec,
	'btn_quick_show': btn_quick_show_exec,
	'go_cisco_pw_decrypt': go_cisco_pw_decrypt_exec,
	'go_cisco_pw_mask': go_cisco_pw_mask_exec, 
	'go_juniper_pw_decrypt': go_juniper_pw_decrypt_exec,
	'go_juniper_pw_mask': go_juniper_pw_mask_exec,
}
IPSCANNER_EVENT_FUNCS = {
	'btn_ipscanner': btn_ipscanner_exec,
	'go_subnet_scanner': subnet_scanner_exec,
	'go_compare_scanner_outputs': compare_scanner_outputs_exec,
	'go_create_batch': create_batch_exec,
	'btn_minitools': btn_minitools_exec,
	'go_pfxs_summary': prefixes_oper_summary_exec,
	'go_pfxs_issubset' : prefixes_oper_issubset_exec,
	'go_pfxs_break': prefixes_oper_pieces_exec,
}
CATPUREIT_EVENT_FUNCS = {
	'cred_un': 	update_cache_cred_un,
	'cit_op_folder': update_cache_cit_op_folder,
	'device_ip_list_file': device_ip_list_file_exec,
	'cisco_cmd_list_file': cisco_cmd_list_file_exec,
	'juniper_cmd_list_file': juniper_cmd_list_file_exec,
	'cit_common': cit_common_exec,
	'custom_cit_file': custom_cit_file_exec,
	'custom_dynamic_cmd_class_name': custom_dynamic_cmd_class_name_exec,
	'custom_ff_file_cit': custom_ff_file_cit_exec,
	'custom_fk_file_cit': custom_fk_file_cit_exec,
	'custom_ff_class_name_cit': custom_ff_name_cit_exec,
	'custom_fk_name_cit': custom_fk_name_cit_exec,
	'btn_captureit': btn_captureit_exec,
}
FACTSFINDER_EVENT_FUNCS = {
	'btn_ff_gen': btn_ff_gen_exec, 
	'btn_factsfinder': btn_factsfinder_exec,
	'custom_ff_file': custom_ff_file_exec,
	'custom_fk_file': custom_fk_file_exec,
	'custom_ff_class_name': custom_ff_name_exec,
	'custom_fk_name': custom_fk_name_exec,
}
J2CONFIG_EVENT_FUNCS = {
	'j2_output_folder': update_cache_j2_output_folder,
	'j2_rfile': update_cache_j2_rfile,
	'j2_reg_class': update_cache_j2_reg_class,
	'j2_custom_cls': update_cache_j2_custom_cls,
	'j2_custom_fn': update_cache_j2_custom_fn,
	'btn_j2config': btn_j2config_exec,
	'btn_j2_gen': btn_j2_gen_exec,
	'j2_custom_reg': j2_custom_reg_exec,
}
PYVIG_EVENT_FUNCS = {
	'py_datafile_output_folder': update_cache_py_datafile_output_folder,
	'py_datafile': update_cache_py_datafile,
	'py_stencil_folder': update_cache_py_stencil_folder,
	'py_default_stencil': update_cache_py_default_stencil,
	'py_output_folder': update_cache_py_output_folder,
	'pv_custom_pkg': update_cache_pv_custom_pkg,
	'pv_custom_mandatory_fns': update_cache_pv_custom_mandatory_fns,
	'pv_custom_opt_var_fns': update_cache_pv_custom_opt_var_fns,
	'btn_pyvig': btn_pyvig_exec,
	'pv_data_start': pv_data_start_exec,
	'pv_start': pv_start_exec,
}
CONFIGURE_EVENT_FUNCS = {
	'btn_configure': btn_configure_exec,
	'btn_config_by_excel': config_by_excel_exec,
	'config_excel_files': update_lb_config_excel_files,
	'cred_un1': update_cache_cred1_un,
	'configuration_log_folder': update_cache_cit_op1_folder,
	'lb_config_excel_files': add_to_lb_config_excel_files_sequenced,
	'lb_config_excel_files_sequenced': remove_from_lb_config_excel_files_sequenced,
}

# ---------------------------------------------------------------------------------------
EVENT_FUNCTIONS = {}
EVENT_FUNCTIONS.update(MINITOOLS_EVENT_FUNCS)
EVENT_FUNCTIONS.update(IPSCANNER_EVENT_FUNCS)
EVENT_FUNCTIONS.update(CATPUREIT_EVENT_FUNCS)
EVENT_FUNCTIONS.update(FACTSFINDER_EVENT_FUNCS)
EVENT_FUNCTIONS.update(J2CONFIG_EVENT_FUNCS)
EVENT_FUNCTIONS.update(PYVIG_EVENT_FUNCS)
EVENT_FUNCTIONS.update(CONFIGURE_EVENT_FUNCS)
# ---------------------------------------------------------------------------------------
__all__ = [EVENT_FUNCTIONS]

