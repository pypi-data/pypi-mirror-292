from .fits import lorentzian, lorentzianFit, gaussian2DFit, gaussianFit, gaussian
import os
from .Images import approximatePositionOfTheCloud, rcParams
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import matplotlib.patches as patch
from scipy.constants import *
from scipy.special import wofz as w
from scipy.optimize import curve_fit
import numpy as np

def spectroscopy(ODimages, f, d=4, atom_loss=False, plot=True, fileNum='', lor_fit=False, savefig=False):
    '''
    Adds the OD of the pixels around the centre and uses the sum to plot the spectrum of the scan
    corresponding to the given frequencies. This is then fit to a gaussian (or a lorentzian)
    to find the center and width.

    Parameters:
        ODimages: ODimages extracted from ShadowImaging sequences
        f: array of frequencies for which the scan is done
        d: int, default is 4, size of the image area to consider around the centre of OD
        atom_loss: bool, default is False, flag to specify if atom loss spectroscopy is done
        plot: bool, default is True, flag to specify if the data has to be plotted
        fileNum: string, file number (plus any additional description) of the image file for which the analysis is done
        lor_fit: bool, default is False. This is a flag to fit the data to a lorentzian instead of a gaussian
        savefig: bool, default is False. Change it to true if you want to save the spectrum as .png

    Returns:
        a tuple, (amp, centre, sigma, offset) of the gaussian fit or (amp, centre, gamma, offset) of the lorentzian fit
    '''
    n = len(ODimages)
    f_smooth = np.linspace(f[0], f[-1]+(f[1]-f[0]), 200, endpoint=False)
    if n!=len(f):
        raise ValueError('No of images and no. of  frequencies are not equal')
    step = np.round(f[1]-f[0], 3)
    # finding approximate center of the cloud
    y, x, size = approximatePositionOfTheCloud(np.mean(ODimages, axis=0))
    index = []
    for i in range(n):
        index.append(np.sum(np.sum(ODimages[i][y+1-d:y+1+d, x+1-d:x+1+d])))
    maxODAt = np.argmax(index)
    minODAt = np.argmin(index)
    critical = maxODAt
    title = 'Max.'
    if lor_fit == False:
        try:
            if atom_loss==True:
                pOpt, pCov = gaussianFit(f, np.array(index), p0=[min(index), f[minODAt], 0.1, 0], plot=False, display=False)
                critical = minODAt
                title = 'Min.'
            else:
                pOpt, pCov = gaussianFit(f, np.array(index), p0=[max(index), f[maxODAt], 0.1, 0], plot=False, display=False)
        except RuntimeError:
            pOpt = []
    else:
        try:
            if atom_loss==True:
                pOpt, pCov = lorentzianFit(f, np.array(index), p0=[min(index), f[minODAt], 0.1, 0], plot=False, display=False)
                critical = minODAt
                title = 'Min.'
            else:
                pOpt, pCov = lorentzianFit(f, np.array(index), p0=[max(index), f[maxODAt], 0.1, 0], plot=False, display=False)
        except RuntimeError:
            pOpt = []
    if plot == True:
        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(9,3))
        i = ax[0].imshow(ODimages[critical])
        fig.colorbar(i, ax=ax[0])
        ax[0].scatter(x+1, y+1, marker='+', color='r')
        ax[0].set_title(title+' OD at: '+str(critical))
        rectangle = patch.Rectangle((x+1-d, y+1-d), 2*d, 2*d, linewidth=1,edgecolor='r',facecolor='none')
        ax[0].add_patch(rectangle)
        ax[0].grid(False)
        ax[1].plot(f, index, 'o')
        if pOpt!=[]:
            if lor_fit == True:
                ax[1].plot(f_smooth, lorentzian(f_smooth, *pOpt), 'k',
                           label='lor. fit:\n$\Gamma = {:.3f}$\n$f_0 = {:.3f}$'.format(abs(pOpt[2]), pOpt[1]))
            else:
                ax[1].plot(f_smooth, gaussian(f_smooth, *pOpt), 'k',
                           label='gaus. fit:\n $\sigma = {:.3f}$\n$f_0 = {:.3f}$'.format(abs(pOpt[2]), pOpt[1]))
            ax[1].legend()
        ax[1].set_ylabel('$\propto$ OD')
        ax[1].set_xlabel('$f$')
        ax[1].set_title(r'$f_{start}$ = '+str(f[0])+', $f_{step}$ = '+str(step)+', file = '+fileNum)
        plt.tight_layout()
        if savefig==True:
            try:
                plt.savefig('ColdTOFU_results/spectroscopy_result_for'+fileNum+'.png', transparent=True)
            except FileNotFoundError:
                pwd = os.getcwd()
                os.mkdir(os.path.join(pwd, 'ColdTOFU_results'))
                plt.savefig('ColdTOFU_results/spectroscopy_result_for'+fileNum+'.png', transparent=True)
    return pOpt, index # amp, centre, gamma, offset

def bv(f, f0, b0, T, s, offset):
    '''
    Function representing convolution of the lorentzian line shape of the red transition and gaussian maxwell
    distribution. This is taken from 5.13 from Chang chi's thesis and added the effect of saturation parameter.

    Args:
        f: numpy.array, frequency vector
        f0: float, resonance frequency or centre of the spectrum
        b0: float, optical depth at resonance at zero temperature
        T: float, temperature in micro K
        s: float, saturation parameter of the probe, :math:`I/I_s`.
        offset: float, offset

    Returns:
        optical depth for frequencies f in the shape f.
    '''
    gamma = 2*pi*7.5*milli
    vavg = np.sqrt(T*micro*Boltzmann/(87*m_p))
    k = 2*pi/(689*nano)
    x = w((2*pi*(f-f0) + 1j*gamma*np.sqrt(1+s)/2)*1e6/(np.sqrt(2)*k*vavg))
    return b0*np.sqrt(pi/8)*(1/(1+s))*(gamma*np.sqrt(1+s)*1e6/(k*vavg))*x.real+offset

