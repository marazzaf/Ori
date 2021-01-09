#coding: utf-8

from arcth import atanh
from dolfin import *
import numpy as np
import ufl
import sys

size_ref = 20 #5 for debug
L,l = 1,1
mesh = RectangleMesh(Point(-L/2,-l/2), Point(L/2, l/2), size_ref, size_ref, "crossed")
bnd = MeshFunction('size_t', mesh, 1)
bnd.set_all(0)

V = VectorFunctionSpace(mesh, 'CG', 1)
phi = Function(V, name="surface")
psi = TestFunction(V)

#Dirichlet BC
R = 10 #radius of the outer circle
x = SpatialCoordinate(mesh)
theta = ufl.atan_2(x[0], x[1])
#phi_D = Expression(('R*cos(', 'R*'), R=R, degree = 2)
phi_D = as_vector((R*cos(theta), R*sin(theta)))

#creating the bc object
bc = DirichletBC(V, phi_D, bnd, 0)

#Writing energy. No constraint for now...
norm_phi_x = sqrt(inner(phi.dx(0), phi.dx(0)))
norm_phi_y = sqrt(inner(phi.dx(1), phi.dx(1)))
#f = as_vector((2*np.arctanh(0.5*norm_phi_x), -4/norm_phi_y)) #how can I create a ufl function computing arctanh?
#f = as_vector((2*ufl.atanh(0.5*norm_phi_x), -4/norm_phi_y))


#bilinear form
#a = inner(as_vector((2*ufl.atan(0.5*norm_phi_x),norm_phi_y)), grad(psi)) * dx - psi * dx
a = (2*atanh(0.5*norm_phi_x) * (psi[0].dx(0)+psi[1].dx(0)) - 4/norm_phi_y * (psi[0].dx(1)+psi[1].dx(1))) * dx
#solving problem
solve(a == 0, phi, bc, solver_parameters={"newton_solver":{"relative_tolerance":1e-6}})

#solution verifies constraints?
ps = inner(phi.dx(0), phi.dx(1)) * dx
ps = assemble(ps)
print(ps) #should be 0
cons = (1 - 0.25*norm_phi_x) * norm_phi_y * dx
cons = assemble(cons)
print(cons) #should be one

#checking intervals
U = FunctionSpace(mesh, 'CG', 1)
interval_x = project(inner(phi.dx(0), phi.dx(0)), U)
interval_y = project(inner(phi.dx(1), phi.dx(1)), U)

# Save solution in VTK format
file = File("test/no_constraint.pvd")
file << phi
file << interval_x
file << interval_y

