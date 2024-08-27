dir_poscar# SAMBA_ilum Copyright (C) 2024 - Closed source


from pymatgen.io.vasp import Poscar
from pymatgen.core import Structure
from pymatgen.analysis.structure_matcher import StructureMatcher
#---------------------------------------------------------------
import numpy as np
import filecmp
import shutil
import uuid
import sys  
import os


#----------------------------------------------------------------------------------------------------------------------------------------------
# Rotulo temporário para os ions inequivalentes da célula unitária ----------------------------------------------------------------------------
alphabet  = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'X', 'Z', 'Y', 'W' ]
alphabet += ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'x', 'z', 'y', 'w' ]
alphabet += ['a0','b0','c0','d0','e0','f0','g0','h0','i0','j0','k0','l0','m0','n0','o0','p0','q0','r0','s0','t0','u0','v0','x0','z0','y0','w0'] 
alphabet += ['a1','b1','c1','d1','e1','f1','g1','h1','i1','j1','k1','l1','m1','n1','o1','p1','q1','r1','s1','t1','u1','v1','x1','z1','y1','w1'] 
alphabet += ['a2','b2','c2','d2','e2','f2','g2','h2','i2','j2','k2','l2','m2','n2','o2','p2','q2','r2','s2','t2','u2','v2','x2','z2','y2','w2'] 
alphabet += ['a3','b3','c3','d3','e3','f3','g3','h3','i3','j3','k3','l3','m3','n3','o3','p3','q3','r3','s3','t3','u3','v3','x3','z3','y3','w3'] 
alphabet += ['a4','b4','c4','d4','e4','f4','g4','h4','i4','j4','k4','l4','m4','n4','o4','p4','q4','r4','s4','t4','u4','v4','x4','z4','y4','w4'] 
alphabet += ['a5','b5','c5','d5','e5','f5','g5','h5','i5','j5','k5','l5','m5','n5','o5','p5','q5','r5','s5','t5','u5','v5','x5','z5','y5','w5']
alphabet += ['a6','b6','c6','d6','e6','f6','g6','h6','i6','j6','k6','l6','m6','n6','o6','p6','q6','r6','s6','t6','u6','v6','x6','z6','y6','w6']
alphabet += ['a7','b7','c7','d7','e7','f7','g7','h7','i7','j7','k7','l7','m7','n7','o7','p7','q7','r7','s7','t7','u7','v7','x7','z7','y7','w7']
alphabet += ['a8','b8','c8','d8','e8','f8','g8','h8','i8','j8','k8','l8','m8','n8','o8','p8','q8','r8','s8','t8','u8','v8','x8','z8','y8','w8']
alphabet += ['a9','b9','c9','d9','e9','f9','g9','h9','i9','j9','k9','l9','m9','n9','o9','p9','q9','r9','s9','t9','u9','v9','x9','z9','y9','w9']
alphabet += ['a10','b10','c10','d10','e10','f10','g10','h10','i10','j10','k10','l10','m10','n10','o10','p10','q10','r10','s10','t10','u10','v10','x10','z10','y10','w10'] 
alphabet += ['a11','b11','c11','d11','e11','f11','g11','h11','i11','j11','k11','l11','m11','n11','o11','p11','q11','r11','s11','t11','u11','v11','x11','z11','y11','w11'] 
alphabet += ['a12','b12','c12','d12','e12','f12','g12','h12','i12','j12','k12','l12','m12','n12','o12','p12','q12','r12','s12','t12','u12','v12','x12','z12','y12','w12'] 
alphabet += ['a13','b13','c13','d13','e13','f13','g13','h13','i13','j13','k13','l13','m13','n13','o13','p13','q13','r13','s13','t13','u13','v13','x13','z13','y13','w13'] 
alphabet += ['a14','b14','c14','d14','e14','f14','g14','h14','i14','j14','k14','l14','m14','n14','o14','p14','q14','r14','s14','t14','u14','v14','x14','z14','y14','w14'] 
alphabet += ['a15','b15','c15','d15','e15','f15','g15','h15','i15','j15','k15','l15','m15','n15','o15','p15','q15','r15','s15','t15','u15','v15','x15','z15','y15','w15']
alphabet += ['a16','b16','c16','d16','e16','f16','g16','h16','i16','j16','k16','l16','m16','n16','o16','p16','q16','r16','s16','t16','u16','v16','x16','z16','y16','w16']
alphabet += ['a17','b17','c17','d17','e17','f17','g17','h17','i17','j17','k17','l17','m17','n17','o17','p17','q17','r17','s17','t17','u17','v17','x17','z17','y17','w17']
alphabet += ['a18','b18','c18','d18','e18','f18','g18','h18','i18','j18','k18','l18','m18','n18','o18','p18','q18','r18','s18','t18','u18','v18','x18','z18','y18','w18']
alphabet += ['a19','b19','c19','d19','e19','f19','g19','h19','i19','j19','k19','l19','m19','n19','o19','p19','q19','r19','s19','t19','u19','v19','x19','z19','y19','w19']
#----------------------------------------------------------------------------------------------------------------------------------------------
# letters  = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'x', 'z', 'y', 'w' ]
# alphabet = []
#------------------------------------------------------
# Gerando 1040 rótulos temporários para os ions da rede
#------------------------------------------------------
# for k in range(40):
#     for i in range(len(letters)):
#        alphabet.append(letters[i] + str(k+1))       
#--------------------------------------------------------------------------------------------
vLattice = [dir_poscar + '/' + Lattice1, dir_poscar + '/' + Lattice2, dir_poscar + '/' + Lattice3];  n = n_Lattice -2
label_htstructure = '';  label_material = ['']*n_Lattice
dZ = [0]*3;  dens_ions = [0]*3
#--------------------------------------------------------------------------------------------
orig = 0   # [0] O centro da SuperCélula será a origem do sistema de coordenadas.
           # [1] O centro do vetor A1 da SuperCélula será a origem do sistema de coordenadas.
#--------------------------------------------------------------------------------------------


#---------------------------------------------------
# Testando a compatibilidade dos arquivos POSCAR ---
#---------------------------------------------------
A1x0 = [];  A1y0 = [];  A2x0 = [];  A2y0 = []  # Listas para armazenar os vetores A1 e A2 de cada rede
#-----------------------------------------------------------------------------------------------------
for k in range(n_Lattice):
    #---------------------
    Lattice = dir_files + '/' + vLattice[k]
    poscar = open(Lattice, "r")
    #-------------------------------------------
    for i in range(2): VTemp = poscar.readline()
    param = float(VTemp)
    #-------------------------------------------
    A1 = poscar.readline().split();  A1x = float(A1[0])*param; A1y = float(A1[1])*param; A1z = float(A1[2])*param  
    A2 = poscar.readline().split();  A2x = float(A2[0])*param; A2y = float(A2[1])*param; A2z = float(A2[2])*param  
    A3 = poscar.readline().split();  A3x = float(A3[0])*param; A3y = float(A3[1])*param; A3z = float(A3[2])*param  
    #------------------------------------------------------------------------------------------------------------
    A1x0.append(A1x);  A1y0.append(A1y);  A2x0.append(A2x);  A2y0.append(A2y)   # Armazenando os vetores A1 e A2 de cada rede
    #------------------------------------------------------------------------------------------------------------------------
    if ((A1z != 0.0) or (A2z != 0.0) or (A3x != 0.0) or (A3y != 0.0)):
       print(f' ')
       print(f'========================================')
       print(f'Verifique os arquivos POSCAR utilizados!')
       print(f'INCOMPATIBILIDADE com o código detectada')
       print(f'========================================')
       print(f' ')
       #==========
       sys.exit()   
       #=========
    #-------------------------------------------------------
    # Vetores A1 e A2
    A1 = np.array([A1x, A1y])
    A2 = np.array([A2x, A2y])
    #-------------------------------------------------------
    # Área da célula unitária
    Area = np.linalg.norm(np.cross(A1, A2))
    #-------------------------------------------------------
    nion = 0
    for i in range(2): VTemp = poscar.readline().split()
    for i in range(len(VTemp)):  nion += int(VTemp[i])
    #-------------------------------------------------------
    dens_ions[k] = nion/Area                                # Obtendo a densidade de ions de cada material
    #-----------------------
    poscar.close()
    #-------------


#---------------------------------------------------
# Verificando a existância do diretório 'output' ---
#---------------------------------------------------
if os.path.isdir(dir_files + '/' + 'output'):
   0 == 0
else:
   os.mkdir(dir_files + '/' + 'output')
#--------------------------------------
diret = dir_files + '/' + 'output/'
#----------------------------------


formula = []
id_materials = []
unique_id = str(uuid.uuid4().hex[:16])


