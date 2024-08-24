r"""
Ramanujan methods
-----------------
Author @ Nikesh Bajaj
updated on Date: 1 jan 2021, Version : 0.0.1
Github :  https://github.com/Nikeshbajaj/spkit
Contact: n.bajaj@qmul.ac.uk | n.bajaj@imperial.ac.uk
"""

from __future__ import absolute_import, division, print_function
name = "Signal Processing toolkit | Ramanujan methods"
import sys

if sys.version_info[:2] < (3, 3):
    old_print = print
    def print(*args, **kwargs):
        flush = kwargs.pop('flush', False)
        old_print(*args, **kwargs)
        if flush:
            file = kwargs.get('file', sys.stdout)
            # Why might file=None? IDK, but it works for print(i, file=None)
            file.flush() if file is not None else sys.stdout.flush()

import numpy as np
import matplotlib.pyplot as plt
import sys, scipy
from scipy import linalg as LA
import warnings
from ..utils import deprecated

#ramanujan


def ramanujan_filter(x, Pmax=10, Rcq=10, Rav=2, Th=0.2,Penalty=None,return_filters=False, apply_averaging=True):
    r"""Ramanujan Filter Banks for Estimation and Tracking of Periodicity

    Ramanujan Filter Banks for Estimation and Tracking of Periodicity

    Parameters
    ----------
    x    : 1d array, sequence of signal
    Pmax : the largest expected period.
    Rcq  : Number of repeats in each Ramanujan filter
    Rav  : Number of repeats in each averaging filter
    Th   : Outputs of the RFB are thresholded to zero for all values less than Th*max(output)
    Penalt = penalty for each period shape=(len(Pmax)),
             If None, then set to 1, means no penalty

    Returns
    -------
    y: 2d array of shape = (len(x),Pmax)
      - time vs period matrix, normalized

    if return_filters==True,
       - also returns
        * FR : list of Ramanujan Filters
        * FA : list of Averaging Filters

    References
    ----------
    * [1] S.V. Tenneti and P. P. Vaidyanathan, "Ramanujan Filter Banks for Estimation
      and Tracking of Periodicity", Proc. IEEE Int. Conf. Acoust.
      Speech, and Signal Proc., Brisbane, April 2015.

    * [2] P.P. Vaidyanathan and S.V. Tenneti, "Properties of Ramanujan Filter Banks",
      Proc. European Signal Processing Conference, France, August 2015.

    * Python impletation is done by using matlab code version from - http://systems.caltech.edu/dsp/students/srikanth/Ramanujan/

    Notes
    -----
    * 

    See Also
    --------
    ramanujan_filter_prange, regularised_period_estimation, create_dictionary

    Examples
    --------
    #sp.ramanujan_filter
    import numpy as np
    import matplotlib.pyplot as plt
    import spkit as sp
    np.random.seed(2)
    #period = 10 #SNR = 0
    period = 8
    x1 = np.zeros(30)
    x2 = np.random.randn(period)
    x2 = np.tile(x2,10)
    x3 = np.zeros(30)
    x  = np.r_[x1,x2,x3]
    x_noise = sp.add_noise(x,snr_db=0)
    Pmax=40
    y,FR, FA = sp.ramanujan_filter(x_noise,Pmax=Pmax, Rcq=15, Rav=2, Th=0.2,return_filters=True)
    print('top 10 periods: ',np.argsort(np.sum(y,0))[::-1][:10]+1)
    plt.figure(figsize=(12,6))
    plt.subplot(211)
    plt.plot(x,label='signal: x')
    plt.plot(x_noise, label='signal+noise: x_noise')
    plt.text(5,3.5,f'signal with repitative patterns')
    plt.xlim([0,len(x)])
    #plt.xlabel('sample (n)')
    plt.legend(bbox_to_anchor=(1,1))
    plt.subplot(223)
    im = plt.imshow(y.T,aspect='auto',cmap='jet',extent=[1,len(x_noise),Pmax,1])
    plt.colorbar(im)
    plt.xlabel('sample (n)')
    plt.ylabel('period (in samples)')
    plt.subplot(224)
    plt.stem(np.arange(1,y.shape[1]+1),np.sum(y,0))
    plt.xlabel('period (in samples)')
    plt.ylabel('strength')
    plt.tight_layout()
    plt.show()
    """
    return _RFB(x, Pmax=Pmax, Rcq=Rcq, Rav=Rav, Th=Th,
           Penalty=Penalty,return_filters=return_filters,
           apply_averaging=apply_averaging)

def create_dictionary(Nmax, rowSize, method='Ramanujan'):
    r"""Creating Dictionary for RFB
    
    **Creating Dictionary for RFB**


    Parameters
    ----------
    Nmax    : maximum expected Period,
    rowSize : number of rows (e.g. samples in signal)
    method  : 'Ramanujan' 'random', 'NaturalBasis', 'DFT'


    Returns
    -------
    A :  Matrix of (rowSize, q)

    References
    ----------
    The relevant paper is:
    [1] S.V. Tenneti and P. P. Vaidyanathan, "Nested Periodic Matrices and Dictionaries:
        New Signal Representations for Period Estimation", IEEE Transactions on Signal
        Processing, vol.63, no.14, pp.3736-50, July, 2015.

    Python impletation is done by using matlab code version from
    - http://systems.caltech.edu/dsp/students/srikanth/Ramanujan/

    
    Notes
    -----
    * spkit

    See Also
    --------
    ramanujan_filter_prange, regularised_period_estimation, create_dictionary

    Examples
    --------
    import numpy as np
    import spkit as sp
    """

    return _create_dictionary(Nmax, rowSize, method=method)

