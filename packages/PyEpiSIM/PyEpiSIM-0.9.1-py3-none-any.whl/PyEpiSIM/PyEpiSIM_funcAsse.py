import numpy as np
import sympy as sp
import time
import math
from scipy import stats
import threading
from itertools import product
import sympy
# from sympy import *
from numpy.linalg import inv, eig, norm
def thread_it(func, *args):
    t = threading.Thread(target=func, args=args)
    t.setDaemon(True)
    t.start()


def PureEpistasis(Maf1,Maf2,PD,H2,f11,f22,f33,veracity):
    # give a pure epistasis model
    # MAF and genotype frequencies
    P1 = [(1-Maf1)**2, 2*(1-Maf1)*Maf1, Maf1**2]  # The genotype frequency of the first SNP, key formula
    P2 = [(1-Maf2)**2, 2*(1-Maf2)*Maf2, Maf2**2]  # Genotype frequency of the second SNP, key formula
    # Assuming a linkage balance exists between K SNPs,
    # the frequency of the combined genotype p (Gi) will be the product of the genotype frequencies corresponding to each SNP
    P = np.transpose(np.mat(P1)) * np.mat(P2)

    # solving equations
    f12, f13, f21, f23, f31, f32=sympy.symbols('f12 f13 f21 f23 f31 f32')
    eqs=[sympy.Eq(P2[0]*f11 + P2[1]*f12 + P2[2]*f13, PD),
        sympy.Eq(P2[0]*f21 + P2[1]*f22 + P2[2]*f23, PD),
        sympy.Eq(P1[0]*f11 + P1[1]*f21 + P1[2]*f31, PD),
        sympy.Eq(P1[0]*f12 + P1[1]*f22 + P1[2]*f32, PD),
        sympy.Eq(P1[0]*f13 + P1[1]*f23 + P1[2]*f33, PD),
        sympy.Eq((f11-PD)**2*P[0,0] + (f12-PD)**2*P[0,1] + (f13-PD)**2*P[0,2]+ \
            (f21-PD)**2*P[1,0] + (f22-PD)**2*P[1,1] + (f23-PD)**2*P[1,2]+ \
            (f31-PD)**2*P[2,0] + (f32-PD)**2*P[2,1] + (f33-PD)**2*P[2,2], H2*PD*(1-PD))]
    ans = sympy.solve(eqs,[f12, f13, f21, f23, f31, f32])
    f12, f13, f21, f23, f31, f32 = [], [], [], [], [], []
    for one_root in ans:
        one_root = [complex(item) for item in one_root]
        f12.append(one_root[0])
        f13.append(one_root[1])
        f21.append(one_root[2])
        f23.append(one_root[3])
        f31.append(one_root[4])
        f32.append(one_root[5])
    #
    if12 = abs(np.imag(f12))
    if13 = abs(np.imag(f13))
    if21 = abs(np.imag(f21))
    if23 = abs(np.imag(f23))
    if31 = abs(np.imag(f31))
    if32 = abs(np.imag(f32))
    # 。
    rf12 = np.round(np.real(f12),3)
    if rf12[0] == 0: rf12[0] = 0
    if rf12[1] == 0: rf12[1] = 0
    rf13 = np.round(np.real(f13),3)
    if rf13[0] == 0: rf13[0] = 0
    if rf13[1] == 0: rf13[1] = 0
    rf21 = np.round(np.real(f21),3)
    if rf21[0] == 0: rf21[0] = 0
    if rf21[1] == 0: rf21[1] = 0
    rf23 = np.round(np.real(f23),3)
    if rf23[0] == 0: rf23[0] = 0
    if rf23[1] == 0: rf23[1] = 0
    rf31 = np.round(np.real(f31),3)
    if rf31[0] == 0: rf31[0] = 0
    if rf31[1] == 0: rf31[1] = 0
    rf32 = np.round(np.real(f32),3)
    if rf32[0] == 0: rf32[0] = 0
    if rf32[1] == 0: rf32[1] = 0
    # compare imag
    tag = np.zeros((2,1))
    for i in range(2):
        if (if12[i] > veracity) or (if13[i] > veracity) or (if21[i] > veracity)\
            or (if23[i] > veracity) or (if31[i] > veracity) or (if32[i] > veracity): 
            tag[i,0] = 1
    # compare real
    for i in range(2):
        if ((rf12[i] > 1) or (rf12[i] < 0)) or ((rf13[i] > 1) or (rf13[i] < 0))\
            or ((rf21[i] > 1) or (rf21[i] < 0)) or ((rf23[i] > 1) or (rf23[i] < 0))\
            or ((rf31[i] > 1) or (rf31[i] < 0)) or ((rf32[i] > 1) or (rf32[i] < 0)):
            tag[i,0] = 1
    # tag
    if (tag[0,0] == 1) and (tag[1,0] == 1):
        num = 0
        Pure = []
    elif ((tag[0,0] == 0) and (tag[1,0] == 1)) or ((tag[0,0] == 1) and (tag[1,0] == 0)):
        if tag[0,0] == 0: i = 0
        else: i = 1
        num = 1
        Pure = [[[np.array(['AABB: '+str(f11)])], [np.array(['AABb: '+str(rf12[0])])], [np.array(['AAbb: '+str(rf13[0])])],\
                [np.array(['AaBB: '+str(rf21[0])])], [np.array(['AaBb: '+str(f22)])], [np.array(['Aabb: '+str(rf23[0])])],\
                [np.array(['aaBB: '+str(rf31[0])])], [np.array(['aaBb: '+str(rf32[0])])], [np.array(['aabb: '+str(f33)])]]]
    elif (tag[0,0] == 0) and (tag[1,0] == 0):
        if (rf12[0] == rf12[1]) and (rf13[0] == rf13[1]) and (rf21[0] == rf21[1])\
            and (rf23[0] == rf23[1]) and (rf31[0] == rf31[1]) and (rf32[0] == rf32[1]):
            num = 1
            Pure = [[[np.array(['AABB: '+str(f11)])], [np.array(['AABb: '+str(rf12[0])])], [np.array(['AAbb: '+str(rf13[0])])],\
                    [np.array(['AaBB: '+str(rf21[0])])], [np.array(['AaBb: '+str(f22)])], [np.array(['Aabb: '+str(rf23[0])])],\
                    [np.array(['aaBB: '+str(rf31[0])])], [np.array(['aaBb: '+str(rf32[0])])], [np.array(['aabb: '+str(f33)])]]] 
        else:
            num = 2
            Pure = [[], []]
            Pure[0] = [[np.array(['AABB: '+str(f11)])], [np.array(['AABb: '+str(rf12[0])])], [np.array(['AAbb: '+str(rf13[0])])],\
                    [np.array(['AaBB: '+str(rf21[0])])], [np.array(['AaBb: '+str(f22)])], [np.array(['Aabb: '+str(rf23[0])])],\
                    [np.array(['aaBB: '+str(rf31[0])])], [np.array(['aaBb: '+str(rf32[0])])], [np.array(['aabb: '+str(f33)])]]
            Pure[1] = [[np.array(['AABB: '+str(f11)])], [np.array(['AABb: '+str(rf12[1])])], [np.array(['AAbb: '+str(rf13[1])])],\
                    [np.array(['AaBB: '+str(rf21[1])])], [np.array(['AaBb: '+str(f22)])], [np.array(['Aabb: '+str(rf23[1])])],\
                    [np.array(['aaBB: '+str(rf31[1])])], [np.array(['aaBb: '+str(rf32[1])])], [np.array(['aabb: '+str(f33)])]]
    return num, Pure