for k in range(n_Lattice):

    #------------------------------------------------
    ion_label  = []; ion_label_string  = ''
    ion_label_temp  = []; ion_label_temp_string  = ''
    nlabel = []; nions = 0
    #------------------------------------------------
    Lattice = dir_files + '/' + vLattice[k]
    label = 'Lattice' + str(k+1)


    #=========================================================
    # Obtendo a ID das Redes =================================
    #=========================================================
    poscar = open(Lattice, "r")
    VTemp = poscar.readline().split()
    poscar.close()
    #------------------------------------------------------------
    if (VTemp[0] == 'SAMBA'): id_materials.append(str(VTemp[-1]))
    if (VTemp[0] != 'SAMBA'): id_materials.append('none') 
    #----------------------------------------------------


    #==========================================================================
    # Copiando os arquivos POSCAR para o diretório 'output/' ==================
    #==========================================================================
    structure = Poscar.from_file(Lattice).structure
    supercell = structure.copy()
    supercell.make_supercell([1,1,1])
    Poscar(supercell).write_file(diret + 'temp0_' + label + '.vasp')


    #=========================================================
    # Obtendo a estequiometria das Redes =====================
    #=========================================================
    poscar = open(diret + 'temp0_' + label + '.vasp', "r")
    for i in range(5): VTemp = poscar.readline()
    VTemp0 = poscar.readline().split()
    VTemp1 = poscar.readline().split()
    poscar.close()
    #----------------
    temp_formula = ''
    #---------------------------
    for i in range(len(VTemp0)):
        temp_formula += str(VTemp0[i])
        if (str(VTemp1[i]) != '1'): temp_formula += str(VTemp1[i])
    formula.append(temp_formula) 
    #---------------------------


    #==========================================================================
    # Obtendo a altura no eixo-z dos diferentes materiais =====================
    #==========================================================================
    poscar = open(diret + 'temp0_' + label + '.vasp', "r")
    #-----------------------------------------------------
    for i in range(2): VTemp = poscar.readline()
    param = float(VTemp)
    #---------------------------------------------------
    for i in range(3): VTemp = poscar.readline().split()
    fator_Z = float(VTemp[2])*param
    #---------------------------------------------------
    passo = 0
    VTemp1 = poscar.readline().split()
    VTemp2 = poscar.readline().split()
    for i in range(len(VTemp1)):
        passo += int(VTemp2[i])
        # label_material[k] += str(VTemp1[i]) + str(VTemp2[i])
        label_material[k] += str(VTemp1[i])
        if (i < (len(VTemp1) -1)):  label_material[k] += '_' 
    label_htstructure += label_material[k]
    if (k < (n_Lattice -1)): label_htstructure += '+'
    #---------------------------------------------------
    VTemp = poscar.readline()
    #------------------------
    vZ = []
    for i in range(passo):
        VTemp = poscar.readline().split()
        vZ.append(float(VTemp[2]))
    #--------------------------------------------
    dZ[k] = (max(vZ) - min(vZ))*fator_Z
    minZ = min(vZ)
    for i in range(len(vZ)): vZ[i] = vZ[i] - minZ
    #--------------------------------------------
    poscar.close()
    #-------------


    #==========================================================================
    # Deslocando os materiais para Z = 0.0 ====================================
    #==========================================================================
    poscar = open(diret + 'temp0_' + label + '.vasp', "r")
    poscar_new = open(diret + 'temp1_' + label + '.vasp', "w")
    #---------------------------------------------------------
    for i in range(8):
        VTemp = poscar.readline()
        poscar_new.write(f'{VTemp}')
    for i in range(passo):
        VTemp = poscar.readline().split()
        poscar_new.write(f'{float(VTemp[0])} {float(VTemp[1])} {float(VTemp[2]) -minZ} \n')
    #-------------
    poscar.close()
    poscar_new.close()
    #-----------------

    #=============================================================================
    # Reescrita dos arquivos POSCAR, de forma a separar as diferentes subredes ===
    #=============================================================================
    poscar = open(diret + 'temp1_' + label + '.vasp', "r")
    poscar_new = open(diret + 'POSCAR_' + label + '.vasp', "w")

    for i in range(5):
        VTemp = poscar.readline()
        poscar_new.write(f'{VTemp}')

    #=================================================
    VTemp = poscar.readline().split()
    for i in range(len(VTemp)):  
        ion_label.append(str(VTemp[i]))                    # Armazenando o label de cada ion da rede (individualmente) na posição de um vetor.        
        ion_label_string += str(VTemp[i]) + ' '            # Criando uma String única contendo os labels de todos os ions da rede.         
    ion_label_string = ion_label_string[:-1]
    #-------------------------------------------------
    VTemp = poscar.readline().split()
    for i in range(len(VTemp)):                         
        nlabel.append(int(VTemp[i]))                       # Armazenando o número de cada tipo de ion da rede (individualmente) na posição de um vetor.
        nions += int(VTemp[i])                             # Obtendo o nº total de ions da rede.
    #-------------------------------------------------
    cont = -1;
    for i in range(len(ion_label)):                        # Loop sobre os diferentes tipos de ions da rede.
        ion_label_temp.append('')                          # Para cada diferente tipo de ion da rede, cria-se uma String.
        temp_label = ''
        for j in range(nlabel[i]):                         # Loop sobre o número de cada tipo de ion da rede.
            cont += 1
            temp_label += alphabet[cont] + ' '                                           
        ion_label_temp_string += temp_label        
        ion_label_temp[i] += temp_label[:-1]               # Criando uma String (para cada ion da rede individualmente) que armazena os rotulos temporários das correspondentes subredes.
    ion_label_temp_string = ion_label_temp_string[:-1]     # Criando uma String única que armazena os rotulos de todas as subredes.
    #-------------------------------------------------
    if (k == 0):
       vector_ions_labels_1    = ion_label                 # Armazenando o label de cada ion da rede (individualmente) na posição de um vetor.
       string_ions_labels_1    = ion_label_string          # Armazenando a String contendo os labels de todos os ions da rede.
       vector_subrede_labels_1 = ion_label_temp            # Armazenando os labels de subrede referentes a cada ion da rede (individualmente) na posição de um vetor.
       string_subrede_labels_1 = ion_label_temp_string     # Armazenando a String contendo os labels de subrede referentes a todos os ions da rede.
    if (k == 1):
       vector_ions_labels_2    = ion_label
       string_ions_labels_2    = ion_label_string
       vector_subrede_labels_2 = ion_label_temp
       string_subrede_labels_2 = ion_label_temp_string
    if (k == 2):
       vector_ions_labels_3    = ion_label
       string_ions_labels_3    = ion_label_string
       vector_subrede_labels_3 = ion_label_temp
       string_subrede_labels_3 = ion_label_temp_string
    #---------------------------------------------------------
    for i in range(nions): poscar_new.write(f'{alphabet[i]} ')
    poscar_new.write("\n")
    #--------------------------------------------
    for i in range(nions): poscar_new.write("1 ")
    poscar_new.write("\n")
    #-------------------------------------------------
    VTemp = poscar.readline()
    poscar_new.write(f'{VTemp}')
    #-------------------------------------------------
    for i in range(nions+1):
        VTemp = poscar.readline()
        poscar_new.write(f'{VTemp}')
    #-------------------------------------------------
    poscar.close()
    poscar_new.close()
    #=================================================

    os.remove(diret + 'temp0_' + label + '.vasp')
    os.remove(diret + 'temp1_' + label + '.vasp')


    #==========================================================================
    # Criando a Supercélula das redes (em coordenadas diretas) ================
    #==========================================================================
    structure = Poscar.from_file(diret + 'POSCAR_' + label + '.vasp').structure
    # Cria uma supercélula multiplicando os vetores da rede
    supercell = structure.copy()
    supercell.make_supercell(cell_fator)
    Poscar(supercell).write_file(diret + 'POSCAR_Supercell_' + label + '_direct.vasp')
    #===========================================================================================================
    # Evitando erro na escrita do rotulo das subredes (bug no pymatgen) ========================================
    #===========================================================================================================
    with open(diret + 'POSCAR_Supercell_' + label + '_direct.vasp', 'r') as arquivo: lines = arquivo.readlines()
    if (k == 0): lines[6 -1] = string_subrede_labels_1 + '\n'
    if (k == 1): lines[6 -1] = string_subrede_labels_2 + '\n'
    if (k == 2): lines[6 -1] = string_subrede_labels_3 + '\n'
    with open(diret + 'POSCAR_Supercell_' + label + '_direct.vasp', 'w') as arquivo: arquivo.writelines(lines)
    #===========================================================================================================


    #==========================================================================
    # Convertendo as coordenadas da Supercélula para a forma cartesiana =======
    #==========================================================================

    #------------------------------------------------------
    # Obtenção dos novos vetores da rede ------------------
    #------------------------------------------------------
    poscar = open(diret + 'POSCAR_Supercell_' + label + '_direct.vasp', "r")
    VTemp = poscar.readline()
    VTemp = poscar.readline(); param = float(VTemp)
    VTemp = poscar.readline().split(); A = [float(VTemp[0])*param, float(VTemp[1])*param, float(VTemp[2])*param]
    VTemp = poscar.readline().split(); B = [float(VTemp[0])*param, float(VTemp[1])*param, float(VTemp[2])*param]
    VTemp = poscar.readline().split(); C = [float(VTemp[0])*param, float(VTemp[1])*param, float(VTemp[2])*param]
   
    #----------------------------------------------------------------------
    # Obtenção das coordenadas da nova origem do sistema de coordenadas ---
    #----------------------------------------------------------------------
    if (orig == 0):
       center_x = 0.5*A[0] + 0.5*B[0] + 0.5*C[0]
       center_y = 0.5*A[1] + 0.5*B[1] + 0.5*C[1]
       center_z = 0.5*A[2] + 0.5*B[2] + 0.5*C[2]
    if (orig == 1):
       center_x = 0.5*A[0]
       center_y = 0.5*A[1]
       center_z = 0.5*A[2]

    #-----------------------------------------------------------------
    # Armazenando os rótulos das subredes (em um vetor de strings) ---
    #-----------------------------------------------------------------
    VTemp = poscar.readline().split()
    vector_ion = []
    for i in range(len(VTemp)):
        vector_ion.append(str(VTemp[i]))
    #-----------------------------------------------------------------------------------------
    # Armazenando o nº de ions de cada subrede (em um vetor), e o nº total de ions da rede ---
    #-----------------------------------------------------------------------------------------
    VTemp = poscar.readline().split()
    vector_nion = []; passo = 0
    for i in range(len(VTemp)):
        vector_nion.append(str(VTemp[i]))
        passo += int(VTemp[i])
    #-------------
    poscar.close()
    #-----------------------------------------------------------------------------------
    # Criando um vetor que associa a cada ion da rede o correspondente rotulo de subrede
    #-----------------------------------------------------------------------------------
    vector_rot_subredes = ['0']*passo
    number = -1
    for i in range(len(vector_nion)):
        for j in range(int(vector_nion[i])):
            number += 1 
            vector_rot_subredes[number] = str(vector_ion[i])
            #-----------------------------------------------

    #---------------------------------------------------------
    # Escrita do arquivo POSCAR em coordenadas cartesianas ---
    #---------------------------------------------------------
    poscar = open(diret + 'POSCAR_Supercell_' + label + '_direct.vasp', "r")
    poscar_new = open(diret + 'POSCAR_Supercell_' + label + '_cartesian.vasp', "w")
    #------------------------------------------------------------------------------
    poscar_new.write(f'{ion_label_string} \n')
    VTemp = poscar.readline()
    #------------------------
    for i in range(6):
        VTemp = poscar.readline()
        poscar_new.write(f'{VTemp}')
    VTemp = poscar.readline()
    poscar_new.write(f'cartesian \n')
    #--------------------------------
    for j in range(passo):
        VTemp = poscar.readline().split()
        k1 = float(VTemp[0]); k2 = float(VTemp[1]); k3 = float(VTemp[2])
        coord_x = ((k1*A[0]) + (k2*B[0]) + (k3*C[0]))*param
        coord_y = ((k1*A[1]) + (k2*B[1]) + (k3*C[1]))*param
        coord_z = ((k1*A[2]) + (k2*B[2]) + (k3*C[2]))*param
        poscar_new.write(f'{coord_x:>28,.21f} {coord_y:>28,.21f} {coord_z:>28,.21f}  {vector_rot_subredes[j]} \n')
    #-----------------    
    poscar_new.close()
    #-----------------


    #============================================================================
    # Encontrando o ion mais próximo da nova origem do sistema de coordenadas ===
    #============================================================================

    #-------------------------------------------------------------------------
    # Obtenção das coordenadas do átomo mais próximo da nova origem ----------
    #-------------------------------------------------------------------------
    poscar = open(diret + 'POSCAR_Supercell_' + label + '_cartesian.vasp', "r")
    for i in range(8): VTemp = poscar.readline()
    temp_d = 1000.0
    for i in range(passo):
        VTemp = poscar.readline().split()
        #------------------------
        coord_x = float(VTemp[0])
        coord_y = float(VTemp[1])
        coord_z = 0.0
        #------------------------
        dist = ((coord_x -center_x)**2 + (coord_y -center_y)**2)**(0.5)
        if (dist <= temp_d):
           temp_d = dist 
           new_center_x = coord_x; new_center_y = coord_y; new_center_z = 0.0
    #-------------
    poscar.close()
    #-------------

    #--------------------------------------------------------------------------
    # Deslocando e Armazenando as coordenadas cartesianas ---------------------
    #--------------------------------------------------------------------------
    poscar = open(diret + 'POSCAR_Supercell_' + label + '_cartesian.vasp', "r")
    poscar_new = open(diret + 'Coord_Supercell_Lattice' + str(k+1) + '.dat', "w")
    #----------------------------------------------------------------------------
    for i in range(8):  VTemp = poscar.readline()
    for i in range(passo):
        VTemp = poscar.readline().split()
        #---------------------------------------
        coord_x = float(VTemp[0]) - new_center_x
        coord_y = float(VTemp[1]) - new_center_y
        coord_z = float(VTemp[2]) - new_center_z
        label_ion = str(VTemp[3])
        #-------------------------------------------
        if (abs(coord_x) < 0.0000001): coord_x = 0.0  
        if (abs(coord_y) < 0.0000001): coord_y = 0.0  
        if (abs(coord_z) < 0.0000001): coord_z = 0.0
        #----------------------------------------------
        m_vector = ((coord_x)**2 + (coord_y)**2)**(0.5)
        #----------------------------------------------
        if (coord_x == 0.0 and coord_y == 0.0):
           if (k == 0): type1 = label_ion[0]; ion1_z = coord_z
           if (k == 1): type2 = label_ion[0]; ion2_z = coord_z
           if (k == 2): type3 = label_ion[0]; ion3_z = coord_z
        #--------------------------------------------------------------------------------------------------------------------
        poscar_new.write(f'{coord_x:>28,.21f} {coord_y:>28,.21f} {coord_z:>28,.21f} {m_vector:>28,.21f}   {label_ion[0]} \n')
    #-----------------
    poscar.close()
    poscar_new.close()
    #-----------------


    #==========================================================================================
    # Obtendo e Armazenando todas as possíveis células (Combinações dos vetores A1 e A2) ======
    #==========================================================================================

    diret_structures = 'Lattice' + str(k+1)

    #----------------------------------------------------
    # Verificando a existância do diretório 'Lattice' ---
    #----------------------------------------------------
    if os.path.isdir(diret + diret_structures):
       0 == 0
    else:
       os.mkdir(diret + diret_structures)
    #------------------------------------

    #--------------------------------------------------------------------------------------------------------
    SLattice = np.loadtxt(diret + 'Coord_Supercell_Lattice' + str(k+1) + '.dat', dtype='str'); SLattice.shape
    cell_Lattice = open(diret + 'Cells_Lattice' + str(k+1) + '.dat', "w")
    #----------------------------------------------------------------------------------------------------
    vx = SLattice[:,0]; vy = SLattice[:,1]; vz = SLattice[:,2]; dist = SLattice[:,3]; ion = SLattice[:,4]
    #----------------------------------------------------------------------------------------------------

    print(f' ')
    print(f'===================================================================================================')
    print(f'Passo {k+1}: Analisando todas as possíveis células do {k+1}º Material (Combinações dos vetores A1 e A2) ===')
    print(f'===================================================================================================')

    #--------------------------------------------------
    temp = 1.0; number = -1; n_passos = len(vx)*len(vx)
    #-----------------------
    for i in range(len(vx)):
        for j in range(len(vx)):
            #---------------------------
            number += 1
            porc = (number/n_passos)*100        
            #---------------------------
            if (porc >= temp and porc <= 100):
               print(f'Analyzed  {porc:>3,.0f}%')                 
               number += 1
               if (number == 1): temp = 1
               if (number == 2): temp = 5
               if (number >= 3): temp = temp + 5

            #--------------------------------------------------------------------------------------------------
            v1x = float(vx[i]); v1y = float(vy[i]); v1z = float(vz[i]); d1 = float(dist[i]); ion1 = str(ion[i])
            v2x = float(vx[j]); v2y = float(vy[j]); v2z = float(vz[j]); d2 = float(dist[j]); ion2 = str(ion[j])
            #--------------------------------------------------------------------------------------------------

            #--------------------------------------------------------------
            vector1 = np.array([v1x, v1y]);  vector2 = np.array([v2x, v2y])
            #--------------------------------------------------------------
            Area = np.linalg.norm(np.cross(vector1, vector2))
            if (n_Lattice == 2):  n_ions = Area*(dens_ions[0] + dens_ions[1])
            if (n_Lattice == 3):  n_ions = Area*(dens_ions[0] + dens_ions[1] + dens_ions[2])
            #-------------------------------------------------------------------------------
            if (n_ions >= ions_crit_i and n_ions <= ions_crit_f): 
               try:

                   #-----------------------------------------------------------------------------------------------
                   # Filtrando redes cujo produto triplo seja negativo --------------------------------------------
                   #-----------------------------------------------------------------------------------------------
                   a = np.array([v1x, v1y, 0.0])
                   b = np.array([v2x, v2y, 0.0])
                   c = np.array([0.0, 0.0, 15.0])
                   produto_vetorial = np.cross(a, b)              # Calculo do produto vetorial entre os vetores a e b
                   produto_triplo = np.dot(c, produto_vetorial)   # Calculo o produto escalar do vetor c com o resultado do produto vetorial (axb)

                   if (produto_triplo > 0):
                      #-----------------------------------------------------------------------
                      u = vector1/np.linalg.norm(vector1);  v = vector2/np.linalg.norm(vector2)
                      #------------------------------------------------------------------------
                      if (k == 0):
                         type = type1; ion_z = ion1_z
                      if (k == 1):
                         type = type2; ion_z = ion2_z
                      if (k == 2):
                         type = type3; ion_z = ion3_z
                      if (ion1 == ion2 == type and v1z == v2z == ion_z):
                         #----------------------------------------------- 
                         dot_product = np.dot(u, v)
                         angle = np.arccos(dot_product) / np.pi * 180
                         angle = round(angle, 3)                 
                         #----------------------------------------------
                         if (angle >= angle_min and angle <= angle_max):
                            if (angle != 0.0 and angle != 180.0):
                               cell_Lattice.write(f'{v1x:>28,.21f} {v1y:>28,.21f} {d1:>28,.21f} {v2x:>28,.21f} {v2y:>28,.21f} {d2:>28,.21f} {angle:>28,.21f} ')
                               #---------------------------------------------------------------------------------------------------------------------------------
                               # Obtenção das Matrizes de Transformação que levam a célula unitária original com todas as possível células do {k+1}º Material ---
                               #---------------------------------------------------------------------------------------------------------------------------------
                               Lattice_A = [ [A1x0[k], A1y0[k]], [A2x0[k], A2y0[k]] ]
                               Lattice_B = [ [v1x, v1y], [v2x, v2y] ]
                               #-------------------------------------
                               Lattice_A_inv = np.linalg.inv(Lattice_A)
                               MTransf = np.dot(Lattice_B, Lattice_A_inv)
                               #------------------------------------------
                               for aa in range(2):
                                   for bb in range(2):
                                       MTransf[aa][bb] = round(MTransf[aa][bb], 4)
                               #------------------------------------------------------
                               New_MTransf = [[0 for _ in range(2)] for _ in range(2)]
                               for aa in range(2):
                                   for bb in range(2):
                                       if ( (MTransf[aa][bb] -int(MTransf[aa][bb])) == 0.0): New_MTransf[aa][bb] = int(MTransf[aa][bb])
                                       if ( (MTransf[aa][bb] -int(MTransf[aa][bb])) != 0.0): New_MTransf[aa][bb] = MTransf[aa][bb]
                               #--------------------------------------------------------------------------------------------------
                               cell_Lattice.write(f'{New_MTransf[0][0]} {New_MTransf[0][1]} {New_MTransf[1][0]} {New_MTransf[1][1]} \n')
                   ...
   
               except Exception as e:
                   0 == 0

    #-------------------
    cell_Lattice.close()
    #-------------------


