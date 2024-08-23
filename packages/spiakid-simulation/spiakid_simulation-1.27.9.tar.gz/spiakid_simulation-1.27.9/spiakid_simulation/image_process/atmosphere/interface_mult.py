import numpy as np
from tkinter import * 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.figure import Figure
from scipy.ndimage import convolve

def generateKolmoScreen(N, pixelSize, r0, L0):
    """
    Generate a couple of AO-compensated screens.

    Parameters
    ----------
    N         : int : size of the created phase map [pixels]
    pixelSize : float : pix size of produced phase map [metres]
    r0        : float : r0 [metres]
    L0        : float : outer scale L0 [metres]

    Returns
    -------
    A tuple of phase screens (phi1, phi2)
    """
    # Remember that Fourier pairs are always linked through FFTs using the relation
    #      dx * dk * N = 1
    # where dx is the pixel size in one of the Fourier space, dk is the pixel
    # size in the dual space, N is the number of pixels across the image.
    
    
    # multipurpose array of N consecutive integers, with 0 at index N/2,
    # i.e. starting at N/2, ending at N/2-1, and then FFT-shifted.
    # Always useful when you're about to deal with FFTs.
    x = np.arange(N) - (N/2)
    x = np.fft.fftshift(x)   # Center the 0 value
    
    
    dk = 1. / (N*pixelSize)    # pixel size in frequency space
    # generating 2D spatial frequencies arrays with null frequency at index [0,0]
    nu, xi = np.meshgrid(x*dk, x*dk, indexing='ij')
    k = np.sqrt( nu**2 + xi**2 )  # map of modulus of spatial frequencies
    
    # spectrum of turbulence in "radians^2 per (1/meters)^2",
    # i.e. in radians^2.m^2
    W = 0.023 * r0**(-5./3.) * (k**2 + L0**-2)**(-11.0/6.0)
    
    # square root of W, useful later to spare CPU time
    w = np.sqrt(W)
    
    # ............... Now generating phases .................
    argu = np.random.rand(N,N) * (2*np.pi)  # flat random numbers between 0 and 2pi
    # Fourier transforming  w*exp(i*argu) :
    # Here the normalisation is important and non-trivial. A classical Fourier
    # transform would have required a normalisation using
    #     (dk**2) * FFT( w*exp(i*argu) )
    # but here it will be different. The random phases are not the fourier
    # transform because of a normalisation of the energy over the area of the
    # support. As a final consequence, after non-trivial calculus, the
    # normalisation shall be
    #     dk * FFT( w*exp(i*argu) )
    phi = dk * np.fft.fft2(w * np.exp(1j * argu))  # Fourier transform
    # phi is complex, and both real and imag parts can be useful. However, the
    # total energy of the spectrum has been spread between them so that they
    # need a factor of sqrt(2) to be properly scaled.
    
    # phi1 and phi2 are in radians, at the wavelength where r0 was given.
    phi1 = np.sqrt(2) * phi.real
    phi2 = np.sqrt(2) * phi.imag

    return (phi1, phi2)

def computePSF(phase, pixelSize, D, obscu):
    """
    Compute the PSF for some given phase screen and telescope diameter with
    obscuration

    Parameters
    ----------
    phase     : 2D array : phase screen [radians]
    pixelSize : float : pixel size of the phase screen [metres]
    D         : float : telescope diameter [metres]
    obscu     : float : telescope obscuration [metres]

    Returns
    -------
    PSF array, normalised as Strehl.
    """
    # first we need a pupil, so we generate a map of distances
    N, _ = phase.shape
    x = np.arange(N) - (N/2)
    xx, yy = np.meshgrid(x*pixelSize, x*pixelSize, indexing='ij')
    r = np.sqrt( xx**2 + yy**2 )  # map of distances
    pupil = np.logical_and( r<(D/2.), r>(obscu/2.) )
    pupil = pupil / np.sum(pupil)  # to get a Strehl-normalised psf on output
    
    complexPsf = np.fft.fftshift(np.fft.fft2( pupil * np.exp(1j*phase) ))
    
    # CCD-detected PSF
    PSF = np.abs(complexPsf)**2
    return PSF

