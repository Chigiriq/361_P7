//pushconstant111
@111
D=A
@SP
A=M
M=D
@SP
M=M+1


//pushconstant333
@333
D=A
@SP
A=M
M=D
@SP
M=M+1


//pushconstant888
@888
D=A
@SP
A=M
M=D
@SP
M=M+1


//popstatic8
@SP
AM=M-1
D=M
@StaticTest.8
M=D

//popstatic3
@SP
AM=M-1
D=M
@StaticTest.3
M=D

//popstatic1
@SP
AM=M-1
D=M
@StaticTest.1
M=D

//pushstatic3
@StaticTest.3
D=M
@SP
A=M
M=D
@SP
M=M+1


//pushstatic1
@StaticTest.1
D=M
@SP
A=M
M=D
@SP
M=M+1


//sub
@SP
AM=M-1
D=M
A=A-1
M=M-D

//pushstatic8
@StaticTest.8
D=M
@SP
A=M
M=D
@SP
M=M+1


//add
@SP
AM=M-1
D=M
A=A-1
M=D+M

(LOOP0)
@LOOP0
0;JMP