#=====================================================
# Obtendo a formula Quimica da Heteroestrutura =======
#=====================================================
formula_bilayer = ''
for i in range(len(formula)):
    formula_bilayer += formula[i]
    if (i < (len(formula) -1)): formula_bilayer += '+'


#=====================================================
# Analisando todos os possíveis casamentos de Rede ===
#=====================================================

#------------------------
n_test1 = 0;  n_test2 = 0
#------------------------
try:
    SLattice1 = np.loadtxt(diret + 'Cells_Lattice1.dat'); SLattice1.shape; n_test1 = len(SLattice1[:,0])
    SLattice2 = np.loadtxt(diret + 'Cells_Lattice2.dat'); SLattice2.shape; n_test2 = len(SLattice2[:,0])
    ...
except Exception as e: 0 == 0
#--------------------------------
if (n_test1 == 0 or n_test2 == 0):
   print(f' ')
   print(f'=============================')
   print(f'Nenhuma célula foi encontrada')
   print(f'=============================')
   print(f' ')
   #========================================
   shutil.rmtree(dir_files + '/' + 'output')
   sys.exit()   
   #==========
#----------------------------------------------------------------------------
if (n_Lattice == 2):  Structures = open(diret + 'Matching_Lattices.dat', "w")
if (n_Lattice == 3):  Structures = open(diret + 'Matching_Lattices_12.dat', "w")
#------------------------------------------------------------------------------------------------------------------------------------------------------------
v1Ax = SLattice1[:,0]; v1Ay = SLattice1[:,1]; d1A = SLattice1[:,2]; v1Bx = SLattice1[:,3]; v1By = SLattice1[:,4]; d1B = SLattice1[:,5]; ang1 = SLattice1[:,6]
v2Ax = SLattice2[:,0]; v2Ay = SLattice2[:,1]; d2A = SLattice2[:,2]; v2Bx = SLattice2[:,3]; v2By = SLattice2[:,4]; d2B = SLattice2[:,5]; ang2 = SLattice2[:,6]
#------------------------------------------------------------------------------------------------------------------------------------------------------------
MT1_00 = SLattice1[:,7];  MT1_01 = SLattice1[:,8];  MT1_10 = SLattice1[:,9];  MT1_11 = SLattice1[:,10]
MT2_00 = SLattice2[:,7];  MT2_01 = SLattice2[:,8];  MT2_10 = SLattice2[:,9];  MT2_11 = SLattice2[:,10]
#-----------------------------------------------------------------------------------------------------