def setMyParameters(fov_arcsec, wavelength_array, seeing, wind, D, obs_time):
    """
    Genere les bons parametres puor appeler les fonctions de calcul d'ecran
    de phase  generateKolmoScreen()  et  computePSF(), à partir de params
    système plus simples

    Parameters
    ----------
    fov_arcsec : flaot, field of view of the simulated image [arcsec]
    nb_pixels_img : int. Nb of pixels of the simulated image.
    time_step : float. Number of seconds between two simulated images [s].
    nb_image : int. Number of images to be simulated in the time-series.
    wavelength_array : list of floats. List of wavelengths to be simulated.
    seeing : float. Value of seeing [arcsec].
    wind : float. Wind speed in m/s.
    D : float. Telescope diameter [m].
    obscuration : float. Diameter of the telescope central obscuration [m].

    Returns
    -------
    pixel_screen_size : 
    N_big_screen : int. Nb of pix of the phase screen.
    Npup : int. Number of pixels across the telescope pupil.
    r0_short : float. Value of r0 at the shortest wavelength. [m]
    """
    RASC = 3600 * 180 / np.pi  # conversion rad to arcsec
    lam = np.array(wavelength_array) * 1e-6  # form a numpy array
    lam_short = np.min(lam)
    fov_radians = fov_arcsec / RASC
    
    # pixel size of the phase screen
    pixel_screen_size = lam_short / fov_radians 
    # pixel scale of the image
    # pixel_image_scale = fov_radians / nb_pixels_img
    # # size of the support for the FFT (integer, and even)
    # Nsupport = lam_short / (pixel_image_scale * pixel_screen_size)
    # Nsupport = int( np.round(Nsupport) )
    # if Nsupport%2:
    #     Nsupport += 1
    # wind computation. Here, the size of the "big screen" si defined in such
    # a way that it will cover the distance required to allow the wind to
    # displace during the duration of the time-series.
    size_big_screen = wind * obs_time# factor of 2 just to take a margin
    N_big_screen = int(size_big_screen / pixel_screen_size)
    if N_big_screen%2:
        N_big_screen += 1  # even number is preferred for fft
    
    # seeing conversion, from arcsec to a r0 value, as a function of wavelength
    lam_seeing = 500e-9 # wavelength used for the definition of the seeing (500nm as a standard)
    r0_seeing = lam_seeing / (seeing / RASC) # r0 at 500 nm
    # Conversion of r0 to another wavelength (to the shortest one)
    r0_short = r0_seeing * (lam_short/lam_seeing)**(6/5.)
    
    return pixel_screen_size, N_big_screen, r0_short

def pad_array(im, N):
    """
    Modify the size of an image <im> by padding with zeros all around.

    Parameters
    ----------
    im : image.
    N : int. Size of new image (square).

    Returns
    -------
    im_out : the new image.
    """
    if N%2:
        print("nombres pairs uniquement, svp ...")
    N += 1
    ni, nj = im.shape
    im_out = np.zeros((N, N)) # on reserve l'image finale
    di = (N - ni)//2 # petits calculs d'index pour placer l'image dedans
    dj = (N - nj)//2
    im_out[di:di+ni, dj:dj+nj] = im # on lui carre l'image dans le groin
    return im_out # et paf


def crop_array(im, N):
    """
    Crop a large image to a reduced dimension (N,N)

    Parameters
    ----------
    im : image
    N  : int. dimension of output image (N, N).

    Returns
    -------
    Cropped image.
    """
    ni, nj = im.shape
    di = (ni - N)//2 # petits calculs d'index pour placer l'image dedans
    dj = (nj - N)//2
    return im[di:di+N, dj:dj+N]
    

def makeven(i):
    # Increments the argument if odd number. Makes it even.
    if i%2:
        i += 1
    return i

