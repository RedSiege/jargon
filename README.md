# Jargon

Jargon  
/ˈjärɡən/  
noun: jargon; plural noun: jargons  
Definition: special words or expressions that are used by a particular profession or group and are difficult for others to understand.

## Usage
```
python3 jargon.py -i input.bin -d /path/to/dictionary.txt -o output.c
```
## Instructions
Jargon takes raw shellcode bytes (output format Raw in Cobalt Strike) as input. It also requires a dictionary file containing unique words, one per line, as input. **_The input file must be deduplicated_**. If your dictionary contains duplicate words, Jargon may select the same word for two different shellcode values, resulting in a broken loader.

## Background
In order to protect our shellcode loaders, we often use encryption to obfuscate our shellcode.  Encryption increases the entropy of our shellcode loader.  Some AV & EDR use entropy analysis to determine if a binary is trustworthy for execution.  If the entropy of a binary is too high, the agent makes a decision the binary is not trustworth for execution. This is, of course, an oversimplified explanation, but it will work for our purposes.

This project takes raw shellcode and encodes it using a dictionary of words. The dictionary could be a dictionary of English words, the text of a Shakespearean tragedy, or it could be strings extracted from your favorite system DLL. The only requirement is that the dictionary contains at least 256 unique entries and all characters are valid for string literals in C/C++.

_tldr: Use this program to translate shellcode bytes into words for entropy analysis evasion._

## How it works
We typically see shellcode represented as hex bytes - 0x00 to 0xff. However, we can also use integers to represent our shellcode. Since our shellcode can only possibly consist of 256 different values, the program reads the dictionary, selects 256 random words, and places them in an array. A word's position in this tranlsation array represents its shellcode value. Consider the following example:
```
unsigned char* translation_table[5] = { "petition","creates","proposal","maintain","winner" };
```
To tranlsate our shellcode into an array of words, we read each byte of shellcode and pull the word from the translation table using the shellcode value as the index. Using the example above, if our first byte of shellcode is `0x01`, the value at `translation_table[1]` is `creates`. We take the word found at our index and append it to a new array that represents our translated shellcode. We repeat this process until we've reached the end of our shellcode. This will give us two arrays that look like the following abbreviated examples:
```
const char* translation_table[256] = { "petition","creates","proposal","maintain","winner","accommodations","submitted"..." };

const char* translated_shellcode[287] = { "staying","valuation","differences","score","disks","interests","controls" ... };
```
To use this translated shellcode in our loader, we simply reverse the process.  For each entry in the translated_shellcode array, we search the translation table for that value. The array index of the word is our shellcode byte. Given the first 4 bytes of 64-bit shellcode are typically `0xfc,0x48,0x83,0xe4,` we can surmise that `"staying","valuation","differences","score"` translates to translation_table[252], translation_table[72], translation_table[131], translation_table[228]. As a result, the first 4 bytes of our reconstructed shellcode will be `252,72,131,228.`

This program will generate C source code containing the two array definitions and the translation routine to recover the shellcode bytes.

## Prior art
Before I wrote this tool, I tried to find examples that people had written before me.  I came up short, despite a lot of searching.  Since originally writing the tool, I became aware of people who have written similar tools, but their tools are not public. These projects are using similar concepts:

[https://github.com/moloch--/wire-transfer](wire-transfer): Encode binary files into English text for transfer over HTTP.  
[https://github.com/BishopFox/sliver/blob/master/util/encoders/english.go](Sliver C2): Encode binary file as English text.  
