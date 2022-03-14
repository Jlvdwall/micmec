// YAFF is yet another force-field code.
// Copyright (C) 2011 Toon Verstraelen <Toon.Verstraelen@UGent.be>,
// Louis Vanduyfhuys <Louis.Vanduyfhuys@UGent.be>, Center for Molecular Modeling
// (CMM), Ghent University, Ghent, Belgium; all rights reserved unless otherwise
// stated.
//
// This file is part of YAFF.
//
// YAFF is free software; you can redistribute it and/or
// modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 3
// of the License, or (at your option) any later version.
//
// YAFF is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>
//
// --


#include <stdlib.h>
#include <math.h>
#include "cell.h"

cell_type* cell_new(void) {
  return malloc(sizeof(cell_type));
}

void cell_free(cell_type* cell) {
  free(cell);
}

void cell_update(cell_type* cell, double *rvecs, double *gvecs, int nvec) {
  double tmp;
  int i;
  // Copy everything.
  (*cell).nvec = nvec;
  for (i=0; i<9; i++) {
    (*cell).rvecs[i] = rvecs[i];
    (*cell).gvecs[i] = gvecs[i];
  }
  // Compute the spacings.
  for (i=0; i<3; i++) {
    (*cell).rspacings[i] = 1.0/sqrt(gvecs[3*i]*gvecs[3*i] + gvecs[3*i+1]*gvecs[3*i+1] + gvecs[3*i+2]*gvecs[3*i+2]);
    (*cell).gspacings[i] = 1.0/sqrt(rvecs[3*i]*rvecs[3*i] + rvecs[3*i+1]*rvecs[3*i+1] + rvecs[3*i+2]*rvecs[3*i+2]);
  }
  // Compute the volume.
  switch(nvec) {
    case 0:
      (*cell).volume = 0.0;
      break;
    case 1:
      (*cell).volume = sqrt(
        rvecs[0]*rvecs[0]+rvecs[1]*rvecs[1]+rvecs[2]*rvecs[2]
      );
      break;
    case 2:
      tmp = rvecs[0]*rvecs[3]+rvecs[1]*rvecs[4]+rvecs[2]*rvecs[5];
      tmp = (rvecs[0]*rvecs[0]+rvecs[1]*rvecs[1]+rvecs[2]*rvecs[2])*
            (rvecs[3]*rvecs[3]+rvecs[4]*rvecs[4]+rvecs[5]*rvecs[5]) - tmp*tmp;
      if (tmp > 0) {
        (*cell).volume = sqrt(tmp);
      } else {
        (*cell).volume = 0.0;
      }
      break;
    case 3:
      (*cell).volume = fabs(
        rvecs[0]*(rvecs[4]*rvecs[8]-rvecs[5]*rvecs[7])+
        rvecs[1]*(rvecs[5]*rvecs[6]-rvecs[3]*rvecs[8])+
        rvecs[2]*(rvecs[3]*rvecs[7]-rvecs[4]*rvecs[6])
      );
      break;
  }
}

void cell_mic(double *delta, cell_type* cell) {
  // Applies the Minimum Image Convention. Well, sort of. It does not always work like this.
  // This function contains an unrolled loop for speed.
  int nvec;
  double x;
  double *rvecs;
  double *gvecs;
  nvec = (*cell).nvec;
  if (nvec == 0) return;
  rvecs = (*cell).rvecs;
  gvecs = (*cell).gvecs;
  x = ceil(gvecs[0]*delta[0] + gvecs[1]*delta[1] + gvecs[2]*delta[2] - 0.5);
  delta[0] -= x*rvecs[0];
  delta[1] -= x*rvecs[1];
  delta[2] -= x*rvecs[2];
  if (nvec == 1) return;
  x = ceil(gvecs[3]*delta[0] + gvecs[4]*delta[1] + gvecs[5]*delta[2] - 0.5);
  delta[0] -= x*rvecs[3];
  delta[1] -= x*rvecs[4];
  delta[2] -= x*rvecs[5];
  if (nvec == 2) return;
  x = ceil(gvecs[6]*delta[0] + gvecs[7]*delta[1] + gvecs[8]*delta[2] - 0.5);
  delta[0] -= x*rvecs[6];
  delta[1] -= x*rvecs[7];
  delta[2] -= x*rvecs[8];
}


void cell_to_center(double *cart, cell_type* cell, long *center) {
  // Transfroms to fractional coordinates.
  int nvec;
  double *gvecs;
  nvec = (*cell).nvec;
  if (nvec == 0) return;
  gvecs = (*cell).gvecs;
  center[0] = -ceil(gvecs[0]*cart[0] + gvecs[1]*cart[1] + gvecs[2]*cart[2] - 0.5);
  if (nvec == 1) return;
  center[1] = -ceil(gvecs[3]*cart[0] + gvecs[4]*cart[1] + gvecs[5]*cart[2] - 0.5);
  if (nvec == 2) return;
  center[2] = -ceil(gvecs[6]*cart[0] + gvecs[7]*cart[1] + gvecs[8]*cart[2] - 0.5);
}


void cell_add_vec(double *delta, cell_type* cell, long* r) {
  // Simply adds an linear combination of cell vectors to delta.
  // This function contains an unrolled loop for speed.
  int nvec;
  double *rvecs;
  nvec = (*cell).nvec;
  if (nvec == 0) return;
  rvecs = (*cell).rvecs;
  delta[0] += r[0]*rvecs[0];
  delta[1] += r[0]*rvecs[1];
  delta[2] += r[0]*rvecs[2];
  if (nvec == 1) return;
  delta[0] += r[1]*rvecs[3];
  delta[1] += r[1]*rvecs[4];
  delta[2] += r[1]*rvecs[5];
  if (nvec == 2) return;
  delta[0] += r[2]*rvecs[6];
  delta[1] += r[2]*rvecs[7];
  delta[2] += r[2]*rvecs[8];
}

int cell_get_nvec(cell_type* cell) {
  return (*cell).nvec;
}

double cell_get_volume(cell_type* cell) {
  return (*cell).volume;
}

void cell_copy_rvecs(cell_type* cell, double *rvecs, int full) {
  int i, n;
  n = (full)?9:(*cell).nvec*3;
  for (i=0; i<n; i++) rvecs[i] = (*cell).rvecs[i];
}

void cell_copy_gvecs(cell_type* cell, double *gvecs, int full) {
  int i, n;
  n = (full)?9:(*cell).nvec*3;
  for (i=0; i<n; i++) gvecs[i] = (*cell).gvecs[i];
}

void cell_copy_rspacings(cell_type* cell, double *rspacings, int full) {
  int i, n;
  n = (full)?3:(*cell).nvec;
  for (i=0; i<n; i++) rspacings[i] = (*cell).rspacings[i];
}

void cell_copy_gspacings(cell_type* cell, double *gspacings, int full) {
  int i, n;
  n = (full)?3:(*cell).nvec;
  for (i=0; i<n; i++) gspacings[i] = (*cell).gspacings[i];
}

void cell_to_frac(cell_type* cell, double *cart, double* frac) {
  double *gvecs = (*cell).gvecs;
  frac[0] = gvecs[0]*cart[0] + gvecs[1]*cart[1] + gvecs[2]*cart[2];
  frac[1] = gvecs[3]*cart[0] + gvecs[4]*cart[1] + gvecs[5]*cart[2];
  frac[2] = gvecs[6]*cart[0] + gvecs[7]*cart[1] + gvecs[8]*cart[2];
}