def DAR(Z, Lam0, Lam, TC=11.5, RH=14.5, P=743):
    """
    The routine compute the Differential Atmospheric Dispersion
    for a given zenithal distance "Z" for different wavelengths "Lam"
    with respect to a reference wavelength "Lam0".

    The atmospheric parameters can be adjusted to those characterstic
    of the site the computation is made for.
    The parameters listed below refer to the average Paranal conditions.
    
    Routine from Enrico Marchetti, taken on eso.org website, translated from
    IDL by E Gendron.
    
    Parameters
    ----------
    Z       : float. The zenithal distance in degrees.
    Lam0 : float. The reference wavelength in microns.
    Lam  : float or array. Wavelength(s) in microns.
    TC      : float. Temperature at the ground [C°]
    RH      : flaot. Relative humidity at the ground [%]
    P       : float. Pressure at the ground [mbar]
    
    For La Silla site, the median params are TC=11.5, RH=14.5, P=743.
    For Armazones site, the median params are TC=7.5, RH=15, P=712.

    Returns
    -------
    DR : Same array as Lam. Amplitude of the differential atmospheric
    dispersion with respect to the reference wavelength Lam0.
    """
    ZD = Z*np.pi/180
    T = TC + 273.16
    PS = -10474.0+116.43*T-0.43284*T**2+0.00053840*T**3
    P2 = RH/100.0*PS
    P1 = P-P2
    D1 = P1/T*(1.0+P1*(57.90*1.0E-8-(9.3250*1.0E-4/T)+(0.25844/T**2)))
    D2 = P2/T*(1.0+P2*(1.0+3.7E-4*P2)*(-2.37321E-3+(2.23366/T)-
            (710.792/T**2)+(7.75141E4/T**3)))
    S0 = 1.0/Lam0
    S = 1.0/Lam
    N0_1 = 1.0E-8*((2371.34+683939.7/(130-S0**2)+4547.3/(38.9-S0**2))*D1+
            (6487.31+58.058*S0**2-0.71150*S0**4+0.08851*S0**6)*D2)
    N_1 = 1.0E-8*((2371.34+683939.7/(130-S**2)+4547.3/(38.9-S**2))*D1+
            (6487.31+58.058*S**2-0.71150*S**4+0.08851*S**6)*D2)
    DR = np.tan(ZD)*(N0_1-N_1)*206264.8
    return DR


