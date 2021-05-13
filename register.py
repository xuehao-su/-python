#This file is designed to convert register file to UVM register model sv file

#version 1.1

#modify number start
#modify add reg function

#created by xuehao on 4/15 2021
#second modified by xuehao on 4/28 2021

target = 'I2C_reg'
#target = 'I3C_reg'
target_txt = target + '.txt'
target_sv = target + '.sv'
start = 1 # used to control to switch to the next register
count_empty_lines = 0 # used to control eat extra empty lines
reg_name = [] # used to save the names of different registors
width = []
offset = []
def class_write(f, reg_name, width, field_name, field_width, access_ctrl):
    f.write('class '+reg_name+' extends uvm_reg;'+'\n')
    f.write('\n')
    field_number = len(field_name)
    #declaration for all the fields
    for i in range(field_number):
        f.write('rand '+"uvm_reg_field "+field_name[i]+';\n')
        f.write('\n')
    #build function declaration
    f.write('virtual function void build();'+'\n')
    f.write('\n')
    # create and configuration statements
    for j in range(field_number):
        width_tmp = field_width[j].split(":")
        if(len(width_tmp)==1):
            width_num = '1'
        else:
            width_num = str(1+int(width_tmp[0])-int(width_tmp[1]))
        f.write('    '+field_name[j]+'=uvm_reg_field::type_id::create("'+field_name[j]+'");\n')
        f.write('    //parameter: parent, size, lsb_pos, access, volatile, reset value, has_reset, is_rand, individually accessible'+'\n')
        f.write('    '+field_name[j]+'.configure(this,'+width_num+','+width_tmp[-1] +',"'+access_ctrl[j]+'"'+',1,0,1,1,0);\n') 
        f.write('\n')

    f.write('endfunction\n')
    f.write('\n')
    f.write('\'uvm_object_utils('+reg_name+')\n')
    f.write('\n')
    f.write('function new(input string name = "'+reg_name+'");\n')
    f.write('    '+'//parameter name size has_coverage\n')
    f.write('    '+'super.new(name,'+width+',UVM_NO_COVERAGE);\n')
    f.write('endfunction\n')
    f.write('\n')
    f.write('endclass\n')
    f.write('\n')
        
def reg_block_write(f,reg_name,offset):
    endian = 'BIG'
    f.write('class reg_model extends uvm_reg_block;')
    f.write('\n')
    reg_num = len(reg_name)
    #declaration of registors
    for i in range(reg_num):
        f.write('rand '+ reg_name[i] + ' ' + reg_name[i]+'_ins'+';\n')
    f.write('\n')
    #declaration of default_map
    f.write('virtual function void build();\n')
    f.write('\n')
    f.write('    ' + 'default_map = create_map("default_map",0,4,UVM_'+endian+'_ENDIAN,0);\n')
    f.write('\n')
    #registration of registors
    for i in range(reg_num):
        f.write('    '+reg_name[i]+'_ins='+ reg_name[i]+'::type_id::create("'+reg_name[i]+'_ins'+'");'+'\n')
        f.write('    '+reg_name[i]+'_ins'+'.configure(this,"");'+'\n')
        f.write('    '+reg_name[i]+'_ins'+'.build();'+'\n')
        f.write('    '+reg_name[i]+'_ins'+'.lock_model();'+'\n')
        f.write('    '+'default_map.add_submap('+reg_name[i]+'_ins.default_map, '+offset[i]+');\n')
        f.write('\n')
  
    f.write('\n')
    f.write('endfunction\n')
    f.write('\n')

    f.write('\'uvm_object_utils(reg_model)\n')
    f.write('\n')

    f.write('function new(input string name="reg_model");\n')
    f.write('    '+'super.new(name,UVM_NO_COVERAGE);\n')
    f.write('endfunction\n')
    f.write('\n')

    f.write('endclass')






#open file. automatical closed after with block
with open(target_txt,'r',encoding='utf-8') as f1:

    #open generated target file
    with open(target_sv,'w+',encoding='utf-8') as f2:

        #read all the lines in txt file
        all_lines = f1.readlines()
        reg_count = 0
        reserved_count = 0
        for each in all_lines:
            arr_line = each.split()
            
            #new register start
            if len(arr_line) == 0:
                start = 1
                reserved_count = 0
                if(count_empty_lines == 0):
                    class_write(f2, reg_name[reg_count], width[reg_count], field_name, field_width, access_ctrl)
                    reg_count = reg_count + 1
                count_empty_lines = count_empty_lines + 1
                continue

            #process the 1st line  'name offset width'
            if(start == 1):
                count_empty_lines = 0
                reg_name.append(arr_line[0])
                offset.append(arr_line[1])
                width.append(arr_line[2])
                start = 0
                field_name = []
                field_width = []
                access_ctrl = []
                description = []
            else:
                if(arr_line[0]=='RESERVED'):
                    field_name.append(arr_line[0]+'_'+str(reserved_count))
                    reserved_count=reserved_count+1
                else:
                    field_name.append(arr_line[0])
                field_width.append(arr_line[1])
                if(arr_line[0]=='RESERVED'):
                    access_ctrl.append('R') #reserved is set with read-only
                    description.append('Reserved field')
                else:
                    access_ctrl.append(arr_line[2])
                   # description.append(arr_line[3])

        reg_block_write(f2,reg_name,offset)