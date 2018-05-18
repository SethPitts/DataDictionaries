LIBNAME prot "G:\NIDADSC\spitts\Python_Projects\DataDicts\Data_Dictionaries\NDC\0067_MetaData";

data prot;
	set prot.prot_meta;
	drop PROJID PROTSEG;
	if OBJTYPE ^= 'HIDDEN';
run;

proc sort data=prot
	nodupkey
	out=sortedprot;
	by SCREENID FIELD_NAME;
run;
