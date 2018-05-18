LIBNAME sasdata "G:\NIDADSC\NDB\SAS\PROD_SAS_CUP\SAS\meta";

LIBNAME protdata "G:\NIDADSC\spitts\Python_Projects\DataDicts\Data_Dictionaries\NDB\0051_MetaData";

/* filter the metadata sas table by the protocol you're looking for
by filter PROTSEG by the protocol8*/

data protdata.prot_meta;
 set sasdata.meta;
 if find(PROTSEG, "0051") > 0;
run;

proc sort data= protdata.prot_meta;
	by PROTSEG SCREENID SEQ;
run;

proc export data= protdata.prot_meta
	dbms=csv
	replace
	outfile='G:\NIDADSC\spitts\Python_Projects\DataDicts\Data_Dictionaries\NDB\0051_MetaData\0051_Data_Dict_by_seq.csv';
run;

proc sort data= protdata.prot_meta;
	by PROTSEG SCREENID FIELD_NAME;
run;

proc export data= protdata.prot_meta
	dbms=csv
	replace
	outfile='G:\NIDADSC\spitts\Python_Projects\DataDicts\Data_Dictionaries\NDB\0051_MetaData\0051_Data_Dict_by_field_name.csv';
run;
    