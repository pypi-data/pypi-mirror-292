#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "global.h"
#include "getDir.h"

//****DEBUGGING************
#ifdef DBG
#include "memwatch.h"
#endif
//*************************

//Global variables
char DIR[1024]; //Directory

//gets the directory from the config file and puts it in the dir variable
//This will get the directory from the config file, make the directory if necessary
//and set it to the global DIR
//If the config file doesn't exist, then ask the user for a directory, write it to a config
//in the CWD
int getDir()
{
	char str[128];
	size_t len = 128;
	FILE *file = NULL;
	
	file = fopen("configECHAIM.dat", "r");
	
	if (file == NULL)
	{
				printf("Configuration file not found\n");
		printf("Enter the directory which contains the ECHAIM requirement files: ");
		
		fgets(str, len, stdin);
	
		file = fopen("configECHAIM.dat", "w+");
	
		fprintf(file, "#This is the directory which contains the ECHAIM database (.DB) file,\n");
		fprintf(file, "#the AACGM coefficient file, the COEFS database, and downloaded indices.\n");
		fprintf(file, "%s", str);
		
		fclose(file);

	} else
	{
	
		//read through the configuration file
		while ((fgets(str, len, file)) != NULL)
		{
			//Skip header and comments
			if (str[0] == '#') continue;
			
			fclose(file);
			
			break;
		}
	}
	
	//putting the directory in dataDir
	int n = strcspn(str, "\n");
	str[n] = 0;	
	
	if (str[n-1] == '\r') 
	{
		str[n-1] = 0;
		n--;
	}
	
	if (str[n] != '/') {str[n] = '/';}

	strcpy(DIR,str);
	
	return 1;
}

