# Heat conduction problem

import matplotlib.pyplot as plt
import numpy as np
from fenics import *

## Global settings
#plt.ion()
#plt.show()
plt.rcParams['image.cmap'] = 'jet'
fig = plt.figure()
fig.show()


set_log_active(False)
# Variables
alpha = 18.7 # Thermal diffusivity mm^2/s
k = 63.9e3 # Thermal conductivity W/(mm-K)
vel = 500/60 # Velocity in mm/sec
qmax = 113.35e6 # Max power per unit area supplied to the material, Power of laser = integral of q over laser circle
r_b = 2 # Radius of the beam in mm where intensity becomes 1/e 
sigma_z = 1e-5 # Penetration depth in z direction in mm
T0 = Constant(25) # Ambient temperature in Kelvin or deg C anything will work
## Time discretisation parameters dt, num_steps, tf are below mesh definition 

tol = 1e-6

# Define mesh 
L = 25.0 # Length of cube/cuboid
n = 10 # Number of cells in x,y,z direction

x0,y0,z0 = -L/2,-L/2,0
x1,y1,z1 = 3*L/2,L/2,-L

tf = abs((x1-x0)/vel/2)           # final time in seconds

mesh = BoxMesh(Point(x0,y0,z0),Point(x1,y1,z1),int(n*abs(x1-x0)/L),int(n*abs(y1-y0)/L),int(n*abs(z1-z0)/L))

# Refine region of mesh
cell = MeshFunction('bool',mesh,0)
cell.set_all(False)

w = 3 # Refinement width as a multiple of L

class Ref(SubDomain):
    def inside(self, x, on_boundary):
        return abs(x[1])<w*r_b and x[2]>-w*r_b  

ref = Ref()
ref.mark(cell, True) 

mesh = refine(mesh,cell)
mesh = refine(mesh,cell)

# plot(mesh)

# Time discretisation
dt = mesh.hmin()/vel # time step size
num_steps = int(tf/dt)     # number of time steps

# Define Function Space
V = FunctionSpace(mesh, 'P', 1)

# Define boundary condition
def boundary(x, on_boundary):
    return on_boundary and not(near(x[2],0,tol)) and not(near(x[0],x1,tol))

bc = DirichletBC(V, T0, boundary)

# Define initial value
T_n = interpolate(T0, V)
#T_n = project(T0, V)

def sol():
    # Define variational problem
    T = TrialFunction(V)
    v = TestFunction(V)
    f = Expression('(alpha*dt/k)*qmax*exp(-(pow(x[0]-vel*t,2)+x[1]*x[1])/(r_b*r_b)-x[2]*x[2]/(sigma_z*sigma_z))', degree=1, alpha=alpha, dt=dt, k=k, qmax=qmax, vel=vel, r_b=r_b, sigma_z=sigma_z, t=0)
    # f = interpolate(f0, V)

    F = T*v*dx + alpha*dt*dot(grad(T), grad(v))*dx - (T_n + alpha*dt*f)*v*dx
    a, L = lhs(F), rhs(F)

    # Time-stepping
    T = Function(V)
    t = 0
    for n in range(num_steps):

        # Update current time
        t += dt
        f.t = t

        # Compute solution
        solve(a == L, T, bc)

        # Plot solution
        fig.clear()
        p = plot(T,title='Temperature Field (deg C)')
        fig.colorbar(p)
        #fig.gca().set_zlim((0, 2))
        fig.canvas.draw()
        #plt.pause(5)
        # Update previous solution
        T_n.assign(T)

    return T

def hard_dep():
    T = sol()
    mshco = mesh.coordinates()
    x = mshco[:,0]
    y = mshco[:,1]
    z = mshco[:,2]
    vertex_values_T = T.compute_vertex_values(mesh)
    T_max_loc = np.argmax(vertex_values_T)
    x_T_max = x[T_max_loc]
    y_max = y[x==x_T_max]
    z_max = z[x==x_T_max]
    T_yz_max = vertex_values_T[x==x_T_max]
    try:
        hard_depth = np.min(z_max[727<T_yz_max])
    except:
        hard_depth = 0

    return hard_depth

