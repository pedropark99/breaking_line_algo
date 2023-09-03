#include <stdio.h>
#include <string.h>
#include <stdlib.h>



typedef enum block_type {
	GLUE,
	BLOCK,
	PENALTY
} block_type;


typedef struct block_indexes {
	block_type block_type;
	double block_width;
	double shrink_factor;
	double stretch_factor;
	double penalty_factor;
	unsigned short int flag;
} block_indexes;



void read_csv()
{
	char *filename = "glyph_positions.csv";
	FILE *file_handler = fopen(filename, "r");
	if (file_handler == NULL) {
		printf("Not able to open the file.");
	}
	fclose(file_handler);
}



int main ()
{
	read_csv();
	return 1;
}