def ramanujan_filter_prange(x,Pmin=1,Pmax=10,skip=1,Rcq=10,Rav=2,thr=0.2,Penalty=None,return_filters=False,apply_averaging=True):
    r"""Ramanujan Filter Banks for Estimation and Tracking of Periodicity with given range.
    
    **Ramanujan Filter Banks for Estimation and Tracking of Periodicity**

    - for range of period given by Pmin and Pmax.

    Parameters
    ----------

    x    = 1d array, sequence of signal
    Pmin = the smallest expected period. (default=1)
    Pmax = the largest expected period.
    skip = int >=1: if to skip period (default=1 --> no skipping) (>1 is not recomended)
    Rcq  = Number of repeats in each Ramanujan filter
    Rav  = Number of repeats in each averaging filter
    thr   = Outputs of the RFB are thresholded to zero for all values less than Th*max(output)
    Penalty = penalty for each period shape=(len(Pmax)),
             If None, then set to 1, means no penalty
    apply_averaging: bool, if False, no averaging is applied (deault=True)
    return_filters: bool, ifTrue, return FR - Ramanujan and FA - Averaging filters

    Returns
    -------

    y = 2d array of shape = (len(x),Pmax), time vs period matrix, normalized

    if return_filters==True: also returns

    FR = list of Ramanujan Filters
    FA = list of Averaging Filters

    References
    ----------

    * [1] S.V. Tenneti and P. P. Vaidyanathan, "Ramanujan Filter Banks for Estimation
       and Tracking of Periodicity", Proc. IEEE Int. Conf. Acoust.
       Speech, and Signal Proc., Brisbane, April 2015.

    * [2] P.P. Vaidyanathan and S.V. Tenneti, "Properties of Ramanujan Filter Banks",
        Proc. European Signal Processing Conference, France, August 2015.

    * Python impletation is done by using matlab code version from - http://systems.caltech.edu/dsp/students/srikanth/Ramanujan/

    Notes
    -----
    * 

    See Also
    --------
    ramanujan_filter, regularised_period_estimation, create_dictionary

    Examples
    --------
    #sp.RFB_prange
    import numpy as np
    import matplotlib.pyplot as plt
    import spkit as sp
    np.random.seed(2)
    #period = 10 #SNR = 0
    period = 8
    x1 = np.zeros(30)
    x2 = np.random.randn(period)
    x2 = np.tile(x2,10)
    x3 = np.zeros(30)
    x  = np.r_[x1,x2,x3]
    x_noise = sp.add_noise(x,snr_db=0)
    Pmin = 4
    Pmax = 20
    y,plist, FR, FA = sp.RFB_prange(x_noise,Pmin=Pmin, Pmax=Pmax, skip=2, Rcq=10, Rav=2, thr=0.2,return_filters=True)
    idx = np.argsort(np.sum(y,0))[::-1]
    print('top 10 periods: ',plist[idx[:10]])
    plt.figure(figsize=(12,6))
    plt.subplot(211)
    plt.plot(x,label='signal: x')
    plt.plot(x_noise, label='signal+noise: x_noise')
    plt.text(5,3.5,f'signal with repitative patterns')
    plt.xlim([0,len(x)])
    #plt.xlabel('sample (n)')
    plt.legend(bbox_to_anchor=(1,1))
    plt.subplot(223)
    im = plt.imshow(y.T,aspect='auto',cmap='jet',extent=[1,len(x_noise),Pmax,Pmin])
    plt.yticks(plist)
    plt.colorbar(im)
    plt.xlabel('sample (n)')
    plt.ylabel('period (in samples)')
    plt.subplot(224)
    plt.stem(plist,np.sum(y,0))
    plt.xlabel('period (in samples)')
    plt.ylabel('strength')
    plt.tight_layout()
    plt.show()
    """
    return _RFB_prange(x,Pmin=Pmin,Pmax=Pmax,skip=skip,Rcq=Rcq,Rav=Rav,
                      thr=thr,Penalty=Penalty,
                      return_filters=return_filters,
                      apply_averaging=apply_averaging)

def regularised_period_estimation(x,Pmax,method='Ramanujan',lambd=1,L=1,cvxsol=False):
    r"""Computing strength of periods
    
    **Computing strength of periods**

    for given signal x, using method and respective loss fun (e.g. l1, l2)

    Parameters
    ----------

    x   :  one dimentional sequence (signal)
    Pmax: largest expected period in the signal
    method: type of dictionary used to create transform matrix A
          : 'Ramanujan', 'NaturalBasis', 'random' or Farray (DFT)

    lambd: for penalty vector, to force towards lower (usually) or higher periods
         : if 0, then penalty vector is 1, means no penalization
         : if >0, then lambd is multiplied to penalty vector

    L : regularazation: L=1, minimize ||s||_1, L=2, ||s||_2

    cvxsol: bool, wether to use cvxpy solver of matrix decomposition approach
          : matrix decomposition approach works only for L=2
          : for L=1, use cvxpy as solver

    Returns
    -------

    period_energy: vecotor shape: (Pmax,): strength of each period


    Reference:
    [1] S.V. Tenneti and P. P. Vaidyanathan, "Nested Periodic Matrices and Dictionaries:
       New Signal Representations for Period Estimation", IEEE Transactions on Signal
       Processing, vol.63, no.14, pp.3736-50, July, 2015.

    Python impletation is done by using matlab code version from
    - http://systems.caltech.edu/dsp/students/srikanth/Ramanujan/


    See Also
    --------
    ramanujan_filter, ramanujan_filter_prange, regularised_period_estimation, create_dictionary

    Examples
    --------
    >>> import numpy as np
    >>> import spkit as sp
    """
    return _periodstrength(x,Pmax,method=method,lambd=lambd,L=L,cvxsol=cvxsol)

