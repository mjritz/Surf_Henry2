#!/usr/bin/env python 

import sys
import numpy as np
import variables
import os
import subprocess

#Read in the surfactant structure and input file for moltemplate 
lammps_file = open('system_all.in', 'wa')

xbox, ybox, zbox, w_filename, w_mol, pack_tol, bead_dist, boxx, boxy, boxz,     bead_per, main_branch, equil_time, surf_x, surf_y, surf_zlow, surf_zhi,         per_loop, steps,temp, z_distance, epsilon, sigma, r_distance, equil_dcd,        prod_dcd, cutoff = variables.read_variables('input_file.txt')

os.system('./seed.x > seed.txt')
seed_file = open('seed.txt','rb')
for line in seed_file.readlines():
    variable = line.split(' ')
    seed = int(variable[0])
print seed

string =" %d %g %20.15g %20.15g %20.15g"
#string2 = "fix zwall all wall/harmonic zlo -%4.2f %3.1f %3.1f %3.1f zhi %4.2f %3.1f %3.1f %3.1f pbc yes\n" % (float(z_wall),float(epsilon), float(sigma),float(r_distance),float(z_wall),float(epsilon),float(sigma),float(r_distance))

h = """
variable T equal %6.2f

processors 2 2 *
units           real
boundary        p p p
atom_style      full
bond_style      harmonic
angle_style     harmonic

pair_style table spline 32802
special_bonds lj 0.0 1.0 1.0

read_data system.data

pair_coeff 1 1 surf_mie.table CMCM 20.0
pair_coeff 1 2 surf_mie.table CMOA 20.0
pair_coeff 1 3 surf_mie.table CMW 20.0
pair_coeff 2 2 surf_mie.table OAOA 20.0
pair_coeff 2 3 surf_mie.table OAW 20.0
pair_coeff 3 3 surf_mie.table WW 20.0

min_style       cg
neigh_modify    delay 10 every 1 check yes

group water type 3
group surf type 1 2

minimize 1.0e-6 1.0e-8 250 2508

fix 1 all nvt temp ${T} ${T} 100.0
velocity all create ${T} %i mom yes rot yes dist gaussian
velocity all zero linear
velocity all zero angular
""" % (temp, seed)

h+="fix zwall all wall/harmonic zlo -%4.2f %3.1f %3.1f %3.1f zhi %4.2f %3.1f %3.1f %3.1f pbc yes\n" % (float(z_distance),float(epsilon), float(sigma),float(r_distance),float(z_distance),float(epsilon),float(sigma),float(r_distance))