print(f' ')
print(f'=================================================================')
print(f'Passo {3+n}: Analisando os casamentos de rede (1º e 2º materiais) ===')
print(f'=================================================================')

#------------------------------------------------------
temp = 1.0; number = -1; n_passos = len(v1Ax)*len(v2Ax)
#-------------------------
for i in range(len(v1Ax)):
    for j in range(len(v2Ax)):
        #---------------------------
        number += 1
        porc = (number/n_passos)*100        
        #---------------------------------
        if (porc >= temp and porc <= 100):
           print(f'Analyzed  {porc:>3,.0f}%')                 
           number += 1
           if (number == 1): temp = 1
           if (number == 2): temp = 5
           if (number >= 3): temp = temp + 5

        #--------------------------------------------------------------------------------------------------
        # Cálculo do mismatch entre as duas redes ---------------------------------------------------------
        #--------------------------------------------------------------------------------------------------
        mm_ang12 = ((ang1[i] -ang2[j])/ang1[i])*100
        mm_ang21 = ((ang2[j] -ang1[i])/ang2[j])*100
        mismatch_ang = (abs(mm_ang12) + abs(mm_ang21))/2
        mismatch_ang_diff = abs(ang1[i] -ang2[j])
        #----------------------------------------
        vA1 = np.array([v1Ax[i], v1Ay[i]]);  vB1 = np.array([v1Bx[i], v1By[i]]);  area_cell1 = np.linalg.norm(np.cross(vA1, vB1))
        vA2 = np.array([v2Ax[j], v2Ay[j]]);  vB2 = np.array([v2Bx[j], v2By[j]]);  area_cell2 = np.linalg.norm(np.cross(vA2, vB2))
        mm_area12 = ((area_cell1 -area_cell2)/area_cell1)*100
        mm_area21 = ((area_cell2 -area_cell1)/area_cell2)*100
        mismatch_area = (abs(mm_area12) + abs(mm_area21))/2
        #--------------------------------------------------

        #------------------------------------------------------------------------------------------------------------
        if (mismatch_ang <= crit_angle_perc and mismatch_ang_diff <= crit_angle_diff and mismatch_area <= crit_area):
           #---------------------------------------------------------------------------------------------------------
           mm_A12 = ((d1A[i] -d2A[j])/d1A[i])*100
           mm_A21 = ((d2A[j] -d1A[i])/d2A[j])*100
           mismatch_A = (abs(mm_A12) + abs(mm_A21))/2
           #-----------------------------------------
           if (mismatch_A <= crit_mismatch):
              mm_B12 = ((d1B[i] -d2B[j])/d1B[i])*100
              mm_B21 = ((d2B[j] -d1B[i])/d2B[j])*100
              mismatch_B = (abs(mm_B12) + abs(mm_B21))/2
              if (mismatch_B <= crit_mismatch):
                 #------------------------------------------------
                 average_mismatch_AB = (mismatch_A + mismatch_B)/2
                 #------------------------------------------------
                 if (n_Lattice == 2):
                    #============================================================================================
                    Structures.write(f'{v1Ax[i]:>14,.9f} {v1Ay[i]:>14,.9f} {v1Bx[i]:>14,.9f} {v1By[i]:>14,.9f} ')
                    Structures.write(f'{v2Ax[j]:>14,.9f} {v2Ay[j]:>14,.9f} {v2Bx[j]:>14,.9f} {v2By[j]:>14,.9f} ')
                    Structures.write(f'0.0 0.0 0.0 0.0 ')
                    Structures.write(f'{mismatch_area:>7,.4f} {average_mismatch_AB:>7,.4f} {mismatch_ang:>7,.4f} ')
                    Structures.write(f'0.0 0.0 0.0 ')
                    Structures.write(f'{MT1_00[i]} {MT1_01[i]} {MT1_10[i]} {MT1_11[i]} ')
                    Structures.write(f'{MT2_00[j]} {MT2_01[j]} {MT2_10[j]} {MT2_11[j]} ')
                    Structures.write(f'0.0 0.0 0.0 0.0 \n')
                    #============================================================================================
                 if (n_Lattice == 3):
                    #========================================================================================
                    Structures.write(f'{v1Ax[i]} {v1Ay[i]} {d1A[i]} {v1Bx[i]} {v1By[i]} {d1B[i]} {ang1[i]} ')
                    Structures.write(f'{v2Ax[j]} {v2Ay[j]} {d2A[j]} {v2Bx[j]} {v2By[j]} {d2B[j]} {ang2[j]} ')
                    Structures.write(f'{mismatch_A:>7,.4f} {mismatch_B:>7,.4f} {mismatch_ang:>7,.4f} ')
                    Structures.write(f'{MT1_00[i]} {MT1_01[i]} {MT1_10[i]} {MT1_11[i]} ')
                    Structures.write(f'{MT2_00[j]} {MT2_01[j]} {MT2_10[j]} {MT2_11[j]} \n')
                    #========================================================================================
#-----------------
Structures.close()
#-----------------


