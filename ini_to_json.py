import os
import json
import re
from shutil import copyfile

INI_DIR = "ini/"
JSON_DIR = "json/"
OUTPUT_DIR = "output_files/"
TABLE_MAPPING_DIR = "table_mappings/"

SOLUTION_PATH = "C:/Users/reza.yovan/CoreServices/core-services-api/"

SIM_INI_FILE_PATH = INI_DIR + "SIM.ini"
HEADER_DIR =  "headers/"

### ASSUMPTIONS ###
### ColHeader comes right after output file name ###

class Converter:
    def __init__(self, filepath, technology):
        self.filePath = filepath
        self.lines = []
        self.schema_file = []
        with open(filepath) as f:
            self.lines = f.readlines()
        self.pos = 1
        self.technology = technology
        self.table_mappings = self.get_table_mappings(technology)

    def copy_files(self):
        pass

    def write_to_file(self):
        technology = self.technology
        output_name = self.technology
        if technology == 'IO':
            technology = 'InvOpt'
            output_name = "SSO"
        elif technology == 'NO':
            technology = 'NetOpt'
        elif technology == 'TO':
            output_name = "VRO"
            technology = 'TransOpt'
        with open(JSON_DIR + technology + "OutputSchema.json", "w+") as f:
            j = json.dumps(self.schema_file)
            j = json.loads(j)
            j = json.dumps(j, indent=2)
            f.write(j)
        copyfile(JSON_DIR + technology + "OutputSchema.json", SOLUTION_PATH + "LLamasoft.Services." + output_name + ".OutputProcessing/" + technology + "OutputSchema.json")

    def convert(self):
        lines = self.lines
        while self.pos < len(lines):
            if lines[self.pos][0] == '[':
                try:
                    new_table = self.convert_table()
                    if "columns" in new_table.keys():
                        self.schema_file.append(new_table)
                except FileNotFoundError as f:
                    # ("file not found error : " + str(f))
                    pass
                    pass
                except IndexError as e:
                    print("test: " + lines[self.pos])
            else:
                self.pos += 1

    def convert_table(self):
        lines = self.lines
        output_file = lines[self.pos].replace("[", "").replace("]", "").replace('\n', "")
        # print("output file: " + output_file)
        map = "NO TABLENAME", "NO ID"
        has_tablename = True
        try:
            if "SimulationOutputInter" in output_file:
                pass # print("hi")
            map = self.table_mappings[output_file]
        except:
            # print(output_file)
            has_tablename = False
        file_col_mapping = []
        try:
            newoutput = get_filename_ignore_case(OUTPUT_DIR + self.technology + "/", output_file)
            output_file = newoutput if newoutput is not None else output_file
            with open(OUTPUT_DIR + self.technology + '/' + output_file) as f:
                line = f.readline()
                file_col_mapping = line.replace('\n', "").replace('\t', ",").split(',')
        except FileNotFoundError:
            try:
                with open(OUTPUT_DIR + self.technology + '/output/' + output_file) as f:
                    line = f.readline()
                    file_col_mapping = line.replace('\n', "").replace('\t', ",").split(',')
                    output_file = "output/" + output_file
            except FileNotFoundError:
                print("{}: file {} doesnt exsit".format(self.technology, output_file))
        table = {'filename': output_file, 'tablename': map[0], 'id': map[1]}
        table_options = {}
        columns = []
        self.pos += 1
        num = 0
        while self.pos < len(lines) and lines[self.pos] != '\n' and lines[self.pos][0] != '[' and lines[self.pos] != '':
            # print(num)
            num += 1
            line = lines[self.pos].replace("\n", "").split('=')
            if 'ColNameHeader' in line[0] or 'Col' not in line[0]:
                line = [x.replace(" ", "") for x in line]
                table_options[line[0]] = line[1]
            else:
                col_num = int(line[0].replace("Col", ""))
                col_name, col_type = line[1].split()
                file_col = "doesnt exist"
                file_exists = True
                try:
                    file_col = file_col_mapping[col_num - 1]
                except:
                    file_exists = False
                    pass
                column = {"fileColName": file_col.strip(), "tableColName": col_name, "type": col_type}
                if file_exists:
                    # print(line)
                    columns.append(column)
            self.pos += 1
        # need to add default text delimiter
        # if "TextDelimiter" not in table_options.keys():
        #    table_options["TextDelimiter"] = "none"

        if not has_tablename:
            # print(table)
            raise FileNotFoundError
        if len(columns) > 0:
            table['options'] = table_options
            table['columns'] = columns
        # print(table)
        return table

    def get_table_mappings(self, technology):
        try:
            with open(TABLE_MAPPING_DIR + technology + ".txt") as f:
                lines = f.readlines()
                mapping = {}
                for line in lines:
                    # print(line)
                    file, table, id = line.split(':')
                    # print("split file: '" + table + "' : " + id)
                    mapping[file] = (table.strip(), id.strip('\n').strip())
                return mapping
        except:
            print("should not be printing this")
            return {}


def get_filename_ignore_case(dir, filename):
    for file in os.listdir(dir):
        print(file)
        print(filename.lower())
        if file.lower() == filename.lower():
            return file
    print ("filenotfound: " + dir + " " + filename)

def write_sim_headers(ini_file):
    with open(ini_file) as f:
        lines = f.readlines()
        name_headers_dict = {}
        output_file = None
        for line in lines:
            if line == "\n":
                output_file = None
                continue
            if line[0] == "[":
                output_file = line
                continue
            if "ColNameHeader" in line:
                continue
            if "Col" in line:
                spl = line.split("=")
                col_name = spl[1].split()
                col_name = col_name[0]
                # print(output_file)
                # print(col_name)
                if output_file not in name_headers_dict.keys():
                    name_headers_dict[output_file] = col_name
                else:
                    name_headers_dict[output_file] = name_headers_dict[output_file] + "\\t" + col_name

        with open(HEADER_DIR + "SIM.txt", "w+") as f:
            for key in name_headers_dict.keys():
                f.write("{{ \"{}\" , \"{}\" }},\n".format(key.strip().strip("[").strip("]"), name_headers_dict[key].strip("\t")))




def run():
    for filename in os.listdir(INI_DIR):
        technology = filename.split('.')[0]
        converter = Converter(INI_DIR + filename, technology)
        converter.convert()
        converter.write_to_file()
    write_sim_headers(SIM_INI_FILE_PATH)


if __name__ == '__main__':
    run()
