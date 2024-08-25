# Uglifyc

This python script uglifies a C file by moving the charachters in char_list to the right (10 spaces to the right of the longest line)

## Installation

Install it via pip

```bash
pip install uglifyc
```

It can be run 2 ways:

```bash
uglifyc [input] -o [output]
```

```bash
uglifyc [input]
```

This last one will output to [file]_uglified.c

## Examples

### Input

```c
#include <stdio.h>
struct student {
    char name[50];
    int roll;
    float marks;
} s;

int main() {
    printf("Enter information:\n");
    printf("Enter name: ");
    fgets(s.name, sizeof(s.name), stdin);

    printf("Enter roll number: ");
    scanf("%d", &s.roll);
    printf("Enter marks: ");
    scanf("%f", &s.marks);

    printf("Displaying Information:\n");
    printf("Name: ");
    printf("%s", s.name);
    printf("Roll number: %d\n", s.roll);
    printf("Marks: %.1f\n", s.marks);

    return 0;
}
```

### Output

```c
#include <stdio.h>                                 
struct student                                    {
    char name[50]                                 ;
    int roll                                      ;
    float marks                                   ;
} s                                               ;

int main(                                       ) {
    printf("Enter information:\n"                );
    printf("Enter name: "                        );
    fgets(s.name, sizeof(s.name), stdin          );

    printf("Enter roll number: "                 );
    scanf("%d", &s.roll                          );
    printf("Enter marks: "                       );
    scanf("%f", &s.marks                         );

    printf("Displaying Information:\n"           );
    printf("Name: "                              );
    printf("%s", s.name                          );
    printf("Roll number: %d\n", s.roll           );
    printf("Marks: %.1f\n", s.marks              );

    return 0                                      ;
}
```
