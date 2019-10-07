"""
Mapping from environment to QATE QA/UAT DB

NOT FOR PRODUCTION USE - just a convenience for testing
"""

_dbs read write = {
	'EMEA-UAT' : ' oracle://BRUSER_2_DT:bam12011@//tkshl-dbl-d.japan.ml.com:1582/TKSH1D1',
	'JP-HKMM-UAT'  : 'oracle://JPOATEuser2:n2wqatejp@//tkshl-dbl-q.japan.ml.com:1582/TKSH101',
	'HK-HKMM-UAT'  : 'oracle://KROATEUSER2_DT:bam112340//HKOATE-DB1-D.HKZTWGG.APAC.BANKOFAMERICA.COM:49130/HKQATED1.bankofamerica.com', 
	'HK-HKWAR-UAT'  : 'oracle://KROATEUSER2'
	}

_dbs_read = {
	'EMEA-UAT' : 'oracle://BRREAD_2_DT:bam12011@tkshl-dbl-d.japan.ml.com:1582/TKSH1D1'
	}

def get_connection_string(environment, write_permission=False):
    if write_permission:
        return _dbs_read_write[environment]
    return _dbs_read[environment]