if (n_Lattice == 3):
   #--------
   n = n + 1
   #--------------------------------------------------------------------------
   SLattice1 = np.loadtxt(diret + 'Matching_Lattices_12.dat'); SLattice1.shape
   SLattice3 = np.loadtxt(diret + 'Cells_Lattice3.dat'); SLattice3.shape
   #--------------------------------------------------------------------
   Structures = open(diret + 'Matching_Lattices.dat', "w")
   #---------------------------------------------------------------------------------------------------------------------------------------------------------------
   v1Ax = SLattice1[:,0]; v1Ay = SLattice1[:,1]; d1A = SLattice1[:,2]; v1Bx = SLattice1[:,3];  v1By = SLattice1[:,4];  d1B = SLattice1[:,5];  ang1 = SLattice1[:,6]
   v2Ax = SLattice1[:,7]; v2Ay = SLattice1[:,8]; d2A = SLattice1[:,9]; v2Bx = SLattice1[:,10]; v2By = SLattice1[:,11]; d2B = SLattice1[:,12]; ang2 = SLattice1[:,13]
   mismatch_area12 = SLattice1[:,14]; mismatch_AB12 = SLattice1[:,15]; mismatch_ang12 = SLattice1[:,16]
   v3Ax = SLattice3[:,0]; v3Ay = SLattice3[:,1]; d3A = SLattice3[:,2]; v3Bx = SLattice3[:,3];  v3By = SLattice3[:,4];  d3B = SLattice3[:,5];  ang3 = SLattice3[:,6]
   #---------------------------------------------------------------------------------------------------------------------------------------------------------------
   MT3_00 = SLattice3[:,7];  MT3_01 = SLattice3[:,8];  MT3_10 = SLattice3[:,9];  MT3_11 = SLattice3[:,10]
   #-----------------------------------------------------------------------------------------------------

   print(f' ')
   print(f'=================================================================')
   print(f'Passo {3+n}: Analisando os casamentos de rede (1º e 3º materiais) ===')
   print(f'=================================================================')

   #------------------------------------------------------
   temp = 1.0; number = -1; n_passos = len(v1Ax)*len(v3Ax)
   #-------------------------
   for i in range(len(v1Ax)):
       for j in range(len(v3Ax)):
           #---------------------------
           number += 1
           porc = (number/n_passos)*100        
           #---------------------------------
           if (porc >= temp and porc <= 100):
              print(f'Analyzed  {porc:>3,.0f}%')                 
              number += 1
              if (number == 1): temp = 1
              if (number == 2): temp = 5
              if (number >= 3): temp = temp + 5

           #--------------------------------------------------------------------------------------------------
           # Cálculo do mismatch entre as duas redes ---------------------------------------------------------
           #--------------------------------------------------------------------------------------------------
           mm_ang13 = ((ang1[i] -ang3[j])/ang1[i])*100
           mm_ang31 = ((ang3[j] -ang1[i])/ang3[j])*100
           mismatch_ang = (abs(mm_ang13) + abs(mm_ang31))/2
           #-----------------------------------------------
           vA1 = np.array([v1Ax[i], v1Ay[i]]);  vB1 = np.array([v1Bx[i], v1By[i]]);  area_cell1 = np.linalg.norm(np.cross(vA1, vB1))
           vA3 = np.array([v3Ax[j], v3Ay[j]]);  vB3 = np.array([v3Bx[j], v3By[j]]);  area_cell3 = np.linalg.norm(np.cross(vA3, vB3))
           mm_area13 = ((area_cell1 -area_cell3)/area_cell1)*100
           mm_area31 = ((area_cell3 -area_cell1)/area_cell3)*100
           mismatch_area = (abs(mm_area13) + abs(mm_area31))/2
           #--------------------------------------------------
           if (mismatch_ang <= crit_angle_perc and mismatch_ang_diff <= crit_angle_diff and mismatch_area <= crit_area):
              #---------------------------------------------------------------------------------------------------------
              mm_A13 = ((d1A[i] -d3A[j])/d1A[i])*100
              mm_A31 = ((d3A[j] -d1A[i])/d3A[j])*100
              mismatch_A = (abs(mm_A13) + abs(mm_A31))/2
              #-----------------------------------------
              if (mismatch_A <= crit_mismatch):
                 mm_B13 = ((d1B[i] -d3B[j])/d1B[i])*100
                 mm_B31 = ((d3B[j] -d1B[i])/d3B[j])*100
                 mismatch_B = (abs(mm_B13) + abs(mm_B31))/2
                 if (mismatch_B <= crit_mismatch):
                    #------------------------------------------------
                    average_mismatch_AB = (mismatch_A + mismatch_B)/3
                    #------------------------------------------------
                    #============================================================================================
                    Structures.write(f'{v1Ax[i]:>14,.9f} {v1Ay[i]:>14,.9f} {v1Bx[i]:>14,.9f} {v1By[i]:>14,.9f} ')
                    Structures.write(f'{v2Ax[i]:>14,.9f} {v2Ay[i]:>14,.9f} {v2Bx[i]:>14,.9f} {v2By[i]:>14,.9f} ')
                    Structures.write(f'{v3Ax[j]:>14,.9f} {v3Ay[j]:>14,.9f} {v3Bx[j]:>14,.9f} {v3By[j]:>14,.9f} ')
                    Structures.write(f'{mismatch_area12[i]:>7,.4f} {mismatch_AB12[i]:>7,.4f} {mismatch_ang12[i]:>7,.4f} ')
                    Structures.write(f'{mismatch_area:>7,.4f} {average_mismatch_AB:>7,.4f} {mismatch_ang:>7,.4f} \n')
                    Structures.write(f'{MT1_00[i]} {MT1_01[i]} {MT1_10[i]} {MT1_11[i]} ')
                    Structures.write(f'{MT2_00[i]} {MT2_01[i]} {MT2_10[i]} {MT2_11[i]} ')
                    Structures.write(f'{MT3_00[j]} {MT3_01[j]} {MT3_10[j]} {MT3_11[j]} \n')
                    #======================================================================
   #-----------------
   Structures.close()
   #-----------------


n_structures = 0
#----------------
try:
    structures = np.loadtxt(diret + 'Matching_Lattices.dat', dtype='str'); structures.shape
    n_structures = len(structures[:,0])
    ...
except Exception as e: 0 == 0

if (n_structures == 0):
   print(f' ')
   print(f'=============================')
   print(f'Nenhuma célula foi encontrada')
   print(f'=============================')
   print(f' ')
   #========================================
   shutil.rmtree(dir_files + '/' + 'output')
   sys.exit()   
   #==========


if (n_structures != 0):

   #=============================================================================
   # Obtendo os arquivos POSCAR para cada uma das redes e células encontradas ===
   #=============================================================================

   #-----------------------------------------------------------
   # Novo módulo para o vetor A3 da célula das Heteroestruturas
   #-----------------------------------------------------------
   if (n_Lattice == 2):  d = dZ[0] + dZ[1] + separacao1 + vacuum                        
   if (n_Lattice == 3):  d = dZ[0] + dZ[1] + dZ[2] + separacao1 + separacao2 + vacuum

   print(f' ')
   print(f'========================================================================')
   print(f'Passo {4+n}: Escrevendo os arquivos POSCAR para as redes dos {n_Lattice} materiais ===')
   print(f'========================================================================')

   #-------------------------------------------------
   temp = 1.0; number = -1; n_passos = 2*n_structures
   #-----------------
   for k in range(n_Lattice):
       match = open(diret + 'Matching_Lattices.dat', "r")
       for j in range(n_structures):
           #---------------------------
           number += 1
           porc = (number/n_passos)*100        
           #---------------------------
           if (porc >= temp and porc <= 100):
              print(f'Analyzed  {porc:>3,.0f}%')                 
              number += 1
              if (number == 1): temp = 1
              if (number == 2): temp = 5
              if (number >= 3): temp = temp + 5

           #-----------------------------------
           if (k == 0):
              label = 'Lattice1'; p = 0
              s_old = string_ions_labels_1;  s_new = string_subrede_labels_1
              rotulo_old = vector_ions_labels_1;  rotulo = vector_subrede_labels_1
           if (k == 1):
              label = 'Lattice2'; p = 4
              s_old = string_ions_labels_2;  s_new = string_subrede_labels_2
              rotulo_old = vector_ions_labels_2;  rotulo = vector_subrede_labels_2
           if (k == 2):
              label = 'Lattice3'; p = 8
              s_old = string_ions_labels_3;  s_new = string_subrede_labels_3
              rotulo_old = vector_ions_labels_3;  rotulo = vector_subrede_labels_3
           #-----------------------------------------------  
           VTemp = match.readline().split()

           try:
               #---------------------------------------------
               x1 = float(VTemp[p+0]); y1 = float(VTemp[p+1])
               x2 = float(VTemp[p+2]); y2 = float(VTemp[p+3])
               null = 0.0
               #---------------------------------------------
               a = np.array([x1,   y1,   null])
               b = np.array([x2,   y2,   null])
               c = np.array([null, null,    d])
               #---------------------------------------------
               # Definir a matriz de transformação
               T = np.linalg.inv(np.array([a, b, c]).T)
               #---------------------------------------------
               poscar1 = open(diret + 'POSCAR_Supercell_' + label + '_cartesian.vasp', "r")
               poscar2 = open(diret + 'Coord_Supercell_' + label + '.dat', "r")
               poscar_new = open(diret + 'Lattice' + str(k+1) + '/temp_' + str(j+1) + '.vasp', "w")
               #---------------------------------------------
               for i in range(2):
                   VTemp = poscar1.readline()
                   poscar_new.write(f'{VTemp}')
               #---------------------------------------------
               for i in range(3):
                   VTemp = poscar1.readline()
               #---------------------------------------------
               poscar_new.write(f' {x1:>28,.21f} {y1:>28,.21f} {null:>28,.21f} \n')
               poscar_new.write(f' {x2:>28,.21f} {y2:>28,.21f} {null:>28,.21f} \n')
               poscar_new.write(f' {null:>28,.21f} {null:>28,.21f} {d:>28,.21f} \n')
               #---------------------------------------------
               VTemp = poscar1.readline()     
               poscar_new.write(f'{VTemp}')  # poscar_new.write(f'{s_old}')
               #---------------------------------------------
               passo = 0
               VTemp = poscar1.readline().split()
               for i in range(len(VTemp)):
                   passo += int(VTemp[i]) 

               #--------------
               poscar1.close()
               #--------------

               #####################################################################

               poscar_new.write(f'direct \n')

               #----------------------------------------------------------------------------------------------------
               # Convertendo as posições atômicas cartesianas de todos os átomos da Supercélula para a forma direta,
               # e filtrando/excluindo os átômos que não se encontram no interior das células selecionadas.
               #-------------------------------------------------------------------------------------------
               for i in range(passo):
                   VTemp = poscar2.readline().split()
                   x = float(VTemp[0])
                   y = float(VTemp[1])
                   z = float(VTemp[2])
                   l = str(VTemp[4])
    
                   # Definir a posição cartesiana do átomo
                   r = np.array([x, y, z])  

                   # Calcular a posição fracionária
                   f = np.dot(T, r)
                   f = np.where(f < 0, f + 1, f)

                   if ((f[0] >= 0.0) and (f[0] <= 1.0)):
                      if ((f[1] >= 0.0) and (f[1] <= 1.0)):
                         if ((f[2] >= 0.0) and (f[2] <= 1.0)):
                            for m in range(3):
                                f[m] = round(f[m], 6)
                                if (f[m] > 0.99999 or f[m] < 0.00001):
                                   f[m] = 0.0
                            poscar_new.write(f'{f[0]} {f[1]} {f[2]} {l} \n')

               #-----------------
               poscar_new.close()
               #-----------------

               #----------------------------------------------------------------------------------
               # Eliminando linhas (posições atômicas) duplicadas em cada arquivo POSCAR ---------
               #----------------------------------------------------------------------------------
               inputFile = open(diret + 'Lattice' + str(k+1) + '/temp_' + str(j+1) + '.vasp', "r") 
               outputFile = open(diret + 'Lattice' + str(k+1) + '/POSCAR_' + str(j+1) + '.vasp', "w") 
               lines_seen_so_far = set() 
               for line in inputFile:    
                   if line not in lines_seen_so_far: 
                       outputFile.write(line) 
                       lines_seen_so_far.add(line)         
               inputFile.close() 
               outputFile.close()

               os.remove(diret + 'Lattice' + str(k+1) + '/temp_' + str(j+1) + '.vasp')

               #--------------------------------------------------------------------------
               # Inserindo a quantidade de cada tipo de ion presente no arquivo POSCAR ---
               #--------------------------------------------------------------------------
               poscar = open(diret + 'Lattice' + str(k+1) + '/POSCAR_' + str(j+1) + '.vasp', "r")

               for i in range(7):
                   VTemp = poscar.readline()

               test = 1
               #----------------------------
               n_label = [0]*len(rotulo_old)
               #----------------------------
               while (test != 0):
                     VTemp = poscar.readline().split()
                     if (len(VTemp) != 0):
                        l = str(VTemp[3])
                        for i in range(len(rotulo_old)):
                            sub_rede = rotulo[i].split()
                            n_sb = len(sub_rede)
                            for ii in range(n_sb):
                                if (sub_rede[ii] == l):
                                   n_label[i] += 1 
                     if (len(VTemp) == 0):
                        test = 0
               #--------------------------------   
               nlabel = ''
               for i in range(len(n_label)):
                   nlabel += str(n_label[i]) + ' '
               nlabel = nlabel[:-1] 
               #--------------------------------   

               #-------------
               poscar.close()
               #-------------

               file = open(diret + 'Lattice' + str(k+1) + '/POSCAR_' + str(j+1) + '.vasp', 'r')
               lines = file.readlines()
               file.close()
               linha = 6
               lines.insert(linha, f'{nlabel} \n')
               #----------------------------------
               file = open(diret + 'Lattice' + str(k+1) + '/POSCAR_' + str(j+1) + '.vasp', 'w')
               file.writelines(lines)
               file.close()

               file = open(diret + 'Lattice' + str(k+1) + '/POSCAR_' + str(j+1) + '.vasp', 'r')
               conteudo = file.read()
               file.close()
               #------------------------------------------
               string_new = conteudo.replace(s_new, s_old)
               file = open(diret + 'Lattice' + str(k+1) + '/POSCAR_' + str(j+1) + '.vasp', 'w')
               file.write(string_new)
               file.close()

               ...

           except Exception  as e:
               print(f"error detected: {e}")

       match.close()


