from ot.utils import list_to_array
from ot.backend import get_backend
import warnings
import argparse
import numpy as np
import time
from scipy.optimize import linprog
from qpsolvers import solve_qp
from ot.utils import unif, dist, list_to_array
import autoray as ar
# from .backend import get_backend


"""
This function 'params' is defined to provide a dictionary of default parameters for the StochasticGhost optimizer.
It is not intended to be called directly by the user. Instead, it serves as a reference for the parameters
that need to be passed when initializing the optimizer.

The dictionary returned by this function includes various hyperparameters and settings that control the behavior
of the optimizer. These include the number of iterations, trust region sizes, Hessian computation method, minibatch size,
number of constraint functions, step decay strategy, and initial stepsize, among others.

Users can call this function to obtain a dictionary of these default parameters, which can then be modified if needed
before being passed to the StochasticGhost optimizer. This ensures that all necessary parameters are set, providing
a convenient way to manage optimizer configurations.

Usually it is recommended that users define their own dictionary params and pass it while calling the StochasticGhost optimizer.

"""

def params(maxiter=1, beta=10, rho=0.8, lamb=0.5, hess='diag', tau=1., mbsz=1, numcon=1, geomp=0.7, stepdecay='dimin', gammazero=0.1, zeta=0.1):
    params = {
        'maxiter': maxiter,  # number of iterations performed
        'beta': beta,  # trust region size
        'rho': rho,  # trust region for feasibility subproblem
        'lamb': lamb,  # weight on the subfeasibility relaxation
        'hess': hess,  # method of computing the Hessian of the QP, options include 'diag' 'lbfgs' 'fisher' 'adamdiag' 'adagraddiag'
        'tau': tau,  # parameter for the hessian
        'mbsz': mbsz,  # the standard minibatch size, used for evaluating the progress of the objective and constraint
        'numcon': numcon,  # number of constraint functions
        'geomp': geomp,  # parameter for the geometric random variable defining the number of subproblem samples
        'stepdecay': stepdecay, # strategy for step decrease, options include 'dimin' 'stepwise' 'slowdimin' 'constant'
        'gammazero': gammazero,  # initial stepsize
        'zeta': zeta,  # parameter associated with the stepsize iteration
    }
    return params



def computekappa(cval, cgrad, lamb, rho, mc, n):
    r"""Compute Kappa parameter used to relax the infeasibility bound of the problem.

    

    Parameters
    ----------
    cval :
        Vector containing constraint function evaluations at current iter.
    cgrad :
        Jacobian Matrix of constraint gradient w.r.t. parameters at current iter.
    lamb :
        A weight constant between 0 and 1.
    rho :
        The bound on the sup norm of step size.
    mc :
        Number of constraint functions.
    n :
        Number of optimization parameters.

    Note
    ----
    In quadratic programming, the matrix :math:`P` should be symmetric. Many
    solvers (including CVXOPT, OSQP and quadprog) leverage this property and
    may return unintended results when it is not the case. You can set
    project :math:`P` on its symmetric part by:

    .. code:: python

        P = 0.5 * (P + P.transpose())

    Returns
    -------
    :
        Kappa (infeasibility relaxation param).

    Notes
    -------
    :
         Ensures that the problem is always feasible
    """  
    obj = np.concatenate(([1.], np.zeros((n,))))
    Aubt = np.column_stack((-np.ones(mc), np.array(cgrad)))
    res = linprog(c=obj, A_ub=Aubt, b_ub=-np.array(cval), bounds=[(-rho, rho)])
    return (1-lamb)*max(0, sum(cval)) + lamb*max(0, res.fun)




def solvesubp(fgrad, cval, cgrad, kap_val, beta, tau, hesstype, mc, n):
    r"""Solves the quadratic subproblem for each iterate.

    

    Parameters
    ----------
    fgrad :
        Vector containing objective function evaluations at current iter.
    cval :
        Vector containing constraint function evaluations at current iter.
    cgrad :
        Jacobian Matrix of constraint gradient w.r.t. parameters at current iter.
    kap_val :
        The kappa value calculated through lpp
    beta :
        
    tau :
        Entries in the hessian.
    hesstype :
        The type of hessian matrix tau 
    Note
    ----
    Note that currently the Hessian of tau is an identity but we later plan to extend it to 
    take any positive definite matrix

    Returns
    -------
    :
        The gradient step at current iterate
    """
    if hesstype == 'diag':
       # P = tau*nx.eye(n)
       P = tau*np.identity(n)
       kap = kap_val * np.ones(mc)
       cval = np.array(cval)
    return solve_qp(P, fgrad.reshape((n,)), cgrad.reshape((mc, n)), kap-cval, np.zeros((0, n)), np.zeros((0,)), -beta*np.ones((n,)), beta*np.ones((n,)), solver='osqp')

