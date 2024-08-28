import numpy as np
import matplotlib.pyplot as plt

class Beam:
    def __init__(self,
                 *args,
                 **kwargs) -> None:
        
        """
        Beam is an object to generate a Ince-Gaussian Mode, Laguerre-Gaussian Mode and Hermite-Gaussian mode with the soecified valuess

        Input

        

        """
        
        assert kwargs['type'] is not None, 'Beam type has to be specified'
        self.type = 'HermiteGaussian' if 'type' not in kwargs else kwargs['type']
        self.w0 = 4e-4 if 'w0' not in kwargs else kwargs['w0']
        self.k = (2*np.pi/632.8e-9) if 'k' not in kwargs else kwargs['k']
        self.z = 0 if 'z' not in kwargs else kwargs['z']
        self.N = 501 if 'shape' not in kwargs else kwargs['shape']
        self.L = 15e-3 if 'size' not in kwargs else kwargs['size']


        match self.type:

            case 'InceGaussian':
                self.p = 2 if 'p' not in kwargs else kwargs['p']
                self.m = 2 if 'm' not in kwargs else kwargs['m']
                self.e = 2 if 'elipticity' not in kwargs else kwargs['elipticity']
                self.parity = 0 if 'parity' not in kwargs else kwargs['parity']
                from InceGauss import InceGaussian
                self.Beam = InceGaussian(L = self.L,
                                        N = self.N,
                                        parity = self.parity,
                                        p = self.p,
                                        m = self.m,
                                        e = self.e,
                                        w0 = self.w0,
                                        k = self.k,
                                        z = self.z)
            
            case 'HermiteGaussian':
                self.m = 2 if 'm' not in kwargs else kwargs['m']
                self.n = 2 if 'n' not in kwargs else kwargs['n']

                from HermiteGauss import HermiteGaussian
                self.Beam = HermiteGaussian(L = self.L,
                                            size = self.N,
                                            n = self.n,
                                            m = self.m,
                                            w0 = self.w0,
                                            k = self.k,
                                            z = self.z)
            
            case 'LaguerreGaussian':
                self.p = 2 if 'p' not in kwargs else kwargs['p']           
                self.l = 2 if 'm' not in kwargs else kwargs['l']

                from LaguerreGauss import LaguerreGaussian
                self.Beam = LaguerreGaussian(L = self.L,
                                            size = self.N,
                                            p = self.p,
                                            l = self.l,
                                            w0 = self.w0,
                                            k = self.k,
                                            z = self.z)
            
            case 'Gaussian':
                from Gaussian import Gaussian
                self.Beam = Gaussian(L = self.L,
                                    N = self.N,
                                    w0= self.w0,
                                    k = self.k,
                                    z = self.z)

            
            case _:
                raise ValueError('Type not found')
        
    def plot_amplitude(self):
        self.Beam.plot_amplitude()

    def plot_phase(self):
        self.Beam.plot_phase()

    def Hologram(self, gamma:float, theta:float, save:bool = False):
        self.Beam.Hologam(save = save, gamma = gamma, theta = theta)

