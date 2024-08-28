

# ---------------------------------------------------------------------------------------
#   sets of event updator variables
# ---------------------------------------------------------------------------------------

MINITOOLS_EVENT_UPDATERS = {
	'go_md5_calculator',
	'go_pw_enc_cisco', 'go_pw_dec_cisco', 'go_pw_enc_juniper', 'go_pw_dec_juniper',
	'go_cisco_pw_decrypt', 'go_cisco_pw_mask', 'go_juniper_pw_decrypt', 'go_juniper_pw_mask',
}
IPSCANNER_EVENT_UPDATERS = {
	'go_pfxs_summary', 'go_pfxs_issubset', 'go_pfxs_break',
}
CAPTUREIT_EVENT_UPDATERS = {
	'cit_common',
	'device_ip_list_file', 'cisco_cmd_list_file', 'juniper_cmd_list_file',
	'custom_cit_file', 'custom_dynamic_cmd_class_name',
	'custom_ff_file_cit', 'custom_ff_class_name_cit', 'custom_fk_file_cit', 'custom_fk_name_cit',	
}

FACTSFINDER_EVENT_UPDATERS = {
	'btn_ff_gen',
	'custom_ff_file', 'custom_ff_class_name', 'custom_fk_file', 'custom_fk_name',	
}
J2CONFIG_EVENT_UPDATERS = {
	'btn_j2_gen', 'j2_custom_reg', 
}
PYVIG_EVENT_UPDATERS = {
	'pv_data_start', 'pv_start',
}
CONFIGURE_EVENT_UPDATERS = {
	'config_excel_files', 'btn_config_by_excel',
}


# ---------------------------------------------------------------------------------------
EVENT_UPDATORS = set()
EVENT_UPDATORS = EVENT_UPDATORS.union(MINITOOLS_EVENT_UPDATERS)
EVENT_UPDATORS = EVENT_UPDATORS.union(IPSCANNER_EVENT_UPDATERS)
EVENT_UPDATORS = EVENT_UPDATORS.union(CAPTUREIT_EVENT_UPDATERS)
EVENT_UPDATORS = EVENT_UPDATORS.union(FACTSFINDER_EVENT_UPDATERS)
EVENT_UPDATORS = EVENT_UPDATORS.union(J2CONFIG_EVENT_UPDATERS)
EVENT_UPDATORS = EVENT_UPDATORS.union(PYVIG_EVENT_UPDATERS)
EVENT_UPDATORS = EVENT_UPDATORS.union(CONFIGURE_EVENT_UPDATERS)		
# ---------------------------------------------------------------------------------------


__all__ = [EVENT_UPDATORS]