# res1/res2
def RelativeRisk(ModelInfo,SelectModel):
    # Calculate the function of phase to external visibility
    freq = np.zeros((ModelInfo[SelectModel-1][2], 3))
    for i in range(ModelInfo[SelectModel-1][2]):
        freq[i,:] = [(1-ModelInfo[SelectModel-1][3][i])**2, 2*(1-ModelInfo[SelectModel-1][3][i])*(ModelInfo[SelectModel-1][3][i]), (ModelInfo[SelectModel-1][3][i])**2]
    Combin_Freq=np.zeros((3**ModelInfo[SelectModel-1][2], 1))
    if ModelInfo[SelectModel-1][2] == 1:
        Combin_Freq = np.transpose(freq)
    elif ModelInfo[SelectModel-1][2] == 2:
        Combin_Freq = (np.transpose([freq[0]])*[freq[1]]).reshape(len(freq[0])*len(freq[1]) ,1)
    elif ModelInfo[SelectModel-1][2] == 3:
        Combin_Freq = ((np.transpose([freq[0]])*[freq[1]]).reshape(len(freq[0])*len(freq[1]) ,1)*[freq[2]])\
            .reshape(len(freq[0])*len(freq[1])*len(freq[2]) ,1)
    elif ModelInfo[SelectModel-1][2] == 4:
        Combin_Freq = (((np.transpose([freq[0]])*[freq[1]]).reshape(len(freq[0])*len(freq[1]) ,1)*[freq[2]])\
            .reshape(len(freq[0])*len(freq[1])*len(freq[2]) ,1)*[freq[3]]).reshape(len(freq[0])*len(freq[1])*len(freq[2])*len(freq[3]) ,1)
    f = sympy.symbols('f')
    b = sympy.symbols('b')
    RTable = []
    for i in range(3**ModelInfo[SelectModel-1][2]):
        RTable.append(ModelInfo[SelectModel-1][1][i][(ModelInfo[SelectModel-1][1][i].find(':'))+2: ])

    # eq1
    eq1 = 0
    for i in range(3**ModelInfo[SelectModel-1][2]):
        eq1 = eq1 + eval(RTable[i])*Combin_Freq[i,0]
    eq1 = eq1*b
    eq1 = sympy.simplify(eq1) - ModelInfo[SelectModel-1][4]

    # eq2
    if int(ModelInfo[SelectModel-1][0]) == 2:
        eq2 = 0
        for i in range(3**ModelInfo[SelectModel-1][2]):
            eq2 = eq2 + (b*eval(RTable[i])-eq1)*(b*eval(RTable[i])-eq1)*Combin_Freq[i,0]
        eq2 = sympy.simplify(eq2)/(eq1*(1-eq1))-ModelInfo[SelectModel-1][5]
        eq2 = sympy.simplify(eq2)
    else:
        PD_AA, PD_Aa, PND_AA, PND_Aa = 0, 0, 0, 0
        k = ModelInfo[SelectModel-1][2] - 1
        for i in range(3**k):
            PD_AA = PD_AA + eval(RTable[i])*(Combin_Freq[i,0] + Combin_Freq[3**k+i,0] + Combin_Freq[2*3**k+i,0])
            PD_Aa = PD_Aa + eval(RTable[3**k+i])*(Combin_Freq[i,0] + Combin_Freq[3**k+i,0] + Combin_Freq[2*3**k+i,0])
            PND_AA = PND_AA + (1-b*eval(RTable[i]))*(Combin_Freq[i,0] + Combin_Freq[3**k+i,0] + Combin_Freq[2*3**k+i,0])
            PND_Aa = PND_Aa + (1-b*eval(RTable[3**k+i]))*(Combin_Freq[i,0] + Combin_Freq[3**k+i,0] + Combin_Freq[2*3**k+i,0])
        eq2 = (PD_Aa/PD_AA)/(PND_Aa/PND_AA)-1-ModelInfo[SelectModel-1][6]
    eqs = [sympy.Eq(eq1, 0),sympy.Eq(eq2, 0)]
    ans = sympy.solve(eqs,[f,b])   # solution of equations
    if len(ans) == 0:
        RTable = []
        return RTable
    Baseline, Relative = [], []
    for each_root in ans:
        each_root = [complex(item) for item in each_root]
        Baseline.append(each_root[1])
        Relative.append(each_root[0])
    ifBaseline = abs(np.imag(Baseline))
    ifRelative = abs(np.imag(Relative))
    rfBaseline = np.round(np.real(Baseline).astype('float'),3)
    rfRelative = np.round(np.real(Relative).astype('float'),3)
    tag = len(ans)*[0]
    for i in range(len(ans)):
        if (ifBaseline[i] > 0.01) or (ifRelative[i] > 0.01) or (rfBaseline[i] < 0) or (rfRelative[i] < 0):
            tag[i] = 1
    RealSolution = tag.index(0) if 0 in tag else -1
    if RealSolution == -1:
        RTable = []
        return RTable
    b = rfBaseline[RealSolution]
    f = rfRelative[RealSolution]
    for i in range(len(RTable)):
        RTable[i] = b * eval(RTable[i])
    return RTable

#res3
def nfold(s):
    n = len(s)
    if n == 2:
        A = np.meshgrid(s[0], s[1]) 
    if n == 3:
        A = np.meshgrid(s[1], s[2], s[0]) 
    if n == 4:
        A = np.meshgrid(s[2], s[3], s[1], s[0]) 
    if n == 5:
        A = np.meshgrid(s[3], s[4], s[2], s[1], s[0]) 
    for i in range(n):
        A[i] = A[i].reshape(3**n,1,order='F')
    return A

def genotype_probabilities(mafs):
    m = mafs
    M = [(1-index) for index in m]
    s = [[0 for index in range(3)] for index in range(len(m))]
    for i in range(len(m)):
        s[i][0], s[i][1], s[i][2] = M[i]**2, 2*M[i]*m[i], m[i]**2
    A = nfold(s)
    p = [1 for index in range(3**len(s))]
    for index in range(3**len(s)):
        for j in range(len(s)):
            p[index] = p[index] * A[j][index][0]
    # print(p)
    return p

# res3-prevalence Model
def find_max_prevalence(Info):
    # print('Info', Info)
    mafs = Info[3]
    h = Info[5]
    x, y = sympy.symbols('x y')

    def heritability(mafs):
        gp = genotype_probabilities(mafs)
        penetrance = []
        for i in range(3**Info[2]):
            penetrance.append(Info[1][i][(Info[1][i].find(':'))+2: ])
        #print('penetrance', penetrance)
        x, y = sympy.symbols('x y')
        p = 0
        for i in range(3**Info[2]):
            p = p + eval(penetrance[i])*gp[i]
        p = sp.nsimplify(p)
        print('ppp', p)
        h = 0
        for i in range(3**Info[2]):
            h = h + ((eval(penetrance[i])-p)**2*gp[i])
        h = h/(p*(1-p))

        return h, penetrance

    c1,  penetrance = heritability(mafs)
    eq1 = c1 - h
    eq2 = eval(max(penetrance)) - 1
    #print('eq1', eq1)
    #print('eq2', eq2)
    eqs = [sympy.Eq(eq1, 0),sympy.Eq(eq2, 0)]
    ans = sympy.solve(eqs,[x,y],manual=True,rational=False)
    #print('ans', ans)
    if len(ans) == 0:
        pt = []
        return pt
    else:
        x_ans = ans[0][0]
        y_ans = ans[0][1]
    pt = [0 for index in range(3**Info[2])]
    for i in range(3**Info[2]):
        pt[i] = (eval(penetrance[i])).subs(x,x_ans).subs(y,y_ans)
    # print('pt', pt)
    print('H2=', h)
    print('xans', x_ans)
    print('yans', y_ans)
    return pt

# res3-heritability
def find_max_heritability(Info):
    # print('Info', Info)
    mafs = Info[3]
    p = Info[5]
    x, y = sympy.symbols('x y')

    def prevalence(mafs):
        gp = genotype_probabilities(mafs)
        penetrance = []
        for i in range(3**Info[2]):
            penetrance.append(Info[1][i][(Info[1][i].find(':'))+2: ])
        x, y = sympy.symbols('x y')
        p = 0
        for i in range(3**Info[2]):
            p = p + eval(penetrance[i])*gp[i]
        #print('pd', p)
        return p, penetrance

    c1,  penetrance = prevalence(mafs)
    eq1 = c1 - p
    eq2 = eval(max(penetrance)) - 1
    eqs = [sympy.Eq(eq1, 0),sympy.Eq(eq2, 0)]
    ans = sympy.solve(eqs,[x,y],manual=True,rational=False)   # 方程组的解
    # print('ans', ans)
    if len(ans) == 0:
        pt = []
        return pt
    else:
        x_ans = ans[0][0]
        y_ans = ans[0][1]
    pt = [0 for index in range(3**Info[2])]
    for i in range(3**Info[2]):
        pt[i] = (eval(penetrance[i])).subs(x,x_ans).subs(y,y_ans)
    # print('pt', pt)
    #print('hhh', h)
    print('p(D)=', p)
    print('xans', x_ans)
    print('yans', y_ans)
    return pt


def genotype_probabilities(mafs):
    # print(mafs)
    n = len(mafs)
    m = [float(c) for c in mafs]
    M = [float(1-c) for c in m]
    s = [0 for index in range(n)]
    for k in range(n):
        s[k] = [M[k]**2, 2*M[k]*m[k], m[k]**2]
    p = []
    for elem in product(*s):
        result = 1
        for x in elem:
            result = result * x  
        p.append(result)
    return p

