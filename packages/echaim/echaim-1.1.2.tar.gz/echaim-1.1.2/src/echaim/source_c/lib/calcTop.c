#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include "getIndices.h"
#include "mathlib.h"
#include "prepInd.h"
#include "getMagCoords.h"
#include "parameterTop.h"
#include "getCoefs.h"
#include "date.h"
#include "otherIndices.h"
#include "global.h"
#include "calcTop.h"
#include "maxIndices.h"
#include "parameterAE.h"
#include "sqlite3.h"

//****DEBUGGING************
#ifdef DBG
#include "memwatch.h"
#endif
//*************************

#define D2R 0.017453292519943295769

//Routine to calculate the HF1 part of the model
//input is 3 arrays, magnetic latitude and longitude
// Julian times, and altitudes
//arrays are the same length l0
//output is array, size of l0
double *calcTop (double *jd, double *glat, double *glon, double *lat, double *mlt, int l0, sqlite3 *db, sqlite3 *dbCoefs)
{
	//declare variables
	//output array, magnetic coordinates
	//model coefficients
	double *output, *alt, *coefs; //length = l0
	double *modip, *inclen; //length=l0
	
	//interpolated indices array
	double *f10_27ip, *f10_81ip, *aeip, *igip; //length = l0
	
	//F10.7 flux indices, smoothed to 27 days, smoothed to 81 days, time array
	double *f10_27, *f10_81, *f10x, *f1081x; //length = lf10
	int lf10;
	
	//AE indices, integrated AE
	double *aex, *aeInt; //length of lig
	int lae;

	//IG indices
	double *ig, *igx; //length of lig
	int lig;
	
	//solar zenith angle, dipole tilt
	double *sza, *dp; //length =l0
	
	//bottomside parameters
	double **params; //length = 263x24
	
	int r, *lx; //temporary, min and max jd, length placeholder
	double jd0, jd1, jd0IG, jd1IG;
	
	sza = calloc(l0, sizeof(double));
	dp = calloc(l0, sizeof(double));
	alt = calloc(l0, sizeof(double));
	output = calloc(l0, sizeof(double));
	modip = calloc(l0, sizeof(double));
	inclen = calloc(l0, sizeof(double));

	
	//get the min and max JD inputted
	//The time range will got from min(jd) - 81 days to max(jd) + 81
	//this is specific to the F10 data
	//*** range needs to be decided here
	r = minInd(jd, l0);
	jd0 = jd[r];
	r = maxInd(jd,l0);
	jd1 = jd[r];

	//setting the time range for the IG data
	//Need to be one month before and after the chosen date
	int *gd = gregDate(jd0);
	jd0IG = (gd[1] == 1) ? julianDate(gd[0]-1,12,1,0,0,0) - 1.0 : julianDate(gd[0],gd[1]-1,1,0,0,0) - 1.0;
	free(gd);
	
	gd = gregDate(jd1);
	jd1IG = (gd[1] == 12) ? julianDate(gd[0]+1,1,1,0,0,0) + 1.0 : julianDate(gd[0],gd[1]+1,1,0,0,0) + 1.0;	
	free(gd);
	
	//get the data for each input time/location pair
	for (int i=0; i<l0; i++)
	{
		double *t;
			
		//inclination angle and modip
		inclen[i] = atan(2.0 * tan(D2R * lat[i])) / D2R;
		modip[i] = atan((inclen[i] * D2R) / sqrt(cos(D2R * glat[i]))) / D2R;

		//dipole tilt
		dp[i] = dpTilt(jd[i]);
		
		//input DOY, hour, latitude, longitude
		t = zenSun(jdDOY(jd[i]), (jd[i] - jdDaily(jd[i])) * 24.0, glat[i], glon[i]);
		sza[i] = t[0];
	}
	
	//get the F10.7 data
	f10_27 = F10_27(jd0-43.0, jd1+43.0, &f10x, &lx, db);
	lf10 = lx[0];
	f10_81 = F10_81(jd0-43.0, jd1+43.0, &f1081x, &lx, db);

	//get the IG data
	//adding 30 days to 	
	ig = IG(jd0IG, jd1IG, &igx, &lx, db);
	lig = lx[0];
	
	//interpolate the indices to the inputted times
	f10_81ip = interp(f10_81, f10x, lf10, jd, l0);
	f10_27ip = interp(f10_27, f1081x, lf10, jd, l0);
	igip = interp(ig, igx, lig, jd, l0);
	
	//Time integrate AE
	//Check if time is beyond where time integrated AE exists
	if (jd1+1 > maxAE(1,NULL))
	{
		//getting the max time of AE values
		double mae = maxAE(1,NULL);
		
		//if the entire interval is greater than the max AE time
		if (jd0-1 > mae)
		{
			lae = 0;
			aeip = calloc(l0, sizeof(double));
			
		}else //get the AE up to the maximum time
		{
			aeInt = AE(jd0-1, mae, &aex, &lx, db);
			lae = lx[0];
		
			aeip = interp(aeInt, aex, lae, jd, l0);
			
			free(aeInt);
			free(aex);
		}
		
		//get PC for the rest of the time
		double *pcx;
		double *pcInt = PC(mae, jd1+1, &pcx, &lx, db);
		
		//interpolate to the input times
		double *pcip = interp(pcInt, pcx, lx[0], jd, l0);
		
		//setting requested times gt max pc to 0
		double mpc = maxPC(1,NULL);
		for (int i=0; i<l0; i++)
		{
			if (jd[i] > mpc) pcip[i] = 0.0;
		}
		
		//calculate the synthetic AE from PC
		double **aeparams = parametersAE(jd, f10_81ip, dp, pcip, l0);
		double *aecoefs = getAE(dbCoefs);
		
		double *aepcip = calloc(l0, sizeof(double));
		
		double s;
		for (int i=0; i<l0; i++)
		{
			s=0;
			
			for (int j=0; j<6; j++)
			{
				s += aeparams[i][j] * aecoefs[j+1];
			}
			
			aepcip[i] = s + aecoefs[0];
			
		}
		
		//append synthetic AE to AE array
		for (int i=0; i<l0; i++)
		{
			if (jd[i] > mae) 
			{
				if (aepcip[i] >= 15.0)  aeip[i] = aepcip[i]; else aeip[i] = 15.0;
			}
		}
		
		
		free(pcInt);
		free(pcx);
		for (int i=0; i<l0; i++) {free(aeparams[i]);}
		free(aeparams);
		free(aecoefs);
		free(aepcip);	
		free(pcip);
		
	//if the range contains the 1976-1977 range
	}else if (jd0-1 <  2443509.5 && jd1+1 > 2442778.5) //Jan 1 1976, Jan 1 1976
	{
		//create the synthetic AE from PC=0 for all times
		double *pcip = calloc(l0, sizeof(double));
		
		for (int i=0; i<l0; i++) {pcip[i] = 0.0;}
		
		//calculate the synthetic AE from PC
		double **aeparams = parametersAE(jd, f10_81ip, dp, pcip, l0);
		double *aecoefs = getAE(dbCoefs);
		
		double *aepcip = calloc(l0, sizeof(double));
		
		double s;
		for (int i=0; i<l0; i++)
		{
			s=0;
			
			for (int j=0; j<6; j++)
			{
				s += aeparams[i][j] * aecoefs[j+1];
			}
			
			aepcip[i] = s + aecoefs[0];
			
		}
		
		//if the entire interval is within 1976/77
		if (jd0-1 > 2442778.5 && jd1+1 < 2443509.5)
		{
			lae = 0;
			aeip = calloc(l0, sizeof(double));
			
			for (int i=0; i<l0; i++) 
			{
				if (aepcip[i] >= 15.0)  aeip[i] = aepcip[i]; else aeip[i] = 15.0;
			}
			
			
		}else //years are only part of the entire range
		{
			aeInt = AE(jd0, jd1+1, &aex, &lx, db);
			lae = lx[0];
		
			aeip = interp(aeInt, aex, lae, jd, l0);
			
			free(aeInt);
			free(aex);
			
			for (int i=0; i<l0; i++) 
			{
				if (jd[i] < 2442778.5 || jd[i] > 2443509.5) continue; 
				if (aepcip[i] >= 15.0)  aeip[i] = aepcip[i]; else aeip[i] = 15.0;
			}
			
		}
		
		for (int i=0; i<l0; i++) {free(aeparams[i]);}
		free(aeparams);
		free(aecoefs);
		free(aepcip);	
		free(pcip);
	
	//if the range contains the 1988-1989 range
	}else if (jd0-1 <  2447892.5 && jd1+1 > 2447161.5) //Jan 1 1990, Jan 1 1988
	{
		//create the synthetic AE for all times
		double *pcx;
		double *pcInt = PC(jd0-1, jd1+1, &pcx, &lx, db);
		
		//interpolate to the input times
		double *pcip = interp(pcInt, pcx, lx[0], jd, l0);
				
		//calculate the synthetic AE from PC
		double **aeparams = parametersAE(jd, f10_81ip, dp, pcip, l0);
		double *aecoefs = getAE(dbCoefs);
		
		double *aepcip = calloc(l0, sizeof(double));
		
		double s;
		for (int i=0; i<l0; i++)
		{
			s=0;
			
			for (int j=0; j<6; j++)
			{
				s += aeparams[i][j] * aecoefs[j+1];
			}
			
			aepcip[i] = s + aecoefs[0];
			
		}
		
		//if the entire interval is within 1976/77
		if (jd0-1 > 2447161.5 && jd1+1 < 2447892.5)
		{
			lae = 0;
			aeip = calloc(l0, sizeof(double));
			
			for (int i=0; i<l0; i++) 
			{
				if (aepcip[i] >= 15.0)  aeip[i] = aepcip[i]; else aeip[i] = 15.0;
			}
			
			
		}else //years are only part of the entire range
		{
			aeInt = AE(jd0, jd1+1, &aex, &lx, db);
			lae = lx[0];
		
			aeip = interp(aeInt, aex, lae, jd, l0);
			
			free(aeInt);
			free(aex);
			
			for (int i=0; i<l0; i++) 
			{
				if (jd[i] < 2447161.5 || jd[i] > 2447892.5) continue; 
				if (aepcip[i] >= 15.0)  aeip[i] = aepcip[i]; else aeip[i] = 15.0;
			}
			
		}
		
		for (int i=0; i<l0; i++) {free(aeparams[i]);}
		free(aeparams);
		free(aecoefs);
		free(aepcip);	
		free(pcip);
	
	}else //get AE for entire range
	{
		aeInt = AE(jd0-1, jd1+1, &aex, &lx, db);
		lae = lx[0];
		
		aeip = interp(aeInt, aex, lae, jd, l0);
		
		free(aeInt);
		free(aex);
	}

	//free the flux and IG arrays
	free(f10_27);
	free(f10_81);
	free(f10x);
	free(f1081x);
	free(igx);
	free(ig);
	free(alt);
	
	//get the bottomside parameters
	params = parametersTop(lat, mlt, jd, sza, igip, f10_27ip, f10_81ip, dp, aeip, modip, inclen, l0);
	
	//free arrays
	free(f10_81ip);
	free(f10_27ip);
	free(igip);
	free(dp);
	free(aeip);
	free(modip);
	free(inclen);
	
	//get the coefs
	coefs = getNe(dbCoefs);
	
	//loop through the input times
	for (int i=0; i<l0; i++)
	{
		//sums
		double s=0;
		
		for (int j=0; j<741; j++) //741
		{
			s +=  params[i][j] * coefs[j+1];
		}

		//calculating final outputs
		output[i] = s + coefs[0];
	
		//reset the sum to 0
		s = 0;
				
		if (lat[i] < 45)
		{
			output[i] = 0.0/0.0;
		}
		
	}
	
	//free memory
	free(sza);
	for (int i=0; i<l0; i++) {free(params[i]);}
	free(params);
	free(coefs);
	
	//return output array
	return output;
	
}