################################################################################
##                                                                            ##
##  This file is part of NCrystal (see https://mctools.github.io/ncrystal/)   ##
##                                                                            ##
##  Copyright 2015-2024 NCrystal developers                                   ##
##                                                                            ##
##  Licensed under the Apache License, Version 2.0 (the "License");           ##
##  you may not use this file except in compliance with the License.          ##
##  You may obtain a copy of the License at                                   ##
##                                                                            ##
##      http://www.apache.org/licenses/LICENSE-2.0                            ##
##                                                                            ##
##  Unless required by applicable law or agreed to in writing, software       ##
##  distributed under the License is distributed on an "AS IS" BASIS,         ##
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  ##
##  See the License for the specific language governing permissions and       ##
##  limitations under the License.                                            ##
##                                                                            ##
################################################################################

################################################################################
#                                                                              #
# Exports NCrystal targets, and provides a few paths and values of build       #
# options.                                                                     #
#                                                                              #
# Geant4 targets will not be exported unless the GEANT4BINDINGS component is   #
# explicitly requested                                                         #
#                                                                              #
################################################################################

#First make sure our file work when CMake is new enough, but the user have a
#very old version in their cmake_minimum_required statements (cf. github
#discussion/issue #137):
cmake_policy(PUSH)#NB: We POP at the end of this file.
cmake_policy(VERSION 3.3...3.27)

#Export a few directory paths (relocatable):
set( NCrystal_CMAKEDIR "${CMAKE_CURRENT_LIST_DIR}" )
get_filename_component( NCrystal_PREFIX "${NCrystal_CMAKEDIR}/../../../../../" ABSOLUTE )
get_filename_component( NCrystal_DATAROOT "${NCrystal_PREFIX}/NCrystal/ncrystal_pyinst_data/data/NCrystal" ABSOLUTE )

get_filename_component( NCrystal_BINDIR "${NCrystal_CMAKEDIR}/../../../../../bin" ABSOLUTE )
get_filename_component( NCrystal_LIBDIR "${NCrystal_CMAKEDIR}/../../" ABSOLUTE )
get_filename_component( NCrystal_INCDIR "${NCrystal_CMAKEDIR}/../../../include" ABSOLUTE )
if ( "ON" AND NOT "ON" AND EXISTS "${NCrystal_CMAKEDIR}//NCrystal/__init__.py" )
  get_filename_component( NCrystal_PYPATH "${NCrystal_CMAKEDIR}/" ABSOLUTE )
endif()
if ( "xEMBED" STREQUAL "xON" )
  get_filename_component( NCrystal_DATAFILESDIR "${NCrystal_CMAKEDIR}/../../../stdlib_data" ABSOLUTE )
  set( NCrystal_OPTION_INSTALL_DATA        "ON" )
else()
  set( NCrystal_DATAFILESDIR "")
  set( NCrystal_OPTION_INSTALL_DATA        "OFF" )
endif()

if ( "xEMBED" STREQUAL "xEMBED" )
  set( NCrystal_OPTION_EMBED_DATA          "ON" )
else()
  set( NCrystal_OPTION_EMBED_DATA          "OFF" )
endif()

#Config variables (backwards compatible names):
set( NCrystal_OPTION_BUILD_EXAMPLES      "OFF" )
set( NCrystal_OPTION_BUILD_G4HOOKS       "OFF" )
set( NCrystal_OPTION_INSTALL_PY          "ON" )
set( NCrystal_OPTION_INSTALL_SETUPSH     "OFF" )
set( NCrystal_OPTION_MODIFY_RPATH        "OFF" )
set( NCrystal_OPTION_NO_DIRECT_PYMODINST "ON" )

#Config variables (autogenerated list):
set( _tmpnc_opts "NCRYSTAL_ENABLE_EXAMPLES;NCRYSTAL_ENABLE_GEANT4;NCRYSTAL_ENABLE_PYTHON;NCRYSTAL_ENABLE_DATA;NCRYSTAL_ENABLE_SETUPSH;NCRYSTAL_MODIFY_RPATH;NCRYSTAL_ENABLE_DYNLOAD;NCRYSTAL_SKIP_PYMODINST;NCRYSTAL_BUILD_STRICT;NCRYSTAL_ENABLE_CPACK;NCRYSTAL_QUIET;NCRYSTAL_SKIP_INSTALL;NCRYSTAL_ENABLE_SOVERSION;NCRYSTAL_ENABLE_THREADS;NCRYSTAL_BUILTIN_PLUGINS;NCRYSTAL_NAMESPACE" )
set( _tmpnc_optsvals "OFF;OFF;ON;ON;OFF;ON;IFAVAILABLE;OFF;OFF;OFF;OFF;OFF;ON;IFAVAILABLE;;" )
while( _tmpnc_opts )
  list( POP_FRONT _tmpnc_opts _tmpnc_o )
  list( POP_FRONT _tmpnc_optsvals _tmpnc_v )
  string( REPLACE "NCRYSTAL_" "NCrystal_OPT_" _tmpnc_o "${_tmpnc_o}" )
  set( "${_tmpnc_o}" "${_tmpnc_v}" )