def pre_seidel(A,b,n):
    A_array = np.array(A)
    b_array = np.array(b)
    b = np.dot(np.transpose(A_array), b_array)
    A = np.dot(np.transpose(A_array), A_array)
    D = np.diag(np.diag(A))
    L = np.tril(A, k = -1)
    U = np.triu(A, k = 1)
    #B2 = np.dot(-inv((D + L).astype(np.float)), U)
    #g2 = np.dot(inv((D + L).astype(np.float)), b)
    B2 = np.dot(-inv((D + L).astype(float)), U)
    g2 = np.dot(inv((D + L).astype(float)), b)
    eigen_value, eigen_vector = eig(np.mat(B2, dtype=float))
    radies = max(abs(eigen_value))
    x = [0 for index in range(len(b))]
    error = 0.0001
    count = 0
    while 1:
        tmp = np.dot(B2, x)+g2
        if max(abs(tmp-x)) < error:
            break
        x = tmp
        count += 1
    # print(x)
    return x

def verification(x_result,n,D):
    PD = [[0 for index in range(3)] for index in range(n)]
    if n == 2:
        k = n -1
        for i in range(3**k):
            PD[0][0] += x_result[i] * (D[i]+D[3**k+i]+D[2*3**k+i])
            PD[0][1] += x_result[3**k+i] * (D[i]+D[3**k+i]+D[2*3**k+i])
            PD[0][2] += x_result[2*3**k+i] * (D[i]+D[3**k+i]+D[2*3**k+i])
        for j in range(3**k):
            i = 3*j + 1
            PD[1][0] += x_result[i-1] * (D[i-1]+D[i]+D[i+1])
            PD[1][1] += x_result[i] * (D[i-1]+D[i]+D[i+1])
            PD[1][2] += x_result[i+1] * (D[i-1]+D[i]+D[i+1])
        # print(PD)

    if n == 3:
        k = n -1
        for i in range(3**k):
            PD[0][0] += x_result[i] * (D[i]+D[3**k+i]+D[2*3**k+i])
            PD[0][1] += x_result[3**k+i] * (D[i]+D[3**k+i]+D[2*3**k+i])
            PD[0][2] += x_result[2*3**k+i] * (D[i]+D[3**k+i]+D[2*3**k+i])
        for o in range(3):
            for j in range(1,3**(k-1)+1):
                i = o*3**k + j
                PD[1][0] += x_result[i-1] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])
                PD[1][1] += x_result[3**(k-1)+i-1] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])
                PD[1][2] += x_result[2*3**(k-1)+i-1] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])       
        for o in range(3):
            for j in range(k+1):
                i = o*3**k + 3*j + 1
                PD[2][0] += x_result[i-1] * (D[i-1]+D[i]+D[i+1])
                PD[2][1] += x_result[i] * (D[i-1]+D[i]+D[i+1])
                PD[2][2] += x_result[i+1] * (D[i-1]+D[i]+D[i+1])
        # print(PD)

    if n == 4:
        k = n -1
        for i in range(3**k):
            PD[0][0] += x_result[i] * (D[i]+D[3**k+i]+D[2*3**k+i])
            PD[0][1] += x_result[3**k+i] * (D[i]+D[3**k+i]+D[2*3**k+i])
            PD[0][2] += x_result[2*3**k+i] * (D[i]+D[3**k+i]+D[2*3**k+i])
        for o in range(3):
            for j in range(1,3**(k-1)+1):
                i = o*3**k + j
                PD[1][0] += x_result[i-1] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])
                PD[1][1] += x_result[3**(k-1)+i-1] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])
                PD[1][2] += x_result[2*3**(k-1)+i-1] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])       
        for o in range(3**(k-1)):
            for j in range(1,4):
                i = o*3**(k-1) + j
                PD[2][0] += x_result[i-1] * (D[i-1] + D[3**1+i-1] + D[2*3**1+i-1])
                PD[2][1] += x_result[1*3+i-1] * (D[i-1] + D[3**1+i-1] + D[2*3**1+i-1])
                PD[2][2] += x_result[2*3+i-1] * (D[i-1] + D[3**1+i-1] + D[2*3**1+i-1])
        for o in range(3):
            for j in range(k+1):
                i = o*3**k + 3*j + 1
                PD[3][0] += x_result[i-1] * (D[i-1]+D[i]+D[i+1])
                PD[3][1] += x_result[i] * (D[i-1]+D[i]+D[i+1])
                PD[3][2] += x_result[i+1] * (D[i-1]+D[i]+D[i+1])
        # print(PD)

    if n == 5:
        k = n -1
        for i in range(3**k):
            PD[0][0] += x_result[i] * (D[i]+D[3**k+i]+D[2*3**k+i])
            PD[0][1] += x_result[3**k+i] * (D[i]+D[3**k+i]+D[2*3**k+i])
            PD[0][2] += x_result[2*3**k+i] * (D[i]+D[3**k+i]+D[2*3**k+i])
        for o in range(3):
            for j in range(1,3**(k-1)+1):
                i = o*3**k + j
                PD[1][0] += x_result[i-1] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])
                PD[1][1] += x_result[3**(k-1)+i-1] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])
                PD[1][2] += x_result[2*3**(k-1)+i-1] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])       
        for o in range(3**(n-3)):
            for j in range(1,3**2+1):
                i = o*3**(n-2) + j
                PD[2][0] += x_result[i-1] * (D[i-1] + D[3**(k-2)+i-1] + D[2*3**(k-2)+i-1])
                PD[2][1] += x_result[3**(k-2)+i-1] * (D[i-1] + D[3**(k-2)+i-1] + D[2*3**(k-2)+i-1])
                PD[2][2] += x_result[2*3**(k-2)+i-1] * (D[i-1] + D[3**(k-2)+i-1] + D[2*3**(k-2)+i-1])
        for o in range(3**(k-1)):
            for j in range(1,4):
                i = o*3**(n-3) + j
                PD[3][0] += x_result[i-1] * (D[i-1] + D[3**(k-3)+i-1] + D[2*3**(k-3)+i-1])
                PD[3][1] += x_result[3**(k-3)+i-1] * (D[i-1] + D[3**(k-3)+i-1] + D[2*3**(k-3)+i-1])
                PD[3][2] += x_result[2*3**(k-3)+i-1] * (D[i-1] + D[3**(k-3)+i-1] + D[2*3**(k-3)+i-1])
        for o in range(3**k):
            j = 1
            i = j + o*3**(n-4)
            PD[4][0] += x_result[i-1] * (D[i-1]+D[i]+D[i+1])
            PD[4][1] += x_result[i] * (D[i-1]+D[i]+D[i+1])
            PD[4][2] += x_result[i+1] * (D[i-1]+D[i]+D[i+1])
        # print(PD)

    pd = np.dot(D, x_result)
    h = 0
    for i in range(3**n):
        h += np.dot(D[i], (x_result[i] - pd)**2)
    h = h/(pd*(1-pd))
    if (max(list(map(abs, [(pd-i) for i in min(PD)])))<0.05) and (max(list(map(abs, [(pd-i) for i in max(PD)])))<0.05):
        v = 1
    else:
        v = 0
    return v, pd, h

