import os
import shutil
import subprocess
import compare_csvs


def create_protocol_directories(data_dict_base_path: str, platform: str, platform_pathway: str,  protocols: list):
    """

    :param data_dict_base_path:
    :param platform:
    :param platform_pathway:
    :param protocols:
    :return:
    """
    # create a directory for each protocol
    protocol_directories = []
    protocol_directory_path_template = "{}_MetaData"
    for protocol in protocols:
        protocol_directory_path = protocol_directory_path_template.format(protocol)
        protocol_full_pathway = os.path.join(data_dict_base_path, protocol_directory_path)
        if not os.path.exists(protocol_full_pathway):
            os.makedirs(protocol_full_pathway)
            print("Created {}".format(protocol_full_pathway), "directory")
        protocol_info = [platform, platform_pathway, protocol, protocol_full_pathway]
        create_protocol_specific_files(*protocol_info)
        protocol_directories.append(protocol_full_pathway)
    return protocol_directories


def create_protocol_specific_files(platform: str, platform_pathway: str, protocol: str, protocol_pathway: str):
    """

    :param platform:
    :param platform_pathway:
    :param protocol:
    :param protocol_pathway:
    :return:
    """
    protocol_info = {'platoform': platform,
                     'platform_pathway': platform_pathway,
                     'protocol': protocol,
                     'protocol_pathway': protocol_pathway
                     }
    # Create Sas File for the protocol

    # make copy of previous files for comparison
    current_field_name_file = "{}_Data_Dict_by_field_name.csv".format(protocol)
    current_field_name_file_path = os.path.join(protocol_pathway, current_field_name_file)
    copy_field_name_file = current_field_name_file.replace("name", "name_old")
    copy_field_name_file_path = os.path.join(protocol_pathway, copy_field_name_file)
    if os.path.exists(current_field_name_file_path):
        shutil.copy(current_field_name_file_path, copy_field_name_file_path)

    sas_template = r"""LIBNAME sasdata "{platform_pathway}";

LIBNAME protdata "{protocol_pathway}";

/* filter the metadata sas table by the protocol you're looking for
by filter PROTSEG by the protocol8*/

data protdata.prot_meta;
 set sasdata.meta;
 if find(PROTSEG, "{protocol}") > 0;
run;

proc sort data= protdata.prot_meta;
	by PROTSEG SCREENID SEQ;
run;

proc export data= protdata.prot_meta
	dbms=csv
	replace
	outfile='{protocol_pathway}\{protocol}_Data_Dict_by_seq.csv';
run;

proc sort data= protdata.prot_meta;
	by PROTSEG SCREENID FIELD_NAME;
run;

proc export data= protdata.prot_meta
	dbms=csv
	replace
	outfile='{protocol_pathway}\{protocol}_Data_Dict_by_field_name.csv';
run;
    """.format(**protocol_info)

    sas_file_name = "Create_{}_Data_Dict.sas".format(protocol)
    sas_file_pathway = os.path.join(protocol_pathway, sas_file_name)
    with open(sas_file_pathway, 'w') as sasfile:
        sasfile.write(sas_template)

    print("Completed writing {}".format(sas_file_name), "sas file")
    subprocess.run([r'S:\SAS 9.4\x86\SASFoundation\9.4\sas.exe', sas_file_pathway])
    print("Ran {}".format(sas_file_pathway))
    if os.path.exists(current_field_name_file_path) and os.path.exists(copy_field_name_file_path):
        compare_csvs.compare(current_field_name_file_path, copy_field_name_file_path,
                             ['FIELD_NAME', 'PROTSEG', 'SCREENID'])


def main():
    data_dict_base_path = r"G:\NIDADSC\spitts\Python_Projects\DataDicts\Data_Dictionaries"
    ndc_protocols = ['0064', '0067', '0068', '0069', '0075', '0073', '0079']
    ndb_protocols = ['0051', '0052', '0053', '0054']
    ndc_path = r'G:\NIDADSC\NDC\SAS\PROD_SAS_CUP\SAS\meta'
    ndb_path = r'G:\NIDADSC\NDB\SAS\PROD_SAS_CUP\SAS\meta'
    ndc_info = {'data_dict_base_path': os.path.join(data_dict_base_path, 'NDC'),
                'platform': 'ndc',
                'platform_pathway': ndc_path,
                'protocols': ndc_protocols}
    ndb_info = {'data_dict_base_path': os.path.join(data_dict_base_path, 'NDB'),
                'platform': 'ndb',
                'platform_pathway': ndb_path,
                'protocols': ndb_protocols}
    
    platforms = [ndb_info, ndc_info]
    
    for platform in platforms:
        create_protocol_directories(**platform)


if __name__ == '__main__':
    main()