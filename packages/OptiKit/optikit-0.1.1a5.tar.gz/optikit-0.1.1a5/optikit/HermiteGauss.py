import numpy as np
import matplotlib.pyplot as plt
from scipy.special import factorial, hermite
from PIL import Image

def HP(n, x):
    """
    Generate the Hermite polynomial H_n(x) using the Rodrigues formula.

    Parameters:
    n (int): The degree of the Hermite polynomial.
    x (float or np.ndarray): The point(s) at which to evaluate the polynomial.

    Returns:
    H_n_x (float or np.ndarray): The value(s) of the Hermite polynomial H_n(x).
    """
    p_monic = hermite(n)
    H_n_x = p_monic(x)

    return H_n_x

class HermiteGaussian:
    def __init__(self,
                L:int,
                size: int, 
                n,
                m,
                w0,
                k,
                z) -> None:
        self.size = size
        self.L = L
        self.w0 = w0
        self.n = n
        self.m = m
        self.k = k
        self.z = z


        x, y = np.linspace(-self.L, self.L, self.size), np.linspace(-self.L, self.L, self.size)
        Y, X = np.meshgrid(x, y)

        if self.z == 0:
            self.HGB = (1/self.w0) * np.sqrt(2/(np.pi * (2 ** (self.m+self.n)) * factorial(self.m) * factorial(self.n))) * HP(self.m, np.sqrt(2)*X/self.w0) * HP(self.n, np.sqrt(2)*Y/self.w0) * np.exp(-(X**2 + Y **2)/self.w0**2)

        else:

            zr = 1/2 * self.k * self.w0 ** 2
            wz = self.w0 * np.sqrt(1 + (z/zr) ** 2)
            Rz = z * (1 + (zr / z) ** 2)

            self.GouyPhase = np.arctan(z/zr)

            self.HGB = (1/wz) * np.sqrt(2/(np.pi * 2 ** (self.m+self.n) * factorial(self.m) * factorial(self.n))) * HP(self.m, np.sqrt(2)*X/wz) * HP(self.n, np.sqrt(2)*Y/wz)*np.exp(-(X**2 + Y **2)/wz**2) * np.exp(-1j * (self.k * z + (self.m + self.n + 1)*self.GouyPhase - self.k*(X**2 + Y**2)/(2*Rz)))


    def plot_amplitude(self):
        plt.imshow(np.abs(self.HGB), extent=[-self.L, self.L, -self.L, self.L] , cmap= 'gray')
        plt.title(f'Hermite-Gaussian Mode m={self.m}, n = {self.n}, z = {self.z}')
        plt.xlabel('x(m)')
        plt.ylabel('y(m)')
        plt.show()

    def plot_phase(self):
        plt.imshow(np.angle(self.HGB) ,cmap= 'gray')
        plt.title(f'Phase Hermite-Gaussian Mode m={self.m}, n = {self.n}, z = {self.z}')
        plt.xlabel('x(m)')
        plt.ylabel('y(m)')
        plt.show()

    def Hologam(self, gamma, theta, save:bool = False):
        '''
        Considering a DMD resolution of 1920x1080
        '''

        self.kxy = self.k *np.sin(gamma)
        self.kx = self.kxy * np.cos(theta)
        self.ky = self.kxy * np.sin(theta)

        Hologram = np.zeros((1080, 1920), dtype= np.uint8)

        Beam = np.exp(1j* (self.kx * self.X + self.ky * self.Y)) * self.HGB

        Amp = np.abs(Beam)
        Amp = Amp/np.max(Amp)

        phi = np.angle(Beam)
        pp = np.arcsin(Amp)

        qq = phi

        CoGH = _insertImage(1 - (0.5 + 0.5 * np.sign(np.cos(pp) + np.cos(qq))), Hologram)

        if save:
            Image.fromarray(CoGH * 255).convert('1').save('InceGauss.png')

        return np.round((2**8-1)* CoGH).astype('uint8')



def _insertImage(image,image_out):

    N_v, N_u = image_out.shape

    S_u = image.shape[1]
    S_v = image.shape[0]
  
    u1, u2 = int(N_u/2 - S_u/2), int(N_u/2 + S_u/2)
    v1, v2 = int(N_v/2 - S_v/2), int( N_v/2 + S_v/2)

    if u1 < 0 or u2 > N_u:
        raise Exception("Image could not be inserted because it is either too large in the u-dimension or the offset causes it to extend out of the input screen size")
    if v1 < 0 or v2 > N_v:
        raise Exception("Image could not be inserted because it is either too large in the v-dimension or the offset causes it to extend out of the input screen size")
        
    image_out[v1:v2,u1:u2] = image


    return image_out



HGM = HermiteGaussian(L = 15e-3,
                      size = 501,
                      n = 3,
                      m = 3,
                      w0 = 4e-3,
                      k = (2*np.pi/632.8e-9),
                      z = 0.375)
HGM.plot_phase()


