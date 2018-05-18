import csv


def compare(base_csv: str, updated_csv: str, common_fields: list):
    print("comparing {} and {}".format(base_csv, updated_csv))
    key_field = common_fields[0]
    prot_seg = common_fields[1]
    screenid = common_fields[2]
    with open(base_csv, 'r') as base_file, open(updated_csv, 'r') as updated_file:
        base_csv_reader = csv.DictReader(base_file)
        base_data = {row[key_field] + "-" + row[prot_seg]: row for row in base_csv_reader
                     if prot_seg is not None
                     if row[key_field] is not None}
        updated_csv_reader = csv.DictReader(updated_file)
        updated_data = {row[key_field] + "-" + row[prot_seg]: row for row in updated_csv_reader
                        if prot_seg is not None
                        if row[key_field] is not None}

        # get common fields from each file
        # TODO: try;except block for if the field is actually in the csv file
        base_fields = list(base_data)
        updated_fields = list(updated_data)
        # TODO: if fields are added ore deleted
        with open('{}_metadata_changes.txt'.format(base_csv.replace(".csv", "")), 'w') as change_log:
            for field in base_fields:
                if updated_data.get(field):
                    base_row = base_data[field]
                    updated_row = updated_data[field]
                    if base_row != updated_row:
                        screen = base_row[screenid]
                        metadata_key = list(base_row)

                        for key in metadata_key:
                            base_value = base_row[key]
                            updated_value = updated_row[key]
                            if base_value != updated_value:
                                change_log.write("""
Screen: {}
Field-Protseg: {}
Attribute: {}
Changed 
from: {} 
to: {}\n""".format(screen, field, key, base_value, updated_value))
                else:
                    change_log.write(("{} is not present in the updated file\n".format(field)))


def main():
    compare('0067_Data_Dict_by_field_name.csv', '0067_Data_Dict_by_field_name2.csv',
            ['FIELD_NAME', 'PROTSEG', 'SCREENID'])


if __name__ == '__main__':
    main()
