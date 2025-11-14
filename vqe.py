import multiprocessing 
from multiprocessing import Manager
from qiskit import QuantumCircuit, execute, Aer, ClassicalRegister, QuantumRegister
import numpy as np
import random
from qiskit.aqua.components.optimizers import SPSA
from qiskit.util import local_hardware_info
import datetime


backend = Aer.get_backend("qasm_simulator")


N = 1024 #shots 8192, 4096, 2048, 512
maxiter = 100 # 200, 150, 125, 100, 75, 50


def sign(matrix0, matrix1):
    matrix = np.kron(matrix0, matrix1)
    diagonal = list(np.diag(matrix))
    return diagonal


def term(counts, sign):
    i = 0
    if "00" in list(counts):
        i = i + (sign[0] * counts["00"] / N)
    if "01" in list(counts):
        i = i + (sign[1] * counts["01"] / N)
    if "10" in list(counts):
        i = i + (sign[2] * counts["10"] / N)
    if "11" in list(counts):
        i = i + (sign[3] * counts["11"] / N)
    return i  


def Hamiltonian(angle):
    
    q1 = QuantumRegister(2) 
    c1 = ClassicalRegister(2) 
    qc1 = QuantumCircuit(q1, c1)

    qc1.ry(angle[0], q1[0])
    qc1.ry(angle[1], q1[1])
    qc1.cx(q1[0], q1[1])
    qc1.ry(angle[2], q1[0])
    qc1.ry(angle[3], q1[1])  
    qc1.measure(q1[0], c1[0])
    qc1.measure(q1[1], c1[1])
    
    q2 = QuantumRegister(2) 
    c2 = ClassicalRegister(2) 
    qc2 = QuantumCircuit(q2, c2)

    qc2.ry(angle[0], q2[0])
    qc2.ry(angle[1], q2[1])
    qc2.cx(q2[0], q2[1])
    qc2.ry(angle[2], q2[0])
    qc2.ry(angle[3], q2[1])  
    qc2.ry(np.pi/2,q2[1]) #x
    qc2.ry(np.pi/2,q2[0]) #x
    qc2.measure(q2[0], c2[0])
    qc2.measure(q2[1], c2[1])
    
    qc = [qc1, qc2]
    
    job = execute(qc, backend = backend, shots = N)
    x = job.result().get_counts()
    
    counts0 = x[0]
    counts1 = x[1]
    
    I = np.array([[1, 0], [0, 1]])
    Z = np.array([[1, 0], [0, -1]])
    
    Id = term(counts0, sign(I, I)) 
    Z0 = term(counts0, sign(I, Z))
    Z1 = term(counts0, sign(Z, I))
    Z2 = term(counts0, sign(Z, Z))
    Z3 = term(counts1, sign(Z, Z))
          
    A = -1.0501604336972703
    B = 0.4042146605457886
    C = 0.4042146605457887
    D = 0.011346884397300416
    E = 0.18037524720542222
    
    H = A * Id + B * Z0 + C * Z1 + D * Z2 + E * Z3 
    values.append(H)
    return H    


values = []
def energy(energy_min, angles, y):
    for i in range(1, y):
        angle0 = []
        for j in range(0, 4):
            n = random.uniform(0, 2 * np.pi)
            angle0.append(n)
        
        optimizer = SPSA(maxiter = maxiter)
    
        res = optimizer.optimize(num_vars =  4, objective_function = Hamiltonian, initial_point = angle0)
            
        print(str(i) + ":" + str(res))
        
        energy_min.append(res[1])
        angles.append(list(res[0]))
    
        values[:] == [] # clear
    
    return 


CPU_COUNT = local_hardware_info()['cpus']
if __name__ == '__main__':
    with Manager() as manager:
        energy_min = manager.list()
        angles = manager.list()
        values = manager.list()
        start = datetime.datetime.now()
        processes = []
        
        for i in range(CPU_COUNT):
            p = multiprocessing.Process(target = energy, args = (energy_min, angles, 251, ))
            p.start()
            processes.append(p)
    
        for process in processes:
            process.join()
                  
        file = open("H2_shots" + str(N) + "_maxiter" + str(maxiter) + ".txt", "w+")
        file.write("E = " + str(energy_min) + "\n")
        file.write("vector = " + str(angles) + "\n")
        finish = datetime.datetime.now()
        time = finish - start
        file.write("time: " + str(time))
        file.close()



