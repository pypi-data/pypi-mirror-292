#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 15:37:53 2024

@author: diegomorencos
"""

import numpy as np
from scipy.sparse import csr_matrix

def massref1D(m): # Funcion que calcula las matrices en el elemento de ref
 if m==1:
        phi0 = lambda x: 0.5 * (1 - x)
        phi1 = lambda x: 0.5 * (1 + x)

        # Utilizo Cuadratura de Gauss Legendre (G-L)
        xgi = np.array([-np.sqrt(3)/3, np.sqrt(3)/3])
        wi = np.array([1, 1])

        Mg = np.zeros((2, 2))

        phi0i = phi0(xgi)
        phi1i = phi1(xgi)

        Mg[0, 0] = np.sum(wi * phi0i * phi0i)
        Mg[1, 1] = np.sum(wi * phi1i * phi1i)
        Mg[0, 1] = np.sum(wi * phi0i * phi1i)
        Mg[1, 0] = np.sum(wi * phi1i * phi0i)

        dphi0 = lambda x: -0.5
        dphi1 = lambda x: 0.5

        Rg = np.zeros((2, 2))

        dphi0i = dphi0(xgi)
        dphi1i = dphi1(xgi)

        Rg[0, 0] = np.sum(wi * dphi0i * dphi0i)
        Rg[1, 1] = np.sum(wi * dphi1i * dphi1i)
        Rg[0, 1] = np.sum(wi * dphi0i * dphi1i)
        Rg[1, 0] = np.sum(wi * dphi1i * dphi0i)
 else :
        def phi0(x):
            return -0.5 * (1 - np.array(x)) * np.array(x)

        def phi1(x):
            return (1 - np.array(x)*np.array(x)) 

        def phi2(x):
            return 0.5 * (1 + np.array(x)) * np.array(x)

        xgi = [-np.sqrt(3/5), 0, np.sqrt(3/5)]
        wi = [5/9, 8/9, 5/9]

        Mg = np.zeros((3, 3))

        phi0i = phi0(xgi)
        phi1i = phi1(xgi)
        phi2i = phi2(xgi)

        Mg[0, 0] = np.sum(wi * phi0i * phi0i)
        Mg[1, 1] = np.sum(wi * phi1i * phi1i)
        Mg[2, 2] = np.sum(wi * phi2i * phi2i)
        Mg[0, 1] = np.sum(wi * phi0i * phi1i)
        Mg[0, 2] = np.sum(wi * phi0i * phi2i)
        Mg[1, 0] = np.sum(wi * phi1i * phi0i)
        Mg[2, 0] = np.sum(wi * phi0i * phi2i)
        Mg[1, 2] = np.sum(wi * phi1i * phi2i)
        Mg[2, 1] = np.sum(wi * phi1i * phi2i)
        
        def dphi0(x):
            return 0.5 * (2 * np.array(x)-1)
        def dphi1(x):
            return -2 * np.array(x)

        def dphi2(x):
            return 0.5 * (2 * np.array(x)+1)

        Rg = np.zeros((3, 3))

        dphi0i = dphi0(xgi)
        dphi1i = dphi1(xgi)
        dphi2i = dphi2(xgi)

        Rg[0, 0] = np.sum(wi * dphi0i * dphi0i)
        Rg[1, 1] = np.sum(wi * dphi1i * dphi1i)
        Rg[2, 2] = np.sum(wi * dphi2i * dphi2i)
        Rg[0, 1] = np.sum(wi * dphi0i * dphi1i)
        Rg[1, 0] = np.sum(wi * dphi1i * dphi0i)
        Rg[0, 2] = np.sum(wi * dphi0i * dphi2i)
        Rg[2, 0] = np.sum(wi * dphi0i * dphi2i)
        Rg[1, 2] = np.sum(wi * dphi1i * dphi2i)
        Rg[2, 1] = np.sum(wi * dphi1i * dphi2i)
         
 return Mg, Rg

def kmglobal1D(xi,Ne,Nn,m):  
    Mg, Rg = massref1D(m)  # Asumo que matrizdemasaselementoref() devuelve Mg y Rg

    M = csr_matrix((len(xi), len(xi)))
    R = M.copy()
  
    if m == 1:
        for i in range(Ne):
            hi = xi[i + 1] - xi[i]
            M[i:i+2, i:i+2] += hi * 0.5 * Mg
            R[i:i+2, i:i+2] += 2 / hi * Rg
    else:
        for i in range(0, Nn - m + 1, 2):
            hi = xi[i + 2] - xi[i]
            M[i:i+3, i:i+3] += hi * Mg * 0.5
            R[i:i+3, i:i+3] += 2 / hi * Rg
    return M, R

def massrefT2D(m): 
    if m == 1:
        
        # Declaracion de variables
        
        Mg = np.zeros((3, 3))
        
        # Funciones de forma
        
        phi0 = lambda x, y: 1 - x - y
        phi1 = lambda x, y: x
        phi2 = lambda x, y: y
        
        # Cuadratura G-L

        xgi = np.array([[1/2, 0], [1/2, 1/2], [0, 1/2]])
        wi = np.array([1/6, 1/6,1/6])

        # Evaluacion de las funciones de forma en los puntos de integracion de G-L
        
        phi0i = phi0(xgi[:, 0], xgi[:, 1])
        phi1i = phi1(xgi[:, 0], xgi[:, 1])
        phi2i = phi2(xgi[:, 0], xgi[:, 1])

        # Calculo de la matriz de masas de referencia

        Mg[0, 0] = np.sum(wi * phi0i * phi0i)
        Mg[1, 1] = np.sum(wi * phi1i * phi1i)
        Mg[2, 2] = np.sum(wi * phi2i * phi2i)
        Mg[0, 1] = Mg[1, 0] = np.sum(wi * phi0i * phi1i)
        Mg[0, 2] = Mg[2, 0] = np.sum(wi * phi0i * phi2i)
        Mg[1, 2] = Mg[2, 1] = np.sum(wi * phi1i * phi2i)
        
        
    if m == 2:
        
        # Declaracion de las funciones de forma 
        
        Mg = np.zeros((6, 6))
        
        
        phi0 = lambda x, y: (1 - x - y)*(1-2*x-2*y)
        phi1 = lambda x, y: x*(2*x-1)
        phi2 = lambda x, y: y*(2*y-1)
        phi3 = lambda x, y: (1 - x - y)*4*x
        phi4 = lambda x, y: 4*x*y
        phi5 = lambda x, y: (1 - x - y)*4*y
        
        # Cuadratura G-L
        

        xgi = np.array([[0.445948490915965, 0.445948490915965], [0.445948490915965,0.108103018168070], [0.108103018168070, 0.445948490915965], [0.091576213509771, 0.091576213509771],[0.091576213509771, 0.816847572980459],[0.816847572980459, 0.091576213509771]])
        wi = np.array([0.1116907948,0.1116907948,0.1116907948,0.05497587183,0.05497587183,0.05497587183])

        # Evaluacion de las funciones en los puntos de integracion de G-L
        
        phi0i = phi0(xgi[:, 0], xgi[:, 1])
        phi1i = phi1(xgi[:, 0], xgi[:, 1])
        phi2i = phi2(xgi[:, 0], xgi[:, 1])
        phi3i = phi3(xgi[:, 0], xgi[:, 1])
        phi4i = phi4(xgi[:, 0], xgi[:, 1])
        phi5i = phi5(xgi[:, 0], xgi[:, 1])

        
        
        Mg[0, 0] = np.sum(wi * phi0i * phi0i)       
        Mg[1, 1] = np.sum(wi * phi1i * phi1i)
        Mg[2, 2] = np.sum(wi * phi2i * phi2i)
        Mg[3, 3] = np.sum(wi * phi3i * phi3i)
        Mg[4, 4] = np.sum(wi * phi4i * phi4i)
        Mg[5, 5] = np.sum(wi * phi5i * phi5i)
        Mg[0, 1] = Mg[1, 0] = np.sum(wi * phi0i * phi1i)
        Mg[0, 2] = Mg[2, 0] = np.sum(wi * phi0i * phi2i)
        Mg[0, 3] = Mg[3, 0] = np.sum(wi * phi0i * phi3i)
        Mg[0, 4] = Mg[4, 0] = np.sum(wi * phi0i * phi4i)
        Mg[0, 5] = Mg[5, 0] = np.sum(wi * phi0i * phi5i)
        Mg[1, 2] = Mg[2, 1] = np.sum(wi * phi1i * phi2i)
        Mg[1, 3] = Mg[3, 1] = np.sum(wi * phi1i * phi3i)
        Mg[1, 4] = Mg[4, 1] = np.sum(wi * phi1i * phi4i)
        Mg[1, 5] = Mg[5, 1] = np.sum(wi * phi1i * phi5i)
        Mg[2, 3] = Mg[3, 2] = np.sum(wi * phi2i * phi3i)
        Mg[2, 4] = Mg[4, 2] = np.sum(wi * phi2i * phi4i)
        Mg[2, 5] = Mg[5, 2] = np.sum(wi * phi2i * phi5i)
        Mg[3, 4] = Mg[4, 3] = np.sum(wi * phi3i * phi4i)
        Mg[3, 5] = Mg[5, 3] = np.sum(wi * phi3i * phi5i)
        Mg[4, 5] = Mg[5, 4] = np.sum(wi * phi4i * phi5i)

    return Mg
def kmglobal2D(m,p,t,p1,t1):  
    
    Mg = massrefT2D(m)

    if m == 1:
           
           ## CONSTRUCCION MATRICES Y DECLARACION DE VARIABLES ##
           
           # Ubicacion de los nodos a transformar
           
           xi=p[0,:]
           yi=p[1,:]
           
           # Generacion de las matrices
           
           Rg=np.zeros((3,3))
           M = csr_matrix((len(xi), len(yi)))
           R = csr_matrix((len(xi), len(yi)))
           
           elem = t[0:3, :].T  
           Ne = elem.shape[0]
           
           # Cuadratura a emplear
           
           xgi = np.array([[1/2, 0], [1/2, 1/2], [0, 1/2]])
           wi = np.array([1/6, 1/6,1/6])
           
            ## DERIVADAS DE LAS FUNCIONES DE FORMA
           
            # Declaracion de las funciones de manera simbolica
           
           dphi0_x = lambda x,y: -1
           dphi0_y = lambda x,y: -1
           dphi1_x = lambda x,y: 1
           dphi1_y = lambda x,y: 0
           dphi2_x = lambda x,y: 0
           dphi2_y = lambda x,y: 1
           
           # Evaluacion de las funciones en los puntos de la cuadratura
           
           dphi0_x = dphi0_x(xgi[:, 0], xgi[:, 1])
           dphi0_y  = dphi0_y(xgi[:, 0], xgi[:, 1])
           dphi1_x  = dphi1_x(xgi[:, 0], xgi[:, 1])
           dphi1_y  = dphi1_y(xgi[:, 0], xgi[:, 1])
           dphi2_x  = dphi2_x(xgi[:, 0], xgi[:, 1])
           dphi2_y  = dphi2_y(xgi[:, 0], xgi[:, 1])
           
           # Calculo de la matriz Ai
           
           for i in range(Ne):
               
               X1 = p[:, elem[i, 0]-1]  # vertice 1 de cada elemento
               X2 = p[:, elem[i, 1]-1]  # vertice 2 de cada elemento
               X3 = p[:, elem[i, 2]-1]  # vertice 3 de cada elemento
               
               
               # Transformacion triangulos
               
               Ai = np.column_stack((X2 - X1, X3 - X1))
               #print(Ai)
               det_Ai = np.linalg.det(Ai)
               
               areaT=0.5*abs(det_Ai)

               indices = t[0:3, i] - 1
               
               # Ensamblamiento de la matriz de masas global

               fila_indices, col_indices = np.meshgrid(indices, indices, indexing='ij')
               M[fila_indices, col_indices] += 2 * areaT * Mg 
               
               ## Calculo de los gradientes ##
               
               Ai_inv=np.linalg.inv(Ai)
               
               d0jx = lambda x,y: Ai_inv[0,0]*dphi0_x+Ai_inv[1,0]*dphi0_y
               d0jy = lambda x,y:Ai_inv[0,1]*dphi0_x+Ai_inv[1,1]*dphi0_y
               
               d1jx = lambda x,y:Ai_inv[0,0]*dphi1_x+Ai_inv[1,0]*dphi1_y
               d1jy = lambda x,y:Ai_inv[0,1]*dphi1_x+Ai_inv[1,1]*dphi1_y
               
               d2jx = lambda x,y:Ai_inv[0,0]*dphi2_x+Ai_inv[1,0]*dphi2_y
               d2jy = lambda x,y:Ai_inv[0,1]*dphi2_x+Ai_inv[1,1]*dphi2_y
               
               # Evaluacion de las derivadas
               
               d0jx = d0jx(xgi[:, 0], xgi[:, 1])
               d0jy = d0jy(xgi[:, 0], xgi[:, 1])
               
               d1jx = d1jx(xgi[:, 0], xgi[:, 1])
               d1jy = d1jy(xgi[:, 0], xgi[:, 1])
               
               d2jx = d2jx(xgi[:, 0], xgi[:, 1])
               d2jy = d2jy(xgi[:, 0], xgi[:, 1])
               
               # Declaracion de los gradientes
               
               grad0 = np.zeros((2, 1))
               grad1 = np.zeros((2, 1))
               grad2 = np.zeros((2, 1))
               
               # Relleno de los gradientes
               
               grad0[0, 0] = d0jx
               grad0[1, 0] = d0jy
               
               grad1[0, 0] = d1jx
               grad1[1, 0] = d1jy
               
               grad2[0, 0] = d2jx
               grad2[1, 0] = d2jy
               
               
               # Generacion de la matriz de rigidez de referencia
               
               v=np.dot(grad0.T, grad0) # producto escalar de los gradientes
               Rg[0, 0] = np.sum(wi*v)  # integracion numerica aplicando cuadratura G-L
               
               v=np.dot(grad1.T, grad1)
               Rg[1, 1] = np.sum(wi*v)
               
               v=np.dot(grad2.T, grad2)
               Rg[2, 2] = np.sum(wi*v)
               
               v=np.dot(grad0.T, grad1)
               Rg[0, 1] = np.sum(wi*v)
               
               v=np.dot(grad0.T, grad2)
               Rg[0, 2] = np.sum(wi*v)
               
               v=np.dot(grad1.T, grad2)
               Rg[1, 2] = np.sum(wi*v)
               
               v=np.dot(grad1.T, grad0)
               Rg[1, 0] = np.sum(wi*v)
               
               v=np.dot(grad2.T, grad0)
               Rg[2, 0] = np.sum(wi*v)
               
               v=np.dot(grad2.T, grad1)
               Rg[2, 1] = np.sum(wi*v)
               
               # Ensamblamiento de la matriz de rigidez global
               
               indices = t[0:3, i] - 1
               
               fila_indices, col_indices = np.meshgrid(indices, indices, indexing='ij')
               R[fila_indices, col_indices] += 2 * Rg * areaT

               
    if m == 2:
        
        # Declaracion variables
        
         xi=p1[0,:]
         yi=p1[1,:]
         
         elem1 = t1[0:6, :].T 
         

         M = csr_matrix((len(xi), len(yi)))
         R = csr_matrix((len(xi), len(yi))) 

         Ne=elem1.shape[0]
         
         # Cuadratura G-L
         
         xgi = np.array([[0.445948490915965, 0.445948490915965], [0.445948490915965,0.108103018168070], [0.108103018168070, 0.445948490915965], [0.091576213509771, 0.091576213509771],[0.091576213509771, 0.816847572980459],[0.816847572980459, 0.091576213509771]])
         wi = np.array([0.1116907948,0.1116907948,0.1116907948,0.05497587183,0.05497587183,0.05497587183])
         
         # Derivadas de las funciones base
         
         dphi0_x = lambda x,y: 4*x+4*y-3
         dphi0_y = lambda x,y: 4*x+4*y-3
         
         dphi1_x = lambda x,y: 4*x-1
         dphi1_y = lambda x,y: 0
         
         dphi2_x = lambda x,y: 0
         dphi2_y = lambda x,y: 4*y-1
         
         dphi3_x = lambda x,y: 4-8*x-4*y
         dphi3_y = lambda x,y: -4*x
         
         dphi4_x = lambda x,y: 4*y
         dphi4_y = lambda x,y: 4*x
         
         dphi5_x = lambda x,y: -4*y
         dphi5_y = lambda x,y: 4-8*y-4*x
         
         # Evaluacion en los puntos de integracion
         
         dphi0_x  = dphi0_x(xgi[:, 0], xgi[:, 1])
         dphi0_y  = dphi0_y(xgi[:, 0], xgi[:, 1])
         
         dphi1_x  = dphi1_x(xgi[:, 0], xgi[:, 1])
         dphi1_y  = dphi1_y(xgi[:, 0], xgi[:, 1])
         
         dphi2_x  = dphi2_x(xgi[:, 0], xgi[:, 1])
         dphi2_y  = dphi2_y(xgi[:, 0], xgi[:, 1])
         
         dphi3_x  = dphi3_x(xgi[:, 0], xgi[:, 1])
         dphi3_y  = dphi3_y(xgi[:, 0], xgi[:, 1])
         
         dphi4_x  = dphi4_x(xgi[:, 0], xgi[:, 1])
         dphi4_y  = dphi4_y(xgi[:, 0], xgi[:, 1])
         
         dphi5_x  = dphi5_x(xgi[:, 0], xgi[:, 1])
         dphi5_y  = dphi5_y(xgi[:, 0], xgi[:, 1])
         
         # Calculo de la matriz Ai

         for i in range(Ne):
 
             
             X1 = p1[:, elem1[i, 0]-1]  # vertice 1 de cada elemento
             X2 = p1[:, elem1[i, 1]-1]
             X3 = p1[:, elem1[i, 2]-1] 
             
             Ai = np.column_stack((X2 - X1, X3 - X1))
             
             det_Ai = np.linalg.det(Ai)
             
             areaT=0.5*abs(det_Ai)
             
             indices = t1[0:6, i]-1
             
             # Ensamblamiento de la matriz M
             
             fila_indices, col_indices = np.meshgrid(indices, indices, indexing='ij')
             M[fila_indices, col_indices] += 2 * areaT * Mg
             
             
             Ai_inv=np.linalg.inv(Ai)
             
             # Calculo de las derivadas
             
             d0jx = lambda x,y:Ai_inv[0,0]*dphi0_x+Ai_inv[1,0]*dphi0_y
             d0jy = lambda x,y:Ai_inv[0,1]*dphi0_x+Ai_inv[1,1]*dphi0_y
             d1jx = lambda x,y:Ai_inv[0,0]*dphi1_x+Ai_inv[1,0]*dphi1_y
             d1jy = lambda x,y:Ai_inv[0,1]*dphi1_x+Ai_inv[1,1]*dphi1_y
             d2jx = lambda x,y:Ai_inv[0,0]*dphi2_x+Ai_inv[1,0]*dphi2_y
             d2jy = lambda x,y:Ai_inv[0,1]*dphi2_x+Ai_inv[1,1]*dphi2_y
             d3jx = lambda x,y:Ai_inv[0,0]*dphi3_x+Ai_inv[1,0]*dphi3_y
             d3jy = lambda x,y:Ai_inv[0,1]*dphi3_x+Ai_inv[1,1]*dphi3_y
             d4jx = lambda x,y:Ai_inv[0,0]*dphi4_x+Ai_inv[1,0]*dphi4_y
             d4jy = lambda x,y:Ai_inv[0,1]*dphi4_x+Ai_inv[1,1]*dphi4_y
             d5jx = lambda x,y:Ai_inv[0,0]*dphi5_x+Ai_inv[1,0]*dphi5_y
             d5jy = lambda x,y:Ai_inv[0,1]*dphi5_x+Ai_inv[1,1]*dphi5_y
             
             #Evaluacion de las derivadas en los puntos de integracion
               
             d0jx = d0jx(xgi[:, 0], xgi[:, 1])
             d0jy = d0jy(xgi[:, 0], xgi[:, 1])
             
             d1jx = d1jx(xgi[:, 0], xgi[:, 1])
             d1jy = d1jy(xgi[:, 0], xgi[:, 1])
             
             d2jx = d2jx(xgi[:, 0], xgi[:, 1])
             d2jy = d2jy(xgi[:, 0], xgi[:, 1])
             
             d3jx = d3jx(xgi[:, 0], xgi[:, 1])
             d3jy = d3jy(xgi[:, 0], xgi[:, 1])
             
             d4jx = d4jx(xgi[:, 0], xgi[:, 1])
             d4jy = d4jy(xgi[:, 0], xgi[:, 1])
             
             d5jx = d5jx(xgi[:, 0], xgi[:, 1])
             d5jy = d5jy(xgi[:, 0], xgi[:, 1])
             
             # Generacion de los gradientes
             
             grad0 = np.zeros((2, 6))
             grad1 = np.zeros((2, 6))
             grad2 = np.zeros((2, 6))
             grad3 = np.zeros((2, 6))
             grad4 = np.zeros((2, 6))
             grad5 = np.zeros((2, 6))
               
             grad0[0, :] = d0jx
             grad0[1, :] = d0jy
             
             grad1[0, :] = d1jx
             grad1[1, :] = d1jy
             
             grad2[0, :] = d2jx
             grad2[1, :] = d2jy
             
             grad3[0, :] = d3jx
             grad3[1, :] = d3jy
             
             grad4[0, :] = d4jx
             grad4[1, :] = d4jy
             
             grad5[0, :] = d5jx
             grad5[1, :] = d5jy
               
               
             Rg=np.zeros((6,6))
             
             # Calculo matriz de Rigidez de referencia

             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad0[:, k], grad0[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[0, 0] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad1[:, k], grad1[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[1, 1] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad2[:, k], grad2[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[2, 2] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad3[:, k], grad3[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[3, 3] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad4[:, k], grad4[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[4, 4] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad5[:, k], grad5[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[5, 5] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad0[:, k], grad1[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[0, 1] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad1[:, k], grad0[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[1, 0] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad0[:, k], grad2[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[0, 2] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad2[:, k], grad0[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[2, 0] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad0[:, k], grad3[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[0, 3] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad3[:, k], grad0[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[3, 0] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad0[:, k], grad4[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[0, 4] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad4[:, k], grad0[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[4, 0] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad0[:, k], grad5[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[0, 5] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad5[:, k], grad0[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[5, 0] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad1[:, k], grad2[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[1, 2] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad2[:, k], grad1[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[2, 1] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad1[:, k], grad3[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[1, 3] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad3[:, k], grad1[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[3, 1] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad1[:, k], grad4[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[1, 4] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad4[:, k], grad1[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[4, 1] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad1[:, k], grad5[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[1, 5] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad5[:, k], grad1[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[5, 1] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad2[:, k], grad3[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[2, 3] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad3[:, k], grad2[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[3, 2] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad2[:, k], grad4[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[2, 4] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad4[:, k], grad2[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[4, 2] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad2[:, k], grad5[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[2, 5] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad5[:, k], grad2[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[5, 2] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad3[:, k], grad4[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[3, 4] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad4[:, k], grad3[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[4, 3] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad3[:, k], grad5[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[3, 5] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad5[:, k], grad3[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[5, 3] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad4[:, k], grad5[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[4, 5] = sum_results
             results=[]
             
             for k in range(6):
              dot_product = np.dot(grad5[:, k], grad4[:, k])
              result = dot_product * wi[k]
              results.append(result)
             sum_results = np.sum(results)
             Rg[5, 4] = sum_results
             results=[]
             
             # Ensamble de la matriz global de rigidez
             
             indices = t1[0:6, i] - 1
             
             fila_indices, col_indices = np.meshgrid(indices, indices, indexing='ij')
             R[fila_indices, col_indices] += 2 * Rg * areaT
             
  
    return M,R
def massC2D(m,p,t,p1,t1): 
    
    if m == 1:
        
        # Declaracion de variables
        
        xi=p[0,:]
        yi=p[1,:]
        
        elem = t[0:4, :].T  
        Ne = elem.shape[0]
        
        
        Mg = np.zeros((4, 4))
        
        # Funciones de forma
        
        phi0 = lambda x, y: (1 - x) * (1 - y) / 4
        phi1 = lambda x, y: (1 + x) * (1 - y) / 4
        phi2 = lambda x, y: (1 + x) * (1 + y) / 4
        phi3 = lambda x, y: (1 - x) * (1 + y) / 4
        
        # Cuadratura G-L

        xgi = np.array([[-1/np.sqrt(3), -1/np.sqrt(3)], [-1/np.sqrt(3), 1/np.sqrt(3)], [1/np.sqrt(3), -1/np.sqrt(3)],[1/np.sqrt(3), 1/np.sqrt(3)]])
        wi = np.array([1,1,1,1])

        # Derivadas de las funciones de forma
       
        dphi0_x = lambda x, y: -(1 - y) / 4
        dphi0_y = lambda x, y: -(1 - x) / 4
        
        dphi1_x = lambda x, y: (1 - y) / 4
        dphi1_y = lambda x, y: -(1 + x) / 4
        
        dphi2_x = lambda x, y: (1 + y) / 4
        dphi2_y = lambda x, y: (1 + x) / 4
        
        dphi3_x = lambda x, y: -(1 + y) / 4
        dphi3_y = lambda x, y: (1 - x) / 4
        
        # Evaluacion de las derivadas en los puntos de G-L
        
        dphi0i_x = dphi0_x(xgi[:, 0], xgi[:, 1])
        dphi0i_y = dphi0_y(xgi[:, 0], xgi[:, 1])
        
        dphi1i_x = dphi1_x(xgi[:, 0], xgi[:, 1])
        dphi1i_y = dphi1_y(xgi[:, 0], xgi[:, 1])
        
        
        dphi2i_x = dphi2_x(xgi[:, 0], xgi[:, 1])
        dphi2i_y = dphi2_y(xgi[:, 0], xgi[:, 1])
        
        dphi3i_x = dphi3_x(xgi[:, 0], xgi[:, 1])
        dphi3i_y = dphi3_y(xgi[:, 0], xgi[:, 1])
        
        # Matriz que contiene las derivadas evaluadas
        
        dphi_x = np.array([dphi0i_x, dphi1i_x, dphi2i_x, dphi3i_x])
        dphi_y = np.array([dphi0i_y, dphi1i_y, dphi2i_y, dphi3i_y])
        
        
        JFi = np.zeros((2,2))
        M = csr_matrix((len(xi), len(yi)))
        
        for i in range(Ne):
            
            X1 = p[:, elem[i, 0]-1]  # vertice 1 de cada elemento
            X2 = p[:, elem[i, 1]-1]  # vertice 2 de cada elemento
            X3 = p[:, elem[i, 2]-1]
            X4 = p[:, elem[i, 3]-1]
            
            # vectores con las coordendas x e y de los puntos
            
            xk=[X1[0],X2[0],X3[0],X4[0]]
            yk=[X1[1],X2[1],X3[1],X4[1]]
            
            Mg = np.zeros((4, 4))
            
            # Calculo del jacobiano
            
            for k in range(4):
                    
                xgi_x = dphi_x[:, k]
                result=np.dot(xk,xgi_x)
                JFi[0,0] = result
                
                xgi_y = dphi_y[:, k]
                result=np.dot(xk,xgi_y)
                JFi[0,1] = result
                
                result=np.dot(yk,xgi_x)
                JFi[1,0] = result
                
                result=np.dot(yk,xgi_y)
                JFi[1,1] = result
                
                det_JFi = np.linalg.det(JFi)
                det_JFi=abs(det_JFi)
                
                # Evaluacion de las funciones de forma 
                
                phi0i = phi0(xgi[k, 0], xgi[k, 1])
                phi1i = phi1(xgi[k, 0], xgi[k, 1])
                phi2i = phi2(xgi[k, 0], xgi[k, 1])
                phi3i = phi3(xgi[k, 0], xgi[k, 1])
                
                # Calculo matriz de masas de referencia
                
                v=np.dot(phi0i.T, phi0i)
                Mg[0, 0] += wi[k]*v*det_JFi
                
                v=np.dot(phi1i.T, phi1i)
                Mg[1, 1] += wi[k]*v*det_JFi
                
                v=np.dot(phi2i.T, phi2i)
                Mg[2, 2] += wi[k]*v*det_JFi
                
                v=np.dot(phi3i.T, phi3i)
                Mg[3, 3] += wi[k]*v*det_JFi
                
                v=np.dot(phi0i.T, phi1i)
                Mg[0, 1] += wi[k]*v*det_JFi 
                Mg[1,0] = Mg[0,1]
                
                v=np.dot(phi0i.T, phi2i)
                Mg[0, 2] += wi[k]*v*det_JFi
                Mg[2,0] = Mg[0,2]
                
                v=np.dot(phi0i.T, phi3i)
                Mg[0, 3] += wi[k]*v*det_JFi
                Mg[3,0] = Mg[0,3]
                
                v=np.dot(phi1i.T, phi2i)
                Mg[1, 2] += wi[k]*v*det_JFi
                Mg[2,1] = Mg[1,2]
                
                v=np.dot(phi1i.T, phi3i)
                Mg[1, 3] += wi[k]*v*det_JFi
                Mg[3,1] = Mg[1,3]
                
                v=np.dot(phi2i.T, phi3i)
                Mg[2, 3] += wi[k]*v*det_JFi
                Mg[3,2] = Mg[2,3]
                
            # Ensamblamiento matriz de masas
                
                
            indices = t[0:4, i] - 1
                
            fila_indices, col_indices = np.meshgrid(indices, indices, indexing='ij')
            M[fila_indices, col_indices] += Mg
            
        return M
        

    if m == 2:
        
        # Declaracion variables
        
        xi=p1[0,:]
        yi=p1[1,:]
        elem1 = t1[0:9, :].T 
        Ne = elem1.shape[0]
        
        # Declaracion funciones de forma
        
        phi0 = lambda x, y: 1/4 * (x - 1) * (y - 1) * x * y
        phi1 = lambda x, y: 1/4 * (x + 1) * (y - 1) * x * y
        phi2 = lambda x, y: 1/4 * (x + 1) * (y + 1) * x * y
        phi3 = lambda x, y: 1/4 * (x - 1) * (y + 1) * x * y
        phi4 = lambda x, y: 1/2 * (1 - x**2) * (y - 1) * y
        phi5 = lambda x, y: 1/2 * (x + 1) * (1 - y**2) * x
        phi6 = lambda x, y: 1/2 * (1 - x**2) * (y + 1) * y
        phi7 = lambda x, y: 1/2 * (x - 1) * (1 - y**2) * x
        phi8 = lambda x, y: (1 - x**2) * (1 - y**2)
        
        #Cuadratura G-L

        xgi = np.array([[-0.7745966692414834, -0.7745966692414834], [0.7745966692414834, -0.7745966692414834], [0.7745966692414834, 0.7745966692414834], [-0.7745966692414834, 0.7745966692414834],[0,-0.7745966692414834],[0.7745966692414834, 0],[0,0.7745966692414834],[-0.7745966692414834,0],[0,0]])
        wi = np.array([25/81,25/81,25/81,25/81,40/81,40/81,40/81,40/81,64/81])
        
        # Evaluacion en los puntos G-L

        phi0i = phi0(xgi[:, 0], xgi[:, 1])
        phi1i = phi1(xgi[:, 0], xgi[:, 1])
        phi2i = phi2(xgi[:, 0], xgi[:, 1])
        phi3i = phi3(xgi[:, 0], xgi[:, 1])
        phi4i = phi4(xgi[:, 0], xgi[:, 1])
        phi5i = phi5(xgi[:, 0], xgi[:, 1])
        phi6i = phi6(xgi[:, 0], xgi[:, 1])
        phi7i = phi7(xgi[:, 0], xgi[:, 1])
        phi8i = phi8(xgi[:, 0], xgi[:, 1])
        
        # Derivadas de las funciones de forma
               
        dphi0_x = lambda x, y: (2*x*y**2-2*x*y-y**2+y)*0.25
        dphi0_y = lambda x, y: x*(x-1)*(2*y-1)*0.25
        
        dphi1_x = lambda x, y: (2*x*y**2-2*x*y+y**2-y)*0.25
        dphi1_y = lambda x, y: x*(x+1)*(2*y-1)*0.25
        
        dphi2_x = lambda x, y: (2*x*y**2+2*x*y+y**2+y)*0.25
        dphi2_y = lambda x, y: x*(x+1)*(2*y+1)*0.25
        
        dphi3_x = lambda x, y: (2*x*y**2+2*x*y-y**2-y)*0.25
        dphi3_y = lambda x, y: x*(x-1)*(2*y+1)*0.25
        
        dphi4_x = lambda x, y: -x*y**2+x*y
        dphi4_y = lambda x, y: (1-x**2)*(2*y-1)*0.5
        
        dphi5_x = lambda x, y: x-x*y**2+((1-y**2)/2)
        dphi5_y = lambda x, y: -y*x*(x+1)
        
        dphi6_x = lambda x, y: -x*y**2-x*y
        dphi6_y = lambda x, y: (1-x**2)*(2*y+1)*0.5
        
        dphi7_x = lambda x, y: x-x*y**2+((-1+y**2)/2)
        dphi7_y = lambda x, y: -y*x*(x-1)
        
        dphi8_x = lambda x, y: -2*x*(1 - y**2)
        dphi8_y = lambda x, y: -2*y*(1 - x**2)
        
        # Evaluacion de las derivadas
        
        dphi0i_x = dphi0_x(xgi[:, 0], xgi[:, 1])
        dphi0i_y = dphi0_y(xgi[:, 0], xgi[:, 1])
        
        dphi1i_x = dphi1_x(xgi[:, 0], xgi[:, 1])
        dphi1i_y = dphi1_y(xgi[:, 0], xgi[:, 1])
        
        dphi2i_x = dphi2_x(xgi[:, 0], xgi[:, 1])
        dphi2i_y = dphi2_y(xgi[:, 0], xgi[:, 1])
        
        dphi3i_x = dphi3_x(xgi[:, 0], xgi[:, 1])
        dphi3i_y = dphi3_y(xgi[:, 0], xgi[:, 1])
        
        dphi4i_x = dphi4_x(xgi[:, 0], xgi[:, 1])
        dphi4i_y = dphi4_y(xgi[:, 0], xgi[:, 1])
        
        dphi5i_x = dphi5_x(xgi[:, 0], xgi[:, 1])
        dphi5i_y = dphi5_y(xgi[:, 0], xgi[:, 1])
        
        dphi6i_x = dphi6_x(xgi[:, 0], xgi[:, 1])
        dphi6i_y = dphi6_y(xgi[:, 0], xgi[:, 1])
        
        dphi7i_x = dphi7_x(xgi[:, 0], xgi[:, 1])
        dphi7i_y = dphi7_y(xgi[:, 0], xgi[:, 1])
        
        dphi8i_x = dphi8_x(xgi[:, 0], xgi[:, 1])
        dphi8i_y = dphi8_y(xgi[:, 0], xgi[:, 1])
        
        # Generacion de matrices con todas las derivadas

        dphi_x = np.array([dphi0i_x, dphi1i_x, dphi2i_x, dphi3i_x,dphi4i_x,dphi5i_x,dphi6i_x,dphi7i_x,dphi8i_x])
        dphi_y = np.array([dphi0i_y, dphi1i_y, dphi2i_y, dphi3i_y,dphi4i_y,dphi5i_y,dphi6i_y,dphi7i_y,dphi8i_y])
        
        
        
        Mg = np.zeros((9, 9))
        JFi = np.zeros((2,2))
        M = csr_matrix((len(xi), len(yi)))
        
        
        
        for i in range(Ne):
            
            
            X1 = p1[:, elem1[i, 0]-1]  # vertice 1 de cada elemento
            
            X2 = p1[:, elem1[i, 1]-1]  # vertice 2 de cada elemento
            
            X3 = p1[:, elem1[i, 2]-1]
            
            X4 = p1[:, elem1[i, 3]-1]
            
            X5 = p1[:, elem1[i, 4]-1]
            
            X6 = p1[:, elem1[i, 5]-1]
            
            X7 = p1[:, elem1[i, 6]-1]
            
            X8 = p1[:, elem1[i, 7]-1]
            
            X9 = p1[:, elem1[i, 8]-1]
            
            
            xk=[X1[0],X2[0],X3[0],X4[0],X5[0],X6[0],X7[0],X8[0],X9[0]]
            #print(xk)
            yk=[X1[1],X2[1],X3[1],X4[1],X5[1],X6[1],X7[1],X8[1],X9[1]]
            det_JFi = []
            
            # Calculo del jacobiano
            
            for k in range(9):
                #print(k)
                xgi_x = dphi_x[:, k]
                result=np.dot(xk,xgi_x)
                JFi[0,0] = result
                
                xgi_y = dphi_y[:, k]
                result=np.dot(xk,xgi_y)
                JFi[0,1] = result
                
                result=np.dot(yk,xgi_x)
                JFi[1,0] = result
                
                result=np.dot(yk,xgi_y)
                JFi[1,1] = result
                #print(JFi)

                det = np.linalg.det(JFi)
                det_JFi.append(det)
                
            # Calculo matriz de masas de referencia

            Mg[0, 0] = np.sum(wi * phi0i * phi0i*det_JFi)
            Mg[1, 1] = np.sum(wi * phi1i * phi1i*det_JFi)
            Mg[2, 2] = np.sum(wi * phi2i * phi2i*det_JFi)
            Mg[3, 3] = np.sum(wi * phi3i * phi3i*det_JFi)
            Mg[4, 4] = np.sum(wi * phi4i * phi4i*det_JFi)
            Mg[5, 5] = np.sum(wi * phi5i * phi5i*det_JFi)
            Mg[6, 6] = np.sum(wi * phi6i * phi6i*det_JFi)
            Mg[7, 7] = np.sum(wi * phi7i * phi7i*det_JFi)
            Mg[8, 8] = np.sum(wi * phi8i * phi8i*det_JFi)
            Mg[0, 1] = Mg[1, 0] = np.sum(wi * phi0i * phi1i*det_JFi)
            Mg[0, 2] = Mg[2, 0] = np.sum(wi * phi0i * phi2i*det_JFi)
            Mg[0, 3] = Mg[3, 0] = np.sum(wi * phi0i * phi3i*det_JFi)
            Mg[0, 4] = Mg[4, 0] = np.sum(wi * phi0i * phi4i*det_JFi)
            Mg[0, 5] = Mg[5, 0] = np.sum(wi * phi0i * phi5i*det_JFi)
            Mg[0, 6] = Mg[6, 0] = np.sum(wi * phi0i * phi6i*det_JFi)
            Mg[0, 7] = Mg[7, 0] = np.sum(wi * phi0i * phi7i*det_JFi)
            Mg[0, 8] = Mg[8, 0] = np.sum(wi * phi0i * phi8i*det_JFi)
            Mg[1, 2] = Mg[2, 1] = np.sum(wi * phi1i * phi2i*det_JFi)
            Mg[1, 3] = Mg[3, 1] = np.sum(wi * phi1i * phi3i*det_JFi)
            Mg[1, 4] = Mg[4, 1] = np.sum(wi * phi1i * phi4i*det_JFi)
            Mg[1, 5] = Mg[5, 1] = np.sum(wi * phi1i * phi5i*det_JFi)
            Mg[1, 6] = Mg[6, 1] = np.sum(wi * phi1i * phi6i*det_JFi)
            Mg[1, 7] = Mg[7, 1] = np.sum(wi * phi1i * phi7i*det_JFi)
            Mg[1, 8] = Mg[8, 1] = np.sum(wi * phi1i * phi8i*det_JFi)
            Mg[2, 3] = Mg[3, 2] = np.sum(wi * phi2i * phi3i*det_JFi)
            Mg[2, 4] = Mg[4, 2] = np.sum(wi * phi2i * phi4i*det_JFi)
            Mg[2, 5] = Mg[5, 2] = np.sum(wi * phi2i * phi5i*det_JFi)
            Mg[2, 6] = Mg[6, 2] = np.sum(wi * phi2i * phi6i*det_JFi)
            Mg[2, 7] = Mg[7, 2] = np.sum(wi * phi2i * phi7i*det_JFi)
            Mg[2, 8] = Mg[8, 2] = np.sum(wi * phi2i * phi8i*det_JFi)
            Mg[3, 4] = Mg[4, 3] = np.sum(wi * phi3i * phi4i*det_JFi)
            Mg[3, 5] = Mg[5, 3] = np.sum(wi * phi3i * phi5i*det_JFi)
            Mg[3, 6] = Mg[6, 3] = np.sum(wi * phi3i * phi6i*det_JFi)
            Mg[3, 7] = Mg[7, 3] = np.sum(wi * phi3i * phi7i*det_JFi)
            Mg[3, 8] = Mg[8, 3] = np.sum(wi * phi3i * phi8i*det_JFi)
            Mg[4, 5] = Mg[5, 4] = np.sum(wi * phi4i * phi5i*det_JFi)
            Mg[4, 6] = Mg[6, 4] = np.sum(wi * phi4i * phi6i*det_JFi)
            Mg[4, 7] = Mg[7, 4] = np.sum(wi * phi4i * phi7i*det_JFi)
            Mg[4, 8] = Mg[8, 4] = np.sum(wi * phi4i * phi8i*det_JFi)
            Mg[5, 6] = Mg[6, 5] = np.sum(wi * phi5i * phi6i*det_JFi)
            Mg[5, 7] = Mg[7, 5] = np.sum(wi * phi5i * phi7i*det_JFi)
            Mg[5, 8] = Mg[8, 5] = np.sum(wi * phi5i * phi8i*det_JFi)
            Mg[6, 7] = Mg[7, 6] = np.sum(wi * phi6i * phi7i*det_JFi)
            Mg[6, 8] = Mg[8, 6] = np.sum(wi * phi6i * phi8i*det_JFi)
            Mg[7, 8] = Mg[8, 7] = np.sum(wi * phi7i * phi8i*det_JFi)
        
            # Ensamblamiento matriz de masas
        
            indices = t1[0:9, i] - 1
        
            fila_indices, col_indices = np.meshgrid(indices, indices, indexing='ij')
            M[fila_indices, col_indices] += Mg

    return M
def kC2D(m,p,t,p1,t1):  
    

    if m == 1:
        
           # Generacion de variables
        
           xi=p[0,:]
           yi=p[1,:]
           
           Rg=np.zeros((3,3))
           
           R = csr_matrix((len(xi), len(yi)))
           
           elem = t[0:4, :].T  
           Ne = elem.shape[0]
           
           # Cuadratura G-L
           
           xgi = np.array([[-1/np.sqrt(3), -1/np.sqrt(3)], [-1/np.sqrt(3), 1/np.sqrt(3)], [1/np.sqrt(3), -1/np.sqrt(3)],[1/np.sqrt(3), 1/np.sqrt(3)]])
           wi = np.array([1,1,1,1])
           
           # Derivadas de las funciones de forma

           dphi0_x = lambda x, y: -(1 - y) / 4
           dphi0_y = lambda x, y: -(1 - x) / 4
           
           dphi1_x = lambda x, y: (1 - y) / 4
           dphi1_y = lambda x, y: -(1 + x) / 4
           
           dphi2_x = lambda x, y: (1 + y) / 4
           dphi2_y = lambda x, y: (1 + x) / 4
           
           dphi3_x = lambda x, y: -(1 + y) / 4
           dphi3_y = lambda x, y: (1 - x) / 4
           
           # Evaluacion de las derivadas
           
           dphi0i_x = dphi0_x(xgi[:, 0], xgi[:, 1])
           dphi0i_y = dphi0_y(xgi[:, 0], xgi[:, 1])

           dphi1i_x = dphi1_x(xgi[:, 0], xgi[:, 1])
           dphi1i_y = dphi1_y(xgi[:, 0], xgi[:, 1])
           
           dphi2i_x = dphi2_x(xgi[:, 0], xgi[:, 1])
           dphi2i_y = dphi2_y(xgi[:, 0], xgi[:, 1])
           
           dphi3i_x = dphi3_x(xgi[:, 0], xgi[:, 1])
           dphi3i_y = dphi3_y(xgi[:, 0], xgi[:, 1])
           
           dphi_x = np.array([dphi0i_x, dphi1i_x, dphi2i_x, dphi3i_x])
           dphi_y = np.array([dphi0i_y, dphi1i_y, dphi2i_y, dphi3i_y])
           

           for i in range(Ne):
               
               X1 = p[:, elem[i, 0]-1]  # vertice 1 de cada elemento
               X2 = p[:, elem[i, 1]-1]  # vertice 2 de cada elemento
               X3 = p[:, elem[i, 2]-1]
               X4 = p[:, elem[i, 3]-1]
               
               xk=[X1[0],X2[0],X3[0],X4[0]]
               yk=[X1[1],X2[1],X3[1],X4[1]]
               
               JFi = np.zeros((2,2))
               det_JFi = []
               Rg=np.zeros((4,4))
               
               # Calculo del jacobiano
               
               for k in range(4):
                   
                   xgi_x = dphi_x[:, k]
                   result=np.dot(xk,xgi_x)
                   JFi[0,0] = result
                   
                   xgi_y = dphi_y[:, k]
                   result=np.dot(xk,xgi_y)
                   JFi[0,1] = result
                   
                   result=np.dot(yk,xgi_x)
                   JFi[1,0] = result
                   
                   result=np.dot(yk,xgi_y)
                   JFi[1,1] = result
                   
                   det_JFi = np.linalg.det(JFi)
                   JFi_inv=np.linalg.inv(JFi)
                   
                   # Evaluacion de las funciones en el punto de integracion correspondiente
                   
                   dphi0i_x = dphi0_x(xgi[k, 0], xgi[k, 1])
                   dphi0i_y = dphi0_y(xgi[k, 0], xgi[k, 1])
                   
                   dphi1i_x = dphi1_x(xgi[k, 0], xgi[k, 1])
                   dphi1i_y = dphi1_y(xgi[k, 0], xgi[k, 1])
                   
                   dphi2i_x = dphi2_x(xgi[k,0], xgi[k, 1])
                   dphi2i_y = dphi2_y(xgi[k, 0], xgi[k, 1])
                   
                   dphi3i_x = dphi3_x(xgi[k, 0], xgi[k, 1])
                   dphi3i_y = dphi3_y(xgi[k, 0], xgi[k, 1])
                   
                   # Calculo de las derivadas
                   
                   d0jx = lambda x,y:JFi_inv[0,0]*dphi0i_x+JFi_inv[1,0]*dphi0i_y
                   d0jy = lambda x,y:JFi_inv[0,1]*dphi0i_x+JFi_inv[1,1]*dphi0i_y
                   
                   d1jx = lambda x,y:JFi_inv[0,0]*dphi1i_x+JFi_inv[1,0]*dphi1i_y
                   d1jy = lambda x,y:JFi_inv[0,1]*dphi1i_x+JFi_inv[1,1]*dphi1i_y
                   
                   d2jx = lambda x,y:JFi_inv[0,0]*dphi2i_x+JFi_inv[1,0]*dphi2i_y
                   d2jy = lambda x,y:JFi_inv[0,1]*dphi2i_x+JFi_inv[1,1]*dphi2i_y
                   
                   d3jx = lambda x,y:JFi_inv[0,0]*dphi3i_x+JFi_inv[1,0]*dphi3i_y
                   d3jy = lambda x,y:JFi_inv[0,1]*dphi3i_x+JFi_inv[1,1]*dphi3i_y
                   
                   # Evaluacion en el punto G-L correspondiente
                   
                   d0jx = d0jx(xgi[k, 0], xgi[k, 1])
                   d0jy = d0jy(xgi[k, 0], xgi[k, 1])
                   
                   d1jx = d1jx(xgi[k, 0], xgi[k, 1])
                   d1jy = d1jy(xgi[k, 0], xgi[k, 1])
                   
                   d2jx = d2jx(xgi[k, 0], xgi[k, 1])
                   d2jy = d2jy(xgi[k, 0], xgi[k, 1])
                   
                   d3jx = d3jx(xgi[k, 0], xgi[k, 1])
                   d3jy = d3jy(xgi[k, 0], xgi[k, 1])
               
                   grad0 = np.zeros((2, 1))
                   grad1 = np.zeros((2, 1))
                   grad2 = np.zeros((2, 1))
                   grad3 = np.zeros((2, 1))
               
                   grad0[0, 0] = d0jx
                   grad0[1, 0] = d0jy
                   
                   grad1[0, 0] = d1jx
                   grad1[1, 0] = d1jy
                   
                   grad2[0, 0] = d2jx
                   grad2[1, 0] = d2jy
                   
                   grad3[0, 0] = d3jx
                   grad3[1, 0] = d3jy
              
                   # Calculo matriz de rigidez de referencia
                   
                   v=np.dot(grad0.T, grad0)
                   Rg[0, 0] += wi[k]*v*det_JFi
                   
                   v=np.dot(grad1.T, grad1)
                   Rg[1, 1] += wi[k]*v*det_JFi
                   
                   v=np.dot(grad2.T, grad2)
                   Rg[2, 2] += wi[k]*v*det_JFi
                   
                   v=np.dot(grad3.T, grad3)
                   Rg[3, 3] += wi[k]*v*det_JFi
                   
                   v=np.dot(grad0.T, grad1)
                   Rg[0, 1] += wi[k]*v*det_JFi 
                   Rg[1,0] = Rg[0,1]
                   
                   v=np.dot(grad0.T, grad2)
                   Rg[0, 2] += wi[k]*v*det_JFi
                   Rg[2,0] = Rg[0,2]
                   
                   v=np.dot(grad0.T, grad3)
                   Rg[0, 3] += wi[k]*v*det_JFi
                   Rg[3,0] = Rg[0,3]
                   
                   v=np.dot(grad1.T, grad2)
                   Rg[1, 2] += wi[k]*v*det_JFi
                   Rg[2,1] = Rg[1,2]
                   
                   v=np.dot(grad1.T, grad3)
                   Rg[1, 3] += wi[k]*v*det_JFi
                   Rg[3,1] = Rg[1,3]
                   
                   v=np.dot(grad2.T, grad3)
                   Rg[2, 3] += wi[k]*v*det_JFi
                   Rg[3,2] = Rg[2,3]
                   
               # Ensamble matriz de rigidez global
                   
               indices = t[0:4, i] - 1
               fila_indices, col_indices = np.meshgrid(indices, indices, indexing='ij')
               R[fila_indices, col_indices] += Rg

               
    if m == 2:
        
        # Declaracion de variables 
         
         xi=p1[0,:]
         yi=p1[1,:]
         
         elem1 = t1[0:9, :].T 
         
         R = csr_matrix((len(xi), len(yi))) 
         
         Ne=elem1.shape[0]
         
         # Cuadratura G-L
         
         xgi = np.array([[-0.7745966692414834, -0.7745966692414834], [0.7745966692414834, -0.7745966692414834], [0.7745966692414834, 0.7745966692414834], [-0.7745966692414834, 0.7745966692414834],[0,-0.7745966692414834],[0.7745966692414834, 0],[0,0.7745966692414834],[-0.7745966692414834,0],[0,0]])
         wi = np.array([25/81,25/81,25/81,25/81,40/81,40/81,40/81,40/81,64/81])
         
         # Declaracion derivadas de las funciones de forma
         
         dphi0_x = lambda x, y: (y-1)*y*(2*x-1)*0.25
         dphi0_y = lambda x, y: (x-1)*x*(2*y-1)*0.25
         
         dphi1_x = lambda x, y: (y-1)*y*(2*x+1)*0.25
         dphi1_y = lambda x, y: (x+1)*x*(2*y-1)*0.25
         
         dphi2_x = lambda x, y: (y+1)*y*(2*x+1)*0.25
         dphi2_y = lambda x, y: (x+1)*x*(2*y+1)*0.25
         
         dphi3_x = lambda x, y: (y+1)*y*(2*x-1)*0.25
         dphi3_y = lambda x, y: (x-1)*x*(2*y+1)*0.25
         
         dphi4_x = lambda x, y: -(y-1)*y*x
         dphi4_y = lambda x, y: -(x**2-1)*(2*y-1)*0.5
         
         dphi5_x = lambda x, y: -(y**2-1)*(2*x+1)*0.5
         dphi5_y = lambda x, y: -(x+1)*x*y
         
         dphi6_x = lambda x, y: -(y+1)*y*x
         dphi6_y = lambda x, y: -(x**2-1)*(2*y+1)*0.5
         
         dphi7_x = lambda x, y: -(y**2-1)*(2*x-1)*0.5
         dphi7_y = lambda x, y: -(x-1)*x*y
         
         dphi8_x = lambda x, y: -2*x*(1 - y**2)
         dphi8_y = lambda x, y: -2*y*(1 - x**2)
         
         # Evaluacion en todos los puntos de G-L
         
         dphi0i_x = dphi0_x(xgi[:, 0], xgi[:, 1])
         dphi0i_y = dphi0_y(xgi[:, 0], xgi[:, 1])
         
         dphi1i_x = dphi1_x(xgi[:, 0], xgi[:, 1])
         dphi1i_y = dphi1_y(xgi[:, 0], xgi[:, 1])
         
         dphi2i_x = dphi2_x(xgi[:, 0], xgi[:, 1])
         dphi2i_y = dphi2_y(xgi[:, 0], xgi[:, 1])
         
         dphi3i_x = dphi3_x(xgi[:, 0], xgi[:, 1])
         dphi3i_y = dphi3_y(xgi[:, 0], xgi[:, 1])
         
         dphi4i_x = dphi4_x(xgi[:, 0], xgi[:, 1])
         dphi4i_y = dphi4_y(xgi[:, 0], xgi[:, 1])
         
         dphi5i_x = dphi5_x(xgi[:, 0], xgi[:, 1])
         dphi5i_y = dphi5_y(xgi[:, 0], xgi[:, 1])
         
         dphi6i_x = dphi6_x(xgi[:, 0], xgi[:, 1])
         dphi6i_y = dphi6_y(xgi[:, 0], xgi[:, 1])
         
         dphi7i_x = dphi7_x(xgi[:, 0], xgi[:, 1])
         dphi7i_y = dphi7_y(xgi[:, 0], xgi[:, 1])

         dphi8i_x = dphi8_x(xgi[:, 0], xgi[:, 1])
         dphi8i_y = dphi8_y(xgi[:, 0], xgi[:, 1])
         
         # Generacion matrices con todas las derivadas evaluadas
         
         dphi_x = np.array([dphi0i_x, dphi1i_x, dphi2i_x, dphi3i_x,dphi4i_x,dphi5i_x,dphi6i_x,dphi7i_x,dphi8i_x])
         dphi_y = np.array([dphi0i_y, dphi1i_y, dphi2i_y, dphi3i_y,dphi4i_y,dphi5i_y,dphi6i_y,dphi7i_y,dphi8i_y])
         
         for i in range(Ne):
             
             X1 = p1[:, elem1[i, 0]-1]  # vertice 1 de cada elemento
             
             X2 = p1[:, elem1[i, 1]-1]  # vertice 2 de cada elemento
             
             X3 = p1[:, elem1[i, 2]-1]
             
             X4 = p1[:, elem1[i, 3]-1]
             
             X5 = p1[:, elem1[i, 4]-1]
             
             X6 = p1[:, elem1[i, 5]-1]
             
             X7 = p1[:, elem1[i, 6]-1]
             
             X8 = p1[:, elem1[i, 7]-1]
             
             X9 = p1[:, elem1[i, 8]-1]
             
             # Coordenadas x e y
             
             xk=[X1[0],X2[0],X3[0],X4[0],X5[0],X6[0],X7[0],X8[0],X9[0]]
             yk=[X1[1],X2[1],X3[1],X4[1],X5[1],X6[1],X7[1],X8[1],X9[1]]
             
             JFi = np.zeros((2,2))
             det_JFi = []
             
             # Calculo del Jacobiano
             
             Rg=np.zeros((9,9))
             
             for k in range(9):
                 
                 
                 xgi_x = dphi_x[:, k]
                 result=np.dot(xk,xgi_x)
                 JFi[0,0] = result
                 
                 xgi_y = dphi_y[:, k]
                 result=np.dot(xk,xgi_y)
                 JFi[0,1] = result
                 
                 result=np.dot(yk,xgi_x)
                 JFi[1,0] = result
                 
                 result=np.dot(yk,xgi_y)
                 JFi[1,1] = result
                 
            
                 det_JFi = np.linalg.det(JFi)
                 JFi_inv=np.linalg.inv(JFi)
                 
                 # Evaluacion derivadas en el punto G-L correspondiente
                 
                 dphi0i_x = dphi0_x(xgi[k, 0], xgi[k, 1])
                 dphi0i_y = dphi0_y(xgi[k, 0], xgi[k, 1])
                 
                 dphi1i_x = dphi1_x(xgi[k, 0], xgi[k, 1])
                 dphi1i_y = dphi1_y(xgi[k, 0], xgi[k, 1])
                 
                 dphi2i_x = dphi2_x(xgi[k, 0], xgi[k, 1])
                 dphi2i_y = dphi2_y(xgi[k, 0], xgi[k, 1])
                 
                 dphi3i_x = dphi3_x(xgi[k, 0], xgi[k, 1])
                 dphi3i_y = dphi3_y(xgi[k, 0], xgi[k, 1])
                 
                 dphi4i_x = dphi4_x(xgi[k, 0], xgi[k, 1])
                 dphi4i_y = dphi4_y(xgi[k, 0], xgi[k, 1])
                 
                 dphi5i_x = dphi5_x(xgi[k, 0], xgi[k, 1])
                 dphi5i_y = dphi5_y(xgi[k, 0], xgi[k, 1])
                 
                 dphi6i_x = dphi6_x(xgi[k, 0], xgi[k, 1])
                 dphi6i_y = dphi6_y(xgi[k, 0], xgi[k, 1])
                 
                 dphi7i_x = dphi7_x(xgi[k, 0], xgi[k, 1])
                 dphi7i_y = dphi7_y(xgi[k, 0], xgi[k, 1])

                 dphi8i_x = dphi8_x(xgi[k, 0], xgi[k, 1])
                 dphi8i_y = dphi8_y(xgi[k, 0], xgi[k, 1])
                 
                 # Calculo derivadas

         
                 d0jx = lambda x,y:JFi_inv[0,0]*dphi0i_x+JFi_inv[1,0]*dphi0i_y
                 d0jy = lambda x,y:JFi_inv[0,1]*dphi0i_x+JFi_inv[1,1]*dphi0i_y
                 
                 d1jx = lambda x,y:JFi_inv[0,0]*dphi1i_x+JFi_inv[1,0]*dphi1i_y
                 d1jy = lambda x,y:JFi_inv[0,1]*dphi1i_x+JFi_inv[1,1]*dphi1i_y
                 
                 d2jx = lambda x,y:JFi_inv[0,0]*dphi2i_x+JFi_inv[1,0]*dphi2i_y
                 d2jy = lambda x,y:JFi_inv[0,1]*dphi2i_x+JFi_inv[1,1]*dphi2i_y
                 
                 d3jx = lambda x,y:JFi_inv[0,0]*dphi3i_x+JFi_inv[1,0]*dphi3i_y
                 d3jy = lambda x,y:JFi_inv[0,1]*dphi3i_x+JFi_inv[1,1]*dphi3i_y
                 
                 d4jx = lambda x,y:JFi_inv[0,0]*dphi4i_x+JFi_inv[1,0]*dphi4i_y
                 d4jy = lambda x,y:JFi_inv[0,1]*dphi4i_x+JFi_inv[1,1]*dphi4i_y
                 
                 d5jx = lambda x,y:JFi_inv[0,0]*dphi5i_x+JFi_inv[1,0]*dphi5i_y
                 d5jy = lambda x,y:JFi_inv[0,1]*dphi5i_x+JFi_inv[1,1]*dphi5i_y
                 
                 d6jx = lambda x,y:JFi_inv[0,0]*dphi6i_x+JFi_inv[1,0]*dphi6i_y
                 d6jy = lambda x,y:JFi_inv[0,1]*dphi6i_x+JFi_inv[1,1]*dphi6i_y
                 
                 d7jx = lambda x,y:JFi_inv[0,0]*dphi7i_x+JFi_inv[1,0]*dphi7i_y
                 d7jy = lambda x,y:JFi_inv[0,1]*dphi7i_x+JFi_inv[1,1]*dphi7i_y
                 
                 d8jx = lambda x,y:JFi_inv[0,0]*dphi8i_x+JFi_inv[1,0]*dphi8i_y
                 d8jy = lambda x,y:JFi_inv[0,1]*dphi8i_x+JFi_inv[1,1]*dphi8i_y

               
                 d0jx = d0jx(xgi[k, 0], xgi[k, 1])
                 d0jy = d0jy(xgi[k, 0], xgi[k, 1])
             
                 d1jx = d1jx(xgi[k, 0], xgi[k, 1])
                 d1jy = d1jy(xgi[k, 0], xgi[k, 1])
             
                 d2jx = d2jx(xgi[k, 0], xgi[k, 1])
                 d2jy = d2jy(xgi[k, 0], xgi[k, 1])
             
                 d3jx = d3jx(xgi[k, 0], xgi[k, 1])
                 d3jy = d3jy(xgi[k, 0], xgi[k, 1])
             
                 d4jx = d4jx(xgi[k, 0], xgi[k, 1])
                 d4jy = d4jy(xgi[k, 0], xgi[k, 1])
             
                 d5jx = d5jx(xgi[k, 0], xgi[k, 1])
                 d5jy = d5jy(xgi[k, 0], xgi[k, 1])
             
                 d6jx = d6jx(xgi[k, 0], xgi[k, 1])
                 d6jy = d6jy(xgi[k, 0], xgi[k, 1])
             
                 d7jx = d7jx(xgi[k, 0], xgi[k, 1])
                 d7jy = d7jy(xgi[k, 0], xgi[k, 1])
             
                 d8jx = d8jx(xgi[k, 0], xgi[k, 1])
                 d8jy = d8jy(xgi[k, 0], xgi[k, 1])
             
                 grad0 = np.zeros((2, 1))
                 grad1 = np.zeros((2, 1))
                 grad2 = np.zeros((2, 1))
                 grad3 = np.zeros((2, 1))
                 grad4 = np.zeros((2, 1))
                 grad5 = np.zeros((2, 1))
                 grad6 = np.zeros((2, 1))
                 grad7 = np.zeros((2, 1))
                 grad8 = np.zeros((2, 1))
                 
                 # Generacion de los gradientes
               
                 grad0[0, 0] = d0jx
                 grad0[1, 0] = d0jy
             
                 grad1[0, 0] = d1jx
                 grad1[1, 0] = d1jy
             
                 grad2[0, 0] = d2jx
                 grad2[1, 0] = d2jy
             
                 grad3[0, 0] = d3jx
                 grad3[1, 0] = d3jy
             
                 grad4[0, 0] = d4jx
                 grad4[1, 0] = d4jy
             
                 grad5[0, 0] = d5jx
                 grad5[1, 0] = d5jy
             
                 grad6[0, 0] = d6jx
                 grad6[1, 0] = d6jy
             
                 grad7[0, 0] = d7jx
                 grad7[1, 0] = d7jy
             
                 grad8[0, 0] = d8jx
                 grad8[1, 0] = d8jy
               
                 
                 # Calculo matriz de rigidez de referencia
             
                 v=np.dot(grad0.T, grad0)
                 Rg[0, 0] += wi[k]*v*det_JFi
                 
                 v=np.dot(grad1.T, grad1)
                 Rg[1, 1] += wi[k]*v*det_JFi
                 
                 v=np.dot(grad2.T, grad2)
                 Rg[2, 2] += wi[k]*v*det_JFi
                 
                 v=np.dot(grad3.T, grad3)
                 Rg[3, 3] += wi[k]*v*det_JFi
                 
                 v=np.dot(grad4.T, grad4)
                 Rg[4, 4] += wi[k]*v*det_JFi
                 
                 v=np.dot(grad5.T, grad5)
                 Rg[5, 5] += wi[k]*v*det_JFi
                 
                 v=np.dot(grad6.T, grad6)
                 Rg[6, 6] += wi[k]*v*det_JFi
                 
                 v=np.dot(grad7.T, grad7)
                 Rg[7, 7] += wi[k]*v*det_JFi
                 
                 v=np.dot(grad8.T, grad8)
                 Rg[8, 8] += wi[k]*v*det_JFi
                 
                 v=np.dot(grad0.T, grad1)
                 Rg[0, 1] += wi[k]*v*det_JFi 
                 Rg[1,0] = Rg[0,1]
                 
                 v=np.dot(grad0.T, grad2)
                 Rg[0, 2] += wi[k]*v*det_JFi
                 Rg[2,0] = Rg[0,2]
                 
                 v=np.dot(grad0.T, grad3)
                 Rg[0, 3] += wi[k]*v*det_JFi
                 Rg[3,0] = Rg[0,3]
                 
                 v=np.dot(grad0.T, grad4)
                 Rg[0, 4] += wi[k]*v*det_JFi
                 Rg[4,0] = Rg[0,4]
                 
                 v=np.dot(grad0.T, grad5)
                 Rg[0, 5] += wi[k]*v*det_JFi
                 Rg[5,0] = Rg[0,5]
                 
                 v=np.dot(grad0.T, grad6)
                 Rg[0, 6] += wi[k]*v*det_JFi
                 Rg[6,0] = Rg[0,6]
                 
                 v=np.dot(grad0.T, grad7)
                 Rg[0, 7] += wi[k]*v*det_JFi
                 Rg[7,0] = Rg[0,7]
                 
                 v=np.dot(grad0.T, grad8)
                 Rg[0, 8] += wi[k]*v*det_JFi
                 Rg[8,0] = Rg[0,8]
                 
                 v=np.dot(grad1.T, grad2)
                 Rg[1, 2] += wi[k]*v*det_JFi
                 Rg[2,1] = Rg[1,2]
                 
                 v=np.dot(grad1.T, grad3)
                 Rg[1, 3] += wi[k]*v*det_JFi
                 Rg[3,1] = Rg[1,3]
                 
                 v=np.dot(grad1.T, grad4)
                 Rg[1, 4] += wi[k]*v*det_JFi
                 Rg[4,1] = Rg[1,4]
                 
                 v=np.dot(grad1.T, grad5)
                 Rg[1, 5] += wi[k]*v*det_JFi
                 Rg[5,1] = Rg[1,5]
                 
                 v=np.dot(grad1.T, grad6)
                 Rg[1, 6] += wi[k]*v*det_JFi
                 Rg[6,1] = Rg[1,6]
                 
                 v=np.dot(grad1.T, grad7)
                 Rg[1, 7] += wi[k]*v*det_JFi
                 Rg[7,1] = Rg[1,7]
                 
                 v=np.dot(grad1.T, grad8)
                 Rg[1, 8] += wi[k]*v*det_JFi
                 Rg[8,1] = Rg[1,8]
                 
                 v=np.dot(grad2.T, grad3)
                 Rg[2, 3] += wi[k]*v*det_JFi
                 Rg[3,2] = Rg[2,3]
                 
                 v=np.dot(grad2.T, grad4)
                 Rg[2, 4] += wi[k]*v*det_JFi
                 Rg[4,2] = Rg[2,4]
                 
                 v=np.dot(grad2.T, grad5)
                 Rg[2, 5] += wi[k]*v*det_JFi
                 Rg[5,2] = Rg[2,5]
                 
                 v=np.dot(grad2.T, grad6)
                 Rg[2, 6] += wi[k]*v*det_JFi
                 Rg[6,2] = Rg[2,6]
                 
                 v=np.dot(grad2.T, grad7)
                 Rg[2, 7] += wi[k]*v*det_JFi
                 Rg[7,2] = Rg[2,7]
                 
                 v=np.dot(grad2.T, grad8)
                 Rg[2, 8] += wi[k]*v*det_JFi
                 Rg[8,2] = Rg[2,8]
                 
                 v=np.dot(grad3.T, grad4)
                 Rg[3, 4] += wi[k]*v*det_JFi
                 Rg[4,3] = Rg[3,4]
                 
                 v=np.dot(grad3.T, grad5)
                 Rg[3, 5] += wi[k]*v*det_JFi
                 Rg[5,3] = Rg[3,5]
                 
                 v=np.dot(grad3.T, grad6)
                 Rg[3, 6] += wi[k]*v*det_JFi
                 Rg[6,3] = Rg[3,6]
                 
                 v=np.dot(grad3.T, grad7)
                 Rg[3, 7] += wi[k]*v*det_JFi
                 Rg[7,3] = Rg[3,7]
                 
                 v=np.dot(grad3.T, grad8)
                 Rg[3, 8] += wi[k]*v*det_JFi
                 Rg[8,3] = Rg[3,8]
                 
                 v=np.dot(grad4.T, grad5)
                 Rg[4, 5] += wi[k]*v*det_JFi
                 Rg[5,4] = Rg[4,5]
                 
                 v=np.dot(grad4.T, grad6)
                 Rg[4, 6] += wi[k]*v*det_JFi
                 Rg[6,4] = Rg[4,6]
                 
                 v=np.dot(grad4.T, grad7)
                 Rg[4, 7] += wi[k]*v*det_JFi
                 Rg[7,4] = Rg[4,7]
                 
                 v=np.dot(grad4.T, grad8)
                 Rg[4, 8] += wi[k]*v*det_JFi
                 Rg[8,4] = Rg[4,8]
                 
                 v=np.dot(grad5.T, grad6)
                 Rg[5, 6] += wi[k]*v*det_JFi
                 Rg[6,5] = Rg[5,6]
                 
                 v=np.dot(grad5.T, grad7)
                 Rg[5, 7] += wi[k]*v*det_JFi
                 Rg[7,5] = Rg[5,7]
                 
                 v=np.dot(grad5.T, grad8)
                 Rg[5, 8] += wi[k]*v*det_JFi
                 Rg[8,5] = Rg[5,8]
                 
                 v=np.dot(grad6.T, grad7)
                 Rg[6, 7] += wi[k]*v*det_JFi
                 Rg[7,6] = Rg[6,7]
                 
                 v=np.dot(grad6.T, grad8)
                 Rg[6, 8] += wi[k]*v*det_JFi
                 Rg[8,6] = Rg[6,8]
                 
                 v=np.dot(grad7.T, grad8)
                 Rg[7, 8] += wi[k]*v*det_JFi
                 Rg[8,7] = Rg[7,8]
             
             # Ensamblamiento matriz de masas
                 
             indices = t1[0:9, i] - 1
                 
             fila_indices, col_indices = np.meshgrid(indices, indices, indexing='ij')
             R[fila_indices, col_indices] += Rg 
             
  
    return R

m=1

def massref3D(m): 
    if m == 1:
        
        
        Mg = np.zeros((4, 4))
        
        # Funciones base
        
        phi0 = lambda x, y, z: 1 - x - y - z
        phi1 = lambda x, y, z: x
        phi2 = lambda x, y, z: y
        phi3 = lambda x, y, z: z

        # Cuadratura G-L
        
        xgi = np.array([[0.5854101966249685, 0.1381966011250105, 0.1381966011250105], [0.1381966011250105, 0.1381966011250105, 0.1381966011250105], [0.1381966011250105, 0.1381966011250105, 0.5854101966249685],[0.1381966011250105, 0.5854101966249685,0.1381966011250105]])
        wi = np.array([1/6*0.25, 1/6*0.25,1/6*0.25,1/6*0.25])

        # Evaluacion de las funciones base
        
        phi0i = phi0(xgi[:, 0], xgi[:, 1],xgi[:, 2])
        phi1i = phi1(xgi[:, 0], xgi[:, 1],xgi[:, 2])
        phi2i = phi2(xgi[:, 0], xgi[:, 1],xgi[:, 2])
        phi3i = phi3(xgi[:, 0], xgi[:, 1],xgi[:, 2])
        
        # Calculo matriz de masas de referencia
        
        Mg = np.zeros((4, 4))
        Mg[0, 0] = np.sum(wi * phi0i * phi0i)
        Mg[1, 1] = np.sum(wi * phi1i * phi1i)
        Mg[2, 2] = np.sum(wi * phi2i * phi2i)
        Mg[3, 3] = np.sum(wi * phi3i * phi3i)
        Mg[0, 1] = Mg[1, 0] = np.sum(wi * phi0i * phi1i)
        Mg[0, 2] = Mg[2, 0] = np.sum(wi * phi0i * phi2i)
        Mg[0, 3] = Mg[3, 0] = np.sum(wi * phi0i * phi3i)
        Mg[1, 2] = Mg[2, 1] = np.sum(wi * phi1i * phi2i)
        Mg[1, 3] = Mg[3, 1] = np.sum(wi * phi1i * phi3i)
        Mg[2, 3] = Mg[3, 2] = np.sum(wi * phi2i * phi3i)
       

    return Mg
def kmglobal3D(m,p,t):  
    
    Mg = massref3D(m)

    if m == 1:
           
           # Declaracion de variablesy matrices
        
           xi=p[0,:]
           yi=p[1,:]
           
           Rg=np.zeros((4,4))
           M = csr_matrix((len(xi), len(yi)))
           R = csr_matrix((len(xi), len(yi)))
           
           elem = t[0:4, :].T  
           Ne = elem.shape[0]
           
           # Cuadratura
           
           xgi = np.array([[0.5854101966249685, 0.1381966011250105, 0.1381966011250105], [0.1381966011250105, 0.1381966011250105, 0.1381966011250105], [0.1381966011250105, 0.1381966011250105, 0.5854101966249685],[0.1381966011250105, 0.5854101966249685,0.1381966011250105]])
           wi = np.array([1/6*0.25, 1/6*0.25,1/6*0.25,1/6*0.25])
           
           # Declaracion derivadas de las funciones de forma
           
           dphi0_x = lambda x,y,z: -1
           dphi0_y = lambda x,y,z: -1
           dphi0_z = lambda x,y,z: -1
           
           dphi1_x = lambda x,y,z: 1
           dphi1_y = lambda x,y,z: 0
           dphi1_z = lambda x,y,z: 0
           
           dphi2_x = lambda x,y,z: 0
           dphi2_y = lambda x,y,z: 1
           dphi2_z = lambda x,y,z: 0
           
           dphi3_x = lambda x,y,z: 0
           dphi3_y = lambda x,y,z: 0
           dphi3_z = lambda x,y,z: 1
           
           # Evaluacion de las derivadas en los puntos de G-L
           
           dphi0_x = dphi0_x(xgi[:, 0], xgi[:, 1],xgi[:, 2])
           dphi0_y = dphi0_y(xgi[:, 0], xgi[:, 1],xgi[:, 2])
           dphi0_z = dphi0_z(xgi[:, 0], xgi[:, 1],xgi[:, 2])
           
           dphi1_x = dphi1_x(xgi[:, 0], xgi[:, 1],xgi[:, 2])
           dphi1_y = dphi1_y(xgi[:, 0], xgi[:, 1],xgi[:, 2])
           dphi1_z = dphi1_z(xgi[:, 0], xgi[:, 1],xgi[:, 2])
           
           dphi2_x = dphi2_x(xgi[:, 0], xgi[:, 1],xgi[:, 2])
           dphi2_y = dphi2_y(xgi[:, 0], xgi[:, 1],xgi[:, 2])
           dphi2_z = dphi2_z(xgi[:, 0], xgi[:, 1],xgi[:, 2])
           
           dphi3_x = dphi3_x(xgi[:, 0], xgi[:, 1],xgi[:, 2])
           dphi3_y = dphi3_y(xgi[:, 0], xgi[:, 1],xgi[:, 2])
           dphi3_z = dphi3_z(xgi[:, 0], xgi[:, 1],xgi[:, 2])
           
           # Calculo matriz Ai
           
           for i in range(Ne):
               
               X1 = p[:, elem[i, 0]-1]  # vertice 1 de cada elemento
               X2 = p[:, elem[i, 1]-1]  # vertice 2 de cada elemento
               X3 = p[:, elem[i, 2]-1]  # vertice 3 de cada elemento
               X4 = p[:, elem[i, 3]-1]  # vertice 4 de cada elemento
 
               # Transformacion triangulos
               
               Ai = np.column_stack((X2 - X1, X3 - X1,X4-X1))
               det_Ai = np.linalg.det(Ai)
               
               areaT=0.5*abs(det_Ai)
               
               # Calculo matriz de masas global

               indices = t[0:4, i] - 1

               fila_indices, col_indices = np.meshgrid(indices, indices, indexing='ij')
               M[fila_indices, col_indices] += 2 * areaT * Mg 
               
               
               Ai_inv=np.linalg.inv(Ai)
               
               # Calculo de derivadas
               
               d0jx = lambda x,y,z: Ai_inv[0,0]*dphi0_x+Ai_inv[1,0]*dphi0_y+Ai_inv[2,0]*dphi0_z
               d0jy = lambda x,y,z: Ai_inv[0,1]*dphi0_x+Ai_inv[1,1]*dphi0_y+Ai_inv[2,1]*dphi0_z
               d0jz = lambda x,y,z: Ai_inv[0,2]*dphi0_x+Ai_inv[1,2]*dphi0_y+Ai_inv[2,2]*dphi0_z
               
               d1jx = lambda x,y,z: Ai_inv[0,0]*dphi1_x+Ai_inv[1,0]*dphi1_y+Ai_inv[2,0]*dphi1_z
               d1jy = lambda x,y,z: Ai_inv[0,1]*dphi1_x+Ai_inv[1,1]*dphi1_y+Ai_inv[2,1]*dphi1_z
               d1jz = lambda x,y,z: Ai_inv[0,2]*dphi1_x+Ai_inv[1,2]*dphi1_y+Ai_inv[2,2]*dphi1_z
               
               d2jx = lambda x,y,z: Ai_inv[0,0]*dphi2_x+Ai_inv[1,0]*dphi2_y+Ai_inv[2,0]*dphi2_z
               d2jy = lambda x,y,z: Ai_inv[0,1]*dphi2_x+Ai_inv[1,1]*dphi2_y+Ai_inv[2,1]*dphi2_z
               d2jz = lambda x,y,z: Ai_inv[0,2]*dphi2_x+Ai_inv[1,2]*dphi2_y+Ai_inv[2,2]*dphi2_z
               
               d3jx = lambda x,y,z: Ai_inv[0,0]*dphi3_x+Ai_inv[1,0]*dphi3_y+Ai_inv[2,0]*dphi3_z
               d3jy = lambda x,y,z: Ai_inv[0,1]*dphi3_x+Ai_inv[1,1]*dphi3_y+Ai_inv[2,1]*dphi3_z
               d3jz = lambda x,y,z: Ai_inv[0,2]*dphi3_x+Ai_inv[1,2]*dphi3_y+Ai_inv[2,2]*dphi3_z
               
               # Evaluacion de las derivadas en los puntos de G-L
               
               d0jx = d0jx(xgi[:, 0], xgi[:, 1], xgi[:, 2])
               d0jy = d0jy(xgi[:, 0], xgi[:, 1], xgi[:, 2])
               d0jz = d0jz(xgi[:, 0], xgi[:, 1], xgi[:, 2])
               
               d1jx = d1jx(xgi[:, 0], xgi[:, 1], xgi[:, 2])
               d1jy = d1jy(xgi[:, 0], xgi[:, 1], xgi[:, 2])
               d1jz = d1jz(xgi[:, 0], xgi[:, 1], xgi[:, 2])
               
               d2jx = d2jx(xgi[:, 0], xgi[:, 1], xgi[:, 2])
               d2jy = d2jy(xgi[:, 0], xgi[:, 1], xgi[:, 2])
               d2jz = d2jz(xgi[:, 0], xgi[:, 1], xgi[:, 2])
               
               d3jx = d3jx(xgi[:, 0], xgi[:, 1], xgi[:, 2])
               d3jy = d3jy(xgi[:, 0], xgi[:, 1], xgi[:, 2])
               d3jz = d3jz(xgi[:, 0], xgi[:, 1], xgi[:, 2])
               
               grad0 = np.zeros((3, 1))
               grad1 = np.zeros((3, 1))
               grad2 = np.zeros((3, 1))
               grad3 = np.zeros((3, 1))
               
               grad0[0, 0] = d0jx
               grad0[1, 0] = d0jy
               grad0[2, 0] = d0jz
               
               grad1[0, 0] = d1jx
               grad1[1, 0] = d1jy
               grad1[2, 0] = d1jz
               
               grad2[0, 0] = d2jx
               grad2[1, 0] = d2jy
               grad2[2, 0] = d2jz
               
               grad3[0, 0] = d3jx
               grad3[1, 0] = d3jy
               grad3[2, 0] = d3jz
               
               # Calculo matriz de rigidez de referencia
               
               v=np.dot(grad0.T, grad0)
               Rg[0, 0] = np.sum(wi*v)
               
               v=np.dot(grad1.T, grad1)
               Rg[1, 1] = np.sum(wi*v)
               
               v=np.dot(grad2.T, grad2)
               Rg[2, 2] = np.sum(wi*v)
               
               v=np.dot(grad3.T, grad3)
               Rg[3, 3] = np.sum(wi*v)
               
               v=np.dot(grad0.T, grad1)
               Rg[0, 1] = np.sum(wi*v)
               
               v=np.dot(grad0.T, grad2)
               Rg[0, 2] = np.sum(wi*v)
               
               v=np.dot(grad0.T, grad3)
               Rg[0, 3] = np.sum(wi*v)
               
               v=np.dot(grad1.T, grad2)
               Rg[1, 2] = np.sum(wi*v)
               
               v=np.dot(grad1.T, grad3)
               Rg[1, 3] = np.sum(wi*v)
               
               v=np.dot(grad1.T, grad0)
               Rg[1, 0] = np.sum(wi*v)
               
               v=np.dot(grad2.T, grad0)
               Rg[2, 0] = np.sum(wi*v)
               
               v=np.dot(grad3.T, grad0)
               Rg[3, 0] = np.sum(wi*v)
               
               v=np.dot(grad2.T, grad1)
               Rg[2, 1] = np.sum(wi*v)
               
               v=np.dot(grad3.T, grad1)
               Rg[3, 1] = np.sum(wi*v)
               
               v=np.dot(grad3.T, grad2)
               Rg[3, 2] = np.sum(wi*v)
               
               v=np.dot(grad2.T, grad3)
               Rg[2, 3] = np.sum(wi*v)
               
               # Ensamblamiento matriz de rigidez
               
               indices = t[0:4, i] - 1
               
               fila_indices, col_indices = np.meshgrid(indices, indices, indexing='ij')
               R[fila_indices, col_indices] += 2 * Rg * areaT

    return M,R