# pure2 H2 = 0
def pure2_calculation(MAF, PD, H2, n):
    k = n-1
    for i in range(3**n):
        globals()['x'+str(i+1)] = sympy.symbols('x'+str(i+1))
    D = genotype_probabilities(MAF)
    
    ################################################################################ pure2二阶 ######################################################################
    if n == 2:
        # PD_AA, PD_Aa, PD_aa
        PD_AA, PD_Aa, PD_aa = 0, 0, 0
        for i in range(3**k):
            PD_AA += globals()['x' + str(i+1)] * (D[i]+D[3**k+i]+D[2*3**k+i])
            PD_Aa += globals()['x' + str(3**k+i+1)] * (D[i]+D[3**k+i]+D[2*3**k+i])
            PD_aa += globals()['x' + str(2*3**k+i+1)] * (D[i]+D[3**k+i]+D[2*3**k+i])
        PD_AA -= PD
        PD_Aa -= PD
        PD_aa -= PD

        # PD_BB, PD_Bb, PD_bb
        PD_BB, PD_Bb, PD_bb = 0, 0, 0
        for j in range(3**k):
            i = 3*j + 1
            PD_BB += globals()['x' + str(i)] * (D[i-1]+D[i]+D[i+1])
            PD_Bb += globals()['x' + str(i+1)] * (D[i-1]+D[i]+D[i+1])
            PD_bb += globals()['x' + str(i+2)] * (D[i-1]+D[i]+D[i+1])
        PD_BB -= PD
        PD_Bb -= PD
        PD_bb -= PD
        
        # f10
        f10 = -PD
        for m in range(3**n):
            f10 += D[m] * globals()['x'+str(m+1)]

        # E
        E = [[0 for index in range(3**n)] for index in range(3*n+1)]
        funcs = sympy.Matrix([PD_AA, PD_Aa, PD_aa, PD_BB, PD_Bb, PD_bb, f10])
        args = sympy.Matrix([globals()['x' + str(index+1)] for index in range(3**n)])
        res = funcs.jacobian(args)
        for j in range(3*n+1):  
            E[j] = np.array(res[j,:]).astype(np.float64)[0].tolist()        

        # F
        F = [PD for index in range(3*n+1)]

        # x_result
        x_result_all = np.linalg.lstsq(E, F)
        x_result = x_result_all[0]
        for i in range(len(x_result)):
            if x_result[i] < 0:
                x_result[i] = 0         
        print('x_result', x_result)
    
    ################################################################################ pure2三阶 ######################################################################
    if n == 3:
        # PD_AA, PD_Aa, PD_aa
        PD_AA, PD_Aa, PD_aa = 0, 0, 0
        for i in range(3**k):
            PD_AA += globals()['x' + str(i+1)] * (D[i] + D[3**k+i] + D[2*3**k+i])
            PD_Aa += globals()['x' + str(3**k+i+1)] * (D[i] + D[3**k+i] + D[2*3**k+i])
            PD_aa += globals()['x' + str(2*3**k+i+1)] * (D[i] + D[3**k+i] + D[2*3**k+i])
        PD_AA -= PD
        PD_Aa -= PD
        PD_aa -= PD

        # PD_BB, PD_Bb, PD_bb
        PD_BB, PD_Bb, PD_bb = 0, 0, 0
        for o in range(3):
            for j in range(1,3**(k-1)+1):
                i = o*3**k + j
                PD_BB += globals()['x' + str(i)] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])
                PD_Bb += globals()['x' + str(3**(k-1)+i)] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])
                PD_bb += globals()['x' + str(2*3**(k-1)+i)] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])
        PD_BB -= PD
        PD_Bb -= PD
        PD_bb -= PD

        # PD_CC, PD_Cc, PD_cc
        PD_CC, PD_Cc, PD_cc = 0, 0, 0
        for o in range(3):
            for j in range(k+1):
                i = o*3**k + 3*j + 1
                PD_CC += globals()['x' + str(i)] * (D[i-1]+D[i]+D[i+1])
                PD_Cc += globals()['x' + str(1+i)] * (D[i-1]+D[i]+D[i+1])
                PD_cc += globals()['x' + str(2+i)] * (D[i-1]+D[i]+D[i+1])
        PD_CC -= PD
        PD_Cc -= PD
        PD_cc -= PD

        # f10
        f10 = -PD
        for m in range(3**n):
            f10 += D[m] * globals()['x'+str(m+1)]

        # E
        E = [[0 for index in range(3**n)] for index in range(3*n+1)]
        funcs = sympy.Matrix([PD_AA, PD_Aa, PD_aa, PD_BB, PD_Bb, PD_bb, PD_CC, PD_Cc, PD_cc, f10])
        args = sympy.Matrix([globals()['x' + str(index+1)] for index in range(3**n)])
        res = funcs.jacobian(args)
        for j in range(3*n+1):  
            E[j] = np.array(res[j,:]).astype(np.float64)[0].tolist()        

        # F
        F = [PD for index in range(3*n+1)]

        # x_result
        x_result_all = np.linalg.lstsq(E, F)
        x_result = x_result_all[0]
        for i in range(len(x_result)):
            if x_result[i] < 0:
                x_result[i] = 0         
        #print('x_result', x_result)
    
    ################################################################################ pure2四阶 ######################################################################
    if n == 4:
        # PD_AA, PD_Aa, PD_aa
        PD_AA, PD_Aa, PD_aa = 0, 0, 0
        for i in range(3**k):
            PD_AA += globals()['x' + str(i+1)] * (D[i] + D[3**k+i] + D[2*3**k+i])
            PD_Aa += globals()['x' + str(3**k+i+1)] * (D[i] + D[3**k+i] + D[2*3**k+i])
            PD_aa += globals()['x' + str(2*3**k+i+1)] * (D[i] + D[3**k+i] + D[2*3**k+i])
        PD_AA -= PD
        PD_Aa -= PD
        PD_aa -= PD

        # PD_BB, PD_Bb, PD_bb
        PD_BB, PD_Bb, PD_bb = 0, 0, 0
        for o in range(3):
            for j in range(1,3**(k-1)+1):
                i = o*3**k + j
                PD_BB += globals()['x' + str(i)] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])
                PD_Bb += globals()['x' + str(3**(k-1)+i)] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])
                PD_bb += globals()['x' + str(2*3**(k-1)+i)] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])
        PD_BB -= PD
        PD_Bb -= PD
        PD_bb -= PD

        # PD_CC, PD_Cc, PD_cc
        PD_CC, PD_Cc, PD_cc = 0, 0, 0
        for o in range(3**(k-1)):
            for j in range(1,4):
                i = o*3**(k-1) + j
                PD_CC += globals()['x' + str(i)] * (D[i-1] + D[3**1+i-1] + D[2*3**1+i-1])
                PD_Cc += globals()['x' + str(1*3+i)] * (D[i-1] + D[3**1+i-1] + D[2*3**1+i-1])
                PD_cc += globals()['x' + str(2*3+i)] * (D[i-1] + D[3**1+i-1] + D[2*3**1+i-1])
        PD_CC -= PD
        PD_Cc -= PD
        PD_cc -= PD

        # PD_DD, PD_Dd, PD_dd
        PD_DD, PD_Dd, PD_dd = 0, 0, 0
        for o in range(3):
            for j in range(k+1):
                i = o*3**k + 3*j + 1
                PD_DD += globals()['x' + str(i)] * (D[i-1]+D[i]+D[i+1])
                PD_Dd += globals()['x' + str(1+i)] * (D[i-1]+D[i]+D[i+1])
                PD_dd += globals()['x' + str(2+i)] * (D[i-1]+D[i]+D[i+1])
        PD_DD -= PD
        PD_Dd -= PD
        PD_dd -= PD

        # f10
        f10 = -PD
        for m in range(3**n):
            f10 += D[m] * globals()['x'+str(m+1)]

        # E
        E = [[0 for index in range(3**n)] for index in range(3*n+1)]
        funcs = sympy.Matrix([PD_AA, PD_Aa, PD_aa, PD_BB, PD_Bb, PD_bb, PD_CC, PD_Cc, PD_cc, PD_DD, PD_Dd, PD_dd, f10])
        args = sympy.Matrix([globals()['x' + str(index+1)] for index in range(3**n)])
        res = funcs.jacobian(args)
        for j in range(3*n+1):  
            E[j] = np.array(res[j,:]).astype(np.float64)[0].tolist()        

        # F
        F = [PD for index in range(3*n+1)]

        # x_result
        x_result_all = np.linalg.lstsq(E, F)
        x_result = x_result_all[0]
        for i in range(len(x_result)):
            if x_result[i] < 0:
                x_result[i] = 0         
        # print('x_result', x_result)
    
    ################################################################################ pure2五阶 ######################################################################
    if n == 5:
        # PD_AA, PD_Aa, PD_aa
        PD_AA, PD_Aa, PD_aa = 0, 0, 0
        for i in range(3**k):
            PD_AA += globals()['x' + str(i+1)] * (D[i] + D[3**k+i] + D[2*3**k+i])
            PD_Aa += globals()['x' + str(3**k+i+1)] * (D[i] + D[3**k+i] + D[2*3**k+i])
            PD_aa += globals()['x' + str(2*3**k+i+1)] * (D[i] + D[3**k+i] + D[2*3**k+i])
        PD_AA -= PD
        PD_Aa -= PD
        PD_aa -= PD

        # PD_BB, PD_Bb, PD_bb
        PD_BB, PD_Bb, PD_bb = 0, 0, 0
        for o in range(3):
            for j in range(1,3**(k-1)+1):
                i = o*3**k + j
                PD_BB += globals()['x' + str(i)] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])
                PD_Bb += globals()['x' + str(3**(k-1)+i)] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])
                PD_bb += globals()['x' + str(2*3**(k-1)+i)] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])
        PD_BB -= PD
        PD_Bb -= PD
        PD_bb -= PD

        # PD_CC, PD_Cc, PD_cc
        PD_CC, PD_Cc, PD_cc = 0, 0, 0
        for o in range(3**(n-3)):
            for j in range(1,3**2+1):
                i = o*3**(n-2) + j
                PD_CC += globals()['x' + str(i)] * (D[i-1] + D[3**(k-2)+i-1] + D[2*3**(k-2)+i-1])
                PD_Cc += globals()['x' + str(3**(k-2)+i)] * (D[i-1] + D[3**(k-2)+i-1] + D[2*3**(k-2)+i-1])
                PD_cc += globals()['x' + str(2*3**(k-2)+i)] * (D[i-1] + D[3**(k-2)+i-1] + D[2*3**(k-2)+i-1])
        PD_CC -= PD
        PD_Cc -= PD
        PD_cc -= PD

        # PD_DD, PD_Dd, PD_dd
        PD_DD, PD_Dd, PD_dd = 0, 0, 0
        for o in range(3**(k-1)):
            for j in range(1,4):
                i = o*3**(n-3) + j
                PD_DD += globals()['x' + str(i)] * (D[i-1] + D[3**(k-3)+i-1] + D[2*3**(k-3)+i-1])
                PD_Dd += globals()['x' + str(3**(k-3)+i)] * (D[i-1] + D[3**(k-3)+i-1] + D[2*3**(k-3)+i-1])
                PD_dd += globals()['x' + str(2*3**(k-3)+i)] * (D[i-1] + D[3**(k-3)+i-1] + D[2*3**(k-3)+i-1])
        PD_DD -= PD
        PD_Dd -= PD
        PD_dd -= PD

        # PD_EE, PD_Ee, PD_ee
        PD_EE, PD_Ee, PD_ee = 0, 0, 0
        for o in range(3**k):
            j = 1
            i = j + o*3**(n-4)
            PD_EE += globals()['x' + str(i)] * (D[i-1]+D[i]+D[i+1])
            PD_Ee += globals()['x' + str(1+i)] * (D[i-1]+D[i]+D[i+1])
            PD_ee += globals()['x' + str(2+i)] * (D[i-1]+D[i]+D[i+1])
        PD_EE -= PD
        PD_Ee -= PD
        PD_ee -= PD

        # f10
        f10 = -PD
        for m in range(3**n):
            f10 += D[m] * globals()['x'+str(m+1)]

        # E
        E = [[0 for index in range(3**n)] for index in range(3*n+1)]
        funcs = sympy.Matrix([PD_AA, PD_Aa, PD_aa, PD_BB, PD_Bb, PD_bb, PD_CC, PD_Cc, PD_cc, PD_DD, PD_Dd, PD_dd, PD_EE, PD_Ee, PD_ee, f10])
        args = sympy.Matrix([globals()['x' + str(index+1)] for index in range(3**n)])
        res = funcs.jacobian(args)
        for j in range(3*n+1):  
            E[j] = np.array(res[j,:]).astype(np.float64)[0].tolist()        

        # F
        F = [PD for index in range(3*n+1)]

        # x_result
        x_result_all = np.linalg.lstsq(E, F)
        x_result = x_result_all[0]
        for i in range(len(x_result)):
            if x_result[i] < 0:
                x_result[i] = 0         
        # print('x_result', x_result)    
    
    v, pd, h = verification(x_result, n, D)

    return x_result, v, pd, h