def bvFit(f, array, p0=None, bounds=None):
    '''
    Function to fit spectroscopy data to real line shape of the transition.

    Args:
        f: numpy.array, frequency vector
        array: float, optical depth at scan frequencies f
        p0: initial guess for the fit as [f_0, b_0, T (in :math:`\mu K`), s]
        bounds: bounds for the fit as ([lower bounds], [upper bounds])

    Returns:
        a tuple with optimized parameters and covariance ex: (pOpt, pCov)
    '''
    pOpt, pCov = curve_fit(bv, f, array, p0, bounds=bounds)
    return pOpt, pCov

def spectroscopyFaddeva(ODimages, f, plot=True, atom_loss=False, fileNum='', savefig=False):
    '''
    Fits od images to a gaussian and uses its amplitude to plot the spectrum of the scan
    corresponding to the given frequencies. This is fit to :math:`b_v(\delta)` from Chang Chi's thesis to extract
    temperature in addition to center.

    Parameters:
        ODimages: ODimages extracted from ShadowImaging sequences
        f: array of frequencies for which the scan is done
        atom_loss: bool, default is False, flag to specify if atom loss spectroscopy is done
        plot: bool, default is True to specify if the data has to be plotted
        fileNum: string, file number (plus any additional description) of the image file for which the analysis is done.
        savefig: bool, default is False. Change it to true if you want to save the spectrum as .png

    Returns:
        a tuple, (centre, :math:`b_0`, T, s) of fit to :math:`b_v(\delta)`
    '''
    n = len(ODimages)
    imaging_params = rcParams().params
    f_smooth = np.linspace(f[0], f[-1] + (f[1] - f[0]), 100, endpoint=False)
    if n!=len(f):
        raise ValueError('No of images and no. of  frequencies are not equal')
    step = np.round(f[1]-f[0], 3)
    y, x, size = approximatePositionOfTheCloud(np.mean(ODimages, axis=0))
    index = []
    title = 'Max.'
    p0 = [1, x, y, size, size, 0, 0.1]
    bounds = ([-3, x-4, y-4, 0.2*size, 0.2*size, 0, -0.1], [4.5, x+4, y+4, 1.8*size, 1.8*size, 6.28, 0.3])
    for i in range(n):
        amp, xo, yo, sx, sy, theta, offset = gaussian2DFit(ODimages[i], p0, bounds, plot=False)[0]
        index.append(amp)
    if atom_loss==False:
        maxODAt = np.argmax(index)
        criticalOD = np.max(index)
    else:
        maxODAt = np.argmin(index)
        criticalOD = np.min(index)
        title = 'Min.'
    try:
        s = imaging_params['saturation'] # this should be for atom-loss probe in case of atom-loss spectroscopy not imaging probe
        b = ([min(f), -300, 0.01,  0.9*s, -100], [max(f), 300, 20,  1.1*s, 100])
        pOpt, pCov = bvFit(f, np.array(index), p0=[f[maxODAt], criticalOD, 5, s, 0], bounds=b)
    except RuntimeError:
        pOpt = [0, 0, 0, 0]
    T = pOpt[2]
    pixelSize = imaging_params['pixelSize']
    magnification = imaging_params['magnification']
    binning = imaging_params['binning']
    sizeFactor = pixelSize*binning/magnification
    

    if plot == True:
        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(9,3))
        if size != 0:
            i = ax[0].imshow(ODimages[maxODAt][y-3*int(size):y+3*int(size), x-3*int(size):x+3*int(size)])
        else:
            i = ax[0].imshow(ODimages[maxODAt])
        scalebar = AnchoredSizeBar(ax[0].transData, 2, str(np.round(2*sizeFactor/1e-6, 1))+r'$\mu$m',
                                   'lower right', color='white', frameon=False,size_vertical=0.2)

        ax[0].add_artist(scalebar)
        ax[0].set_title(title+' OD at: '+str(maxODAt))
        fig.colorbar(i, ax=ax[0])     
        ax[0].grid(False)
        ax[1].plot(f, index, 'o')
        if pOpt!=[]:
            ax[1].plot(f_smooth, bv(f_smooth, *pOpt), 'k', label=r'T='+str(np.round(T, 1))+'$\mu$K \n'+
                                                  '$b_0(0)$='+str(np.round(pOpt[1], 2))+'\n'+
                                                  '$f_0$ = '+str(np.round(pOpt[0], 3))+'\n'+
                                                  's = '+str(np.round(pOpt[3], 2)))
            ax[1].legend(loc='upper right')
        ax[1].set_ylabel('OD') # ignore comment \\times \sigma_x \\times \sigma_y
        ax[1].set_xlabel('$f$')
        ax[1].set_title(r'$f_{start}$ = '+str(f[0])+', $f_{step}$ = '+str(step)+', file = '+fileNum)
        plt.tight_layout()
        if savefig==True:
            try:
                plt.savefig('ColdTOFU_results/spectroscopy_Faddeva_result_for'+fileNum+'.png', transparent=True)
            except FileNotFoundError:
                pwd = os.getcwd()
                os.mkdir(os.path.join(pwd, 'ColdTOFU_results'))
                plt.savefig('ColdTOFU_results/spectroscopy_Faddeva_result_for'+fileNum+'.png', transparent=True)
    return pOpt, index
