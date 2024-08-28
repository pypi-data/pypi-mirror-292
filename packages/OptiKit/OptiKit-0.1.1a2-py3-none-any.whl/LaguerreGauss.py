import numpy as np
import matplotlib.pyplot as plt
from scipy.special import genlaguerre, factorial
from PIL import Image


def LP(n, alpha, x):

    L_n_alpha = genlaguerre(n, alpha)(x)

    return L_n_alpha

class LaguerreGaussian:
    def __init__(self,
                 L: float,
                 size: int,
                 p: int,
                 l: int,
                 w0: float,
                 k: float,
                 z: float) -> None:
        
        if p < 0:
            raise ValueError('p must be positive')
        
        self.size = size
        self.L = L
        self.w0 = w0
        self.p = p
        self.l = l
        self.k = k
        self.z = z

        gamma = np.pi/3000
        theta2 = np.pi/4

        self.kxy = self.k *np.sin(gamma)
        self.kx = self.kxy * np.cos(theta2)
        self.ky = self.kxy * np.sin(theta2)


        x, y = np.linspace(-self.L, self.L, self.size), np.linspace(-self.L, self.L, self.size)
        self.Y, self.X = np.meshgrid(x, y)

        r = np.sqrt(self.X ** 2 + self.Y ** 2)
        theta = np.arctan2(self.Y,self.X)

        if self.z == 0:
            lgb = (1/self.w0) * (r*np.sqrt(2)/self.w0)**(np.abs(self.l)) * np.exp(-r**2/self.w0**2) * LP(self.p, np.abs(self.l), 2*r**2/self.w0**2) * np.exp(-1j*self.l*theta)

        else:
            zr = 1/2 * self.k * self.w0 ** 2
            wz = self.w0 * np.sqrt(1 + (z/zr) ** 2)
            Rz = z * (1 + (zr / z) ** 2)
            CMnumber = np.abs(self.l) + 2 * self.p

            self.GouyPhase = (CMnumber + 1) * np.arctan(z/zr)

            lgb = (1/wz) * (r*np.sqrt(2)/wz)**(np.abs(self.l)) * np.exp(-r**2/wz**2) * LP(self.p, np.abs(self.l), 2*r**2/wz**2) * np.exp(-1j*self.k*r**2/(2*Rz)) * np.exp(-1j*self.l*theta) * np.exp(1j * self.GouyPhase)

        Norm = np.sqrt((2*factorial(self.p))/(np.pi*factorial(self.p + np.abs(self.l))))

        self.LGB = lgb * Norm

    def plot_amplitude(self):
        plt.imshow(np.abs(self.LGB), extent=[-self.L, self.L, -self.L, self.L] , cmap= 'gray')
        plt.title(f'Laguerre-Gaussian Mode l = {self.l}, p = {self.p}, z = {self.z}')
        plt.xlabel('x(m)')
        plt.ylabel('y(m)')
        plt.show()

    def plot_phase(self):
        plt.imshow(np.angle(self.LGB) ,cmap= 'gray')
        plt.title(f'Phase Laguerre-Gaussian Mode l = {self.l}, p = {self.p}, z = {self.z}')
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

        Beam = np.exp(1j* (self.kx * self.X + self.ky * self.Y)) * self.LGB

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

