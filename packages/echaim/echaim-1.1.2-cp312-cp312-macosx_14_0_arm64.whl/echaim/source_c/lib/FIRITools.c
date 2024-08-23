#include <stdlib.h>
#include "FIRITools.h"

//functions used in the D-region FIRI modules

//This function creates the 5D index from a 1D index
//specific to the FIRI arrays
int *indexTo5D(int input)
{
	//define variables
	int *output; 
	int indices[5] = {3,14,11,3,101};
	int cnt = 0;
	
	//define output memory
	output = calloc(5, sizeof(int));
	
	for (int a=0; a<indices[4]; a++)
	{
		for (int b=0; b<indices[3]; b++)
		{
			for (int c=0; c<indices[2]; c++)
			{
				for (int d=0; d<indices[1]; d++)
				{
					for (int e=0; e<indices[0]; e++)
					{
						if (cnt == input)
						{
							output[0] = e;
							output[1] = d;
							output[2] = c;
							output[3] = b;
							output[4] = a;
							return output;
						}
						
						cnt++;
					}
				}
			}
		}
	}
}

//This function takes the 1D FIRI arrays and returns the 5D array
double *****arrayTo5D(double *input)
{
	//define variables
	double *****output; 
	int indices[5] = {3,14,11,3,101};
	int cnt = 0;
	
	//define output memory
	output = calloc(indices[0], sizeof(double));
	for (int a=0; a<indices[0]; a++)
	{
		output[a] = calloc(indices[1], sizeof(double));
		for (int b=0; b<indices[1]; b++)
		{
			output[a][b] = calloc(indices[2], sizeof(double));
			for (int c=0; c<indices[2]; c++)
			{
				output[a][b][c] = calloc(indices[3], sizeof(double));
				for (int d=0; d<indices[3]; d++)
				{
					output[a][b][c][d] = calloc(indices[4], sizeof(double));
				}
			}
		}
	}
	
	for (int a=0; a<indices[4]; a++)
	{
		for (int b=0; b<indices[3]; b++)
		{
			for (int c=0; c<indices[2]; c++)
			{
				for (int d=0; d<indices[1]; d++)
				{
					for (int e=0; e<indices[0]; e++)
					{
						output[e][d][c][b][a] = input[cnt];
						cnt++;
					}
				}
			}
		}
	}
	
	return output;
	
}