import numpy as np

QPs = [10, 20, 40, 50]
Ms = [2, 4, 16, 64, 256]

ALPHA = 0.95
NOISE_SPECTRAL_DENSITY = 1.380649*10.0**(-23.0)*298;
B = float(400*10e6)
P_UAV = 1

FR_H = 1080
FR_W = 1920

FOV_CENTRAL_THETA_E = 30
FOV_CENTRAL_THETA_W = -30
FOV_CENTRAL_PHI_N = 30
FOV_CENTRAL_PHI_S = -30
FOV_PERIPHERAL_THETA_E = 60
FOV_PERIPHERAL_THETA_W = -60
FOV_PERIPHERAL_PHI_N = 60
FOV_PERIPHERAL_PHI_S = -75

CENTRAL_WEIGHT = 0.75
PERIPHERAL_WEIGHT = 0.20
OUTSIDE_PERIPHERAL_WEIGHT = 0.05

METRIC_FOV_WEIGHT = 0.95
GAUSSIAN_MINIMUM = 100
MAX_VIEWING_ANGLE_CHANGE = 120 # per second

THETA_H_PRIMES = np.arange(15, 180, 15)
PHI_N_PRIMES = np.arange(15, 90, 15)
PHI_S_PRIMES = np.arange(-90, -15, 15)