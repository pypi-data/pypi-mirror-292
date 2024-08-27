import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

class Gaussian:
    def __init__(self, L:float,
                 N:int,
                 w0:float,
                 z:float,
                 k:float) -> None:
            
            self.L = L
            self.z = z
            self.N = N
            self.k = k
            self.w0 = w0

            x = np.linspace(-self.L, self.L, self.N)
            self.X, self.Y = np.meshgrid(x,x)
            r = np.sqrt(self.X**2 + self.Y**2)
            if self.z == 0:
                self.Beam = np.exp(-(r/self.w0)**2)

            else:
                zr = 1/2 * self.k * self.w0 ** 2
                wz = self.w0 * np.sqrt(1 + (self.z/zr))

                Rz = self.z * (1 + (zr/self.z) ** 2)
                
                G_pahse = np.arctan(self.z / zr)

                self.Beam = self.w0/wz * np.exp(-(r**2)/wz ** 2) * np.exp(-1j * (self.k*self.z + self.k * (r**2)/(2*Rz) - G_pahse))

    def plot_amplitude(self):
        plt.imshow(np.abs(self.Beam), extent=[-self.L, self.L, -self.L, self.L] ,cmap= 'gray')
        plt.title(f'Gaussian Mode z={self.z}')
        plt.xlabel('x(m)')
        plt.ylabel('y(m)')
        plt.show()

    def plot_phase(self):
        plt.imshow(np.angle(self.Beam) ,cmap= 'gray')
        plt.title(f'Phase Gaussian Mode z = {self.z}')
        plt.colorbar()
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

        Beam = np.exp(1j* (self.kx * self.X + self.ky * self.Y)) * self.Beam

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