endwhile()
unset( _tmpnc_opts )
unset( _tmpnc_optsvals )
unset( _tmpnc_o )
unset( _tmpnc_v )

#Libname + old school NCrystal_LIBRARIES variable:
set( NCrystal_LIBNAME "libNCrystal.3.9.4.dylib" )
set( NCrystal_LIBRARIES "${NCrystal_LIBDIR}/${NCrystal_LIBNAME}" )

#Various scripts:
if ( NCrystal_OPTION_INSTALL_PY )
  set( NCrystal_CMD_NCMAT2CPP "${NCrystal_BINDIR}/ncrystal_ncmat2cpp" )
  if ( NOT EXISTS NCrystal_NCMAT2CPP )
    set( NCrystal_NCMAT2CPP "")
  endif()
  set( NCrystal_CMD_NCRYSTALCONFIG "${NCrystal_BINDIR}/ncrystal-config" )
  if ( NOT EXISTS NCrystal_CMD_NCRYSTALCONFIG )
    set( NCrystal_CMD_NCRYSTALCONFIG "")
  endif()
  set( NCrystal_CMD_NCTOOL "${NCrystal_BINDIR}/nctool" )
  if ( NOT EXISTS NCrystal_CMD_NCTOOL )
    set( NCrystal_CMD_NCTOOL "")
  endif()
  #Obsolete alias:
  set( NCrystal_CMD_NCRYSTALINSPECTFILE "${NCrystal_CMD_NCTOOL}" )
endif()

#The NCrystal targets (not including the G4NCrystal targets!):
if(NOT TARGET NCrystal::NCrystal)
  include( "${NCrystal_CMAKEDIR}/NCrystalTargets.cmake" )
endif()

#For now GEANT4BINDINGS is the only optional component. To avoid injecting a
#dependency on Geant4 into non-Geant4 projects, the Geant4 dependency and G4NCrystal
#targets will only be added if the GEANT4BINDINGS component is explicitly
#requested.

set( NCrystal_COMPONENT_GEANT4BINDINGS "OFF" )

if ( NCrystal_OPTION_BUILD_G4HOOKS )
  #Build with Geant4 bindings. However, only load these targets (and the Geant4
  #dependency) if the GEANT4BINDINGS component was requested.
  if ( NCrystal_FIND_COMPONENTS )#if statements guards against CMP0085-OLD:
    if ( "GEANT4BINDINGS" IN_LIST NCrystal_FIND_COMPONENTS )
      if( NOT TARGET NCrystal::G4NCrystal )
        include( CMakeFindDependencyMacro )
        find_dependency( Geant4 "" EXACT REQUIRED )
        include( "${NCrystal_CMAKEDIR}/G4NCrystalTargets.cmake" )
      endif()
      set( NCrystal_COMPONENT_GEANT4BINDINGS "ON" )
      #A few variables for old-school downstream cmake projects:
      set( G4NCrystal_LIBNAME "" )
      set( G4NCrystal_LIBDIR "${NCrystal_LIBDIR}" )
      set( G4NCrystal_INCDIR "${NCrystal_INCDIR}" )
      set( G4NCrystal_LIBRARIES "${NCrystal_LIBRARIES}" "${G4NCrystal_LIBDIR}/${G4NCrystal_LIBNAME}" )
    endif()
  endif()
else()
  if ( NCrystal_FIND_REQUIRED_GEANT4BINDINGS )
    #GEANT4BINDINGS were explicitly requested but this installation does not
    #support it.
    message("Skipping ineligible NCrystal installation due to absence of required GEANT4BINDINGS")
    set( NCrystal_FOUND "FALSE" )
  endif()
endif()

#Handle other requested components. For forward compatibility, silently ignore
#any requested component name we do not recognise, unless it is REQUIRED:
foreach(tmp ${NCrystal_FIND_COMPONENTS})
  if ( NCrystal_FIND_REQUIRED_${tmp} AND NOT "x${tmp}" STREQUAL "xGEANT4BINDINGS" )
    set( NCrystal_FOUND "FALSE" )
  endif()
endforeach()

#Undo the policy changes we did above:
cmake_policy(POP)
