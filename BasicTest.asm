//pushconstant10
@10
D=A
@SP
A=M
M=D
@SP
M=M+1


//poplocal0
@0
D=A
@LCL
D=D+M
@R13
M=D
@SP
AM=M-1
D=M

@R13
A=M
M=D


//pushconstant21
@21
D=A
@SP
A=M
M=D
@SP
M=M+1


//pushconstant22
@22
D=A
@SP
A=M
M=D
@SP
M=M+1


//popargument2
@2
D=A
@ARG
D=D+M
@R13
M=D
@SP
AM=M-1
D=M

@R13
A=M
M=D


//popargument1
@1
D=A
@ARG
D=D+M
@R13
M=D
@SP
AM=M-1
D=M

@R13
A=M
M=D


//pushconstant36
@36
D=A
@SP
A=M
M=D
@SP
M=M+1


//popthis6
@6
D=A
@THIS
D=D+M
@R13
M=D
@SP
AM=M-1
D=M

@R13
A=M
M=D


//pushconstant42
@42
D=A
@SP
A=M
M=D
@SP
M=M+1


//pushconstant45
@45
D=A
@SP
A=M
M=D
@SP
M=M+1


//popthat5
@5
D=A
@THAT
D=D+M
@R13
M=D
@SP
AM=M-1
D=M

@R13
A=M
M=D


//popthat2
@2
D=A
@THAT
D=D+M
@R13
M=D
@SP
AM=M-1
D=M

@R13
A=M
M=D


//pushconstant510
@510
D=A
@SP
A=M
M=D
@SP
M=M+1


//poptemp6
@SP
AM=M-1
D=M
@11
M=D

//pushlocal0
@0
D=A
@LCL
A=M
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1


//pushthat5
@5
D=A
@THAT
A=M
A=D+A
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

//pushargument1
@1
D=A
@ARG
A=M
A=D+A
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

//pushthis6
@6
D=A
@THIS
A=M
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1


//pushthis6
@6
D=A
@THIS
A=M
A=D+A
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

//sub
@SP
AM=M-1
D=M

A=A-1
M=M-D

//pushtemp6
@11
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
