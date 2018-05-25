import os
import shutil
import subprocess
import compare_csvs


def create_protocol_directories(data_dict_base_path: str, platform: str, platform_pathway: str,  protocols: list):
    """
    Creates a directory for a protocol if it does not exist and creates the protocol specific
    files.
    :param data_dict_base_path: Location where ALL Data Dicts are stored
    :param platform: Plat forms (NDC, NDB)
    :param platform_pathway: Pathway to platform SAS files
    :param protocols: Protocols to create Data Dicts for
    :return: list of all created/existing protocol directories
    """
    # create a directory for each protocol
    protocol_directories = []
    protocol_directory_path_template = "{}_MetaData"  #  0067_MetaData
    for protocol in protocols:
        protocol_directory_path = protocol_directory_path_template.format(protocol)
        protocol_full_pathway = os.path.join(data_dict_base_path, protocol_directory_path)
        if not os.path.exists(protocol_full_pathway):  # Only create the directory the first time
            os.makedirs(protocol_full_pathway)
            print("Created {}".format(protocol_full_pathway), "directory")
        protocol_info = [platform, platform_pathway, protocol, protocol_full_pathway]
        # Create the Data Dict files in the protocols directory
        create_protocol_specific_files(*protocol_info)
        protocol_directories.append(protocol_full_pathway)
    return protocol_directories


def create_protocol_specific_files(platform: str, platform_pathway: str, protocol: str, protocol_pathway: str):
    """
    Creates three files for each protocol from the MetaData. One with the metadata sorted by
    Sequence number. One with the metadata sorted by field name. One file that describes any
    changes in the metadata since the last time the files were generated.

    :param platform: platform to search (NDC, NDB)
    :param platform_pathway: Pathway to platform
    :param protocol: protocol to search for
    :param protocol_pathway: pathway to protocols directory
    :return: No return
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
    if os.path.exists(current_field_name_file_path):  # Only do comparison if there was an original file
        shutil.copy(current_field_name_file_path, copy_field_name_file_path)

    # SAS code to create the 3 files
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
    # Run the created file to create the DD
    subprocess.run([r'S:\SAS 9.4\x86\SASFoundation\9.4\sas.exe', sas_file_pathway])
    print("Ran {}".format(sas_file_pathway))

    # Compare the new file with the old file if both exist
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