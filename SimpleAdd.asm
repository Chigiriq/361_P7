//pushconstant7
@7
D=A
@SP
A=M
M=D
@SP
M=M+1


//pushconstant8
@8
D=A
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
