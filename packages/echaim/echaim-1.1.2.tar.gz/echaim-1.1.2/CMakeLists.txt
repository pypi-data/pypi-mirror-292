cmake_minimum_required(VERSION 3.27)

project(echaimlib)

set(LIB_SOURCES
        src/echaim/source_c/lib/aacgmlib_v2.c
        src/echaim/source_c/lib/astalglib.c
        src/echaim/source_c/lib/calcBot.c
        src/echaim/source_c/lib/calcHmF1.c
        src/echaim/source_c/lib/calcMF2.c
        src/echaim/source_c/lib/calcPert.c
        src/echaim/source_c/lib/calcTop.c
        src/echaim/source_c/lib/date.c
        src/echaim/source_c/lib/densityFunc.c
        src/echaim/source_c/lib/densityPath.c
        src/echaim/source_c/lib/densityProfile.c
        src/echaim/source_c/lib/errorCodes.c
        src/echaim/source_c/lib/genmag.c
        src/echaim/source_c/lib/getCoefs.c
        src/echaim/source_c/lib/getDir.c
        src/echaim/source_c/lib/getIndices.c
        src/echaim/source_c/lib/getMagCoords.c
        src/echaim/source_c/lib/igrflib.c
        src/echaim/source_c/lib/mathlib.c
        src/echaim/source_c/lib/maxIndices.c
        src/echaim/source_c/lib/mlt_v2.c
        src/echaim/source_c/lib/otherIndices.c
        src/echaim/source_c/lib/parameterAE.c
        src/echaim/source_c/lib/parameterBot.c
        src/echaim/source_c/lib/parameterHmF1.c
        src/echaim/source_c/lib/parameterHmF2.c
        src/echaim/source_c/lib/parameterNmF2.c
        src/echaim/source_c/lib/parameterPert.c
        src/echaim/source_c/lib/parameterTop.c
        src/echaim/source_c/lib/prepInd.c
        src/echaim/source_c/lib/rtime.c
        src/echaim/source_c/lib/singleOutput.c
        src/echaim/source_c/lib/sqlite3.c
        src/echaim/source_c/lib/calcPrecip.c
        src/echaim/source_c/lib/ECHAIMFIRI2018.c
        src/echaim/source_c/lib/energyFluxModel.c
        src/echaim/source_c/lib/energyFunctions.c
        src/echaim/source_c/lib/FIRITools.c
        src/echaim/source_c/lib/getFIRI.c
        src/echaim/source_c/lib/getPrecipModel.c
        src/echaim/source_c/lib/nrlmsise-00_data.c
        src/echaim/source_c/lib/nrlmsise00.c
        src/echaim/source_c/lib/runNRLMSISE.c
        src/echaim/source_c/lib/python_api.c
)


set_source_files_properties(src/echaim/source_c/lib/sqlite3.c PROPERTIES COMPILE_OPTIONS "-DSQLITE_THREADSAFE=2")

#create the shared library
add_library (echaim SHARED ${LIB_SOURCES})

#change the runtime output directory
#get_filename_component(PARENT_DIR CMake DIRECTORY)
#set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PARENT_DIR})

#set the compiler C99 flag
set_property(TARGET echaim PROPERTY C_STANDARD 99)

install(TARGETS echaim LIBRARY DESTINATION echaimlib)

set(CMAKE_VERBOSE_MAKEFILE OFF)