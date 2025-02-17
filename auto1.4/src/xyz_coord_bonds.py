#! /usr/bin/env/ python

import sys
import numpy as np
import pdb_create
import variables

in_stream  = open('surf.xyz', 'r')
out_stream = open('surf.lt', 'wa')
structure = open(sys.argv[1], 'r')

xbox, ybox, zbox, w_filename, w_mol, pack_tol, bead_dist, boxx, boxy, boxz,     bead_per, main_branch, equil_time, surf_x, surf_y, surf_zlow, surf_zhi,         per_loop, steps,temp, z_distance, epsilon, sigma, r_distance, equil_dcd,        prod_dcd, cutoff = variables.read_variables('input_file.txt')

#Initialize string that will be appended to file with bond information
s = []
ilines, i,j,k,l = 0,0,0,0,0
ID = []
xyz = []
y = []
z = []

#Write beginning of file 
s = ("""                                                                                                 
import "miesurf_ff.lt"                                                                                   

Surf {                                                                                                   
                                                                                                             
  write('Data Atoms') {                                                                                  
""")   

for ilines in in_stream.readlines():  
  if ilines.startswith ('CM') or ilines.startswith('OA'): 
    data = ilines.split()
    if data[0] == 'CM':
      s+="    $atom:CM%i $mol:. @atom:MieSurf/%s  %3.2f  %8.4f  %8.4f  %8.4f\n" %(i+1,data[0],float(0.0),float(data[1]), float(data[2]),float(data[3]))
      i+=1
    if data[0] == 'OA':
      s+="    $atom:OA%i $mol:. @atom:MieSurf/%s  %2.2f  %8.4f  %8.4f %8.4f\n"%(j+1,data[0],float(0.0),float(data[1]), float(data[2]),float(data[3]))
      j+=1
    k+=1
s+="  }"       

in_stream  = open('surf.xyz', 'r') 

#Initialize string that will be appended to file with bond information                                   
head_groups = 0                                                                                          
number_of_atoms = 0                                                                                      
sum_side_beads = 0                                                                                       
branches = []                                                                                               
branch_location =[]                                                                                      
g = []                                                                                                   
n,i,j,k,l,m = 0,0,0,0,0,0                                                                                
                                                                                                         
g ="""                                                                                                   
                                                                                                         
  write ('Data Bonds') {                                                                                 
"""          

for ilines in structure.readlines():                                                                     
  if 'B' in ilines or 'T' in ilines or 'H' in ilines:                                                       
    atoms_on_each_line = len(ilines.split())                                                             
    number_of_atoms += atoms_on_each_line                                                                
  if ilines.count('B') >= 0:                                                                             
    number_side_beads = len(ilines.split())-1                                                            
    branches.append(number_side_beads)                                                                   
    sum_side_beads += number_side_beads                                                                  
  if ilines.count('H') > 0:                                                                              
    head_group_beads = len(ilines.split())                                                               
    head_groups += head_group_beads                                                                      
main_tail = number_of_atoms-sum_side_beads-head_groups   

for x in range(main_tail):                                                                               
  if k<main_tail-1:                                                                                      
    g += "    $bond:bond%i @bond:MieSurf/%s%s $atom:%s%i $atom:%s%i\n"%(k+1,'CM','CM','CM',n+1,'CM',n+2)
  if k == main_tail-1:                                                                                   
    g+= "    $bond:bond%i @bond:MieSurf/%s%s $atom:%s%i $atom:%s%i\n"%(k+1,'CM','OA','CM',n+1,'OA',i+1)
  n+=1                                                                                                   
  k += 1 

for x in range(head_groups-1):                                                                           
  g+= "    $bond:bond%i @bond:MieSurf/%s%s $atom:%s%i $atom:%s%i\n"%(k+1,'OA','OA','OA',i+1,'OA',i+2)  
  i+=1                                                                                                   
  k+=1  


for lines in in_stream.readlines():                                                                      
  if lines.startswith ('CM') or lines.startswith('OA'):                                                
    data = lines.split()                                                                           
    if data[2] !=  '0.00000':                                                                      
      branch_location.append(data[2])    

