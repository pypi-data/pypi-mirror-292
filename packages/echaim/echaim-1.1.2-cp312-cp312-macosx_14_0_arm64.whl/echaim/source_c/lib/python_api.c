//
// Created by lap1dem on 9/7/22.
//

#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include "sqlite3.h"
#include "ECHAIM.h"
#include "global.h"

void print_d_array(double *arr, int len) {
    for (int j = 0; j < len; j++) {
        printf("%4.3e ", arr[j]);
    }
    printf("\n");
}

void print_i_array(int *arr, int len) {
    for (int j = 0; j < len; j++) {
        printf("%i ", arr[j]);
    }
    printf("\n\n");
}

void pyDensityProfile(double *np_output, char *datadir, double *lat, double *lon, int *year, int *month, int *day, int *hour,
                      int *min, int *sec, int storm, int precip, int dregion, int l0, double *alt, int l1, int err) {
    strcpy(DIR, datadir);
    double **output = densityProfile(lat, lon, year, month, day, hour, min,
                                     sec, storm, precip, dregion, l0, alt, l1, err);

    for (int i = 0; i < l0; i++) {
        memcpy(np_output + l1 * i, output[i], sizeof(double) * l1);
    }
    free(output);
}


void pyNmF2(double *np_output, char *datadir, double *lat, double *lon, int *year, int *month, int *day, \
				int *hour, int *min, int *sec, int l0, int err){
    strcpy(DIR, datadir);
    double * output = NmF2(lat, lon, year, month, day, hour, min, sec, l0, err);
    memcpy(np_output, output, sizeof(double) * l0);
    free(output);
}

void pyNmF2Storm(double *np_output, char *datadir, double *lat, double *lon, int *year, int *month, int *day, \
				int *hour, int *min, int *sec, int l0, int err){
    strcpy(DIR, datadir);
    double * output = NmF2Storm(lat, lon, year, month, day, hour, min, sec, l0, err);
    memcpy(np_output, output, sizeof(double) * l0);
    free(output);
}

void pyHmF2(double *np_output, char *datadir, double *lat, double *lon, int *year, int *month, int *day, \
				int *hour, int *min, int *sec, int l0, int err){
    strcpy(DIR, datadir);
    double * output = HmF2(lat, lon, year, month, day, hour, min, sec, l0, err);
    memcpy(np_output, output, sizeof(double) * l0);
    free(output);
}


void pyHmF1(double *np_output, char *datadir, double *lat, double *lon, int *year, int *month, int *day, \
				int *hour, int *min, int *sec, int l0, int err){
    strcpy(DIR, datadir);
    double * output = HmF1(lat, lon, year, month, day, hour, min, sec, l0, err);
    memcpy(np_output, output, sizeof(double) * l0);
    free(output);
}

void pyDensityPath(double *np_output, char *datadir, double *lat, double *lon, double *alt, \
						int *year, int *month, int *day, \
						int *hour, int *min, int *sec, int storm, int precip, int dregion, int l0, int err){
    strcpy(DIR, datadir);
    double * output = densityPath(lat, lon, alt, year, month, day, hour, min, sec, storm, precip, dregion, l0, err);
    memcpy(np_output, output, sizeof(double) * l0);
    free(output);
}

//void update_database(int * result, char * datadir, int force){
//    strcpy(DIR, datadir);
//    * result = updateLocalDB(force);
//}