# pure3
def pure3_calculation(MAF, PD, H2, n):
    k = n-1
    for i in range(3**n):
        globals()['x'+str(i+1)] = sympy.symbols('x'+str(i+1))
    D = genotype_probabilities(MAF)
    ################################################################################ pure3二阶 ######################################################################
    if n == 2:
        # PD_AA, PD_Aa, PD_aa
        PD_AA, PD_Aa, PD_aa = 0, 0, 0
        for i in range(3**k):
            PD_AA += globals()['x' + str(i+1)] * (D[i]+D[3**k+i]+D[2*3**k+i])
            PD_Aa += globals()['x' + str(3**k+i+1)] * (D[i]+D[3**k+i]+D[2*3**k+i])
            PD_aa += globals()['x' + str(2*3**k+i+1)] * (D[i]+D[3**k+i]+D[2*3**k+i])
        PD_AA -= PD
        PD_Aa -= PD
        PD_aa -= PD

        # PD_BB, PD_Bb, PD_bb
        PD_BB, PD_Bb, PD_bb = 0, 0, 0
        for j in range(3**k):
            i = 3*j + 1
            PD_BB += globals()['x' + str(i)] * (D[i-1]+D[i]+D[i+1])
            PD_Bb += globals()['x' + str(i+1)] * (D[i-1]+D[i]+D[i+1])
            PD_bb += globals()['x' + str(i+2)] * (D[i-1]+D[i]+D[i+1])
        PD_BB -= PD
        PD_Bb -= PD
        PD_bb -= PD
        
        # f10
        f10 = -PD
        for m in range(3**n):
            f10 += D[m] * globals()['x'+str(m+1)]

        # f11
        f11 = 0
        for i in range(3**n):
            f11 += D[i]*((globals()['x' + str(i+1)]-PD)**2)
        f11 -= H2*PD*(1-PD)

        # f 
        f = [PD_AA, PD_Aa, PD_aa, PD_BB, PD_Bb, PD_bb, f10, f11]

        x0 = [0 for index in range(9)]
        error_dxk = 0.01
        error_fkk = 0.05
        num = 10

        for i in range(num):
            # Ak
            Ak = [[0 for index in range(3**n)] for index in range(3*n+2)]
            funcs = sympy.Matrix([PD_AA, PD_Aa, PD_aa, PD_BB, PD_Bb, PD_bb, f10, f11])
            args = sympy.Matrix([globals()['x' + str(index+1)] for index in range(3**n)])
            res = funcs.jacobian(args)
            for j in range(3*n+1):
                Ak[j] = np.array(res[j,:]).astype(np.float64)[0].tolist()
            for i in range(3**n):
                Ak[3*n+2-1][i] = res[3*n+2-1,i].subs([(globals()['x' + str(index+1)], x0[index]) for index in range(3**n)])

            # bk
            bk = [0 for index in range(3*n+2)]
            for z in range(3*n+2):
                bk[z] = f[z].subs([(globals()['x' + str(index+1)], x0[index]) for index in range(3**n)])

            # dxk
            dxk = pre_seidel(Ak,[(0-c) for c in bk],k)
            x0 += dxk

            # fkk
            fkk = [0 for index in range(3*n+2)]
            for z in range(3*n+2):
                fkk[z] = f[z].subs([(globals()['x' + str(index+1)], x0[index]) for index in range(3**n)])

            #ndxk = norm(np.array(dxk).astype(np.float), ord=2)
            #nfkk = norm(np.array(fkk).astype(np.float), ord=2)
            ndxk = norm(np.array(dxk).astype(float), ord=2)
            nfkk = norm(np.array(fkk).astype(float), ord=2)
            if (ndxk < error_dxk) or (nfkk < error_fkk):
                break
        
        # x_result
        x_result = x0
        for i in range(len(x_result)):
            if x_result[i] < 0:
                x_result[i] = 0         
        # print('x_result', x_result)           
    
    ################################################################################ pure3三阶 ######################################################################
    if n == 3:
        # PD_AA, PD_Aa, PD_aa
        PD_AA, PD_Aa, PD_aa = 0, 0, 0
        for i in range(3**k):
            PD_AA += globals()['x' + str(i+1)] * (D[i] + D[3**k+i] + D[2*3**k+i])
            PD_Aa += globals()['x' + str(3**k+i+1)] * (D[i] + D[3**k+i] + D[2*3**k+i])
            PD_aa += globals()['x' + str(2*3**k+i+1)] * (D[i] + D[3**k+i] + D[2*3**k+i])
        PD_AA -= PD
        PD_Aa -= PD
        PD_aa -= PD

        # PD_BB, PD_Bb, PD_bb
        PD_BB, PD_Bb, PD_bb = 0, 0, 0
        for o in range(3):
            for j in range(1,3**(k-1)+1):
                i = o*3**k + j
                PD_BB += globals()['x' + str(i)] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])
                PD_Bb += globals()['x' + str(3**(k-1)+i)] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])
                PD_bb += globals()['x' + str(2*3**(k-1)+i)] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])
        PD_BB -= PD
        PD_Bb -= PD
        PD_bb -= PD

        # PD_CC, PD_Cc, PD_cc
        PD_CC, PD_Cc, PD_cc = 0, 0, 0
        for o in range(3):
            for j in range(k+1):
                i = o*3**k + 3*j + 1
                PD_CC += globals()['x' + str(i)] * (D[i-1]+D[i]+D[i+1])
                PD_Cc += globals()['x' + str(1+i)] * (D[i-1]+D[i]+D[i+1])
                PD_cc += globals()['x' + str(2+i)] * (D[i-1]+D[i]+D[i+1])
        PD_CC -= PD
        PD_Cc -= PD
        PD_cc -= PD

        # f10
        f10 = -PD
        for m in range(3**n):
            f10 += D[m] * globals()['x'+str(m+1)]

        # f11
        f11 = 0
        for i in range(3**n):
            f11 += D[i]*((globals()['x' + str(i+1)]-PD)**2)
        f11 -= H2*PD*(1-PD)
        
        # f 
        f = [PD_AA, PD_Aa, PD_aa, PD_BB, PD_Bb, PD_bb, PD_CC, PD_Cc, PD_cc, f10, f11]
        
        x0 = [0 for index in range(3**n)]
        error_dxk = 0.05
        error_fkk = 0.05
        num = 10
        for i in range(num):
            # Ak
            Ak = [[0 for index in range(3**n)] for index in range(3*n+2)]
            funcs = sympy.Matrix([PD_AA, PD_Aa, PD_aa, PD_BB, PD_Bb, PD_bb, PD_CC, PD_Cc, PD_cc, f10, f11])
            args = sympy.Matrix([globals()['x' + str(index+1)] for index in range(3**n)])
            res = funcs.jacobian(args)
            for j in range(3*n+1):
                Ak[j] = np.array(res[j,:]).astype(np.float64)[0].tolist()
            for i in range(3**n):
                Ak[3*n+2-1][i] = res[3*n+2-1,i].subs([(globals()['x' + str(index+1)], x0[index]) for index in range(3**n)])

            # bk
            bk = [0 for index in range(3*n+2)]
            for z in range(3*n+2):
                bk[z] = f[z].subs([(globals()['x' + str(index+1)], x0[index]) for index in range(3**n)])

            # dxk
            dxk = pre_seidel(Ak,[(0-c) for c in bk],k)
            x0 += dxk

            # fkk
            fkk = [0 for index in range(3*n+2)]
            for z in range(3*n+2):
                fkk[z] = f[z].subs([(globals()['x' + str(index+1)], x0[index]) for index in range(3**n)])

            #ndxk = norm(np.array(dxk).astype(np.float), ord=2)
            #nfkk = norm(np.array(fkk).astype(np.float), ord=2)
            ndxk = norm(np.array(dxk).astype(float), ord=2)
            nfkk = norm(np.array(fkk).astype(float), ord=2)
            if (ndxk < error_dxk) or (nfkk < error_fkk):
                break
        
        # x_result
        x_result = x0
        for i in range(len(x_result)):
            if x_result[i] < 0:
                x_result[i] = 0         
        # print('x_result', x_result)
    
    ################################################################################ pure3四阶 ######################################################################
    if n == 4:
        # PD_AA, PD_Aa, PD_aa
        PD_AA, PD_Aa, PD_aa = 0, 0, 0
        for i in range(3**k):
            PD_AA += globals()['x' + str(i+1)] * (D[i] + D[3**k+i] + D[2*3**k+i])
            PD_Aa += globals()['x' + str(3**k+i+1)] * (D[i] + D[3**k+i] + D[2*3**k+i])
            PD_aa += globals()['x' + str(2*3**k+i+1)] * (D[i] + D[3**k+i] + D[2*3**k+i])
        PD_AA -= PD
        PD_Aa -= PD
        PD_aa -= PD

        # PD_BB, PD_Bb, PD_bb
        PD_BB, PD_Bb, PD_bb = 0, 0, 0
        for o in range(3):
            for j in range(1,3**(k-1)+1):
                i = o*3**k + j
                PD_BB += globals()['x' + str(i)] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])
                PD_Bb += globals()['x' + str(3**(k-1)+i)] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])
                PD_bb += globals()['x' + str(2*3**(k-1)+i)] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])
        PD_BB -= PD
        PD_Bb -= PD
        PD_bb -= PD

        # PD_CC, PD_Cc, PD_cc
        PD_CC, PD_Cc, PD_cc = 0, 0, 0
        for o in range(3**(k-1)):
            for j in range(1,4):
                i = o*3**(k-1) + j
                PD_CC += globals()['x' + str(i)] * (D[i-1] + D[3**1+i-1] + D[2*3**1+i-1])
                PD_Cc += globals()['x' + str(1*3+i)] * (D[i-1] + D[3**1+i-1] + D[2*3**1+i-1])
                PD_cc += globals()['x' + str(2*3+i)] * (D[i-1] + D[3**1+i-1] + D[2*3**1+i-1])
        PD_CC -= PD
        PD_Cc -= PD
        PD_cc -= PD

        # PD_DD, PD_Dd, PD_dd
        PD_DD, PD_Dd, PD_dd = 0, 0, 0
        for o in range(3):
            for j in range(k+1):
                i = o*3**k + 3*j + 1
                PD_DD += globals()['x' + str(i)] * (D[i-1]+D[i]+D[i+1])
                PD_Dd += globals()['x' + str(1+i)] * (D[i-1]+D[i]+D[i+1])
                PD_dd += globals()['x' + str(2+i)] * (D[i-1]+D[i]+D[i+1])
        PD_DD -= PD
        PD_Dd -= PD
        PD_dd -= PD

        # f10
        f10 = -PD
        for m in range(3**n):
            f10 += D[m] * globals()['x'+str(m+1)]

        # f11
        f11 = 0
        for i in range(3**n):
            f11 += D[i]*((globals()['x' + str(i+1)]-PD)**2)
        f11 -= H2*PD*(1-PD)
        
        # f 
        f = [PD_AA, PD_Aa, PD_aa, PD_BB, PD_Bb, PD_bb, PD_CC, PD_Cc, PD_cc, PD_DD, PD_Dd, PD_dd, f10, f11]

        x0 = [0 for index in range(3**n)]
        error_dxk = 0.03
        error_fkk = 0.03
        num = 10

        for i in range(num):
            # Ak
            Ak = [[0 for index in range(3**n)] for index in range(3*n+2)]
            funcs = sympy.Matrix([PD_AA, PD_Aa, PD_aa, PD_BB, PD_Bb, PD_bb, PD_CC, PD_Cc, PD_cc, PD_DD, PD_Dd, PD_dd, f10, f11])
            args = sympy.Matrix([globals()['x' + str(index+1)] for index in range(3**n)])
            res = funcs.jacobian(args)
            for j in range(3*n+1):
                Ak[j] = np.array(res[j,:]).astype(np.float64)[0].tolist()
            for i in range(3**n):
                Ak[3*n+2-1][i] = res[3*n+2-1,i].subs([(globals()['x' + str(index+1)], x0[index]) for index in range(3**n)])

            # bk
            bk = [0 for index in range(3*n+2)]
            for z in range(3*n+2):
                bk[z] = f[z].subs([(globals()['x' + str(index+1)], x0[index]) for index in range(3**n)])

            # dxk
            dxk = pre_seidel(Ak,[(0-c) for c in bk],i+1)
            x0 += dxk

            # fkk
            fkk = [0 for index in range(3*n+2)]
            for z in range(3*n+2):
                fkk[z] = f[z].subs([(globals()['x' + str(index+1)], x0[index]) for index in range(3**n)])

            #ndxk = norm(np.array(dxk).astype(np.float), ord=2)
            #nfkk = norm(np.array(fkk).astype(np.float), ord=2)
            ndxk = norm(np.array(dxk).astype(float), ord=2)
            nfkk = norm(np.array(fkk).astype(float), ord=2)
            if (ndxk < error_dxk) or (nfkk < error_fkk):
                break
        
        # x_result
        x_result = x0
        for i in range(len(x_result)):
            if x_result[i] < 0:
                x_result[i] = 0         
        # print('x_result', x_result)
    
    ################################################################################ pure3五阶 ######################################################################
    if n == 5:
        # PD_AA, PD_Aa, PD_aa
        PD_AA, PD_Aa, PD_aa = 0, 0, 0
        for i in range(3**k):
            PD_AA += globals()['x' + str(i+1)] * (D[i] + D[3**k+i] + D[2*3**k+i])
            PD_Aa += globals()['x' + str(3**k+i+1)] * (D[i] + D[3**k+i] + D[2*3**k+i])
            PD_aa += globals()['x' + str(2*3**k+i+1)] * (D[i] + D[3**k+i] + D[2*3**k+i])
        PD_AA -= PD
        PD_Aa -= PD
        PD_aa -= PD

        # PD_BB, PD_Bb, PD_bb
        PD_BB, PD_Bb, PD_bb = 0, 0, 0
        for o in range(3):
            for j in range(1,3**(k-1)+1):
                i = o*3**k + j
                PD_BB += globals()['x' + str(i)] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])
                PD_Bb += globals()['x' + str(3**(k-1)+i)] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])
                PD_bb += globals()['x' + str(2*3**(k-1)+i)] * (D[i-1] + D[3**(k-1)+i-1] + D[2*3**(k-1)+i-1])
        PD_BB -= PD
        PD_Bb -= PD
        PD_bb -= PD

        # PD_CC, PD_Cc, PD_cc
        PD_CC, PD_Cc, PD_cc = 0, 0, 0
        for o in range(3**(n-3)):
            for j in range(1,3**2+1):
                i = o*3**(n-2) + j
                PD_CC += globals()['x' + str(i)] * (D[i-1] + D[3**(k-2)+i-1] + D[2*3**(k-2)+i-1])
                PD_Cc += globals()['x' + str(3**(k-2)+i)] * (D[i-1] + D[3**(k-2)+i-1] + D[2*3**(k-2)+i-1])
                PD_cc += globals()['x' + str(2*3**(k-2)+i)] * (D[i-1] + D[3**(k-2)+i-1] + D[2*3**(k-2)+i-1])
        PD_CC -= PD
        PD_Cc -= PD
        PD_cc -= PD

        # PD_DD, PD_Dd, PD_dd
        PD_DD, PD_Dd, PD_dd = 0, 0, 0
        for o in range(3**(k-1)):
            for j in range(1,4):
                i = o*3**(n-3) + j
                PD_DD += globals()['x' + str(i)] * (D[i-1] + D[3**(k-3)+i-1] + D[2*3**(k-3)+i-1])
                PD_Dd += globals()['x' + str(3**(k-3)+i)] * (D[i-1] + D[3**(k-3)+i-1] + D[2*3**(k-3)+i-1])
                PD_dd += globals()['x' + str(2*3**(k-3)+i)] * (D[i-1] + D[3**(k-3)+i-1] + D[2*3**(k-3)+i-1])
        PD_DD -= PD
        PD_Dd -= PD
        PD_dd -= PD

        # PD_EE, PD_Ee, PD_ee
        PD_EE, PD_Ee, PD_ee = 0, 0, 0
        for o in range(3**k):
            j = 1
            i = j + o*3**(n-4)
            PD_EE += globals()['x' + str(i)] * (D[i-1]+D[i]+D[i+1])
            PD_Ee += globals()['x' + str(1+i)] * (D[i-1]+D[i]+D[i+1])
            PD_ee += globals()['x' + str(2+i)] * (D[i-1]+D[i]+D[i+1])
        PD_EE -= PD
        PD_Ee -= PD
        PD_ee -= PD

        # f10
        f10 = -PD
        for m in range(3**n):
            f10 += D[m] * globals()['x'+str(m+1)]

        # f11
        f11 = 0
        for i in range(3**n):
            f11 += D[i]*((globals()['x' + str(i+1)]-PD)**2)
        f11 -= H2*PD*(1-PD)
        
        # f 
        f = [PD_AA, PD_Aa, PD_aa, PD_BB, PD_Bb, PD_bb, PD_CC, PD_Cc, PD_cc, PD_DD, PD_Dd, PD_dd, PD_EE, PD_Ee, PD_ee, f10, f11]

        x0 = [0 for index in range(3**n)]
        error_dxk = 0.05
        error_fkk = 0.05
        num = 10

        for i in range(num):
            # Ak
            Ak = [[0 for index in range(3**n)] for index in range(3*n+2)]
            funcs = sympy.Matrix([PD_AA, PD_Aa, PD_aa, PD_BB, PD_Bb, PD_bb, PD_CC, PD_Cc, PD_cc, PD_DD, PD_Dd, PD_dd, PD_EE, PD_Ee, PD_ee, f10, f11])
            args = sympy.Matrix([globals()['x' + str(index+1)] for index in range(3**n)])
            res = funcs.jacobian(args)
            for j in range(3*n+1):
                Ak[j] = np.array(res[j,:]).astype(np.float64)[0].tolist()
            for i in range(3**n):
                Ak[3*n+2-1][i] = res[3*n+2-1,i].subs([(globals()['x' + str(index+1)], x0[index]) for index in range(3**n)])

            # bk
            bk = [0 for index in range(3*n+2)]
            for z in range(3*n+2):
                bk[z] = f[z].subs([(globals()['x' + str(index+1)], x0[index]) for index in range(3**n)])

            # dxk
            dxk = pre_seidel(Ak,[(0-c) for c in bk],i+1)
            x0 += dxk

            # fkk
            fkk = [0 for index in range(3*n+2)]
            for z in range(3*n+2):
                fkk[z] = f[z].subs([(globals()['x' + str(index+1)], x0[index]) for index in range(3**n)])

            #ndxk = norm(np.array(dxk).astype(np.float), ord=2)
            #nfkk = norm(np.array(fkk).astype(np.float), ord=2)
            ndxk = norm(np.array(dxk).astype(float), ord=2)
            nfkk = norm(np.array(fkk).astype(float), ord=2)
            if (ndxk < error_dxk) or (nfkk < error_fkk):
                break
        
        # x_result
        x_result = x0
        for i in range(len(x_result)):
            if x_result[i] < 0:
                x_result[i] = 0         
        # print('x_result', x_result)    
    
    v, pd, h = verification(x_result, n, D)

    return x_result, v, pd, h


