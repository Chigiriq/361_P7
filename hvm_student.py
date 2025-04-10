#!/usr/bin/python3
import os
import sys
from pathlib import Path

# The following dictionaries are used to translate VM language commands to machine language.
def getPopD():
    return f"@SP,AM=M-1,D=M,"

def getPushD():
    return f"@SP,A=M,M=D,@SP,M=M+1,"

# This contains the binary operations add, sub, and, or as values. The keys are the Hack ML code to do them.
# Assume a getPopD() has been called prior to this lookup.
ARITH_BINARY = {
    "add": getPopD() + ",A=A-1,M=D+M,,",
    "sub": getPopD() + ",A=A-1,M=M-D,,",
    "and": getPopD() + ",A=A-1,M=D&M,,",
    "or":  getPopD() + ",A=A-1,M=D|M,,",
}

# As above, but now the keys are unary operations neg, not
# Values are sequences of Hack ML code, seperated by commas.
# In this case do not assume a getPopD() has been called prior to the lookup
ARITH_UNARY = {
    "neg": "@SP,A=M-1,M=-M,,",
    "not": "@SP,A=M-1,M=!M,,",

}

# Now, the code for operations gt, lt, eq as values. 
# These are assumed to be preceded by getPopD()
# The ML code corresponds very nicely to the jump conditions in 
# Hack assembly
ARITH_TEST  = {
    "eq": "JEQ",
    "lt": "JLT",
    "gt": "JGT",
}

# Boring, but needed - translate the long VM names argument, local, this, that
# to the shorthand forms of these found in symbol table used for Hack assembly
SEGLABEL = {
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT"
}


# This will be used to generate unique labels when they are needed.
LABEL_NUMBER = 0
POINTER_BASE = 3  # Base address for pointer segment
TEMP_BASE = 5  # Base address for temp segment
FILENAME = ""

def pointerSeg(pushpop, seg, index):
    """
    Generate Hack assembly code for push/pop operations on pointer-based segments.


    INPUTS:
        pushpop = a text string 'pop' means pop to memory location, 'push' 
                  is push memory location onto stack
        seg     = the name of the segment that will be be the base address
                  in the form of a text string
        index   = an integer that specifies the offset from the base 
                  address specified by seg

    RETURN: 
        The memory address is speficied by segment's pointer (SEGLABEL[seg]) + index (index))
        if pushpop is 'push', push the address contents to the stack
        if pushpop is 'pop' then pop the stack to the memory address.
        The string returned accomplishes this. ML commands are seperated by commas (,).

    NOTE: This function will only be called if the seg is one of:
    "local", "argument", "this", "that"

    """
    output_str = ""
    
    base_address = SEGLABEL[seg]
    if pushpop == "push":
        output_str = "@" + str(index) + ",D=A," + "@" + base_address + ",A=M,A=D+A,D=M," + getPushD()

    else:
        output_str = "@" + str(index) + ",D=A," + "@" + base_address + ",D=D+M,@R13,M=D," + getPopD() + ",@R13,A=M,M=D,"

    return output_str + ",,"


def fixedSeg(pushpop,seg,index):
    """
    For pointer and temp segments
    """
    #Here, the values in the memory address specified by the segment are 
    # defined, 3 and 5 respectively and not indirectly specified pointers.
    if seg == "pointer":
        base = POINTER_BASE

    else:
        base = TEMP_BASE

    addr = f"@{base + index}"
    output_str = ""

    if pushpop == "push":
        output_str = addr + ",D=M," + getPushD()

    else:
        output_str = getPopD() + addr + ",M=D"

    return output_str + ",,"


def constantSeg(pushpop,seg,index):
    """
    This will do constant and static segments
    """
    #constant is a virtual segment
    #need to assign static to a label or something

    #Then something special occurs, in this case it is more akin to direct
    # manipulation of the value in INDEX onto or off of the stack.

    """
    This will do constant and static segments
    """
    output_str = ""

    if seg == "constant":
        output_str= "@" + str(index) + ",D=A," + getPushD()

    else:
        var = f"@{FILENAME}.{index}"

        if pushpop == "push":
            output_str = var + ",D=M," + getPushD()

        else:
            output_str = getPopD() + var + ",M=D,"

    return output_str + ",,"

def line2Command(line):
    """ This just returns a cleaned up line, removing unneeded spaces and comments"""
    line = line.strip()
    if not line or line.startswith('//'):
        return None
    command = line.split('//')[0].strip()

    #adding this because nonetype return error for comments
    if not command:
        return None
    return command

