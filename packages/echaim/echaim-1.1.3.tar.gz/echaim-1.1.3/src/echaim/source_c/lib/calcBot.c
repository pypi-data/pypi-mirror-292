#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include "getIndices.h"
#include "mathlib.h"
#include "prepInd.h"
#include "getMagCoords.h"
#include "parameterBot.h"
#include "getCoefs.h"
#include "date.h"
#include "otherIndices.h"
#include "global.h"
#include "calcBot.h"
#include "maxIndices.h"
#include "parameterAE.h"
#include "sqlite3.h"

//****DEBUGGING************
#ifdef DBG
#include "memwatch.h"
#endif
//*************************

//Routine to calculate the Bot part of the model
//input is 4 arrays, magnetic latitude and longitude
// Julian times, and altitudes
//arrays are the same length l0
//output is 2D double array, size of l0x3
//[0,l0] = HF1
//[1,l0] = HE
//[2,l0] = H0
double **calcBot (double *jd, double *glat, double *glon, double *lat, double *mlt, int l0, sqlite3 *db, sqlite3 *dbCoefs)
{
	//declare variables
	//output array, magnetic coordinates
	double **output, *alt; //length = l0
	
	//interpolated indices array
	double *f10_81ip, *aeip; //length = l0
	
	//F10.7 flux indices, smoothed to 27 days, smoothed to 81 days, time array
	double *f10_81, *f10x; //length = lf10
	int lf10;
	
	//AE indices, integrated AE
	double *aex, *aeInt; //length of lig
	int lae;
	
	//solar zenith angle, dipole tilt
	double *sza, *dp; //length =l0
	
	//bottomside parameters
	double **params; //length = 263x24
	
	//model coefs
	double *coefsHF1, *coefsHE, *coefsH0;
	
	int r, *lx; //temporary, min and max jd, length placeholder
	double jd0, jd1;
	
	sza = calloc(l0, sizeof(double));
	dp = calloc(l0, sizeof(double));
	alt = calloc(l0, sizeof(double));

	//output is 2D, size of l0x3
	//[l0,0] = HF1
	//[l0,1] = HE
	//[l0,2] = H0
	output = (double **)calloc(3, sizeof(double));
	for (int i=0; i<3; i++)
	{
		output[i] = (double *) calloc(l0, sizeof(double));
	}
	
	
	//get the min and max JD inputted
	//The time range will got from min(jd) - 81 days to max(jd) + 81
	//this is specific to the F10 data
	//*** range needs to be decided here
	r = minInd(jd, l0);
	jd0 = jd[r];
	r = maxInd(jd,l0);
	jd1 = jd[r];

	//get the data for each input time/location pair
	for (int i=0; i<l0; i++)
	{
		double *t;
		
		//dipole tilt
		dp[i] = dpTilt(jd[i]);
		
		//input DOY, hour, latitude, longitude
		double doy = jdDOY(jd[i]);
		t = zenSun(doy, (jd[i] - jdDaily(jd[i])) * 24.0, glat[i], glon[i]);
		sza[i] = t[0];
	}
	
	//get the F10.7 data
	f10_81 = F10_81(jd0-43.0, jd1+43.0, &f10x, &lx, db);
	lf10 = lx[0];	
	
	//interpolate the indices to the inputted times
	f10_81ip = interp(f10_81, f10x, lf10, jd, l0);

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
	
	//free  arrays
	free(f10_81);
	free(f10x);
	free(alt);
	
	//get the bottomside parameters
	params = parametersBot(lat, mlt, jd, sza, f10_81ip, dp, aeip, l0);
	
	//free arrays
	free(f10_81ip);
	free(dp);
	free(aeip);
	
	//get the coefs
	coefsHF1 = getHF1(dbCoefs);
	coefsHE = getHE(dbCoefs);
	coefsH0 = getH0(dbCoefs);
	
	
	//loop through the input times
	for (int i=0; i<l0; i++)
	{
		//sums
		double sHF1=0, sHE=0, sH0=0;
		
		for (int j=0; j<263; j++)
		{
			sHF1 += params[i][j] * coefsHF1[j+1];
			sHE += params[i][j] * coefsHE[j+1];
			sH0 += params[i][j] * coefsH0[j+1];
		}
		
		//calculating final outputs
		output[0][i] = sHF1 + coefsHF1[0]; //HF1
		output[1][i] = sHE + coefsHE[0]; //HE
		if (output[1][i] < 0) output[1][i] = 0.0;
		if (output[0][i] < 0) output[0][i] = 0.0;
		output[2][i] = sH0 + coefsH0[0]; //H0
		
		//if sza > 102 then HF1 must be set to zero
		if (sza[i] > 102) output[0][i] = 0.0;
		
		//reset the sum to 0
		sHF1 = 0;
		sHE = 0;
		sH0 = 0;
		
		if (lat[i] < 45)
		{
			output[0][i] = 0.0/0.0; //HF1
			output[1][i] = 0.0/0.0; //HE
			output[2][i] = 0.0/0.0; //H0
			
		}
		
	}
	
	//free memory
	free(sza);
	for (int i=0; i<l0 ;i++) {free(params[i]);}
	free(params);
	free(coefsHF1);
	free(coefsHE);
	free(coefsH0);
	
	//return output array
	return output;
	
}