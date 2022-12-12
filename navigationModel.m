thetas = [-180:5:180];
phis = [-90:5:90];

mean_theta = 0;
sigma_theta = 50;
theta_h = 100;
phi_N = 10;
phi_S = 70;
p = 0.7;

cdfThetaAll = [];
for theta = thetas
    cdfTheta = normcdf(theta, mean_theta, sigma_theta);
    cdfThetaAll = [cdfThetaAll; cdfTheta];
end
figure;
plot(thetas, cdfThetaAll, 'LineWidth', 3);
grid on;
xlabel("Horizontal viewing angle, \theta, with respect to UAV's heading direction (degrees)");
ylabel('CDF of horizontal viewing angle, \n \theta');
set(gca, 'FontSize', 16);

phiZeroPerc = phi_S/(phi_N + phi_S);
phiZeroProbLeft = phiZeroPerc*(1-p);
phiZeroProbRight = phiZeroPerc*(1-p) + p
phiNorthProb = 1;
phis = [-phi_S, 0, 0, phi_N];
cdfPhis = [0, phiZeroProbLeft, phiZeroProbRight, phiNorthProb];
figure;
plot(phis, cdfPhis, 'LineWidth', 3);
xlabel("Vertical viewing angle, \phi, with respect to UAV's heading direction (degrees)");
ylabel('CDF of vertical viewing angle, \phi');
grid on;
set(gca, 'FontSize', 16);