# initw : Initial parameters of the Network (Weights and Biases)


def StochasticGhost(obj_fun, obj_grad, con_funs, con_grads, initw, params):
    N = params["N"]
    n = params["n"]  
    maxiter = params["maxiter"]
    beta = params["beta"]
    rho = params["rho"]
    lamb = params["lamb"]
    tau = params["tau"]
    hess = params["hess"]
    mbsz = params["mbsz"]
    mc = params["numcon"]
    geomp = params["geomp"]
    stepdec = params["stepdecay"]
    gamma0 = params["gammazero"]
    zeta = params["zeta"]
    gamma = gamma0
    lossbound = params["lossbound"]

    
    w = initw
    for i in range(len(w)):
        w[i] = ar.to_numpy(w[i])

    feval = obj_fun(w, mbsz)  
    ceval = np.zeros((mc,))
    Jeval = np.zeros((mc, n))

    # Getting all the constraints
    iterfs = np.zeros((maxiter,))
    iterfs[0] = feval
    for i in range(mc):
       conf = con_funs[i]
       #print("Doing initial run without iteration with b_s: ", mbsz)
       #print(mc)
       #print(conf)
       ceval[i] = np.max(conf(w, mbsz), 0)
    #itercs = np.zeros((maxiter,))
    itercs = np.zeros((maxiter, mc))
    itercs[0,:] = np.max(ceval)

    for iteration in range(0, maxiter):

        if stepdec == 'dimin':
           gamma = gamma0/(iteration+1)**zeta
        if stepdec == 'constant':
           gamma = gamma0
        if stepdec == 'slowdimin':
           gamma = gamma*(1-zeta*gamma)
        if stepdec == 'stepwise':
           gamma = gamma0 / (10**(int(iteration*zeta)))

        Nsamp = np.random.geometric(p=geomp)
        while (2**(Nsamp+1)) > N:
          Nsamp = np.random.geometric(p=geomp)

        """
        Only specify the number of minibatches here.
        Lets the user decide on the samples for each minibatch number.
        The particular minibatch sizes are selected to get an unbiased estimate of noisy stepsize at each iterate of subproblem.
        """
        
        mbatches = [1, 2**Nsamp, 2**Nsamp, 2**(Nsamp+1)]
        dsols = np.zeros((4, n))

        for j in range(4):
          feval = obj_fun(w, mbatches[j])
          fgrad = ar.to_numpy(obj_grad(w, mbatches[j]))
          for i in range(mc):
            # con_funs[i] (conf) and con_grads[i] (conJ) : ith constraint and constraint grad
            conf = con_funs[i]
            conJ = con_grads[i]
            #print("Now doing proper iteration with b_s: ", mbatches[j])

            """
            ceval and Jeval are evaluations of ith constraint and constraint grads for the parameter values
            nx.max(conf(w,mbatches[j]),0) to ensure the problem is always in the feasible region
            """
            ceval[i] = np.max(conf(w, mbatches[j]) - lossbound[i], 0)
            Jeval[i, :] = ar.to_numpy(conJ(w, mbatches[j]))
            

          # Compute Kappa for the Subproblem bound 
          kap = computekappa(ceval, Jeval, rho, lamb, mc, n)
          # Solving the subproblem
          dsol = solvesubp(fgrad, ceval, Jeval, kap, beta, tau, hess, mc, n)
          dsols[j, :] = dsol

        dsol = dsols[0, :] + (dsols[3, :]-0.5*dsols[1, :] -
                              0.5*dsols[2, :])/(geomp*((1-geomp)**Nsamp))
        
        print("iteration:",iteration+1)

        """
        w = w + gamma*dsol
        The stepsize evaluation from the previously calculated gradients
        """
        start = 0
        for i in range(len(w)):
           #print(w[i].size)
           end = start + np.size(w[i])
           w[i] = w[i] + gamma*np.reshape(dsol[start:end], np.shape(w[i]))
           start = end
        
        feval = obj_fun(w, mbsz)
        iterfs[iteration] = feval
        for i in range(mc):
          conf = con_funs[i]
          ceval[i] = np.max(conf(w, mbsz), 0)
        itercs[iteration, :] = ceval

    return w, iterfs, itercs