def _RFB(x, Pmax=10, Rcq=10, Rav=2, Th=0.2,Penalty=None,return_filters=False, apply_averaging=True):
    r"""Ramanujan Filter Banks for Estimation and Tracking of Periodicity

    Ramanujan Filter Banks for Estimation and Tracking of Periodicity

    Parameters
    ----------
    x    : 1d array, sequence of signal
    Pmax : the largest expected period.
    Rcq  : Number of repeats in each Ramanujan filter
    Rav  : Number of repeats in each averaging filter
    Th   : Outputs of the RFB are thresholded to zero for all values less than Th*max(output)
    Penalt = penalty for each period shape=(len(Pmax)),
             If None, then set to 1, means no penalty

    Returns
    -------
    y: 2d array of shape = (len(x),Pmax)
      - time vs period matrix, normalized

    if return_filters==True,
       - also returns
        * FR : list of Ramanujan Filters
        * FA : list of Averaging Filters

    References
    ----------
    * [1] S.V. Tenneti and P. P. Vaidyanathan, "Ramanujan Filter Banks for Estimation
      and Tracking of Periodicity", Proc. IEEE Int. Conf. Acoust.
      Speech, and Signal Proc., Brisbane, April 2015.

    * [2] P.P. Vaidyanathan and S.V. Tenneti, "Properties of Ramanujan Filter Banks",
      Proc. European Signal Processing Conference, France, August 2015.

    * Python impletation is done by using matlab code version from - http://systems.caltech.edu/dsp/students/srikanth/Ramanujan/

    Notes
    -----
    * 

    See Also
    --------
    spkit: # TODO

    Examples
    --------
    #sp.RFB
    import numpy as np
    import matplotlib.pyplot as plt
    import spkit as sp
    np.random.seed(2)
    #period = 10 #SNR = 0
    period = 8
    x1 = np.zeros(30)
    x2 = np.random.randn(period)
    x2 = np.tile(x2,10)
    x3 = np.zeros(30)
    x  = np.r_[x1,x2,x3]
    x_noise = sp.add_noise(x,snr_db=0)
    Pmax=40
    y,FR, FA = sp.RFB(x_noise,Pmax=Pmax, Rcq=15, Rav=2, Th=0.2,return_filters=True)
    print('top 10 periods: ',np.argsort(np.sum(y,0))[::-1][:10]+1)
    plt.figure(figsize=(12,6))
    plt.subplot(211)
    plt.plot(x,label='signal: x')
    plt.plot(x_noise, label='signal+noise: x_noise')
    plt.text(5,3.5,f'signal with repitative patterns')
    plt.xlim([0,len(x)])
    #plt.xlabel('sample (n)')
    plt.legend(bbox_to_anchor=(1,1))
    plt.subplot(223)
    im = plt.imshow(y.T,aspect='auto',cmap='jet',extent=[1,len(x_noise),Pmax,1])
    plt.colorbar(im)
    plt.xlabel('sample (n)')
    plt.ylabel('period (in samples)')
    plt.subplot(224)
    plt.stem(np.arange(1,y.shape[1]+1),np.sum(y,0))
    plt.xlabel('period (in samples)')
    plt.ylabel('strength')
    plt.tight_layout()
    plt.show()
    """

    # Peanlty vector.
    if Penalty is None: Penalty = np.ones(Pmax)

    # Can be (optionally) used to set preference  to a certain set of periods in the
    # time vs period plane.

    FR = [[]]*Pmax #The set of Ramanujan Filters
    FA = [[]]*Pmax #The set of Averaging Filters
    for i in range(Pmax):
        cq = np.zeros(i+1) + 1j*0  #cq shall be the ith ramanujan sum sequnece.
        k_orig = np.arange(i+1)+1
        k = k_orig[np.gcd(k_orig,i+1)==1]
        for n in range(i+1):
            cq[n] += np.sum([np.exp(1j*2*np.pi*a*(n)/(i+1)) for a in k])

        cq = np.real(cq)
        FR[i]  = np.tile(cq,Rcq)
        FR[i] /= np.linalg.norm(FR[i])

        FA[i]  = np.tile(np.ones(i+1),Rav)
        FA[i] /= np.linalg.norm(FA[i])


    #Computing the Outputs of the Filter Bank
    y = np.zeros([len(x),Pmax])

    if np.ndim(x)>1:
        xi = x[:,0].copy()
    else:
        xi = x.copy()

    for i in range(Pmax):
        npad = len(FR[i]) - 1
        xi_padded = np.pad(xi, (npad//2, npad - npad//2), mode='constant')
        y_temp = np.convolve(xi_padded,FR[i],mode='valid')
        y_temp = (np.abs(y_temp))**2
        y_temp = y_temp/Penalty[i]
        if apply_averaging:
            npad = len(FA[i]) - 1
            y_temp_padded = np.pad(y_temp, (npad//2, npad - npad//2), mode='constant')
            y_temp = np.convolve(y_temp_padded,FA[i],mode='valid')
        y[:,i] = y_temp

    y[:,0] = 0;  # Periods 1 give strong features on the time vs period planes. Hence, zeroing them out to view the other periods better.
    y = y - np.min(y)
    y = y/np.max(y)
    y[y<Th]=0
    if return_filters:
        return y,FR, FA
    return y

def _create_dictionary(Nmax, rowSize, method='Ramanujan'):
    r"""Creating Dictionary for RFB
    
    **Creating Dictionary for RFB**


    Parameters
    ----------
    Nmax    : maximum expected Period,
    rowSize : number of rows (e.g. samples in signal)
    method  : 'Ramanujan' 'random', 'NaturalBasis', 'DFT'


    Returns
    -------
    A :  Matrix of (rowSize, q)

    References
    ----------
    The relevant paper is:
    [1] S.V. Tenneti and P. P. Vaidyanathan, "Nested Periodic Matrices and Dictionaries:
        New Signal Representations for Period Estimation", IEEE Transactions on Signal
        Processing, vol.63, no.14, pp.3736-50, July, 2015.

    Python impletation is done by using matlab code version from
    - http://systems.caltech.edu/dsp/students/srikanth/Ramanujan/

    
    Notes
    -----

    See Also
    --------
    spkit: # TODO

    Examples
    --------
    import numpy as np
    import spkit as sp
    """
    A = []
    for N in range(Nmax):
        if method in ['Ramanujan', 'NaturalBasis', 'random', 'ramanujan','natural_basis']:
            if method=='Ramanujan' or method=='ramanujan':
                c1 = np.zeros(N+1) + 1j*0
                k_orig = np.arange(N+1)+1
                k = k_orig[np.gcd(k_orig,N+1)==1]
                for n in range(N):
                    c1[n] += np.sum([np.exp(1j*2*np.pi*a*(n)/(N+1)) for a in k])
                c1 = np.real(c1)

            elif method=='NaturalBasis' or method=='natural_basis':
                c1 = np.zeros(N+1)
                c1[0] = 1

            elif method=='random':
                c1 = np.random.randn(N+1)

            k_orig = np.arange(N+1)+1
            k = k_orig[np.gcd(k_orig,N+1)==1]
            CN_colSize = len(k)  #k.shape[1]

            CN=[]
            for j in range(CN_colSize):
                CN.append(np.roll(c1,j))
            CN = np.vstack(CN).T

        else: #method=='Farey'
            A_dft = LA.dft(N+1)
            a = np.arange(N+1)
            a[0] = N+1
            a = (N+1)/np.gcd(a,N+1)
            I = np.arange(N+1)
            I = I[a==N+1]
            CN = A_dft[:,I]

        CNA = np.tile(CN,(np.floor(rowSize/(N+1)).astype(int),1))
        CN_cutoff = CN[:np.remainder(rowSize,N+1),:]
        CNA =np.vstack([CNA,CN_cutoff])
        A.append(CNA)
    return np.hstack(A)

def _periodstrength(x,Pmax,method='Ramanujan',lambd=1,L=1,cvxsol=False):
    r"""Computing strength of periods
    
    **Computing strength of periods**

    for given signal x, using method and respective loss fun (e.g. l1, l2)

    Parameters
    ----------

    x   :  one dimentional sequence (signal)
    Pmax: largest expected period in the signal
    method: type of dictionary used to create transform matrix A
          : 'Ramanujan', 'NaturalBasis', 'random' or Farray (DFT)

    lambd: for penalty vector, to force towards lower (usually) or higher periods
         : if 0, then penalty vector is 1, means no penalization
         : if >0, then lambd is multiplied to penalty vector

    L : regularazation: L=1, minimize ||s||_1, L=2, ||s||_2

    cvxsol: bool, wether to use cvxpy solver of matrix decomposition approach
          : matrix decomposition approach works only for L=2
          : for L=1, use cvxpy as solver

    Returns
    -------

    period_energy: vecotor shape: (Pmax,): strength of each period


    Reference:
    [1] S.V. Tenneti and P. P. Vaidyanathan, "Nested Periodic Matrices and Dictionaries:
       New Signal Representations for Period Estimation", IEEE Transactions on Signal
       Processing, vol.63, no.14, pp.3736-50, July, 2015.

    Python impletation is done by using matlab code version from
    - http://systems.caltech.edu/dsp/students/srikanth/Ramanujan/
    """

    if cvxsol:
        try:
            import cvxpy
        except Exception as err:
            wst =  "cvxpy is not installed! use 'pip install cvxpy --user' \n"
            wst += "install cvxpy for L1 norm minimization for regularised_period_strength fun (Ramanujan methods)"
            wst += "Or set 'cvxsol=False' to use LMS\n"
            wst += f"Unexpected {err}, {type(err)}"
            warnings.warn(wst,stacklevel=2)
            raise
    assert np.ndim(x)==1
    #Nmax = Pmax
    A = create_dictionary(Pmax,x.shape[0],method)

    #Penalty Vector Calculation
    if lambd>0:
        penalty_vector = []
        for i in range(Pmax):
            k = np.arange(i+1)+1
            k_red = k[np.gcd(k,i+1)==1]
            k_red = len(k_red)
            penalty_vector.append((i+1)*np.ones(k_red))
        penalty_vector = np.hstack(penalty_vector)
        penalty_vector = lambd*(penalty_vector**2)
    else:
        penalty_vector = np.ones(A.shape[1]) #0*(penalty_vector**2)+1


    if cvxsol:
        s = cvxpy.Variable(A.shape[1], complex=np.sum(np.iscomplex(x)))
        cost = cvxpy.norm(cvxpy.multiply(penalty_vector, s),L)
        constraints = [x == A@s]
        prob = cvxpy.Problem(cvxpy.Minimize(cost),constraints)
        prob.solve()
        si = s.value
    else:
        #x = A@s -->  s = inv(A.T@A)@A.T@x
        D = np.diag((1./penalty_vector)**2)
        PP = (D@A.T)@LA.inv(A@D@A.T)
        s = PP@x
        si = s

    if si is None:
        raise ValueError('No solution found with selected optimization setting, try again with differen settings or input.')

    period_energy = np.zeros(Pmax)
    index_end = 0
    for i in range(Pmax):
        k_orig = np.arange(i+1)+1
        k = k_orig[np.gcd(k_orig,i+1)==1]
        index_start = index_end
        index_end   = index_end + len(k)
        period_energy[i] += np.nansum(np.abs(si[index_start:index_end])**2)

    period_energy[0] = 0 #one sample period is stronger, so zeroing it out
    return period_energy

def _RFB_prange(x,Pmin=1,Pmax=10,skip=1,Rcq=10,Rav=2,thr=0.2,Penalty=None,return_filters=False,apply_averaging=True):
    r"""Ramanujan Filter Banks for Estimation and Tracking of Periodicity with given range.
    
    **Ramanujan Filter Banks for Estimation and Tracking of Periodicity**

    - for range of period given by Pmin and Pmax.

    Parameters
    ----------

    x    = 1d array, sequence of signal
    Pmin = the smallest expected period. (default=1)
    Pmax = the largest expected period.
    skip = int >=1: if to skip period (default=1 --> no skipping) (>1 is not recomended)
    Rcq  = Number of repeats in each Ramanujan filter
    Rav  = Number of repeats in each averaging filter
    thr   = Outputs of the RFB are thresholded to zero for all values less than Th*max(output)
    Penalty = penalty for each period shape=(len(Pmax)),
             If None, then set to 1, means no penalty
    apply_averaging: bool, if False, no averaging is applied (deault=True)
    return_filters: bool, ifTrue, return FR - Ramanujan and FA - Averaging filters

    Returns
    -------

    y = 2d array of shape = (len(x),Pmax), time vs period matrix, normalized

    if return_filters==True: also returns

    FR = list of Ramanujan Filters
    FA = list of Averaging Filters

    References
    ----------

    * [1] S.V. Tenneti and P. P. Vaidyanathan, "Ramanujan Filter Banks for Estimation
       and Tracking of Periodicity", Proc. IEEE Int. Conf. Acoust.
       Speech, and Signal Proc., Brisbane, April 2015.

    * [2] P.P. Vaidyanathan and S.V. Tenneti, "Properties of Ramanujan Filter Banks",
        Proc. European Signal Processing Conference, France, August 2015.

    * Python impletation is done by using matlab code version from - http://systems.caltech.edu/dsp/students/srikanth/Ramanujan/

    Notes
    -----
    * 

    See Also
    --------
    spkit: # TODO

    Examples
    --------
    #sp.RFB_prange
    import numpy as np
    import matplotlib.pyplot as plt
    import spkit as sp
    np.random.seed(2)
    #period = 10 #SNR = 0
    period = 8
    x1 = np.zeros(30)
    x2 = np.random.randn(period)
    x2 = np.tile(x2,10)
    x3 = np.zeros(30)
    x  = np.r_[x1,x2,x3]
    x_noise = sp.add_noise(x,snr_db=0)
    Pmin = 4
    Pmax = 20
    y,plist, FR, FA = sp.RFB_prange(x_noise,Pmin=Pmin, Pmax=Pmax, skip=2, Rcq=10, Rav=2, thr=0.2,return_filters=True)
    idx = np.argsort(np.sum(y,0))[::-1]
    print('top 10 periods: ',plist[idx[:10]])
    plt.figure(figsize=(12,6))
    plt.subplot(211)
    plt.plot(x,label='signal: x')
    plt.plot(x_noise, label='signal+noise: x_noise')
    plt.text(5,3.5,f'signal with repitative patterns')
    plt.xlim([0,len(x)])
    #plt.xlabel('sample (n)')
    plt.legend(bbox_to_anchor=(1,1))
    plt.subplot(223)
    im = plt.imshow(y.T,aspect='auto',cmap='jet',extent=[1,len(x_noise),Pmax,Pmin])
    plt.yticks(plist)
    plt.colorbar(im)
    plt.xlabel('sample (n)')
    plt.ylabel('period (in samples)')
    plt.subplot(224)
    plt.stem(plist,np.sum(y,0))
    plt.xlabel('period (in samples)')
    plt.ylabel('strength')
    plt.tight_layout()
    plt.show()
    """



    Plist = np.arange(Pmin,Pmax+1,skip).astype(int)
    nP = len(Plist)

    # Peanlty vector.
    if Penalty is None: Penalty = np.ones(nP)
    # Can be (optionally) used to set preference  to a certain set of periods in the
    # time vs period plane.


    FR = []  #*nP #The set of Ramanujan Filters
    FA = []  #*nP #The set of Averaging Filters

    for p in Plist:      #range(Pmin-1,Pmax):
        cq = np.zeros(p) + 1j*0  #cq shall be the ith ramanujan sum sequnece.
        k_orig = np.arange(p)+1
        k = k_orig[np.gcd(k_orig,p)==1]
        for n in range(p):
            cq[n] += np.sum([np.exp(1j*2*np.pi*a*(n)/(p)) for a in k])

        cq = np.real(cq)
        fr = np.tile(cq,Rcq)
        fr /=np.linalg.norm(fr)
        FR.append(fr)

        fa  = np.tile(np.ones(p),Rav)
        fa /= np.linalg.norm(fa)
        FA.append(fa)


    #Computing the Outputs of the Filter Bank
    y = np.zeros([len(x),nP])

    if np.ndim(x)>1:
        xi = x[:,0].copy()
    else:
        xi = x.copy()

    kii= 0
    for i in range(len(FR)):
        npad = len(FR[i]) - 1
        xi_padded = np.pad(xi, (npad//2, npad - npad//2), mode='constant')
        y_temp = np.convolve(xi_padded,FR[i],mode='valid')
        y_temp = (np.abs(y_temp))**2
        y_temp = y_temp/Penalty[i]
        if apply_averaging:
            npad = len(FA[i]) - 1
            y_temp_padded = np.pad(y_temp, (npad//2, npad - npad//2), mode='constant')
            y_temp = np.convolve(y_temp_padded,FA[i],mode='valid')
        y[:,i] = y_temp

    if Plist[0]==1:
        y[:,0] = 0;  # Periods 1 give strong features on the time vs period planes.
                     # Hence, zeroing them out to view the other periods better.
    y = y - np.min(y)
    y = y/np.max(y)
    y[y<thr]=0
    if return_filters:
        return y,Plist,FR, FA
    return y,Plist

@deprecated("due to naming consistency, please use 'ramanujan_filter' for updated/improved functionality. [spkit-0.0.9.7]")
def RFB(x, Pmax=10, Rcq=10, Rav=2, Th=0.2,Penalty=None,return_filters=False, apply_averaging=True):
    r"""Ramanujan Filter Banks for Estimation and Tracking of Periodicity

    Ramanujan Filter Banks for Estimation and Tracking of Periodicity

    .. warning::
        NOTE: Use :func:`ramanujan_filter` instead. That is most updated version. 
        :func:`RFB` will be removed in future release.

    Parameters
    ----------
    x    : 1d array, sequence of signal
    Pmax : the largest expected period.
    Rcq  : Number of repeats in each Ramanujan filter
    Rav  : Number of repeats in each averaging filter
    Th   : Outputs of the RFB are thresholded to zero for all values less than Th*max(output)
    Penalt = penalty for each period shape=(len(Pmax)),
             If None, then set to 1, means no penalty

    Returns
    -------
    y: 2d array of shape = (len(x),Pmax)
      - time vs period matrix, normalized

    if return_filters==True,
       - also returns
        * FR : list of Ramanujan Filters
        * FA : list of Averaging Filters

    References
    ----------
    * [1] S.V. Tenneti and P. P. Vaidyanathan, "Ramanujan Filter Banks for Estimation
      and Tracking of Periodicity", Proc. IEEE Int. Conf. Acoust.
      Speech, and Signal Proc., Brisbane, April 2015.

    * [2] P.P. Vaidyanathan and S.V. Tenneti, "Properties of Ramanujan Filter Banks",
      Proc. European Signal Processing Conference, France, August 2015.

    * Python impletation is done by using matlab code version from - http://systems.caltech.edu/dsp/students/srikanth/Ramanujan/

    Notes
    -----
    * 

    See Also
    --------
    spkit: # TODO

    Examples
    --------
    #sp.RFB
    import numpy as np
    import matplotlib.pyplot as plt
    import spkit as sp
    np.random.seed(2)
    #period = 10 #SNR = 0
    period = 8
    x1 = np.zeros(30)
    x2 = np.random.randn(period)
    x2 = np.tile(x2,10)
    x3 = np.zeros(30)
    x  = np.r_[x1,x2,x3]
    x_noise = sp.add_noise(x,snr_db=0)
    Pmax=40
    y,FR, FA = sp.RFB(x_noise,Pmax=Pmax, Rcq=15, Rav=2, Th=0.2,return_filters=True)
    print('top 10 periods: ',np.argsort(np.sum(y,0))[::-1][:10]+1)
    plt.figure(figsize=(12,6))
    plt.subplot(211)
    plt.plot(x,label='signal: x')
    plt.plot(x_noise, label='signal+noise: x_noise')
    plt.text(5,3.5,f'signal with repitative patterns')
    plt.xlim([0,len(x)])
    #plt.xlabel('sample (n)')
    plt.legend(bbox_to_anchor=(1,1))
    plt.subplot(223)
    im = plt.imshow(y.T,aspect='auto',cmap='jet',extent=[1,len(x_noise),Pmax,1])
    plt.colorbar(im)
    plt.xlabel('sample (n)')
    plt.ylabel('period (in samples)')
    plt.subplot(224)
    plt.stem(np.arange(1,y.shape[1]+1),np.sum(y,0))
    plt.xlabel('period (in samples)')
    plt.ylabel('strength')
    plt.tight_layout()
    plt.show()
    """
    return _RFB(x, Pmax=Pmax, Rcq=Rcq, Rav=Rav, Th=Th,
           Penalty=Penalty,return_filters=return_filters,
           apply_averaging=apply_averaging)

@deprecated("due to naming consistency, please use 'create_dictionary' for updated/improved functionality. [spkit-0.0.9.7]")
def Create_Dictionary(Nmax, rowSize, method='Ramanujan'):
    r"""Creating Dictionary for RFB
    
    **Creating Dictionary for RFB**
    
    .. warning::
        NOTE: Use :func:`create_dictionary` instead. That is most updated version. 
        :func:`Create_Dictionary` will be removed in future release.


    Parameters
    ----------
    Nmax    : maximum expected Period,
    rowSize : number of rows (e.g. samples in signal)
    method  : 'Ramanujan' 'random', 'NaturalBasis', 'DFT'


    Returns
    -------
    A :  Matrix of (rowSize, q)

    References
    ----------
    The relevant paper is:
    [1] S.V. Tenneti and P. P. Vaidyanathan, "Nested Periodic Matrices and Dictionaries:
        New Signal Representations for Period Estimation", IEEE Transactions on Signal
        Processing, vol.63, no.14, pp.3736-50, July, 2015.

    Python impletation is done by using matlab code version from
    - http://systems.caltech.edu/dsp/students/srikanth/Ramanujan/

    
    Notes
    -----

    See Also
    --------
    spkit: # TODO

    Examples
    --------
    import numpy as np
    import spkit as sp
    """
    return _create_dictionary(Nmax, rowSize, method=method)


@deprecated("due to naming consistency, please use 'regularised_period_estimation' for updated/improved functionality. [spkit-0.0.9.7]")
def PeriodStrength(x,Pmax,method='Ramanujan',lambd=1,L=1,cvxsol=False):
    r"""Computing strength of periods
    
    **Computing strength of periods**

    for given signal x, using method and respective loss fun (e.g. l1, l2)

    .. warning::
        NOTE: Use :func:`regularised_period_estimation` instead. That is most updated version. 
        :func:`PeriodStrength` will be removed in future release.


    Parameters
    ----------

    x   :  one dimentional sequence (signal)
    Pmax: largest expected period in the signal
    method: type of dictionary used to create transform matrix A
          : 'Ramanujan', 'NaturalBasis', 'random' or Farray (DFT)

    lambd: for penalty vector, to force towards lower (usually) or higher periods
         : if 0, then penalty vector is 1, means no penalization
         : if >0, then lambd is multiplied to penalty vector

    L : regularazation: L=1, minimize ||s||_1, L=2, ||s||_2

    cvxsol: bool, wether to use cvxpy solver of matrix decomposition approach
          : matrix decomposition approach works only for L=2
          : for L=1, use cvxpy as solver

    Returns
    -------

    period_energy: vecotor shape: (Pmax,): strength of each period


    Reference:
    [1] S.V. Tenneti and P. P. Vaidyanathan, "Nested Periodic Matrices and Dictionaries:
       New Signal Representations for Period Estimation", IEEE Transactions on Signal
       Processing, vol.63, no.14, pp.3736-50, July, 2015.

    Python impletation is done by using matlab code version from
    - http://systems.caltech.edu/dsp/students/srikanth/Ramanujan/
    """

    return _periodstrength(x,Pmax,method=method,lambd=lambd,L=L,cvxsol=cvxsol)

@deprecated("due to naming consistency, please use 'ramanujan_filter_prange' for updated/improved functionality. [spkit-0.0.9.7]")
def RFB_prange(x,Pmin=1,Pmax=10,skip=1,Rcq=10,Rav=2,thr=0.2,Penalty=None,return_filters=False,apply_averaging=True):
    r"""Ramanujan Filter Banks for Estimation and Tracking of Periodicity with given range.
    
    **Ramanujan Filter Banks for Estimation and Tracking of Periodicity**

    
    .. warning::
        NOTE: Use :func:`ramanujan_filter_prange` instead. That is most updated version. 
        :func:`RFB_prange` will be removed in future release.


    - for range of period given by Pmin and Pmax.

    Parameters
    ----------

    x    = 1d array, sequence of signal
    Pmin = the smallest expected period. (default=1)
    Pmax = the largest expected period.
    skip = int >=1: if to skip period (default=1 --> no skipping) (>1 is not recomended)
    Rcq  = Number of repeats in each Ramanujan filter
    Rav  = Number of repeats in each averaging filter
    thr   = Outputs of the RFB are thresholded to zero for all values less than Th*max(output)
    Penalty = penalty for each period shape=(len(Pmax)),
             If None, then set to 1, means no penalty
    apply_averaging: bool, if False, no averaging is applied (deault=True)
    return_filters: bool, ifTrue, return FR - Ramanujan and FA - Averaging filters

    Returns
    -------

    y = 2d array of shape = (len(x),Pmax), time vs period matrix, normalized

    if return_filters==True: also returns

    FR = list of Ramanujan Filters
    FA = list of Averaging Filters

    References
    ----------

    * [1] S.V. Tenneti and P. P. Vaidyanathan, "Ramanujan Filter Banks for Estimation
       and Tracking of Periodicity", Proc. IEEE Int. Conf. Acoust.
       Speech, and Signal Proc., Brisbane, April 2015.

    * [2] P.P. Vaidyanathan and S.V. Tenneti, "Properties of Ramanujan Filter Banks",
        Proc. European Signal Processing Conference, France, August 2015.

    * Python impletation is done by using matlab code version from - http://systems.caltech.edu/dsp/students/srikanth/Ramanujan/

    Notes
    -----
    * 

    See Also
    --------
    spkit: # TODO

    Examples
    --------
    #sp.RFB_prange
    import numpy as np
    import matplotlib.pyplot as plt
    import spkit as sp
    np.random.seed(2)
    #period = 10 #SNR = 0
    period = 8
    x1 = np.zeros(30)
    x2 = np.random.randn(period)
    x2 = np.tile(x2,10)
    x3 = np.zeros(30)
    x  = np.r_[x1,x2,x3]
    x_noise = sp.add_noise(x,snr_db=0)
    Pmin = 4
    Pmax = 20
    y,plist, FR, FA = sp.RFB_prange(x_noise,Pmin=Pmin, Pmax=Pmax, skip=2, Rcq=10, Rav=2, thr=0.2,return_filters=True)
    idx = np.argsort(np.sum(y,0))[::-1]
    print('top 10 periods: ',plist[idx[:10]])
    plt.figure(figsize=(12,6))
    plt.subplot(211)
    plt.plot(x,label='signal: x')
    plt.plot(x_noise, label='signal+noise: x_noise')
    plt.text(5,3.5,f'signal with repitative patterns')
    plt.xlim([0,len(x)])
    #plt.xlabel('sample (n)')
    plt.legend(bbox_to_anchor=(1,1))
    plt.subplot(223)
    im = plt.imshow(y.T,aspect='auto',cmap='jet',extent=[1,len(x_noise),Pmax,Pmin])
    plt.yticks(plist)
    plt.colorbar(im)
    plt.xlabel('sample (n)')
    plt.ylabel('period (in samples)')
    plt.subplot(224)
    plt.stem(plist,np.sum(y,0))
    plt.xlabel('period (in samples)')
    plt.ylabel('strength')
    plt.tight_layout()
    plt.show()
    """
    return _RFB_prange(x,Pmin=Pmin,Pmax=Pmax,skip=skip,Rcq=Rcq,Rav=Rav,
                      thr=thr,Penalty=Penalty,
                      return_filters=return_filters,
                      apply_averaging=apply_averaging)


def RFB_example_1(period=10,SNR=0,seed=10):
    r"""Example 1 for Ramanujan Filter Bank

    Parameters
    ----------
    period: int, default =10
    SNR: scaler, signal to noise ratio 
       - larger the value, higher the noise
    seed: int, 
      - random seed to reproduce

    See Also
    --------
    RFB_example_2, ramanujan_filter, ramanujan_filter_prange, regularised_period_estimation, create_dictionary

    Examples
    --------
    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> import spkit as sp
    >>> sp.RFB_example_1(period=10,SNR=0,seed=10)
    >>> plt.show()
    """
    np.random.seed(seed)
    #period = 10
    #SNR = 0

    x1 = np.zeros(30)
    x2 = np.random.randn(period)
    x2 = np.tile(x2,10)
    x3 = np.zeros(30)
    x  = np.r_[x1,x2,x3]
    x /= LA.norm(x,2)

    noise  = np.random.randn(len(x))
    noise /= LA.norm(noise,2)

    noise_power = 10**(-1*SNR/20)

    noise *= noise_power
    x_noise = x + noise

    

    Pmax = 40  #Largest expected period in the input
    Rcq  = 10   # Number of repeats in each Ramanujan filter
    Rav  = 2    #Number of repeats in each averaging filter
    Th   = 0.2   #Outputs of the RFB are thresholded to zero for all values less than Th*max(output)

    y,FR, FA = ramanujan_filter(x_noise,Pmax, Rcq, Rav, Th,return_filters=True)



    plt.figure(figsize=(12,6))
    plt.subplot(211)
    plt.plot(x,label='signal: x')
    plt.plot(x_noise, label='signal+noise: x_noise')
    plt.title(f'signal with repitative patterns')
    plt.xlim([0,len(x)])
    plt.xlabel('sample (n)')
    plt.legend(bbox_to_anchor=(1,1))
    plt.subplot(223)
    im = plt.imshow(y.T,aspect='auto',cmap='jet',extent=[1,len(x_noise),Pmax,1])
    plt.colorbar(im)
    plt.xlabel('sample (n)')
    plt.ylabel('period (in samples)')
    plt.subplot(224)
    plt.stem(np.arange(1,y.shape[1]+1),np.sum(y,0))
    plt.xlabel('period (in samples)')
    plt.ylabel('strength')
    plt.tight_layout()
    plt.show()

    print('top 10 periods: ',np.argsort(np.sum(y,0))[::-1][:10]+1)

def RFB_example_2(periods=[3,7,11],signal_length=100,SNR=10,seed=15):
    r"""Example 2 for Ramanujan Filter Bank

    Parameters
    ----------
    periods: list of int, default [3,7,11]
        - list of periods to generate signal
    signal_length: int, default 100
       - length of signal
    SNR: scaler, signal to noise ratio 
       - larger the value, higher the noise
    seed: int, 
      - random seed to reproduce

    
    Notes
    -----

    See Also
    --------
    RFB_example_1, ramanujan_filter, ramanujan_filter_prange, regularised_period_estimation, create_dictionary

    Examples
    --------
    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> import spkit as sp
    >>> sp.RFB_example_2()
    >>> plt.show()
    """
    np.random.seed(seed)
    #periods    = [3,7,11]
    #signal_length = 100
    #SNR = 10
    x = np.zeros(signal_length)
    for period in periods:
        x_temp  = np.random.randn(period)
        x_temp  = np.tile(x_temp,int(np.ceil(signal_length/period)))
        x_temp  = x_temp[:signal_length]
        x_temp /= LA.norm(x_temp,2)
        x += x_temp

    x /= LA.norm(x,2)

    noise  = np.random.randn(len(x))
    noise /= LA.norm(noise,2)
    noise_power = 10**(-1*SNR/20)
    noise *= noise_power
    x_noise = x + noise

    Pmax = 90

    cvxsol_true = True

    try:
        import cvxpy
    except:
        cvxsol_true = False
        warnings.warn("example is executed without use of 'cvxpy'. Try installing cvxpy to be able to use it. ",stacklevel=2)


    period_est_l1_1l = regularised_period_estimation(x_noise,Pmax=Pmax,method='Ramanujan',lambd=1, L=1, cvxsol=cvxsol_true)
    period_est_l1_0l = regularised_period_estimation(x_noise,Pmax=Pmax,method='Ramanujan',lambd=0, L=1, cvxsol=cvxsol_true)
    period_est_l2_1l = regularised_period_estimation(x_noise,Pmax=Pmax,method='Ramanujan',lambd=1, L=2, cvxsol=False)
    y =  ramanujan_filter(x_noise,Pmax = Pmax, Rcq=10, Rav=2, Th=0.2)
    period_est_rbf  = np.sum(y,0)

    print('Top 10 periods : ')
    print(' - using L1 regularisation with penalty    : ',np.argsort(period_est_l1_1l)[::-1][:10]+1)
    print(' - using L1 regularisation with no penalty : ',np.argsort(period_est_l1_0l)[::-1][:10]+1)
    print(' - using L2 regularisation with penalty    : ',np.argsort(period_est_l2_1l)[::-1][:10]+1)
    print(' - using no regularisation no  penalty     : ',np.argsort(period_est_rbf)[::-1][:10]+1)

    plt.figure(figsize=(12,12))
    plt.subplot(411)
    plt.plot(x,label='signal: x')
    plt.plot(x_noise, label='signal+noise: x_noise')
    #plt.text(5,1.01*np.max(x_noise) ,f'signal with repitative patterns')
    plt.xlim([0,len(x)])
    plt.xlabel('sample (n)')
    plt.legend(bbox_to_anchor=(1,1))
    plt.subplot(423)
    XF = np.abs(np.fft.fft(x_noise))[:1+len(x_noise)//2]
    fq = np.arange(len(XF))/(len(XF)-1)
    plt.stem(fq,XF)
    plt.title('DFT')
    plt.ylabel('| X |')
    plt.xlabel(r'frequency $\times$ ($\omega$/2)   ~   1/period ')

    plt.subplot(424)
    plt.stem(np.arange(len(period_est_l1_1l))+1,period_est_l1_1l)
    plt.xlabel('period (in samples)')
    plt.ylabel('strength')
    plt.title('L1 + penality')

    plt.subplot(425)
    plt.stem(np.arange(len(period_est_l2_1l))+1,period_est_l2_1l)
    plt.xlabel('period (in samples)')
    plt.ylabel('strength')
    plt.title('L2 +  penalty')
    plt.subplot(426)
    plt.stem(np.arange(len(period_est_l1_0l))+1,period_est_l1_0l)
    plt.xlabel('period (in samples)')
    plt.ylabel('strength')
    plt.title('L1 without penality')


    plt.subplot(427)
    im = plt.imshow(y.T,aspect='auto',cmap='jet',extent=[1,len(x_noise),Pmax,1])
    plt.colorbar(im)
    plt.xlabel('sample (n)')
    plt.ylabel('period (in samples)')

    plt.subplot(428)
    plt.stem(np.arange(1,y.shape[1]+1),period_est_rbf)
    plt.xlabel('period (in samples)')
    plt.ylabel('strength')
    plt.tight_layout()
    plt.show()