def depth_vs_vel():
    global vel,T_n,tf,dt,num_steps
    vel_arr = np.array([])
    depth_arr = np.array([])
    for i in np.linspace(1,16,16): 
        vel = i
        tf = abs((x1-x0)/vel/2)           # final time in seconds
        dt = mesh.hmin()/vel # time step size
        num_steps = int(tf/dt)     # number of time steps
        T_n = interpolate(T0, V)
        vel_arr = np.append(vel_arr,vel)
        dep = hard_dep()
        depth_arr = np.append(depth_arr,dep)
        print(-dep)

    fig.clear()
    plt.plot(vel_arr,-depth_arr)
    plt.xlabel('v (mm/s)')
    plt.ylabel('Depth (mm)')
    plt.title('Hardened Depth vs Velocity')
    plt.show()

def hard_wid():
    T = sol()
    mshco = mesh.coordinates()
    x = mshco[:,0]
    y = mshco[:,1]
    z = mshco[:,2]
    vertex_values_T = T.compute_vertex_values(mesh)
    T_max_loc = np.argmax(vertex_values_T)
    x_T_max = x[T_max_loc]
    y_max = y[x==x_T_max]
    z_max = z[x==x_T_max]
    T_yz_max = vertex_values_T[x==x_T_max]

    try:
        hard_width = np.max(y_max[727<T_yz_max])
    except:
        hard_width = 0
    
    return hard_width 

def width_vs_vel():
    global vel, T_n, tf, dt, num_steps
    vel_arr = np.array([])
    width_arr = np.array([])
    for i in np.linspace(1,16,16):
        vel = i
        tf = abs((x1-x0)/vel/2)           # final time in seconds
        dt = mesh.hmin()/vel # time step size
        num_steps = int(tf/dt)     # number of time steps
        T_n = interpolate(T0, V)
        vel_arr = np.append(vel_arr,vel)
        wide = hard_wid()
        width_arr = np.append(width_arr,wide)
        print(wide)

    fig.clear()
    plt.plot(vel_arr,2*width_arr)
    plt.xlabel('v (mm/s)')
    plt.ylabel('Width (mm)')
    plt.title('Hardened Width vs Velocity')
    plt.show()

#depth_vs_vel()
width_vs_vel()
'''
mshco = mesh.coordinates()
x = mshco[:,0]
y = mshco[:,1]
z = mshco[:,2]

vertex_values_T = T.compute_vertex_values(mesh)
T_max_loc = np.argmax(vertex_values_T)
x_T_max = x[T_max_loc]
y_max = y[x==x_T_max]
z_max = z[x==x_T_max]

T_yz_max = vertex_values_T[x==x_T_max]
'''
# int(n*abs(x1-x0)/L),int(n*abs(y1-y0)/L),int(n*abs(z1-z0)/L)
'''
fig1 = plt.figure()
ax1 = fig1.add_subplot(1,2,1,projection='3d')
ax1.plot_trisurf(y_max,z_max,T_yz_max,cmap=plt.cm.jet)
ax1.plot_trisurf(y_max[727<T_yz_max],z_max[727<T_yz_max],T_yz_max[727<T_yz_max],cmap=plt.cm.Reds)
ax1.set(xlabel='Y',ylabel='Z',zlabel='Temp',title='Plane of max heating')

x_y0 = x[y==0]
z_y0 = z[y==0]
T_y0 = vertex_values_T[y==0]
ax2 = fig1.add_subplot(1,2,2,projection='3d')
ax2.plot_trisurf(x_y0,z_y0,T_y0,cmap=plt.cm.jet)
ax2.plot_trisurf(x_y0[727<T_y0],z_y0[727<T_y0],T_y0[727<T_y0],cmap=plt.cm.Reds)
ax2.set(xlabel='X',ylabel='Z',zlabel='Temp',title='X-Z Plane')
'''
#plt.show()
'''
# Maximum temperature curve at a particular depth z in the x - z plane
x_t = np.array([])
z_t = np.array([])

z_dist = np.array(list(set(z_y0)))
z_dist = np.sort(z_dist)
print(z_dist)
for i in z_dist:
    z_t = np.append(z_t,i)
    T_temp = T_y0[z_y0==i]
    x_temp = x_y0[z_y0==i]
    x_t = np.append(x_t,x_temp[np.argmax(T_temp)])

fig2 = plt.figure()
ax21 = fig2.add_subplot(1,1,1)
ax21.plot(x_t,z_t)
plt.show()'''