def generateAdjLD(SNP_Num, Aver_LD):
    if Aver_LD == 0:
        Adj_LD_Level = [0 for index in range(SNP_Num-1)]
    else:
        alfa = 10 * Aver_LD
        beta = 10 * (1 - Aver_LD)
        Adj_LD_Level = [0 for index in range(SNP_Num-1)]
        for i in range(SNP_Num-1):
            Adj_LD_Level[i] = np.random.beta(alfa, beta)
    return Adj_LD_Level

def NewPosition(factorTag):
    ZerosPosition = [index for (index, item) in enumerate(factorTag) if item == 0]
    out = np.random.permutation(range(len(ZerosPosition)))
    factor = ZerosPosition[out[0]]
    factorTag[factor] = 1
    return factor, factorTag

def generateMAF(SNP_Num, L_MAF, H_MAF, LDInfo, ModelInformation, Adj_LD_Level):

    MAF = [0 for index in range(SNP_Num)]
    for i in range(len(LDInfo)):
        for j in range(1,3):
            MAF[int(float(LDInfo[i]['Position 1']))] = float(LDInfo[i]['MAF 1'])
            MAF[int(float(LDInfo[i]['Position 2']))] = float(LDInfo[i]['MAF 2'])
    for i in range(len(ModelInformation)):
        for j in range(ModelInformation[i][0]):
            MAF[int(ModelInformation[i][3][j])]=ModelInformation[i][1][j]
    if MAF[0] == 0:
        MAF[0] = One_MAF(L_MAF,H_MAF,L_MAF,H_MAF,L_MAF,H_MAF)
    for i in range(SNP_Num-2):
        if i % 1000 == 0:
            time.sleep(0.0000000001)
        if MAF[i+1] == 0:
            if np.random.rand() > 0.5:
                temp = MAF[i] / (MAF[i] - MAF[i] * Adj_LD_Level[i] + Adj_LD_Level[i])
                MAF[i+1] = One_MAF(L_MAF, H_MAF, MAF[i], temp, L_MAF, H_MAF)
            else:
                temp = (Adj_LD_Level[i] * MAF[i]) / (1 - MAF[i] + MAF[i] * Adj_LD_Level[i])
                MAF[i+1] = One_MAF(L_MAF, H_MAF, temp, MAF[i], L_MAF, H_MAF)
        else:
            if MAF[i] > MAF[i+1]:
                HighLD = MAF[i+1] * (1-MAF[i]) / (MAF[i] * (1-MAF[i+1]))
            else:
                HighLD = MAF[i] * (1-MAF[i+1]) / (MAF[i+1] * (1-MAF[i]))
            if Adj_LD_Level[i] > HighLD:
                Adj_LD_Level[i] = HighLD
    if MAF[SNP_Num-1] == 0:
        i = SNP_Num-2
        if np.random.rand() > 0.5:
            temp = MAF[i] / (MAF[i] -  MAF[i] * Adj_LD_Level[i] + Adj_LD_Level[i])
            MAF[i+1] = One_MAF(L_MAF, H_MAF, MAF[i], temp, L_MAF, H_MAF)
        else:
            temp = (Adj_LD_Level[i] * MAF[i]) / (1 - MAF[i] + MAF[i] * Adj_LD_Level[i])
            MAF[i+1] = One_MAF(L_MAF, H_MAF, temp, MAF[i], L_MAF, H_MAF)
    return  MAF, Adj_LD_Level

