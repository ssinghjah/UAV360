close all;
QPs = 5:5:50;
locations = {'MiamiCity', 'AngelFalls'};
root = './Release/';
numFrames = 4975;
iIndices = 1:50:4975;
iIndicesLogical = ismember(1:4975, iIndices);

figure;
for location = locations
    
    means = [];
    perc95s = [];
    perc99s = [];
    
    meanIs = [];
    perc95Is = [];
    perc99Is = [];
    
    meanNonIs = [];
    perc95nonIs = [];
    perc99nonIs = [];
    
    expCoeffs = [];

    for qp = QPs
        fName = char(strcat(root, location, '/frameSNRs_QP_', num2str(qp), '.csv'));
        distribution = csvread(fName)./10^3;
        distribution(distribution == inf) = [];
        iDistribution = distribution(iIndices);
        csvwrite(char(strcat(root, location, '/i_frameSNRs_QP_', num2str(qp), '.csv')), iDistribution)
        nonIDistribution = distribution(~iIndicesLogical);
        csvwrite(char(strcat(root, location, '/non_i_frameSNRs_QP_', num2str(qp), '.csv')), nonIDistribution)
        
        meanIVal = mean(iDistribution);
        perc95IVal = prctile(iDistribution, 95);
        perc99IVal = prctile(iDistribution, 99);
        
        meanIs = [meanIs; meanIVal];
        perc95Is = [perc95Is; perc95IVal];
        perc99Is = [perc99Is; perc99IVal];
        
        meanNonIVal = mean(nonIDistribution);
        perc95NonIVal = prctile(nonIDistribution, 95);
        perc99NonIVal = prctile(nonIDistribution, 99);
        
        meanNonIs = [meanNonIs; meanNonIVal];
        perc95nonIs = [perc95nonIs; perc95NonIVal];
        perc99nonIs = [perc99nonIs; perc99NonIVal];   
        
        means = [means; mean(distribution)];
        perc95s = [perc95s; prctile(distribution, 95)];
        perc99s = [perc99s; prctile(distribution, 99)]; 
        
    end
    
    csvwrite(char(strcat(root, location, '/frameSNRs_mean.csv')), means);
    f=fit(QPs', means, 'exp2');
    expCoeffs = [expCoeffs; coeffvalues(f)];
    calculateFitError(QPs, means, 'exponential', coeffvalues(f));
    
    f=fit(QPs', means, 'power2');
    calculateFitError(QPs, means, 'power', coeffvalues(f));
    plot(QPs, means);
    hold on;
    
    csvwrite(char(strcat(root, location, '/frameSNRs_perc95.csv')), perc95s);
    f=fit(QPs', perc95s, 'exp2');
    expCoeffs = [expCoeffs; coeffvalues(f)];
    plot(QPs, perc95s);
    hold on;
    
    csvwrite(char(strcat(root, location, '/frameSNRs_perc99.csv')), perc99s);
    f=fit(QPs', perc99s, 'exp2');
    expCoeffs = [expCoeffs; coeffvalues(f)];
%     plot(QPs, perc99s);
%     hold on;
    
    csvwrite(char(strcat(root, location, '/i_frameSNRs_mean.csv')), meanIs);
    f=fit(QPs', meanIs, 'exp2');
    expCoeffs = [expCoeffs; coeffvalues(f)];
%     plot(QPs, meanIs);
%     hold on;
    
    csvwrite(char(strcat(root, location, '/i_frameSNRs_perc95.csv')), perc95Is);
    f = fit(QPs', perc95Is, 'exp2');
    expCoeffs = [expCoeffs; coeffvalues(f)];
%     plot(QPs, perc95Is);
%     hold on;
    
    csvwrite(char(strcat(root, location, '/i_frameSNRs_perc99.csv')), perc99Is);
    f = fit(QPs', perc99Is, 'exp2');
    expCoeffs = [expCoeffs; coeffvalues(f)];
%     plot(QPs, perc99Is);
%     hold on;
    
    csvwrite(char(strcat(root, location, '/non_i_frameSNRs_mean.csv')), meanNonIs);
    f = fit(QPs', meanNonIs, 'exp2');
    expCoeffs = [expCoeffs; coeffvalues(f)];
%     plot(QPs, meanNonIs);
%     hold on;
    
    csvwrite(char(strcat(root, location, '/non_i_frameSNRs_perc95.csv')), perc95nonIs);
    f = fit(QPs', perc95nonIs, 'exp2');
    expCoeffs = [expCoeffs; coeffvalues(f)];
%     plot(QPs, perc95nonIs);
%     hold on;
%     
    csvwrite(char(strcat(root, location, '/non_i_frameSNRs_QP_perc99.csv')), perc99nonIs);
    f = fit(QPs', perc99nonIs, 'exp2');
    expCoeffs = [expCoeffs; coeffvalues(f)];
%     plot(QPs, perc99nonIs);
%     hold on;
    
    csvwrite(char(strcat(root, location, '/expCoefficients.csv')), expCoeffs);
end
