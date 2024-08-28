# Paraxial-Wave-Equation-Solutions
 Solution of the paraxial wave equations using differante coordinates

 * Hermite-Gaussian Modes in cartesian coordinates
 * Laguerre-Gaussian Modes in cylindrical coordinates
 * Ince-Gaussian Modes in elyptical coordinates


## Gaussian Modes
$U(r, \theta, z) = \frac{\omega_0}{\omega(z)}\exp{\frac{-r^2}{\omega(z)^2}} \exp{\left(-i\left(kz + k\frac{r^2}{2R(z)} - \psi(z) \right)\right)}$

### Code implementation

```
from pyOptics import Beam

Gauss = Beam(type = 'Gaussian',
            size = 5e-3, 
            shape = 501, 
            w0 = 1e-3, 
            k = (2*np.pi/632.8e-9),
            z = 0)
Gauss.plot_amplitude()
```

## Ince-Gaussian Modes
The Ince-Gaussian (IG) mode is a solution to the paraxial wave equation expressed in elliptic coordinates $(\xi, \eta)$. The general form of an Ince-Gaussian beam $(\xi, \eta, z)$ can be written as:

$\text{IG}_{p,m}^e(\mathbf{r}, \epsilon) = \frac{C\omega_0}{\omega(z)}C_p^m(i\xi, \epsilon)C_p^m(\eta, \epsilon)\exp\left[\frac{-r^2}{\omega^2(z)}\right] \exp\left(i\left[kz + \frac{kr^2}{2R(z)} - (p - 1) \Psi_G(z)\right]\right)$,

$\text{IG}_{p,m}^o(\mathbf{r}, \epsilon) = \frac{S\omega_0}{\omega(z)}S_p^m(i\xi, \epsilon)S_p^m(\eta, \epsilon)\exp\left[\frac{-r^2}{\omega^2(z)}\right] \exp\left(i\left[kz + \frac{kr^2}{2R(z)} - (p - 1) \Psi_G(z)\right]\right)$

where C and S are normalization constants and the superindices $e$ and $o$ refer to even and odd modes, respectively.

### Code implementation

```
from pyOptics import Beam

Ince = Beam(type = 'InceGaussian',
            size = 5e-3, 
            shape = 501,
            parity = 0,
            p = 2,
            m = 2,
            e = 2,            
            w0 = 1e-3, 
            k = (2*np.pi/632.8e-9),
            z = 0)
Ince.plot_amplitude()
```



## Laguerre-Gaussian modes

$U_{p}^l(r, \phi, z) = \frac{1}{w(z)} \sqrt{\frac{2p!}{\pi (p + |l|)!}} \left(\frac{\sqrt{2} r}{w(z)}\right)^{|l|} L_p^{|l|}\left(\frac{2r^2}{w(z)^2}\right) \exp\left(-\frac{r^2}{w(z)^2}\right) \exp\left(-i \left(k z + k \frac{r^2}{2 R(z)} - l \phi - (2p + |l| + 1)\zeta(z)\right)\right)$

## Hermite-Gaussian modes

$U_{m}^n(x, y, z) = \frac{1}{w(z)} \sqrt{\frac{2}{\pi \, 2^{n+m} \, n! \, m!}} \, H_n\left(\frac{\sqrt{2} \, x}{w(z)}\right) H_m\left(\frac{\sqrt{2} \, y}{w(z)}\right) \exp\left(-\frac{x^2 + y^2}{w(z)^2}\right) \exp\left(-i \left(k z + (n + m + 1) \zeta(z) - \frac{k (x^2 + y^2)}{2 R(z)}\right)\right)$


## Hologram generation


## Library installation
```
git clone https://github.com/ARMANDOMTZ05/pyOptics.git
cd ..\pyOptics
python setup.py install
```

## References

[1] R. W. Gerchberg and W. O. Saxton, “A practical algorithm for the determination of the phase from image and diﬀraction plane pictures”, Optik 35, 237 (1972).

[2] K. Mitchell, S. Turtaev, M. Padgett, T. Cizmár, and D. Phillips, “High-speed spatial control of the intensity, phase and polarisation of vector beams using a digital micro-mirror device”, Opt. Express 24, 29269-29282 (2016).

[3] Forbes A. 2014, Laser Beam Propagation: Generation and Propagation of Customized Light (London: Taylor and Francis).

[4] Bandres MA, Gutiérrez-Vega JC. Ince-Gaussian modes of the paraxial wave equation and stable resonators. J Opt Soc Am A Opt Image Sci Vis. 2004 May;21(5):873-80. doi: 10.1364/josaa.21.000873. PMID: 15139441.