h+="""
thermo      100
thermo_style custom step spcpu etotal ke temp  pe press  pxx pyy pzz

timestep 2.0

dump  4 all dcd 5000 %s
dump_modify 4 unwrap yes

restart 100000 restart_equilibrate.1 restart_equilibrate.2

fix 30 all balance 10000 z 20 1.0

fix 200 all momentum 100 linear 1 1 1

run %s 

#use python script to trim surfactants
shell python execute_trim.py %s system_trimmed.lt trimmed_info.txt

clear

variable T equal %6.2f

units           real
neigh_modify    delay 10 every 1 check yes

atom_style      full
bond_style      harmonic
angle_style     harmonic

pair_style table spline 32802
special_bonds lj 0.0 1.0 1.0
boundary        p p p
read_data       system_trimmed.data
min_style       cg
pair_coeff 1 1 surf_mie.table CMCM 20.0
pair_coeff 1 2 surf_mie.table CMOA 20.0
pair_coeff 1 3 surf_mie.table CMW 20.0
pair_coeff 2 2 surf_mie.table OAOA 20.0
pair_coeff 2 3 surf_mie.table OAW 20.0
pair_coeff 3 3 surf_mie.table WW 20.0

group water type 3
group surf type 1 2

minimize 1.0e-6 1.0e-8 20 20

fix 1 all nvt temp ${T} ${T} 100.0
velocity all create ${T} %i mom yes rot yes dist gaussian
velocity all zero linear
velocity all zero angular

thermo          0
thermo_style custom step spcpu etotal ke temp pe press pxx pyy pzz

timestep        2.0

dump 10 all dcd 5000 third_equil.dcd
dump_modify 10 unwrap yes

#run balance command every 10000 steps in z direction
fix 20 all balance 1000 z 100 1.0

run 1000000

write_data trimmed_minimized.data 

clear
variable T equal %6.2f
variable input_name string system
variable mol_size string %s
variable delta string 0.0005
variable xyz_file string xyz.txt
variable xyz_file_water string xyz_water.txt
variable xyz_p_file string xyz_p.txt
variable xyz_m_file string xyz_m.txt

units           real
neigh_modify    delay 10 every 1 check yes

atom_style      full
bond_style      harmonic
angle_style     harmonic

pair_style table spline 32802
special_bonds lj 0.0 1.0 1.0
boundary        p p p
read_data      trimmed_minimized.data
min_style       cg
pair_coeff 1 1 surf_mie.table CMCM 20.0
pair_coeff 1 2 surf_mie.table CMOA 20.0
pair_coeff 1 3 surf_mie.table CMW 20.0
pair_coeff 2 2 surf_mie.table OAOA 20.0
pair_coeff 2 3 surf_mie.table OAW 20.0
pair_coeff 3 3 surf_mie.table WW 20.0

group water type 3
group surf type 1 2

minimize 1.0e-6 1.0e-8 20 20

fix 1 all nvt temp ${T} ${T} 100.0
velocity all create ${T} %i mom yes rot yes dist gaussian
velocity all zero linear
velocity all zero angular

thermo          0
thermo_style custom step spcpu etotal ke temp pe press pxx pyy pzz cella cellb cellc

timestep        1.0

restart         100000 ${input_name}.restart1 ${input_name}.restart2

dump 10 all dcd 5000 %s
dump_modify 10 unwrap yes

#run balance command every 10000 steps in z direction
fix 20 all balance 1000 z 100 1.0

#open dE.txt file and write header
print "#step pxx pyy pzz" file ${jobdir}/P.txt screen no
print "#step U Up Um U" file ${jobdir}/dE.txt screen no
print "#step volume_fraction" file ${jobdir}/vol_frac.txt screen no
run 0

#define variables for half box lengths
variable x equal cella/2.0
variable boxx2 equal $x
variable x equal cellb/2.0
variable boxy2 equal $x
variable x equal cellc/2.0
variable boxz2 equal $x
variable x equal cella
variable boxx equal $x
variable x equal cellb
variable boxy equal $x
variable x equal cellc
variable boxz equal $x
#define variables for plus and minus perturbation amounts
variable pd equal sqrt(1+${delta})
variable md equal sqrt(1-${delta})

#new
variable pvecx equal pxx
variable pvecy equal pyy
variable pvecz equal pzz
variable i equal step
#--

#number of TA evaluations to run
variable a loop %s
label loop

#number of steps to run between TA evaluations
run %s

#define current step
variable x equal step
variable frame equal $x


#define current potential energy without perturbation
#new
print "${i} ${pvecx} ${pvecy} ${pvecz}" append P.txt screen no
#--
variable x equal pe
variable U equal $x

#write out unscaled surfactant coordinates to file name defined by variable xyz_file
dump 100 surf custom 1000 ${xyz_file} id mass xu yu zu
dump 101 water custom 1000 ${xyz_file_water} id mass xu yu zu
dump_modify 100 sort id first yes format "%s"
dump_modify 101 sort id first yes format "%s"
run 0
undump 100
undump 101

#use python script to rescale surfant molecule coordinates
shell python rescale.py ${xyz_file} ${xyz_p_file} ${xyz_m_file} ${delta} ${mol_size} ${boxx} ${boxy} ${boxz}

#rescale water coordinates
change_box water x scale ${pd} z volume y scale ${pd} z volume remap
#read in rescaled surfactant coordinates
read_dump ${xyz_p_file} 0 x y z box no replace yes scaled no wrapped no
run 0
variable x equal pe
variable Up equal $x

#scale water coordinates to minus perturbation (this could be done in 1 step)
change_box water x final -${boxx2} ${boxx2} y final -${boxy2} ${boxy2} z final -${boxz2} ${boxz2} remap
change_box water x scale ${md} z volume y scale ${md} z volume remap
#read in rescaled surfactant coordinates
read_dump ${xyz_m_file} 0 x y z box no replace yes scaled no wrapped no
run 0
variable x equal pe
variable Um equal $x

#reset box 
change_box water x final -${boxx2} ${boxx2} y final -${boxy2} ${boxy2} z final -${boxz2} ${boxz2} remap
read_dump ${xyz_file} ${frame} x y z box no replace yes scaled no wrapped no

#calculate potential energy after
run 0
variable x equal pe
variable U2 equal $x 
print "${frame} ${U} ${Up} ${Um} ${U2}" append ${jobdir}/dE.txt screen no
variable frac file temp_vol_frac.txt
print "${frame} ${frac}" append ${jobdir}/vol_frac.txt screen no
variable frac delete
next a
jump SELF loop""" % (equil_dcd,equil_time,equil_dcd,temp, seed, temp, bead_per,seed, prod_dcd, per_loop, steps, string, string)  

lammps_file.write(h)
lammps_file.close()
