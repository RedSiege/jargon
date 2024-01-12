import random
import argparse
import sys

def gen_word_combinations(dict_file):
    # read in words dictionary
    try:
        with open(dict_file) as dictionary:
            words = dictionary.readlines()
    except FileNotFoundError:
        exit("\n\nThe dictionary you specified does not exist! Please specify a valid file path.\nExiting...\n")

    # Select random words from dictionary
    # why is this 257?  It fails at 256
    try:
        random_words = random.sample(words, 257)
        return random_words
    except ValueError:
        exit("\n\nThe dictionary file you specified does not contain at least 256 words!\nExiting...\n")

def get_shellcode(input_file):
    file_shellcode = b''
    try:
        with open(input_file, 'rb') as shellcode_file:
            file_shellcode = shellcode_file.read()
            file_shellcode = file_shellcode.strip()
            binary_code = ''

            for byte in file_shellcode:
                binary_code += "\\x" + hex(byte)[2:].zfill(2)

            raw_shellcode = "0" + ",0".join(binary_code.split("\\")[1:])

        return(raw_shellcode)
    
    except FileNotFoundError:
        exit("\n\nThe input file you specified does not exist! Please specify a valid file path.\nExiting...\n")

def main():
    ### Parse our arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dictionary", type=str,
                        help="Dictionary file. Defaults to 'dictionary.txt.'")
    parser.add_argument("-i", "--input", type=str,
                        help="File containing raw shellcode.")
    parser.add_argument("-o", "--output", type=str,
                        help="Output file. Defaults to 'generated.c.'")

    args = parser.parse_args()
    if len(sys.argv) == 1:
        # No arguments received.  Print help and exit
        parser.print_help(sys.stderr)
        sys.exit(0)

    if args.input:
        input_file = args.input
    else:
        input_file = "beacon.bin"

    if args.output:
        output_file = args.output
    else:
        output_file = "generated.c"

    if args.dictionary:
        dict_file = args.dictionary
    else:
        dict_file = "dictionary.txt"

    '''
        Build translation table
    '''
    words = gen_word_combinations(dict_file)
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
    shellcode = get_shellcode(input_file)
    sc_len = len(shellcode.split(','))
    print('Shellcode length: ', sc_len)
    #sc_index = 0


    '''
        Translate shellcode using list comprehension
    '''
    translated_shellcode_gen = ('"{}"'.format(english_array[int(byte, 16)]) for byte in shellcode.split(','))
    translated_shellcode = 'unsigned char* translated_shellcode[XXX] = { ' + ','.join(translated_shellcode_gen)
    translated_shellcode = translated_shellcode.strip(',\'') + ' };\n'
    translated_shellcode = translated_shellcode.replace('XXX', str(sc_len))
    
    shellcode_var = "unsigned char shellcode[XXX] = {0};";
    shellcode_var = shellcode_var.replace('XXX', str(sc_len))

    generated_forloop = '''
        printf("Translating shellcode!\\n");
        /*
         for loop is defined as such:
          for (int sc_index = 0; sc_index < # of shelcode bytes; sc_index++)
        */
        for (int sc_index = 0; sc_index < XXX; sc_index++) {
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
    with open(output_file, "w") as outfile:
        outfile.write(translation_table + '\n')
        outfile.write(translated_shellcode + '\n')
        outfile.write(shellcode_var + '\n')
        outfile.write('int sc_len = sizeof(shellcode);\n')
        outfile.write(generated_forloop + '\n')


if __name__ == '__main__':
    main()