def uniqueLabel(id, label_number):
    """ Uses LABEL_NUMBER to generate and return a unique label"""
    label = f"{id.upper()}{label_number}"
    return label

# Here are the segments
SEGMENTS = {
    "local": pointerSeg,
    "argument": pointerSeg,
    "this": pointerSeg,
    "that": pointerSeg,
    "pointer": fixedSeg,
    "temp": fixedSeg,
    "constant": constantSeg,
    "static": constantSeg,
}

def ParseFile(f):
    outString = ""
    label_number = 0
    for line in f:
        command = line2Command(line)
        if command:  # Only process non-None commands
            args = [x.strip() for x in command.split()]
            
            #Debugging Line
            # print(f"Processing command: {args}")

            if args[0] in ARITH_BINARY.keys():
                """
                Code that will deal with any of the binary operations (add, sub, and, or)
                do so by doing the things all have in common, then do what is specific
                to each by pulling a key from the appropriate dictionary.
                Remember, it's always about putting together strings of Hack ML code.
                """
                outString += f"// {args[0]},"
                outString += ARITH_BINARY[args[0]]
                
            elif args[0] in ARITH_UNARY.keys():
                """
                As above, but now for the unary operators (neg, not)
                """
                outString += f"// {args[0]},"
                outString += ARITH_UNARY[args[0]]

            elif args[0] in ARITH_TEST.keys():
                """
                Deals with the three simple operators (lt,gt,eq), but likely the hardest
                section because you'll have to write assembly to jump to a different part
                of the code, depending on the result.
                To define where to jump to, use the uniqueLabel() function to get labels.
                The result should be true (0xFFFF) or false (0x0000) depending on the test.
                That goes back onto the stack.
                HINT: Review the quiz for this unit!
                """
                jump = ARITH_TEST[args[0]]
                label_true = uniqueLabel("true",label_number)
                label_false = uniqueLabel("false",label_number)
                label_number += 1
                outString += f"// {args[0]},"
                outString += getPopD() + ",@SP,AM=M-1," + "D=M-D," + "@" + label_true + ",D;" + jump + ",@SP,A=M,M=0,@" + label_false + ",0;JMP,(" + label_true + "),@SP,A=M,M=-1,(" + label_false + "),@SP,M=M+1,"
                
            elif args[1] in SEGMENTS.keys():
                """
                Here we deal with code that's like push/pop segment index.
                You've written the functions, the code in here selects the right 
                function by picking a function handle from a dictionary. 
                """
                pushpop, seg, index = args[0:3]

                # invalid push/pop
                if pushpop not in ["push", "pop"]:
                    err += f"Invalid operation, {pushpop}. Use 'push' or 'pop'"
                    raise ValueError(err)

                # invalid segment
                if seg not in SEGMENTS.keys():
                    err += f"Invalid segment, {seg} not in {SEGMENTS.keys()}"
                    raise ValueError(err)

                # invalid index
                if (int(index) < 0 ):
                    err += f"Invalid Index, {index} must be a positive integer"
                    raise ValueError(err)


                outString += f"// {pushpop} {seg} {index},"
                outString += SEGMENTS[seg](pushpop,seg,int(index))

            # invalid segment
            else:
                err += f"Invalid segment, {args[1]} not in {SEGMENTS.keys()}"
                raise ValueError(err)
        else:
            #debugging nonetype return error for comments
            # print(f"Skipping line: {line.strip()}")
            pass

    l = uniqueLabel("loop", label_number)
    outString += '(%s)' % (l) + ',@%s,0;JMP' % l
    return outString.replace(" ", "").replace(',', '\n')

def main():
    global FILENAME

    # FILENAME = "StackArithmetic\\SimpleAdd\\SimpleAdd.vm" #works
    FILENAME = "StackArithmetic\\StackTest\\StackTest.vm" #works
    # FILENAME = "MemoryAccess\\BasicTest\\BasicTest.vm" #works
    # FILENAME = "MemoryAccess\\PointerTest\\PointerTest.vm" #works
    # FILENAME = "MemoryAccess\\StaticTest\\StaticTest.vm" #works 

    

    f = open(FILENAME)
    # print(Path("MemoryAccess\\StaticTest\\StaticTest.vm").stem)
    FILENAME = Path("MemoryAccess\\StaticTest\\StaticTest.vm").stem #only ever called for static so this is ok
    print(ParseFile(f))
    f.close()
    
main()