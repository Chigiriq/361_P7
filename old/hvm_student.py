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
    "gt":  "A=A-1,D=M-D,@isGT,D;JGT,@SP,M=M-1,A=M,M=0,@endGT,0;JMP,(isGT)@SP,M=M-1,A=M,M=-1,(endGT)",
    "eq":  "A=A-1,D=M-D,@isEQ,D;JEQ,@SP,M=M-1,A=M,M=0,@endEQ,0;JMP,(isLT)@SP,M=M-1,A=M,M=-1,(endEQ)",
    "lt":  "A=A-1,D=M-D,@isLT,D;JLT,@SP,M=M-1,A=M,M=0,@endLT,0;JMP,(isLT)@SP,M=M-1,A=M,M=-1,(endLT)",
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
ARITH_TEST  = {
    "gt":  "A=A-1,D=M-D,@isGT,D;JGT,@SP,M=M-1,A=M,M=0,@endGT,0;JMP,(isGT)@SP,M=M-1,A=M,M=-1,(endGT)",
    "eq":  "A=A-1,D=M-D,@isEQ,D;JEQ,@SP,M=M-1,A=M,M=0,@endEQ,0;JMP,(isLT)@SP,M=M-1,A=M,M=-1,(endEQ)",
    "lt":  "A=A-1,D=M-D,@isLT,D;JLT,@SP,M=M-1,A=M,M=0,@endLT,0;JMP,(isLT)@SP,M=M-1,A=M,M=-1,(endLT)",
}

# Boring, but needed - translate the long VM names argument, local, this, that
# to the shorthand forms of these found in symbol table used for Hack assembly
SEGLABEL = {"local": "@LCL,", "argument": "@ARG,", "this": "@THIS,", "that": "@THAT,",}

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
    # This method takes no arguments and returns a string with assembly language
    # that will push the contents of the D register to the stack.
    #@SP 
    #A=M    start at stack pointer address
    #M=D    save D into M
    #@SP    go back to pointer
    #M=M+1  index pointer to be next addr
    return "@SP,A=M,M=D,@SP,M=M+1,"

def getPopD():
    # This method takes no arguments and returns a string with assembly language
    # that will pop the stack to the D register.
    # SIDE EFFECT: The A register contains the SP.
    #@SP 
    #M=M-1 index SP down 1
    #A=M   go to new SP address
    #D=M   save val in there to D
    return "@SP,M=M-1,A=M,D=M,"

def pointerSeg(pushpop,seg,index):
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

    
    ans = "@" + str(index) + ",D=A,"

    if seg in SEGLABEL:
        #those are pointers, meaning the RAM address associated with them in the symbol table contains
        # a RAM address where the SEGMENT begins. INDEX specifies where to go in the SEGMENT.
        if pushpop == 'push':
            ans = ans + SEGLABEL.get(seg) + "A=M,A=A+D,D=M," + getPushD()
            return ans

        elif pushpop == 'pop':
            ans = ans + SEGLABEL.get(seg) + "A=D+M,D=M,@R13,M=D," + getPopD() + "@R13,A=M,M=D,"
            return ans

##XXX WHYHYHYYHY
def fixedSeg(push,seg,index):
    """
    For pointer and temp segments
    """
    #Here, the values in the memory address specified by the segment are 
    # defined, 3 and 5 respectively and not indirectly specified pointers.
    
    if seg == 'pointer':
        addr = '@3'

    elif seg == 'temp':
        addr = '@5'

    ans = addr + str(index) + ",D=A,"

    if push == 'push':
        ans = ans + getPushD()

    elif push == "pop":
        ans = ans + "D=A,@R13,M=D" + getPopD()
    
    return ans


def constantSeg(push,seg,index):
    """
    This will do constant and static segments
    """
    #constant is a virtual segment
    #need to assign static to a label or something

    #Then something special occurs, in this case it is more akin to direct
    # manipulation of the value in INDEX onto or off of the stack.

    if seg == 'constant':
        ans = "@" + str(index) + ",D=A,"

        if push == 'push':
            ans = ans + getPushD()
        
        elif push == 'pop':
            ans = ans + getPopD()

        return ans
    
    elif seg == 'static':
        ans = "@STATIC." + str(index) + ",D=A,"

        if push == 'push':
            ans = ans + getPushD()
        
        elif push == 'pop':
            ans = ans + "@R13,M=D," + getPopD()

        return ans

def line2Command(line):
    """ This just returns a cleaned up line, removing unneeded spaces and comments"""
    line = line.strip()
    if not line or line.startswith('//'):
        return None
    
    line = line.split('//')[0].strip()
    return line     

def uniqueLabel():
    """ Uses LABEL_NUMBER to generate and return a unique label"""
    #when you need to jump to 0 or -1 becuase of arithtest
    ans = "@temp" + str(LABEL_NUMBER)
    LABEL_NUMBER += 1

    return ans


def ParseFile(f):
    outString = ""
    for line in f:
        command = line2Command(line)
        if command:
            args = [x.strip() for x in command.split()] # Break command into list of arguments, no return characters
            if args[0] in ARITH_BINARY.keys():
                """
                Code that will deal with any of the binary operations (add, sub, and, or)
                do so by doing the things all have in common, then do what is specific
                to each by pulling a key from the appropriate dictionary.
                Remember, it's always about putting together strings of Hack ML code.
                """
                outString = outString + ARITH_BINARY[args[0]] + ","

            elif args[0] in ARITH_UNARY.keys():
                """
                As above, but now for the unary operators (neg, not)
                """
                outString = outString + ARITH_UNARY[args[0]] + ","

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
                #if something is less than something else what do you do?....probably cry
                #   remove both and put a true (-1): 0xFFFF on the stack
                #       review the quiz cuz its on there
                TRUElabel = uniqueLabel()
                FALSElabel = uniqueLabel()

                #XXX bro what
                outString = outString + ARITH_TEST[args[0]].replace("isGT", TRUElabel).replace("endGT", FALSElabel) + ","


            elif args[1] in SEGMENTS.keys():
                """
                Here we deal with code that's like push/pop segment index.
                You've written the functions, the code in here selects the right 
                function by picking a function handle from a dictionary. 
                """

                if args[0] == "push":
                    outString = outString + SEGMENTS[args[1]]["push"](args[2]) + ","

                elif args[0] == "pop":
                    outString = outString + SEGMENTS[args[1]]["pop"](args[2]) + ","

            else:
                print("Unknown command!")
                print(args)
                sys.exit(-1)

    l = uniqueLabel()
    outString += '(%s)'%(l)+',@%s,0;JMP'%l # Final endless loop
    return outString.replace(" ","").replace(',','\n')


# filename = sys.argv[1].strip()

# This is ugly - add some error checking on file open.
# f = open(filename)
f = open("SimpleAdd.vm")
print(ParseFile(f))
f.close()