def One_MAF(L1, H1, L2, H2, L3, H3):
    Low = max(L1, L2, L3)
    High = min(H1, H2, H3)
    MAF = Low + (High - Low) * (np.random.rand())
    return MAF

def Match_LD_MAF(Adj_LD_Level, MAF):
    Row = len(Adj_LD_Level)
    Tag = [0 for index in range(Row)]
    for i in range(Row):
        if MAF[i] > MAF[i + 1]:
            HighLD = MAF[i+1] * (1-MAF[i]) / (MAF[i] * (1-MAF[i+1]))
        else:
            HighLD = MAF[i] * (1-MAF[i+1]) / (MAF[i+1] * (1-MAF[i]))
        if Adj_LD_Level[i] <= HighLD: Tag[i] = 1
        else: Tag[i] = 0
    Match = (len(np.where(Tag == 0)[0]))
    return Match, Tag

def R2Equation(LDr2, Maf1, Maf2):
    p, q = Maf1, Maf2
    r = abs(np.sqrt(LDr2))
    x = sympy.symbols('x')
    y = sympy.symbols('y')
    eqs=[sympy.Eq(p*x+(1-p)*y, q),
        sympy.Eq((p*x*(1-p)*(1-y)-p*(1-x)*(1-p)*y)**2/(p*(1-p)*q*(1-q)), r**2)]
    ans = sympy.solve(eqs,[x, y])
    # print('ans', ans)
    if len(ans) == 0:
        x, y = [], []
        return x, y
    for index in range(len(ans)):
        ans[index] = list(ans[index])
        ans[index][0] = 1 - ans[index][0]
        ans[index][1] = 1 - ans[index][1]
    if len(ans) > 1:
        if (isinstance(ans[1][0],complex)==0) and (0<ans[1][0]<=1) and (isinstance(ans[1][1],complex)==0) and (0<ans[1][1]<=1):
            x = ans[1][0]
            y = ans[1][1]
        elif (isinstance(ans[0][0],complex)==0) and (0<ans[0][0]<=1) and (isinstance(ans[0][1],complex)==0) and (0<ans[0][1]<=1):
            x = ans[0][0]
            y = ans[0][1]
        else:
            x = 0
            y = 0            
    elif len(ans) == 1:
        if (isinstance(ans[0][0],complex)==0) and (0<ans[0][0]<=1) and (isinstance(ans[0][1],complex)==0) and (0<ans[0][1]<=1):
            x = ans[0][0]
            y = ans[0][1]
        else:
            x = 0
            y = 0
    else:
        x = 0
        y = 0
    return x, y