def Screen_size(Ntot,Npsf):
    N = Npsf
    while N//Npsf *(N-Npsf) + (N//Npsf - 1 ) * Npsf +  (N%Npsf) <Ntot :
          N+=1
    return(N, N//Npsf *(N-Npsf) + (N//Npsf - 1 ) * Npsf + (N%Npsf) )

def displacement(Ntot,Npsf):
    N,new_ntot  = Screen_size(Ntot,Npsf)

    Disp_x = np.zeros(new_ntot+1)
    Disp_y = np.zeros(new_ntot+1)
    Disp_x[0] = 0
    Disp_y[0] = 0
    ind_x = 0
    ind_y = 0
    dir = 0
    for i in range(1,new_ntot+1):
        # Déplacement coté droit
        if Disp_x[i-1] + 1 + Npsf <= N and Disp_y[i-1] + 1 + Npsf <= N and Disp_y[i-1]%Npsf == 0 and dir == 0: 
            Disp_x[i] = Disp_x[i-1] + 1
            Disp_y[i] = Disp_y[i-1]
            ind_x += 1
            ind_y += 1

        # Déplacement coté gauche
        elif Disp_x[i-1] - 1 >=0 and Disp_y[i-1] - 1 >=0 and Disp_y[i-1]%Npsf == 0 and dir == 1: 

            Disp_x[i] = Disp_x[i-1] -1
            Disp_y[i] = Disp_y[i-1]
            ind_x += 1
            ind_y += 1

        #On monte

        else:
            Disp_x[i] = Disp_x[i-1]
            Disp_y[i] = Disp_y[i-1] + 1
            if Disp_y[i]%Npsf == 0 and Disp_x[i]//(N - Npsf)== 1:
                dir = 1
            elif Disp_y[i]%Npsf == 0 and Disp_x[i]//(N - Npsf) == 0:
                dir = 0
    Displacement = [Disp_x,Disp_y]
    return(Displacement)


# fov_arcsec = 1.15   # field of view of the simulated image [arcsec]
# nb_pixels_img = 36 # Nb of pixels of the simulated image.  Npsf
# time_step = 0.05    # Number of seconds between two simulated images [s].
# nb_image = 100      # Number of images to be simulated in the time-series.
# wavelength_array = np.linspace(0.4,0.8,40) # List of wavelengths to be simulated.
# seeing = 1.0        # Seeing value at 500nm
# wind = [10.0,30.0  ]       # Wind speed m/s
# coeff = [60,40]
# D = 3.5             # Tel diameter [m]
# obscuration = 1.    # Obscuration diameter [m]
# L0 = 30.            # Outer scale [m]
# zenit_angle = 30.   # Angle of observation from zenit [deg]
# obs_time = 1
fov_arcsec = 3.0    # field of view of the simulated image [arcsec]
nb_pixels_img = 300 # Nb of pixels of the simulated image.
time_step = 0.05    # Number of seconds between two simulated images [s].
nb_image = 100      # Number of images to be simulated in the time-series.
wavelength_array = np.linspace(0.4,0.8,40) # List of wavelengths to be simulated.
seeing = 1.0        # Seeing value at 500nm
# wind = 10.0         # Wind speed m/s
D = 3.5             # Tel diameter [m]
obscuration = 1.    # Obscuration diameter [m]
L0 = 30.            # Outer scale [m]
zenit_angle = 30.   # Angle of observation from zenit [deg]
# fov_arcsec = 0.166   # field of view of the simulated image [arcsec]
# nb_pixels_img = 5 # Nb of pixels of the simulated image.  Npsf
# time_step = 0.05    # Number of seconds between two simulated images [s].
# nb_image = 100      # Number of images to be simulated in the time-series.
# wavelength_array = np.linspace(0.4,0.8,40) # List of wavelengths to be simulated.
# seeing = 1.0        # Seeing value at 500nm
wind = [10.0,30.0,50.0]      # Wind speed m/s
coeff = [60,25,15]
# D = 3.5             # Tel diameter [m]
# obscuration = 1.    # Obscuration diameter [m]
obs_time = 1
# L0 = 30.            # Outer scale [m]
# zenit_angle = 30.   # Angle of observation from zenit [deg]
pixel_size_img = fov_arcsec / nb_pixels_img
# PSF = TF.PSF_creation_mult(fov_arcsec,nb_pixels_img,wavelength_array,seeing,wind,D,obscuration,L0,1,coeff)
screens = len(wind)
pixel_screen_size = np.zeros(screens)
Ntot = np.zeros(screens)
r0 = np.zeros(screens)
phi = np.zeros(screens,dtype=object)
Displacement = np.zeros(screens,dtype=object)

lam_short = np.min(np.array(wavelength_array))
for i in range(0,screens):
        pixel_screen_size[i],Ntot[i],r0[i] = setMyParameters( fov_arcsec,wavelength_array, seeing,wind[i], D, obs_time)
        Npsf = nb_pixels_img
        
        Displacement[i] = displacement(Ntot[i],Npsf)
        
        N,new_ntot  = Screen_size(Ntot[i],Npsf)
        phi[i],_ = generateKolmoScreen(N, pixel_screen_size[i], r0[i], L0)
        
arg_max= np.argmax(Ntot)

fenetre = Tk()
fenetre.geometry("1100x1100")
fenetre.grid()
# print(len(Displacement[0][0]),len(Displacement[1][0]),Ntot[arg_max])

figure = Figure(figsize=(5, 5), dpi=100)
figure2 = Figure(figsize=(5, 5),dpi = 100)
figure3 = Figure(figsize=(5,5), dpi = 100)

def phase_screen(event):
    

    axes.clear()
    axes2.clear()
    axes3.clear()

    local_phase = np.zeros((Npsf,Npsf))
    k_wind = np.zeros(screens,dtype = int) 
    a_wind = np.zeros(screens)
    b_wind = np.zeros(screens)
    k = int(x.get())
    
    for i in range(0,screens):
         k_wind[i] = k//(int(np.ceil(len(Displacement[arg_max][0])/len(Displacement[i][0])+1/2)))
         a_wind[i] = Displacement[i][0][k_wind[i]]
         b_wind[i] = Displacement[i][1][k_wind[i]]
         local_phase += phi[i][int(b_wind[i]):int(b_wind[i]+Npsf), int(a_wind[i]):int(a_wind[i]+Npsf)] * coeff[i]/100

    # print(k,k_wind)
    axes3.imshow(local_phase,cmap='gray_r',origin='lower')
    axes3.set_title('Phi sum')

    axes.imshow(phi[0],cmap='gray_r',origin='lower')
    axes.plot([Displacement[0][0][k_wind[0]]-0.5,Displacement[0][0][k_wind[0]]+Npsf-0.5],[Displacement[0][1][k_wind[0]]-0.5,Displacement[0][1][k_wind[0]]-0.5],color='r')
    axes.plot([Displacement[0][0][k_wind[0]]-0.5,Displacement[0][0][k_wind[0]]+Npsf-0.5],[Displacement[0][1][k_wind[0]]-0.5+Npsf,Displacement[0][1][k_wind[0]]-0.5+Npsf],color='r')
    axes.plot([Displacement[0][0][k_wind[0]]-0.5,Displacement[0][0][k_wind[0]]-0.5],[Displacement[0][1][k_wind[0]]-0.5,Displacement[0][1][k_wind[0]]+Npsf-0.5],color='r')
    axes.plot([Displacement[0][0][k_wind[0]]+Npsf-0.5,Displacement[0][0][k_wind[0]]+Npsf-0.5],[Displacement[0][1][k_wind[0]]-0.5,Displacement[0][1][k_wind[0]]-0.5+Npsf],color='r')
    axes.set_title('Phi1')

    axes2.imshow(phi[1],cmap='gray_r',origin='lower')
    axes2.plot([Displacement[1][0][k_wind[1]]-0.5,Displacement[1][0][k_wind[1]]+Npsf-0.5],[Displacement[1][1][k_wind[1]]-0.5,Displacement[1][1][k_wind[1]]-0.5],color='r')
    axes2.plot([Displacement[1][0][k_wind[1]]-0.5,Displacement[1][0][k_wind[1]]+Npsf-0.5],[Displacement[1][1][k_wind[1]]-0.5+Npsf,Displacement[1][1][k_wind[1]]-0.5+Npsf],color='r')
    axes2.plot([Displacement[1][0][k_wind[1]]-0.5,Displacement[1][0][k_wind[1]]-0.5],[Displacement[1][1][k_wind[1]]-0.5,Displacement[1][1][k_wind[1]]+Npsf-0.5],color='r')
    axes2.plot([Displacement[1][0][k_wind[1]]+Npsf-0.5,Displacement[1][0][k_wind[1]]+Npsf-0.5],[Displacement[1][1][k_wind[1]]-0.5,Displacement[1][1][k_wind[1]]-0.5+Npsf],color='r')
    axes2.set_title('Phi2')


#     im = computePSF(pad_array(local_phase / wavelength_scaling_factor, Npad), pixel_screen_size, D, obscuration)
#     im = crop_array(im, nb_pixels_img)
#     axes4.imshow(im,cmap = 'gray_r',origin = 'lower')
#     axes4.set_title('PSF outcome')
    
    canvas.draw()
    canvas2.draw()
    canvas3.draw()
#     canvas4.draw()
    canvas.get_tk_widget().grid(column = 0,row = 0)
    canvas2.get_tk_widget().grid(column=2,row=0)
    canvas3.get_tk_widget().grid(column=2,row=2)
#     canvas4.get_tk_widget().grid(column=0,row = 2)
    

    
x = DoubleVar()



local_phase = phi[0][0:nb_pixels_img, 0:nb_pixels_img] + phi[1][0:nb_pixels_img, 0:nb_pixels_img] 


scale_1 = Scale(fenetre, variable=x,from_=0,to=Ntot[arg_max],orient=HORIZONTAL,length= 300)
axes = figure.add_subplot()
axes.imshow(phi[0],cmap='gray_r')
axes.set_title('Phi1')

canvas = FigureCanvasTkAgg(figure,master = fenetre)  
canvas.get_tk_widget().grid(column = 0,row = 0)

axes2 = figure2.add_subplot()
axes2.imshow(phi[1], cmap = 'gray_r', origin='lower')
axes2.set_title('Phi2')

canvas2 = FigureCanvasTkAgg(figure2,master= fenetre)
canvas2.get_tk_widget().grid(column=2,row=0)

scale_1.grid(column = 0,row = 1)
scale_1.bind("<ButtonRelease-1>",phase_screen)


axes3 = figure3.add_subplot()
axes3.imshow(local_phase,cmap='gray_r',origin ='lower')
axes3.set_title('Shorten Turbulence displacement')

canvas3 = FigureCanvasTkAgg(figure3,master = fenetre)
canvas3.get_tk_widget().grid(column = 2,row = 2)

fenetre.mainloop()