for x in range(len(branches)):
  for x in range(branches[l]):                                                                           
    if branch_location[m] == '%3.5f' %(float(bead_dist)):                                                                  
      g+= "    $bond:bond%i @bond:MieSurf/%s%s $atom:%s%i $atom:%s%i\n"%(k+1,'CM','CM','CM',l+1,'CM',n+1)
      n-=1                                                                                               
    elif branch_location[m] == '-%3.5f' %(float(bead_dist)):                                                               
      g+= "    $bond:bond%i @bond:MieSurf/%s%s $atom:%s%i $atom:%s%i\n"%(k+1,'CM','CM','CM',n+1,'CM',l+1) 
    else:                                                                                                
      g+= "    $bond:bond%i @bond:MieSurf/%s%s $atom:%s%i $atom:%s%i\n"%(k+1,'CM','CM','CM',n+1,'CM',n+2)
    n+=1                                                                                                 
    m+=1                                                                                                 
    k+=1                                                                                                 
  if branches[l] != 0:                                                                                   
    n+=1                                                                                                 
  l+=1                                                                                                   
g+="  }" 
g+="""

  write ('Data Angles'){
"""

n,i,j,k,l,m,o = 0,0,0,0,0,0,0                                                                                

for x in range(main_tail):                                                                               
  if k<main_tail-2:                                                                                      
    g += "    $angle:angle%i @angle:MieSurf/%s%s%s $atom:%s%i $atom:%s%i $atom:%s%i\n"%(k+1,'CM','CM','CM','CM',n+1,'CM',n+2,'CM',n+3)
  n+=1                                                                                                   
  k += 1 

for lines in in_stream.readlines():                                                                      
  if lines.startswith ('CM') or lines.startswith('OA'):                                                
    data = lines.split()                                                                           
    if data[2] !=  '0.00000':                                                                      
      branch_location.append(data[2])    
k-=2

for x in range(len(branches)):
  for x in range(branches[l]):                                                                           
    if branch_location[m] == '%3.5f' %(float(bead_dist)):
      if l < main_tail-2: 
        g+= "    $angle:angle%i @angle:MieSurf/%s%s%s $atom:%s%i $atom:%s%i $atom:%s%i\n"%(k+1,'CM','CM','CM','CM',n+1,'CM',l+1,'CM',l+2)
        k+=1
      if l > 1:
        g+= "    $angle:angle%i @angle:MieSurf/%s%s%s $atom:%s%i $atom:%s%i $atom:%s%i\n"%(k+1,'CM','CM','CM','CM',n+1,'CM',l+1,'CM',l)
        k+=1
    elif branch_location[m] == '-%3.5f' %(float(bead_dist)):                                                               
      if l < main_tail-2:
        g+= "    $angle:angle%i @angle:MieSurf/%s%s%s $atom:%s%i $atom:%s%i $atom:%s%i\n"%(k+1,'CM','CM','CM','CM',n+1,'CM',l+1,'CM',l+2)
        k+=1
      if l> 1:
        g+= "    $angle:angle%i @angle:MieSurf/%s%s%s $atom:%s%i $atom:%s%i $atom:%s%i\n"%(k+1,'CM','CM','CM','CM',n+1,'CM',l+1,'CM',l)
        k+=1
    elif branch_location[m] == '-%3.5f' %(2*float(bead_dist)):
        g+= "    $angle:angle%i @angle:MieSurf/%s%s%s $atom:%s%i $atom:%s%i $atom:%s%i\n"%(k+1,'CM','CM','CM','CM',n+1,'CM',n+2,'CM',l+1)
        k+=1
    elif branch_location[m] == '%3.5f' %(2*float(bead_dist)):
        g+= "    $angle:angle%i @angle:MieSurf/%s%s%s $atom:%s%i $atom:%s%i $atom:%s%i\n"%(k+1,'CM','CM','CM','CM',n+1,'CM',n,'CM',l+1)
        k+=1
    else:                                                                                                
      if branch_location[m] < '-%3.5f' %(2*float(bead_dist)):
        g+= "    $angle:angle%i @angle:MieSurf/%s%s%s $atom:%s%i $atom:%s%i $atom:%s%i\n"%(k+1,'CM','CM','CM','CM',n+1,'CM',n+2,'CM',n+3)
        k+=1
      if branch_location[m] > '%3.5f' %(2*float(bead_dist)):
        g+= "    $angle:angle%i @angle:MieSurf/%s%s%s $atom:%s%i $atom:%s%i $atom:%s%i\n"%(k+1,'CM','CM','CM','CM',n+1,'CM',n+2,'CM',n+3)
        k+=1
    n+=1                                                                                                 
    m+=1                                                                                                 
  #if branches[l] != 0:                                                                                   
  #  n+=1                                                                                                 
  l+=1                                                                                                   

g+= """ }                                                                                                
                                                                                                                     
}"""       
    
out_stream.write(s)
out_stream.write(g)
out_stream.close()

if sum_side_beads == 0:
    descript = 'mb'
if sum_side_beads != 0:
    descript = 'sb'
