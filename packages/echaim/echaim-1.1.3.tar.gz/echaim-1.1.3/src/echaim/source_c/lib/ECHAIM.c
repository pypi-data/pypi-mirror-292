#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include "getDir.h"
#include "date.h"
#include "ECHAIM.h"
#include "global.h"
#include <math.h>

//****DEBUGGING************
#ifdef DBG
#include "memwatch.h"
#endif
//*************************

int main ()
{
	//declare variables
	FILE *file;
	float latInt, lonInt, altInt, timeInt;
	double *lat, *lon, *alt, *yy, *mm, *dd, *hh, *mim, *ss;
	double *latout, *lonout, *altout, *y, *m, *d, *h, *mi, *s;
	char type;
	 //lat length, alt length, time length, storm option, DB update option, precip model option, d region model
	int ll, al, tl, storm, updateDB=0, precip=0, dregion=0;
	double *r, **rr; //output
	char fn[1024]; //file name and directory
	char b[12000]; //fgets buffer
	
	//set the directory from the config file
	getDir();
	
	//set file name and directory
	strcpy(fn,DIR);
	strcat(fn, "ECHAIMInputs.dat");
	
	file = fopen(fn, "r");
	
	if (file == NULL)
	{
		printf("Input file not found, check that your configECHAIM.dat file is set properly \n");
		printf("and the input file is in the correct location.\n");
		
		return 0;
	}
	
	//iterate through the header
	while (!feof(file))
	{
		fgets(b, sizeof(b), file);	
		//break when the header is completed
		if (b[0] != '#') break;
	}
	
	//check if full line was read by checking for the new line character
	char *lc = strchr(b,'\n');
	
	if (lc == NULL)
	{	
		printf("Error: Entire latitude line was not read. The line may exceed the 12000 character limit. Unexpected results may occur.\n");
	}
	
	//get lats
	//read the line and parse the data
	//this is taking the line that was previously determined to not be part of the header
	char *p = strtok(b, " ");
	int x=0;
	
	//initial allocation of memory
	lat = malloc(sizeof(double));
	
	//while string token exist
	while (p != NULL)
	{		
		//if first token set interval, otherwise populate array
		(x == 0) ? (latInt = atof(p)) : (lat[x-1] = atof(p));
		
		//check for another token
		p = strtok(NULL, " ");
		
		if (p != NULL)
		{
			if (p[0] == '\r' || p[0] == '\n') break;
			
			//increase memory
			if (x != 0) (lat = realloc(lat, sizeof(double) * (x + 1)));
			x++;
		}
	}
	
	//length of the lat array
	ll = x;
	
	//get lons
	//read the line and parse the data
	fgets(b, sizeof(b), file);
	
	//check if full line was read by checking for the new line character
	lc = strchr(b,'\n');
	
	if (lc == NULL)
	{	
		printf("Error: Entire longitude line was not read. The line may exceed the 12000 character limit. Unexpected results may occur.\n");
	}
	
	p = strtok(b, " ");
	x=0;
	
	//initial allocation of memory
	lon = malloc(sizeof(double));
	
	//while string token exist
	while (p != NULL)
	{		
		//if first token sent interval, otherwise populate array
		(x == 0) ? (lonInt = atof(p)) : (lon[x-1] = atof(p));
		
		//check for another token
		p = strtok(NULL, " ");
		
		if (p != NULL)
		{
			if (p[0] == '\r' || p[0] == '\n') break;
			
			//increase memory
			if (x != 0) (lon = realloc(lon, sizeof(double) * (x + 1)));
			x++;
		}
	}
	
	//if the lat and long lengths are not the same then error out
	if (ll != x)
	{
		printf("Error, Latitudes and Longitudes should be the same length\n");
		printf("Latitude length = %i\n", ll);
			printf("Longitude length = %i\n", x);
		return 0;
	}


	
	//get alts
	//read the line and parse the data
	fgets(b, sizeof(b), file);
	
	//check if full line was read by checking for the new line character
	lc = strchr(b,'\n');
	
	if (lc == NULL)
	{	
		printf("Error: Entire altitude line was not read. The line may exceed the 12000 character limit. Unexpected results may occur.\n");
	}
	
	p = strtok(b, " ");
	x=0;
	
	//initial allocation of memory
	alt = malloc(sizeof(double));
	
	//while string token exist
	while (p != NULL)
	{		
		//if first token sent interval, otherwise populate array
		(x == 0) ? (altInt = atof(p)) : (alt[x-1] = atof(p));
		
		//check for another token
		p = strtok(NULL, " ");
		
		if (p != NULL)
		{
			if (p[0] == '\r' || p[0] == '\n') break;
			
			//increase memory
			if (x != 0) (alt = realloc(alt, sizeof(double) * (x + 1)));
			x++;
		}
	}
	
	//length of the alt array
	al = x;
	
	//get time interval
	fgets(b, sizeof(b), file);
	sscanf(b, "%f", &timeInt);	
		
	//year
	fgets(b, sizeof(b), file);
	
	//check if full line was read by checking for the new line character
	lc = strchr(b,'\n');
	
	if (lc == NULL)
	{	
		printf("Error: Entire year line was not read. The line may exceed the 12000 character limit. Unexpected results may occur.\n");
	}
	
	p = strtok(b, " ");
	x = 0;
	
	//initial allocation of memory
	yy = malloc(sizeof(double));
	
	//while string token exist
	while (p != NULL)
	{		
		//populate array
		yy[x] = atof(p);
		
		//check for another token
		p = strtok(NULL, " ");
		
		if (p != NULL)
		{
			if (p[0] == '\r' || p[0] == '\n') break;
			
			//increase memory
			if (x != 0) (yy = realloc(yy, sizeof(double) * (x + 2)));
			x++;
		}
	}
	
	//time array length
	tl = x+1;

	//month
	fgets(b, sizeof(b), file);
	
	//check if full line was read by checking for the new line character
	lc = strchr(b,'\n');
	
	if (lc == NULL)
	{	
		printf("Error: Entire month line was not read. The line may exceed the 12000 character limit. Unexpected results may occur.\n");
	}
	
	p = strtok(b, " ");
	x = 0;
	
	//initial allocation of memory
	mm = malloc(sizeof(double));
	
	//while string token exist
	while (p != NULL)
	{
		
		//if first token sent interval, otherwise populate array
		mm[x] = atof(p);
		
		//check for another token
		p = strtok(NULL, " ");
		
		//check for another token
		if (p != NULL)
		{
			if (p[0] == '\r' || p[0] == '\n') break;
			
			//increase memory
			if (x != 0) (mm = realloc(mm, sizeof(double) * (x + 2)));
			x++;
		}
	}
	
	if (tl != x+1)
	{
		printf("Error, time inputs are not the same length\n");
		return 0;
	}
	
	//day
	fgets(b, sizeof(b), file);
	
	//check if full line was read by checking for the new line character
	lc = strchr(b,'\n');
	
	if (lc == NULL)
	{	
		printf("Error: Entire day line was not read. The line may exceed the 12000 character limit. Unexpected results may occur.\n");
	}
	
	p = strtok(b, " ");
	x = 0;
	
	//initial allocation of memory
	dd = malloc(sizeof(double));
	
	//while string token exist
	while (p != NULL)
	{
					
		//if first token sent interval, otherwise populate array
		dd[x] = atof(p);
		
		//check for another token
		p = strtok(NULL, " ");
		
		if (p != NULL)
		{
			if (p[0] == '\r' || p[0] == '\n') break;
			
			//increase memory
			if (x != 0) (dd = realloc(dd, sizeof(double) * (x + 2)));
			x++;
		}

	}
	
	if (tl != x+1)
	{
		printf("Error, time inputs are not the same length\n");
		return 0;
	}
		
	//hour
	fgets(b, sizeof(b), file);
	
	//check if full line was read by checking for the new line character
	lc = strchr(b,'\n');
	
	if (lc == NULL)
	{	
		printf("Error: Entire hour line was not read. The line may exceed the 12000 character limit. Unexpected results may occur.\n");
	}
	
	p = strtok(b, " ");
	x = 0;
	
	//initial allocation of memory
	hh = malloc(sizeof(double));
	
	//while string token exist
	while (p != NULL)
	{		
		//if first token sent interval, otherwise populate array
		hh[x] = atof(p);
		
		//check for another token
		p = strtok(NULL, " ");
		
		//check for another token
		if (p != NULL)
		{
			if (p[0] == '\r' || p[0] == '\n') break;
			
			//increase memory
			if (x != 0) (hh = realloc(hh, sizeof(double) * (x + 2)));
			x++;
		}
	}
	
	if (tl != x+1)
	{
		printf("Error, time inputs are not the same length\n");
		return 0;
	}
	
	//minute
	fgets(b, sizeof(b), file);
	
	//check if full line was read by checking for the new line character
	lc = strchr(b,'\n');
	
	if (lc == NULL)
	{	
		printf("Error: Entire minute line was not read. The line may exceed the 12000 character limit. Unexpected results may occur.\n");
	}
	
	p = strtok(b, " ");
	x = 0;
	
	//initial allocation of memory
	mim = malloc(sizeof(double));
	
	//while string token exist
	while (p != NULL)
	{			
		//if first token sent interval, otherwise populate array
		mim[x] = atof(p);
		
		//check for another token
		p = strtok(NULL, " ");
		
		//check for another token
		if (p != NULL)
		{
			if (p[0] == '\r' || p[0] == '\n') break;
			
			//increase memory
			if (x != 0) (mim = realloc(mim, sizeof(double) * (x + 2)));
			x++;
		}
	}
	
	if (tl != x+1)
	{
		printf("Error, time inputs are not the same length\n");
		return 0;
	}
	
	//second
	fgets(b, sizeof(b), file);
	
	//check if full line was read by checking for the new line character
	lc = strchr(b,'\n');
	
	if (lc == NULL)
	{	
		printf("Error: Entire second line was not read. The line may exceed the 12000 character limit. Unexpected results may occur.\n");
	}
	
	p = strtok(b, " ");
	x = 0;
	
	//initial allocation of memory
	ss = malloc(sizeof(double));
	
	//while string token exist
	while (p != NULL)
	{		
		//if first token sent interval, otherwise populate array
		ss[x] = atof(p);
		
		//check for another token
		p = strtok(NULL, " ");
		
		//check for another token
		if (p != NULL)
		{
			if (p[0] == '\r' || p[0] == '\n') break;
			
			//increase memory
			if (x != 0) (ss = realloc(ss, sizeof(double) * (x + 2)));
			x++;
		}
	}
	
	if (tl != x+1)
	{
		printf("Error, time inputs are not the same length\n");
		return 0;
	}	
	
	//get the type
	fgets(b, sizeof(b), file);
	sscanf(b, "%c", &type);	
	
	//Precip option
	fgets(b, sizeof(b), file);
	sscanf(b, "%i", &precip);	
	
	//d region option
	fgets(b, sizeof(b), file);
	sscanf(b, "%i", &dregion);	
	
	//DB update option
	fgets(b, sizeof(b), file);
	sscanf(b, "%i", &updateDB);
	
	fclose(file);
	
	//update DB if asked
	if (updateDB)
	{
		int rc = updateLocalDB(updateDB-1);
	}
	
	//create arrays
	if (latInt == 0)
	{
		latout = lat;
	} else
	{
		ll = round((lat[1] - lat[0])/latInt)+1;
		latout = calloc(ll, sizeof(double));
		
		for (int i=0; i<ll; i++)
			latout[i] = lat[0] + (i * latInt);
	}
	
	if (lonInt == 0)
	{
		lonout = lon;
	} else
	{
		int tll = round((lon[1] - lon[0])/lonInt)+1;
		
		if (tll != ll)
		{
			printf("Error, latitude and longitude are not the same length\n");
			printf("Latitude length = %i\n", ll);
			printf("Longitude length = %i\n", tll);
			return 0;
		}
		
		lonout = calloc(ll, sizeof(double));
		
		for (int i=0; i<ll; i++)
			lonout[i] = lon[0] + (i * lonInt);
	}
	
	if (altInt == 0)
	{
		altout = alt;
	} else
	{
		al = round((alt[1] - alt[0])/altInt)+1;
		
		altout = calloc(al, sizeof(double));
		
		for (int i=0; i<al; i++)
			altout[i] = alt[0] + (i * altInt);
	}
	
	
	if (timeInt == 0)
	{
		y = (double *)yy;
		m = (double *)mm;
		d = (double *)dd;
		h = (double *)hh;
		mi = (double *)mim;
		s = (double *)ss;
		
	} else
	{
		double jds = julianDate(yy[0],mm[0],dd[0],hh[0],mim[0],ss[0]);
		double jde = julianDate(yy[1],mm[1],dd[1],hh[1],mim[1],ss[1]);
		tl = round(((jde - jds) / (timeInt / 24.0)) + 1);
		
		y = calloc(tl, sizeof(double));
		m = calloc(tl, sizeof(double));
		d = calloc(tl, sizeof(double));
		h = calloc(tl, sizeof(double));
		mi = calloc(tl, sizeof(double));
		s = calloc(tl, sizeof(double));
		
		for (int i=0; i<tl; i++)
		{
			int *g = gregDate(jds + ((i * timeInt) / 24.0));
			
			y[i] = g[0];
			m[i] = g[1];
			d[i] = g[2];
			h[i] = g[3];
			mi[i] = g[4];
			s[i] = g[5];
			
			free(g);
			
		}
	}
	
	switch(type)
	{
		case 'n':
		
			if (tl != ll)
			{
				printf("Error, location and time arrays must be the same length\n");
				printf("Location length = %i\n", ll);
				printf("Time length = %i\n", tl);
				return 0;
			}
		
			r = NmF2(latout, lonout, y, m, d, h, mi, s, ll, 0);
			
		break;
		
		case 'm':
		
			if (tl != ll)
			{
				printf("Error, location and time arrays must be the same length\n");
				printf("Location length = %i\n", ll);
				printf("Time length = %i\n", tl);
				return 0;
			}		
			
			r = NmF2Storm(latout, lonout, y, m, d, h, mi, s, ll, 0);
			
		break;
		
		case '2':

			if (tl != ll)
			{
				printf("Error, location and time arrays must be the same length\n");
				printf("Location length = %i\n", ll);
				printf("Time length = %i\n", tl);
				return 0;
			}
		
			r = HmF2(latout, lonout, y, m, d, h, mi, s, ll, 0);
			
		break;
		
		case '1':

			if (tl != ll)
			{
				printf("Error, location and time arrays must be the same length\n");
				printf("Location length = %i\n", ll);
				printf("Time length = %i\n", tl);
				return 0;
			}
		
			r = HmF1(latout, lonout, y, m, d, h, mi, s, ll, 0);
			
		break;
		
		case 'p':
		
			if (tl != ll)
			{
				printf("Error, location and time arrays must be the same length\n");
				printf("Location length = %i\n", ll);
				printf("Time length = %i\n", tl);
				return 0;
			}
			
			storm = 0;
			
			rr = densityProfile(latout, lonout, y, m, d, h, mi, s, storm, precip, dregion, ll, altout, al, 0); 
			
		break;
		
		case 'r':
		
			if (tl != ll)
			{
				printf("Error, location and time arrays must be the same length\n");
				printf("Location length = %i\n", ll);
				printf("Time length = %i\n", tl);
				return 0;
			}
		
			storm = 1;
			
			rr = densityProfile(latout, lonout, y, m, d, h, mi, s, storm, precip, dregion, ll, altout, al, 0); 
			
		break;
		
		case 's':
		
			if (tl != ll || tl != al || ll != al)
			{
				printf("Error, location, altitude, and time arrays must be the same length\n");
				printf("Location length = %i\n", ll);
				printf("Altitude length = %i\n", al);
				printf("Time length = %i\n", tl);
				return 0;
			}		
		
			storm = 0;
			
			r = densityPath(latout, lonout, altout, y, m, d, h, mi, s, storm, precip, dregion, ll, 0); 
			
		break;
		
		case 'a':

			if (tl != ll || tl != al || ll != al)
			{
				printf("Error, location, altitude, and time arrays must be the same length\n");
				printf("Location length = %i\n", ll);
				printf("Altitude length = %i\n", al);
				printf("Time length = %i\n", tl);
				return 0;
			}
		
			storm = 1;
			
				r = densityPath(latout, lonout, altout, y, m, d, h, mi, s, storm, precip, dregion, ll, 0); 
		
		break;
	}
	
	//output the data
	char fo[1024];
	strcpy(fo,DIR);
	strcat(fo,"ECHAIMOutput.dat");
	file = fopen(fo, "w");
	
	if (type == 'p' || type == 'r')
	{
		fprintf(file, "%i %i\n", ll, al);
		
		for (int i=0; i<ll; i++)
		{
			int j;
			for (j=0; j<al-1; j++) {fprintf(file, "%f ", rr[i][j]);}
			
			fprintf(file, "%f\n", rr[i][j]);
		}
		
		for (int i=0; i<ll; i++) {free(rr[i]);}
		free(rr);
		
	}else
	{
		fprintf(file, "1 %i\n", ll);
		
		for (int i=0; i<ll; i++){fprintf(file, "%f\n", r[i]);}
		
		free(r);
	}

	fclose(file);

	if (latInt == 0) free(lat); else {free(latout); free(lat);}
	if (lonInt ==0) free(lon); else {free(lonout); free(lon);}
	if (altInt ==0) free(alt); else {free(altout); free(alt);}
	free(yy);
	free(mm);
	free(dd);
	free(hh);
	free(mim);
	free(ss);
	
	if (timeInt != 0)
	{
		free(y);
		free(m);
		free(d);
		free(h);
		free(mi);
		free(s);
	}
	
	printf("E-CHAIM calculation is complete.\n");
	
	return 0;
}