#=====================================================================
# Montando as Heteroestruturas =======================================
#=====================================================================

tfile = np.loadtxt(diret + 'Matching_Lattices.dat', dtype='str'); tfile.shape
#-----------------------------------------
mismatch_A12   = tfile[:,12].astype(float)
mismatch_B12   = tfile[:,13].astype(float)
mismatch_ang12 = tfile[:,14].astype(float)
mismatch_12    = (mismatch_A12 + mismatch_B12 + mismatch_ang12)/3
#------------------------------------------------------------------
MT1_00 = tfile[:,18].astype(float);  MT2_00 = tfile[:,22].astype(float)
MT1_01 = tfile[:,19].astype(float);  MT2_01 = tfile[:,23].astype(float)
MT1_10 = tfile[:,20].astype(float);  MT2_10 = tfile[:,24].astype(float)
MT1_10 = tfile[:,21].astype(float);  MT2_10 = tfile[:,25].astype(float)

if (n_Lattice == 3):
   mismatch_A13   = tfile[:,15].astype(float)
   mismatch_B13   = tfile[:,16].astype(float)
   mismatch_ang13 = tfile[:,17].astype(float)
   mismatch_13    = (mismatch_A13 + mismatch_B13 + mismatch_ang13)/3
   #----------------------------------------------------------------
   MT3_00 = tfile[:,26].astype(float)
   MT3_01 = tfile[:,27].astype(float)
   MT3_10 = tfile[:,28].astype(float)
   MT3_10 = tfile[:,29].astype(float)


print(f' ')
print(f'===============================================================')
print(f'Passo {5+n}: Escrevendo os arquivos POSCAR das Heteroestruturas ===')
print(f'===============================================================')  