def GenerateAllele(aToB, Maf1, AToB, ProAllele):
    # if (len(aToB) != 1) or (len(AToB) != 1):
    if ProAllele == -1:
        if np.random.rand() <= Maf1: Allele = 1
        else: Allele = 0
    elif ProAllele == 1:
        if np.random.rand() <= aToB: Allele = 0
        else: Allele = 1
    elif ProAllele == 0:
        if np.random.rand() <= AToB: Allele = 0
        else: Allele = 1
    return Allele

def StatusDecision(SNPs, ModelInformation):
    ModelNum = len(ModelInformation)
    if ModelNum > 0:
        R = [0 for index in range(ModelNum)]
        for i in range(ModelNum):
            num = 0
            for j in range(ModelInformation[i][0]):
                num = num + SNPs[ModelInformation[i][3][j]]*3**(ModelInformation[i][0]-(j+1))
            R[i] = ModelInformation[i][2][int(num)]

        UR = [1 - x for x in R]
        ProCase = 1
        for i in range(ModelNum):
            ProCase = ProCase*UR[i]
        ProCase = 1-ProCase
        if np.random.rand() <= ProCase: Status = 1
        else: Status = 0
    else:
        if np.random.rand() <= 0.5: Status = 1
        else: Status = 0
    return Status

def BoundMAFs(Chr_simulate):
    TotalChr, TotalSNP = Chr_simulate.shape
    MAF = [0 for index in range(TotalSNP)]
    for i in range(TotalSNP):
        MAF[i] = len([index for (index, item) in enumerate(Chr_simulate[:,i]) if item == 0])/TotalChr
    UpperBound = np.max(MAF)
    LowerBound = np.min(MAF)
    return UpperBound, LowerBound

def ComputerLD(source):
    if source.shape[1] != 2:
        r2 = -1
        return r2
    Row = source.shape[0]
    AB, Ab, aB, ab = 0, 0, 0, 0
    for i in range(Row):
        if (source[i,0]==0) and (source[i,1]==0): AB += 1
        elif (source[i,0]==0) and (source[i,1]==1): Ab += 1
        elif (source[i,0]==1) and (source[i,1]==0): aB += 1
        elif (source[i,0]==1) and (source[i,1]==1): ab += 1
    p1 = (AB+Ab)/Row
    q1 = (AB+aB)/Row
    # r2 = (AB/Row-p1*q1)**2 / (p1*q1*(1-p1)*(1-q1))
    r2 = (AB/Row-p1*q1)**2 / ((p1*q1*(1-p1)*(1-q1))+1)
    return r2

def MeanAdjLD(Chr_simulate):
    SNP_Num = Chr_simulate.shape[1]
    LD = [0 for index in range(SNP_Num-1)]
    for i in range(SNP_Num-1):
        LD[i] = ComputerLD(Chr_simulate[:,i:i+2])
    MeanLD = np.mean(LD)
    return MeanLD

def CountSamples(pts, factor, class_var):
    FactorNum = len(factor)
    Result = np.zeros((4,3**FactorNum))
    for i in range(pts.shape[0]):
        info, count = 0, 0
        for j in range(FactorNum):
            if pts[i, factor[j]] != 0:
                count += int((pts[i,factor[j]]-1)*(3**(FactorNum-(j+1))))
            else: 
                info = 1
                break
        if info == 0: 
            Result[1, int(count)] += 1
            if class_var[i] == 1: Result[2, int(count)] += 1
            else: Result[3, int(count)] += 1
    for i in range(3**FactorNum):
        info, count = i+1, 0
        for j in range(FactorNum):
            count += (math.floor((info-1)/(3**(FactorNum-(j+1))))+1)*10**(FactorNum-(j+1))
            info -= math.floor((info-1)/(3**(FactorNum-(j+1))))*(3**(FactorNum-(j+1)))
        Result[0, i] = count
    return Result

def PenetranceCal(ModelInformation,i,SNP_simulate):
    num = ModelInformation[i][0]
    factor = []
    for j in range(num):
        factor.append(ModelInformation[i][3][j])
    pts = SNP_simulate[:, 1:-1] + 1
    class_var = np.transpose(SNP_simulate[:, -1])
    for i in range(len(class_var)):
        if class_var[i] == 0: class_var[i] = 2
    pvalue = CountChi2(pts, factor, class_var)
    Result = CountSamples(pts, factor, class_var)
    Col = Result.shape[1]
    Penetrance = [0 for index in range(Col)]
    Result.astype(np.int)
    for j in range(Col):
        if Result[1,j] == 0: Penetrance[j] = 0
        else: Penetrance[j] = Result[2,j]/Result[1,j]
    return Penetrance, pvalue

def CountChi2(pts,factor,class_var):
    Result = CountSamples(pts, factor, class_var)
    sample = [0 for index in range(4)]
    sample[2] = np.sum(Result, axis=1)[2]
    sample[3] = np.sum(Result, axis=1)[3]
    cstat, num = 0, 0
    for j in range(Result.shape[1]):
        for i in range(3, 4):
            if Result[1,j] == 0:
                cstat += 0
            else:
                cstat += np.square(Result[i,j])/(sample[i]*Result[1,j])
        if Result[1, j] == 0:
            num += 1
    cstat = sum(sample) * (cstat-1)
    df = Result.shape[1]-1-num
    pvalue = 1 - stats.chi2.cdf(cstat,df)
    return pvalue
