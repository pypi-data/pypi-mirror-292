import re
import os
global pc_list
pc_list = []
def read_file_regex(filename, regex):
    with open(filename, "r") as f:
        for line in f:
            match = re.search(regex, line)
            if match:
                #print(match.group())
                a = match.group()
                if a in pc_list:
                    pass 
                else:
                    pc_list.append(a)


def read_folder_regex(folder, regex):
    for i in os.listdir(folder):
        if os.path.isdir(os.path.join(folder, i)):
            if i[0] not in ['@', '.']:
                print(str(os.path.join(folder, i)) + " is not dummy folder")
                read_folder_regex(os.path.join(folder, i), regex)
        else:
            read_file_regex(os.path.join(folder, i),regex)


if __name__ == "__main__":
    folder = "/mnt/d/shared/log3"
    regex = r"[a-zA-Z0-9]{8,12}\.legendbiotech.local"
    read_folder_regex(folder,regex)
    for i in pc_list:
        print(i)