if (n_structures != 0):

   #-----------------------------------------------
   temp = 1.0; number = -1; n_passos = n_structures
   #----------
   for i in range(n_structures):
       #---------------------------
       number += 1
       porc = (number/n_passos)*100        
       #---------------------------
       if (porc >= temp and porc <= 100):
          print(f'Analyzed  {porc:>3,.0f}%')                 
          number += 1
          if (number == 1): temp = 1
          if (number == 2): temp = 5
          if (number >= 3): temp = temp + 5

       #-----------------------------------------------------------------------------
       # Verificando a existância do diretório de salvamento das Heteroestruturas ---
       #-----------------------------------------------------------------------------
       if os.path.isdir(dir_files + '/' + dir_o):
          0 == 0
       else:
          os.mkdir(dir_files + '/' + dir_o)
       #-------------------------------------
       diret2 = dir_files + '/' + dir_o + '/'
       #-------------------------------------
       if (loop_ht == 1):
          if os.path.isdir(dir_files + '/' + dir_o + '/' + dir_loop):
             0 == 0
          else:
             os.mkdir(dir_files + '/' + dir_o + '/' + dir_loop)
          #----------------------------------------------------
          diret2 = diret2 + dir_loop + '/'
          #-------------------------------
          
       #------------------------------------------------------------------------           # Faz sentido esta definição do ângulo ???????????????????????????????????????????????????????
       # Obtendo o angulo de rotação entre os materiais: -----------------------           # Faz sentido esta definição do ângulo ???????????????????????????????????????????????????????
       #------------------------------------------------------------------------           # Faz sentido esta definição do ângulo ???????????????????????????????????????????????????????
       poscar1 = open(diret + 'Lattice1' + '/POSCAR_' + str(i+1) + '.vasp', "r")
       poscar2 = open(diret + 'Lattice2' + '/POSCAR_' + str(i+1) + '.vasp', "r")
       if (n_Lattice == 3):  poscar3 = open(diret + 'Lattice3' + '/POSCAR_' + str(i+1) + '.vasp', "r")
       #----------------------------------------------------------------------------------------------
       VTemp = poscar1.readline()
       VTemp = poscar1.readline(); param = float(VTemp)
       A = poscar1.readline().split(); A1 = np.array([ float(A[0])*param, float(A[1])*param ])
       B = poscar1.readline().split(); B1 = np.array([ float(B[0])*param, float(B[1])*param ])
       #--------------------------------------------------------------------------------------
       VTemp = poscar2.readline()
       VTemp = poscar2.readline(); param = float(VTemp)
       A = poscar2.readline().split(); A2 = np.array([ float(A[0])*param, float(A[1])*param ])
       B = poscar2.readline().split(); B2 = np.array([ float(B[0])*param, float(B[1])*param ])
       #--------------------------------------------------------------------------------------
       if (n_Lattice == 3):
          VTemp = poscar3.readline()
          VTemp = poscar3.readline(); param = float(VTemp)
          A = poscar3.readline().split(); A3 = np.array([ float(A[0])*param, float(A[1])*param ])
          B = poscar3.readline().split(); B3 = np.array([ float(B[0])*param, float(B[1])*param ])
       #-----------------------------------------------------------------------------------------
       V1 = 0.5*A1 + 0.5*B1
       V2 = 0.5*A2 + 0.5*B2
       if (n_Lattice == 3):  V3 = 0.5*A3 + 0.5*B3
       #-----------------------------------------
       u = V1/np.linalg.norm(V1)
       v = V2/np.linalg.norm(V2)
       dot_product = np.dot(u, v)
       angle0 = np.arccos(dot_product) / np.pi * 180
       #--------------------------------------------
       cross_product = np.cross(V1, V2)
       if (cross_product < 0): angle0 = -angle0
       angle0 = round(angle0, 3)
       if (abs(angle0) == 0.0):  angle0 = 0.0
       #-----------------------------------------------------------------
       # if (angle0 < 10):                    angle1 = '00' + str(angle0)
       # if (angle0 >= 10 and angle0 < 100):  angle1 = '0'  + str(angle0)
       # if (angle0 >= 100):                  angle1 = ''   + str(angle0)
       # if (len(angle1) == 5):               angle1 = angle1 + '00'
       # if (len(angle1) == 6):               angle1 = angle1 + '0'
       #-----------------------------------------------------------------
       angle1 = str(angle0)
       #=================================================================
       if (n_Lattice == 3):
          u = V1/np.linalg.norm(V1)
          v = V2/np.linalg.norm(V3)
          dot_product = np.dot(u, v)
          angle2 = np.arccos(dot_product) / np.pi * 180
          #--------------------------------------------
          cross_product = np.cross(V1, V3)
          if (cross_product < 0): angle2 = -angle2
          angle2 = round(angle2, 3)
          if (abs(angle2) == 0.0):  angle2 = 0.0
          #-----------------------------------------------------------------
          # if (angle2 < 10):                    angle3 = '00' + str(angle2)
          # if (angle2 >= 10 and angle2 < 100):  angle3 = '0'  + str(angle2)
          # if (angle2 >= 100):                  angle3 = ''   + str(angle2)
          # if (len(angle3) == 5):               angle3 = angle3 + '00'
          # if (len(angle3) == 6):               angle3 = angle3 + '0'
          #-----------------------------------------------------------------
          angle3 = str(angle2) 
          #=================================================================
       #------------------------------------
       for j in range(3):
           VTemp1 = poscar1.readline().split()
           VTemp2 = poscar2.readline().split()
           if (n_Lattice == 3): VTemp3 = poscar3.readline().split()
       #-----------------------------------------------------------
       nions_1 = nions_2 = nions_3 = 0
       for m in range(len(VTemp1)): nions_1 += int(VTemp1[m])
       for m in range(len(VTemp2)): nions_2 += int(VTemp2[m])
       if (n_Lattice == 3):
          for m in range(len(VTemp3)): nions_3 += int(VTemp3[m])
       #--------------
       poscar1.close()
       poscar2.close()
       if (n_Lattice == 3):  poscar3.close()
       #------------------------------------


       #------------------------------------------------------------------------
       # Escrevendo o arquivo POSCAR das Heteroestruturas: ---------------------
       #------------------------------------------------------------------------
       poscar1 = open(diret + 'Lattice1' + '/POSCAR_' + str(i+1) + '.vasp', "r")
       poscar2 = open(diret + 'Lattice2' + '/POSCAR_' + str(i+1) + '.vasp', "r")
       if (n_Lattice == 3):  poscar3 = open(diret + 'Lattice3' + '/POSCAR_' + str(i+1) + '.vasp', "r")  
       poscar_new = open(diret2 + 'POSCAR_' + str(i+1) + '.vasp', "w")
       #--------------------------------------------------------------
       ID_Heteroestrutura = formula_bilayer + '_' + unique_id
       #-----------------------------------------------------------------
       poscar_new.write(f'SAMBA {label_htstructure} {nions_1} {nions_2}')
       if (n_Lattice == 3): poscar_new.write(f' {nions_3}')
       poscar_new.write(f' | mismatch_12 = {mismatch_A12[i]}_{mismatch_B12[i]}_{mismatch_ang12[i]} | rotation_12 = {angle1}')
       if (n_Lattice == 3): poscar_new.write(f' | mismatch_13 = {mismatch_A13[i]}_{mismatch_B13[i]}_{mismatch_ang13[i]} | rotation_13 = {angle3}')
       poscar_new.write(f' | MTransf_1 = {int(MT1_00[i])}_{int(MT1_01[i])}_{int(MT1_10[i])}_{int(MT1_10[i])}')
       poscar_new.write(f' | MTransf_2 = {int(MT2_00[i])}_{int(MT2_01[i])}_{int(MT2_10[i])}_{int(MT2_10[i])}')
       if (n_Lattice == 3): poscar_new.write(f' | MTrans_3 = {int(MT3_00[i])}_{int(MT3_01[i])}_{int(MT3_10[i])}_{int(MT3_10[i])}')
       poscar_new.write(f' | {ID_Heteroestrutura} \n')
       #----------------------------------------------


       #================================================
       VTemp1 = poscar1.readline()
       VTemp2 = poscar2.readline()
       if (n_Lattice == 3):  VTemp3 = poscar3.readline()
       #================================================
       if (mismatch_type == 0):
          #--------------------------
          VTemp1 = poscar1.readline()
          VTemp2 = poscar2.readline()
          if (n_Lattice == 3):  VTemp3 = poscar3.readline()
          poscar_new.write(f'1.0 \n')
          #----------------------------
          for j in range(2):
              VTemp1 = poscar1.readline()
              VTemp2 = poscar2.readline()
              if (n_Lattice == 3): VTemp3 = poscar3.readline()
          #----------------------------
          modulo_A1 = np.linalg.norm(A1)
          modulo_B1 = np.linalg.norm(B1)
          modulo_A2 = np.linalg.norm(A2)
          modulo_B2 = np.linalg.norm(B2)
          if (n_Lattice == 3): 
             modulo_A3 = np.linalg.norm(A3)
             modulo_B3 = np.linalg.norm(B3)
          #--------------------------------
          if (n_Lattice == 2): 
             modulo_medio_A = (modulo_A1 + modulo_A2)/2
             modulo_medio_B = (modulo_B1 + modulo_B2)/2
          if (n_Lattice == 3): 
             modulo_medio_A = (modulo_A1 + modulo_A2 + modulo_A3)/3
             modulo_medio_B = (modulo_B1 + modulo_B2 + modulo_B3)/3
          #---------------------------------
          A4 = (A1/modulo_A1)*modulo_medio_A
          #---------------------------------
          angle_1 = np.arccos(np.dot(A1,B1)/(modulo_A1*modulo_B1))
          angle_2 = np.arccos(np.dot(A2,B2)/(modulo_A2*modulo_B2))
          if (n_Lattice == 2): angle_medio = (angle_1 + angle_2)/2
          if (n_Lattice == 3):
             angle_3 = np.arccos(np.dot(A3,B3)/(modulo_A3*modulo_B3)) 
             angle_medio = (angle_1 + angle_2 + angle_3)/3
          # Calculando a rotação para ajustar o vetor B4 -------------------
          cos_angle_medio = np.cos(angle_medio)
          sin_angle_medio = np.sin(angle_medio)
          matriz_rotacao = np.array([ [cos_angle_medio, -sin_angle_medio], [sin_angle_medio, cos_angle_medio] ])
          #----------------------------------------------------
          B4 = matriz_rotacao @ ((A1/modulo_A1)*modulo_medio_B)
          #----------------------------------------------------
          poscar_new.write(f'{A4[0]} {A4[1]} 0.0 \n')
          poscar_new.write(f'{B4[0]} {B4[1]} 0.0 \n')
          #--------------------------
          VTemp1 = poscar1.readline()
          VTemp2 = poscar2.readline()
          if (n_Lattice == 3):
             VTemp3 = poscar3.readline()
          poscar_new.write(f'{VTemp1}')
       #================================================
       if (mismatch_type == 1):
          for j in range(4):
              VTemp1 = poscar1.readline()
              VTemp2 = poscar2.readline()
              if (n_Lattice == 3):
                 VTemp3 = poscar3.readline()
              poscar_new.write(f'{VTemp1}') 
       #================================================
       VTemp1 = poscar1.readline().split()
       VTemp2 = poscar2.readline().split()
       if (n_Lattice == 3):  VTemp3 = poscar3.readline().split()
       for j in range(len(VTemp1)): poscar_new.write(f'{str(VTemp1[j])} ')
       for j in range(len(VTemp2)): poscar_new.write(f'{str(VTemp2[j])} ')
       if (n_Lattice == 3):
          for j in range(len(VTemp3)): poscar_new.write(f'{str(VTemp3[j])} ')
       poscar_new.write(f' \n')
       #--------------------------------------------------------------------- 
       VTemp1 = poscar1.readline().split()
       VTemp2 = poscar2.readline().split()
       if (n_Lattice == 3):  VTemp3 = poscar3.readline().split()
       for j in range(len(VTemp1)): poscar_new.write(f'{str(VTemp1[j])} ')
       for j in range(len(VTemp2)): poscar_new.write(f'{str(VTemp2[j])} ')
       if (n_Lattice == 3):
          for j in range(len(VTemp3)): poscar_new.write(f'{str(VTemp3[j])} ')
       poscar_new.write(f' \n')
       #--------------------------------------------------------------------- 
       VTemp1 = poscar1.readline()
       VTemp2 = poscar2.readline()
       if (n_Lattice == 3):  VTemp3 = poscar3.readline()
       poscar_new.write(f'direct \n')
       #-----------------------------
       for j in range(nions_1):
           VTemp1 = poscar1.readline().split()
           Z1 = ((vacuum/2)/d)
           poscar_new.write(f'{float(VTemp1[0])} {float(VTemp1[1])} {Z1 + float(VTemp1[2])} \n')
       for j in range(nions_2):
           VTemp2 = poscar2.readline().split()
           Z2 = Z1 + ((dZ[0] + separacao1)/d)
           poscar_new.write(f'{float(VTemp2[0])} {float(VTemp2[1])} {Z2 + float(VTemp2[2])} \n')
       if (n_Lattice == 3):  
          for j in range(nions_3):
              VTemp3 = poscar3.readline().split()
              Z3 = Z2 + ((dZ[1] + separacao2)/d)
              poscar_new.write(f'{float(VTemp3[0])} {float(VTemp3[1])} {Z3 + float(VTemp3[2])} \n')
       #-------------------------------------------------------------------------------------------
       poscar1.close()
       poscar2.close()
       if (n_Lattice == 3):  poscar3.close()
       poscar_new.close()
       #-----------------

files = os.listdir(diret + 'Lattice1')
n_structures = len(files)
#------------------------
#===================================================
print(f'--------------------------------')
print(f'{n_structures} células foram identificadas')
#===================================================


#=====================================================================
# Excluindo o diretório contendo arquivos temporários do cálculo: ====
#=====================================================================
shutil.rmtree(dir_files + '/' + 'output')


print(f' ')
print(f'============================================')           # Verificar com cuidado este procedimento ???????????????????????????????????????????????????????
print(f'Passo {6+n}: Excluindo celulas não-unitárias ===')       # Verificar com cuidado este procedimento ???????????????????????????????????????????????????????
print(f'============================================')           # Verificar com cuidado este procedimento ???????????????????????????????????????????????????????

files = os.listdir(diret2)

#--------------------------------------------------------------
temp = 1.0; number = -1; n_passos = len(files); n_exclusion = 0
#-------------------------
for i in range(len(files)):
    #----------------------
    number += 1
    porc = (number/n_passos)*100        
    #---------------------------
    if (porc >= temp and porc <= 100):
       print(f'Analyzed  {porc:>3,.0f}%')                 
       number += 1
       if (number == 1): temp = 1
       if (number == 2): temp = 5
       if (number >= 3): temp = temp + 5
    
    structure = Poscar.from_file(diret2 + files[i]).structure            # Lendo o arquivo POSCAR
    matcher = StructureMatcher()                                         # Criando um objeto StructureMatcher  
    reduced_structure = matcher._get_reduced_structure(structure)        # Obtendo a correspondente célula unitária reduzida
    Poscar(reduced_structure).write_file(diret2 + 'temp_' + str(i+1) + '.vasp')

    poscar1 = open(diret2 + files[i], "r")
    poscar2 = open(diret2 +  'temp_' + str(i+1) + '.vasp', "r")

    nion1 = 0; nion2 = 0
    #-------------------
    for ii in range(7):
        VTemp1 = poscar1.readline().split()
        VTemp2 = poscar2.readline().split()
    for j in range(len(VTemp1)): nion1 += int(VTemp1[j])
    for j in range(len(VTemp2)): nion2 += int(VTemp2[j])
    poscar1.close()
    poscar2.close()
    #---------------------------------------------------
    if (nion2 < nion1):
       os.remove(diret2 + files[i])
       n_exclusion += 1

for i in range(len(files)):
    os.remove(diret2 + 'temp_' + str(i+1) + '.vasp')

#========================================================
print(f'--------------------------------------')
print(f'{n_exclusion} células foram filtradas/excluidas')
#========================================================


#=====================================================================           # Verificar com cuidado este procedimento ???????????????????????????????????????????????????????
# Filtrando/Excluindo arquivos POSCAR semelhantes: ===================           # Verificar com cuidado este procedimento ???????????????????????????????????????????????????????
#=====================================================================           # Verificar com cuidado este procedimento ???????????????????????????????????????????????????????

