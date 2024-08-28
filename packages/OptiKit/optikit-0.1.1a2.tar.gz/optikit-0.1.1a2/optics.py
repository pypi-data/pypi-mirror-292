import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from Beam import Beam
from typing import Union

class Propagator:
    def __init__(self,
                 beam: Union[np.ndarray, Beam],
                 **kwargs) -> None:
        
        if isinstance(beam, Beam):
            self.beam = beam.Beam.Beam
            self.k = beam.k
            self.L = beam.L
            self.N = beam.N
        elif isinstance(beam, np.ndarray):
            self.beam = beam
            self.k = (2*np.pi/632.8e-9) if 'k' not in kwargs else kwargs['k']
            self.L = 15e-3 if 'L' not in kwargs else kwargs['L']

            self.N = beam.shape[0]
            if self.beam.shape[0] != self.beam.shape[1]:
                raise ValueError('The shape of the Beam matrix must be NxN')
        else:
            raise ValueError('Beam needs to be either np.ndarray or Beam class')
        
        if self.N % 2 == 0:
            fx = np.arange(-self.N//2, self.N//2) * (np.pi/self.L)

        else:
            fx = np.linspace(-self.N/2, self.N/2, self.N) * (np.pi/self.L)

        self.kx, self.ky = np.meshgrid(fx, fx)

    def Transfer_Function(self, z):
        return np.exp(1j * z * np.sqrt(self.k ** 2 - (self.kx ** 2 + self.ky ** 2)))

    
    def propagate(self, zi, zn):
        self.prop_beam = np.zeros((self.N, self.N, zn), dtype=np.complex64)
        self.prop_beam[:,:,0] = self.beam
        self.z = np.linspace(0,zi,zn)
        a0 = np.fft.fftshift(np.fft.fft2(self.prop_beam[:,:,0]))
        for i,z in enumerate(self.z[1:], 1):
            a1 =  a0 * self.Transfer_Function(z=z)
            self.prop_beam[:,:,i] = np.fft.ifft2(np.fft.ifftshift(a1))
    
    def plot(self):
        plt.imshow(np.abs(self.prop_beam[:,self.N//2,:]))
        plt.colorbar()
        plt.show()

    def plot_amplitude(self):
        plt.imshow(np.abs(self.prop_beam[:,:,-1]), extent=[-self.L, self.L, -self.L, self.L])
        plt.show()


class StokesParameters:
    def __init__(self,
                 P1,
                 P2,
                 P3,
                 P4) -> None:
        self.P1 = P1
        self.P2 = P2
        self.P3 = P3
        self.P4 = P4


        s0 = P1 + P2
        s1 = (P1 - P2)/s0
        s2 = (2*P3 - s0)/s0
        s3 = (s0 - 2*P4)/s0

        self.angle = np.rad2deg(0.5 * np.arctan(s2/s1))
        print(self.angle)
        self.E0x = np.sqrt(0.5*(1 + s1))
        self.E0y = np.sqrt(0.5*(1 - s1))

        self.total_polarization = np.sqrt(s1 ** 2 + s2 ** 2 + s3 ** 2)

        self.plot_polarization()

    def plot_polarization(self):
        fig, ax = plt.subplots()
        ellipse = Ellipse(xy = (0,0), width = 2*self.E0x, height = 2*self.E0y, angle = self.angle,  edgecolor='r', facecolor='none')
        ax.add_patch(ellipse)
        ax.axhline(y=0, color='black', linestyle='-')
        ax.axvline(x=0, color='black', linestyle='-')
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_aspect('equal')
        ax.set_title(f'Polarization: {self.total_polarization}')

        plt.show()
