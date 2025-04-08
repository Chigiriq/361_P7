#!/usr/bin/python3
import os
import sys

# This contains the binary operations add, sub, and, or as values. The keys are the Hack ML code to do them.
# Assume a getPopD() has been called prior to this lookup.
ARITH_BINARY = {
    "add": "@SP,A=A-1,M=M+D",
    "sub": "@SP,A=A-1,M=M-D",
    "and": "@SP,A=A-1,M=M&D",
    "or":  "@SP,A=A-1,M=M|D",
}

# As above, but now the keys are unary operations neg, not
# Values are sequences of Hack ML code, seperated by commas.
# In this case do not assume a getPopD() has been called prior to the lookup
ARITH_UNARY = {
    "neg": "@SP,A=M-1,M=-M",
    "not": "@SP,A=M-1,M=!M",
}

# Now, the code for operations gt, lt, eq as values. 
# These are assumed to be preceded by getPopD()
# The ML code corresponds very nicely to the jump conditions in 
# Hack assembly
ARITH_TEST = {
    "gt": "A=A-1,D=M-D,@isGT,D;JGT,@SP,M=M-1,A=M,M=0,@endGT,0;JMP,(isGT)@SP,M=M-1,A=M,M=-1,(endGT)",
    "eq": "A=A-1,D=M-D,@isEQ,D;JEQ,@SP,M=M-1,A=M,M=0,@endEQ,0;JMP,(isEQ)@SP,M=M-1,A=M,M=-1,(endEQ)",
    "lt": "A=A-1,D=M-D,@isLT,D;JLT,@SP,M=M-1,A=M,M=0,@endLT,0;JMP,(isLT)@SP,M=M-1,A=M,M=-1,(endLT)",
}

# Boring, but needed - translate the long VM names argument, local, this, that
# to the shorthand forms of these found in symbol table used for Hack assembly
SEGLABEL = {"local": "@LCL,", "argument": "@ARG,", "this": "@THIS,", "that": "@THAT,"}

# Here are the segments
SEGMENTS = {
    "constant": "D=A",
    "static": "@%s",
    "pointer": "@3",
    "temp": "@5",
}

# This will be used to generate unique labels when they are needed.
LABEL_NUMBER = 0

# The following dictionaries are used to translate VM language commands to machine language.
def getPushD():
    return "@SP,A=M,M=D,@SP,M=M+1,"

def getPopD():
    return "@SP,M=M-1,A=M,D=M,"

def pointerSeg(pushpop, seg, index):
    """ This function returns Hack ML code to push a memory location to 
    to the stack, or pop the stack to a memory location. 

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
    ans = "@" + str(index) + ",D=A,"  # Load index into D

    if seg in SEGLABEL:
        #those are pointers, meaning the RAM address associated with them in the symbol table contains
        # a RAM address where the SEGMENT begins. INDEX specifies where to go in the SEGMENT.

        if pushpop == 'push':
            ans += SEGLABEL[seg] + "A=M+D,D=M," + getPushD()
        elif pushpop == 'pop':
            ans += SEGLABEL[seg] + "A=M+D,@R13,M=D," + getPopD() + "@R13,A=M,M=D,"
        return ans
    else:
        raise ValueError(f"Invalid segment: {seg}")

def fixedSeg(pushpop, seg, index):
    """
    For pointer and temp segments
    """
    #Here, the values in the memory address specified by the segment are 
    # defined, 3 and 5 respectively and not indirectly specified pointers.

    if seg == 'pointer':
        addr = '@' + str(3 + index)  # Pointer starts at RAM[3]
    elif seg == 'temp':
        addr = '@' + str(5 + index)  # Temp starts at RAM[5]

    if pushpop == 'push':
        return addr + ",D=M," + getPushD()
    elif pushpop == 'pop':
        return getPopD() + addr + ",M=D,"

def constantSeg(pushpop, seg, index):
    """
    This will do constant and static segments
    """
    #constant is a virtual segment
    #need to assign static to a label or something

    #Then something special occurs, in this case it is more akin to direct
    # manipulation of the value in INDEX onto or off of the stack.

    if seg == 'constant':
        if pushpop == 'push':
            return "@" + str(index) + ",D=A," + getPushD()
        else:
            raise ValueError("Cannot pop to constant segment.")

    elif seg == 'static':
        static_var = f"@STATIC.{index}"
        if pushpop == 'push':
            return static_var + ",D=M," + getPushD()
        elif pushpop == 'pop':
            return getPopD() + static_var + ",M=D,"

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

def uniqueLabel():
    """ Uses LABEL_NUMBER to generate and return a unique label"""
    #when you need to jump to 0 or -1 becuase of arithtest
    ans = "temp" + str(LABEL_NUMBER)
    LABEL_NUMBER += 1
    return ans

def ParseFile(f):
    outString = ""
    for line in f:
        command = line2Command(line)
        if command:  # Only process non-None commands
            args = [x.strip() for x in command.split()]
            
            #Debugging Line
            print(f"Processing command: {args}")

            if args[0] in ARITH_BINARY.keys():
                """
                Code that will deal with any of the binary operations (add, sub, and, or)
                do so by doing the things all have in common, then do what is specific
                to each by pulling a key from the appropriate dictionary.
                Remember, it's always about putting together strings of Hack ML code.
                """
                outString += ARITH_BINARY[args[0]] + ","
                
            elif args[0] in ARITH_UNARY.keys():
                """
                As above, but now for the unary operators (neg, not)
                """
                outString += ARITH_UNARY[args[0]] + ","

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
                TRUElabel = uniqueLabel()
                FALSElabel = uniqueLabel()
                outString += ARITH_TEST[args[0]].replace("isGT", TRUElabel).replace("endGT", FALSElabel) + ","
                
            elif args[1] in ["pointer", "temp"]:
                """
                Redundant but it fixes the issue of the pointer and temp segments being handled in the same way.
                """
                segment = args[1]
                index = int(args[2])
                if args[0] == "push":
                    outString += fixedSeg("push", segment, index) + ","
                elif args[0] == "pop":
                    outString += fixedSeg("pop", segment, index) + ","

            elif args[1] in SEGLABEL.keys():
                """
                There's definitely a better way to do this, but it works for now. Fixes this, that ordering
                """
                segment = args[1]
                index = int(args[2])
                if args[0] == "push":
                    outString += pointerSeg("push", segment, index) + ","
                elif args[0] == "pop":
                    outString += pointerSeg("pop", segment, index) + ","

            elif args[1] in SEGMENTS.keys():
                """
                This is normal
                """
                segment = args[1]
                index = int(args[2])
                if args[0] == "push":
                    outString += constantSeg("push", segment, index) + ","
                elif args[0] == "pop":
                    outString += constantSeg("pop", segment, index) + ","

            else:
                print("Unknown segment!")
                print(args)
                sys.exit(-1)
        else:
            #debugging nonetype return error for comments
            print(f"Skipping line: {line.strip()}")

    l = uniqueLabel()
    outString += '(%s)' % (l) + ',@%s,0;JMP' % l
    return outString.replace(" ", "").replace(',', '\n')

# f = open("test.vm")

#memory
# f = open("MemoryAccess\\BasicTest\\BasicTest.vm") #works
# f = open("MemoryAccess\\PointerTest\\PointerTest.vm") #works
# f = open("MemoryAccess\\StaticTest\\StaticTest.vm") #works

#arithmetic
# f = open("StackArithmetic\\SimpleAdd\\SimpleAdd.vm") #works
f = open("StackArithmetic\\StackTest\\StackTest.vm") #works

print(ParseFile(f))
f.close()