#--------
pause = 0
n_loop = 0
#-----------------
while (pause < 2):
    #--------------       
    n_exclusion = 0
    n_loop += 1
    #----------

    print(f' ')
    print(f'========================================')
    print(f'Passo {6 +n_loop +n}: Excluindo Redes semelhantes')
    print(f'========================================')

    files = os.listdir(diret2)
    files_delete = []

    #---------------------------------------------
    temp = 1.0; number = -1; n_passos = len(files)
    #--------------------------
    for i in range(len(files)):
        #---------------------------
        number += 1
        porc = (number/n_passos)*100        
        #---------------------------
        if (porc >= temp and porc <= 100):
           print(f'Analyzed  {porc:>3,.0f}%')           
           number += 1
           if (number == 1): temp = 1
           if (number == 2): temp = 5
           if (number >= 3): temp = temp + 5
 
           if os.path.exists(diret2 + '/' + files[i]):
              #---------------------------------------------------------------
              structure1 = Poscar.from_file(diret2 + '/' + files[i]).structure
              #---------------------------------------------------------------
              poscar = open(diret2 + '/' + files[i], "r")
              VTemp = poscar.readline().split()
              if (n_Lattice == 2): Angle_AB1 = float(VTemp[11])
              if (n_Lattice == 3): Angle_AB1 = float(VTemp[12]) 
              param = poscar.readline(); param = float(param)
              VTemp = poscar.readline().split();  Ax = float(VTemp[0])*param; Ay = float(VTemp[1])*param;  A = np.array([Ax, Ay]);  mA = np.linalg.norm(A)
              VTemp = poscar.readline().split();  Bx = float(VTemp[0])*param; By = float(VTemp[1])*param;  B = np.array([Bx, By]);  mB = np.linalg.norm(B)
              dAB1 = abs(mA - mB)
              poscar.close()
              #---------------------------------------------------------------

              for j in range(len(files)):
                  if (i != j):
                     #------------------------------------------
                     if os.path.exists(diret2 + '/' + files[j]):
                        #---------------------------------------------------------------
                        structure2 = Poscar.from_file(diret2 + '/' + files[j]).structure
                        #---------------------------------------------------------------
                        matcher = StructureMatcher()                   # Criando um objeto StructureMatcher
                        if matcher.fit(structure1, structure2):        # Verificando se as estruturas são similares
                           #----------------------------------------------------------------------------------------
                           poscar = open(diret2 + '/' + files[j], "r")
                           VTemp = poscar.readline().split()
                           if (n_Lattice == 2): Angle_AB2 = float(VTemp[11])
                           if (n_Lattice == 3): Angle_AB2 = float(VTemp[12]) 
                           param = poscar.readline(); param = float(param)
                           VTemp = poscar.readline().split();  Ax = float(VTemp[0])*param; Ay = float(VTemp[1])*param;  A = np.array([Ax, Ay]);  mA = np.linalg.norm(A)
                           VTemp = poscar.readline().split();  Bx = float(VTemp[0])*param; By = float(VTemp[1])*param;  B = np.array([Bx, By]);  mB = np.linalg.norm(B)
                           dAB2 = abs(mA - mB)
                           poscar.close()
                           #-----------------
                           if (dAB1 < dAB2):
                              os.remove(diret2 + '/' + files[j])
                              n_exclusion += 1 
                           #------------------
                           if (dAB1 > dAB2):
                              if os.path.exists(diret2 + '/' + files[i]):
                                 os.remove(diret2 + '/' + files[i])
                                 n_exclusion += 1
                           #---------------------
                           if (dAB1 == dAB2):
                              if (abs(Angle_AB1) < abs(Angle_AB2)):
                                 os.remove(diret2 + '/' + files[j])
                                 n_exclusion += 1 
                              if (abs(Angle_AB1) > abs(Angle_AB2)):
                                 if os.path.exists(diret2 + '/' + files[i]):
                                    os.remove(diret2 + '/' + files[i])
                                    n_exclusion += 1
                              if (abs(Angle_AB1) == abs(Angle_AB2)):
                                 if (Angle_AB1 >= Angle_AB2):
                                    os.remove(diret2 + '/' + files[j])
                                    n_exclusion += 1 
                                 if (Angle_AB1 < Angle_AB2):
                                    if os.path.exists(diret2 + '/' + files[i]):
                                       os.remove(diret2 + '/' + files[i])
                                       n_exclusion += 1

    #========================================================
    print(f'-------------------------------------')
    print(f'{n_exclusion} células foram filtradas/excluidas')
    if (n_exclusion == 0): pause += 1
    #========================================================


#=====================================================================
# Renomeando os arquivos POSCAR para maior organização dos dados: ====
#=====================================================================

#-------------------------
files = os.listdir(diret2)
#--------------------------
for i in range(len(files)):

    #------------------------------------------
    poscar = open(diret2 + '/' + files[i], "r")
    #------------------------------------------ 
    VTemp = poscar.readline().split()
    if (n_Lattice == 2):
       #-------------------------------------------------
       mismatch_temp = VTemp[7].replace('_', ' ').split()
       mismatch_12 = 0
       for j in range(len(mismatch_temp)): mismatch_12 += float(mismatch_temp[j])
       mismatch_12 = mismatch_12/3;  mismatch_12 = round(mismatch_12, 4)
       #----------------------------------------------------------------
       angle_12 = str(VTemp[11])
    if (n_Lattice == 3):
       #-------------------------------------------------
       mismatch_temp = VTemp[8].replace('_', ' ').split()
       mismatch_12 = 0
       for j in range(len(mismatch_temp)): mismatch_12 += float(mismatch_temp[j])
       mismatch_12 = mismatch_12/3;  mismatch_12 = round(mismatch_12, 4)
       #------------------------
       angle_12 = str(VTemp[12])
       #-------------------------------------------------
       mismatch_temp = VTemp[16].replace('_', ' ').split()
       mismatch_13 = 0
       for j in range(len(mismatch_temp)): mismatch_13 += float(mismatch_temp[j])
       mismatch_13 = mismatch_13/3;  mismatch_13 = round(mismatch_13, 4)
       #----------------------------------------------------------------
       angle_13 = str(VTemp[20])
    #---------------------------
    VTemp1 = VTemp[-1].split()
    #-------------------------

    #-------------------------------------------------------
    VTemp = poscar.readline()
    param = float(VTemp)
    #-------------------------------------------------------
    A = poscar.readline().split()
    B = poscar.readline().split()

    for ii in range(3): VTemp = poscar.readline().split()
    nion = 0
    for j in range(len(VTemp)):  nion += int(VTemp[j])
    if (nion < 10):                  n_ion = '00' + str(nion) + 'atoms'
    if (nion >= 10 and nion < 100):  n_ion = '0'  + str(nion) + 'atoms'
    if (nion >= 100):                n_ion = ''   + str(nion) + 'atoms'
    #------------------------------------------------------------------
    poscar.close()
    #-------------

    #-------------------------------------------------------------
    if ((i+1) < 10):                     number = '000' + str(i+1)
    if ((i+1) >= 10  and (i+1) < 100):   number = '00'  + str(i+1)
    if ((i+1) >= 100 and (i+1) < 1000):  number = '0'   + str(i+1)
    if ((i+1) >= 1000):                  number = ''    + str(i+1) 
    #-------------------------------------------------------------

    #-------------------------------------
    current_name = diret2 + '/' + files[i]
    if (n_Lattice == 2):
       new_name = diret2 + '/' +  n_ion + '_' + str(mismatch_12) + '_' + angle_12 + '_' + str(VTemp1[-1]) + '+' + number
    if (n_Lattice == 3):
       new_name = diret2 + '/' +  n_ion + '_' + str(mismatch_12) + '_' + angle_12 + '_'  + str(mismatch_13) + '_' + angle_13 + '_'+ str(VTemp1[-1]) + '+' + number + '.vasp'
    os.rename(current_name, new_name)
    #--------------------------------

    #---------------------------
    poscar = open(new_name, "r")
    VTemp = poscar.readline().split()
    poscar.close()
    #-------------
    t_VTemp = ''
    for ii in range(len(VTemp) -1):
        t_VTemp += str(VTemp[ii]) + ' '
    if (n_Lattice > 1): 
       for ii in range(n_Lattice): t_VTemp += id_materials[ii] + ' ' 
    t_VTemp += str(VTemp[len(VTemp)-1])
    #=-------------------------------------------------------
    with open(new_name, 'r') as file: line = file.readlines()
    line[0] = t_VTemp + '+' + number + '\n'
    with open(new_name, 'w') as file: file.writelines(line)
    #------------------------------------------------------


#------------------------
files = os.listdir(diret2)
n_structures = len(files)
#------------------------
print(f' ')
print(f'============================================')
if (n_structures == 1): print(f'Concluido: {n_structures} célula foi encontrada')
if (n_structures >  1): print(f'Concluido: {n_structures} células foram encontradas')
print(f'============================================')
print(f' ')


#------------------------------------------------------------------------
# Chek List da(s) Heteroestrutura(s) gerada(s) --------------------------
#------------------------------------------------------------------------
if os.path.exists(dir_files + '/' + dir_o + '/check_list_ht.txt'): 0 == 0
else:
   check_list = open(dir_files + '/' + dir_o + '/check_list_ht.txt', 'w')
   check_list.close()
#----------------------------------------------------------------------
check_list = open(dir_files + '/' + dir_o + '/check_list_ht.txt', 'a')
Lattice1 = Lattice1.replace('.vasp', ' ');  Lattice2 = Lattice2.replace('.vasp', ' ')   
if (n_Lattice == 2):
   check_list.write(f'{Lattice1} {Lattice2}')
if (n_Lattice == 3):
   Lattice3 = Lattice3.replace('.vasp', ' ')
   check_list.write(f'{Lattice1} {Lattice2} {Lattice3}')
check_list.close()
#-----------------
