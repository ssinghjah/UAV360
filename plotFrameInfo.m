% grid  on;
% close all;
% rootFolder = './Results/Models/';
% locations = {'Chicago', 'Lucerne', 'SanFrancisco', 'Zurich', 'BryanskForest', 'Hawaii', 'HuangshanChina', 'LakeHibara'};
% FPSs = [30, 24, 30, 30, 30, 30, 50, 30];
% 
% QPs = 10:5:50;
% % colors = {'#0072BD', '#EDB120'};
% % lineStyles = {'--','-'};
% locationCounter = 1;
% 
% for location = locations
%     meanPSNRs = [];
%     meanRates = [];
%     for qp = QPs
%         psnrFName = strcat(rootFolder, char(location), '_frameSNRs_QP_', num2str(qp), '.csv');
%         psnrs = csvread(psnrFName);
% 
%         lenFName = strcat(rootFolder, char(location), '_frameSizes_QP_', num2str(qp), '.csv');
%         lens = csvread(lenFName);
% 
%         duration = numel(lens)/FPSs(locationCounter);
%         rate = sum(lens)*8 / (duration*10^6);
% 
%         meanRates = [meanRates, rate];
%         meanPSNRs = [meanPSNRs, mean(psnrs)];
%     end
%     plot(meanRates, meanPSNRs, 'LineWidth', 2, 'DisplayName', char(location));
%     hold on;
%     locationCounter = locationCounter + 1;
% end
% 
% xlabel("Bit rate (Mbps)");
% ylabel("Encoded frame quality, in Y-PSNR (dB)");
% set(gca, 'FontSize', 22);
% legend show;
close all;
locations = {'Chicago', 'HuangshanChina'};
locationCounter = 1;
QPs = 10:10:50
for location = locations
    color = char(colors(locationCounter));
    lineStyle = char(lineStyles(locationCounter));
    for QP = QPs
       fName = strcat(rootFolder, char(location), '_frameSizes_QP_', num2str(QP), '.csv')
       frameSizes = csvread(fName);
       frameSizes = frameSizes./10^6;
       [f, x] = ecdf(frameSizes); 
       displayName = strcat(char(location), ', QP=', num2str(QP));
       plot(x, f, 'Color', color, 'LineStyle', lineStyle ,'LineWidth', 3, 'DisplayName', displayName);
       hold on;
    end
    locationCounter = locationCounter + 1;
end

grid on;
xlabel('Encoded frame size (megabytes)');
ylabel('CDF of encoded frame size');

% xlabel('Y-PSNR of the encoded frame (dB)');
% ylabel('CDF of Y-PSNR');
legend show;
set(gca, 'FontSize', 26);
% % 


% for location = locations
%     color = char(colors(locationCounter));
%     lineStyle = char(lineStyles(locationCounter));
%     for QP = QPs
%        fName = strcat(rootFolder, char(location), '_frameSNRs_QP_', num2str(QP), '.csv')
%        frameSizes = csvread(fName);
%        % frameSizes = frameSizes./10^6;
%        [f, x] = ecdf(frameSizes); 
%        displayName = strcat(char(location), ', QP=', num2str(QP));
%        plot(x, f, 'Color', color, 'LineStyle', lineStyle ,'LineWidth', 3, 'DisplayName', displayName);
%        hold on;
%     end
%     locationCounter = locationCounter + 1;
% end
% 
% grid on;
% xlabel('Encoded frame size (megabytes)');
% ylabel('CDF of encoded frame size');

% xlabel('Y-PSNR of the encoded frame (dB)');
% ylabel('CDF of Y-PSNR');
legend show;
% % 


% % fileNames = {'./frameSizes_Chicago_5.csv'
% % './frameSizes_Chicago_15.csv', 
% % './frameSizes_Chicago_25.csv',
% % './frameSizes_Chicago_35.csv',
% % './frameSizes_Chicago_45.csv', 
% % './frameSizes_LakeHibara_5.csv',
% % './frameSizes_LakeHibara_15.csv', 
% % './frameSizes_LakeHibara_25.csv', 
% % './frameSizes_LakeHibara_35.csv', 
% % './frameSizes_LakeHibara_45.csv'};
% 
% displayNames = {'Chicago, QP=5',
% 'Chicago, QP=15',
% 'Chicago, QP=25',
% 'Chicago, QP=35', 
% 'Chicago, QP=45', 
% 'LakeHibara, QP=5',
% 'LakeHibara, QP=15',
% 'LakeHibara, QP=25',
% 'LakeHibara, QP=35',
% 'LakeHibara, QP=45'};
% 
% colors = {'#0072BD', 
%     '#EDB120',
%     '#77AC30',
%     '#A2142F',
%     '#7E2F8E',
%     '#0072BD', 
%     '#EDB120',
%     '#77AC30',
%     '#A2142F',
%     '#7E2F8E'}
% 
% 
% numFiles = numel(fileNames);
% for fileCounter = 1:numFiles
%     fPath = char(fileNames(fileCounter))
%     frameSizes = csvread(fPath);
%     frameSizesKB = frameSizes./10^3;
%     [f, x] = ecdf(frameSizesKB); 
%     lineStyle = '-';
%     if contains(fPath, 'Miami')
%         lineStyle = '--';
%     end
%     plot(x, f, 'Color', char(colors(fileCounter)), 'LineStyle', lineStyle ,'LineWidth', 3, 'DisplayName',  char(displayNames(fileCounter)));
%     hold on;
% end
% grid on;
% legend show;
% xticks([0:50:1200]);
% xlim([0, 600]);
% set(gca, 'FontSize', 16);
% xlabel('Encoded frame size (in kilo-bytes)');
% ylabel('CDF of encoded frame size');
% 
% figure;
% 
% % fileNames = {'./Encoded/Miami_5.csv'
% % './Encoded/Miami_15.csv', 
% % './Encoded/Miami_25.csv',
% % './Encoded/Miami_35.csv',
% % './Encoded/Miami_45.csv', 
% % './Encoded/Ven_5.csv',
% % './Encoded/Ven_15.csv', 
% % './Encoded/Ven_25.csv', 
% % './Encoded/Ven_35.csv', 
% % './Encoded/Ven_45.csv'
% % };
% % 
% % displayNames = {'Miami, QP=5',
% % 'Miami, QP=15',
% % 'Miami, QP=25',
% % 'Miami, QP=35', 
% % 'Miami, QP=45', 
% % 'Venuezvela, QP=5',
% % 'Venuezvela, QP=15',
% % 'Venuezvela, QP=25',
% % 'Venuezvela, QP=35',
% % 'Venuezvela, QP=45'};
% % 
% % colors = {'#0072BD', 
% %     '#EDB120',
% %     '#77AC30',
% %     '#A2142F',
% %     '#7E2F8E',
% %     '#0072BD', 
% %     '#EDB120',
% %     '#77AC30',
% %     '#A2142F',
% %     '#7E2F8E'}
% % 
% % numFiles = numel(fileNames);
% % for fileCounter = 1:numFiles
% %     fPath = char(fileNames(fileCounter));
% %     PSNRs = csvread(fPath);
% %     [f, x] = ecdf(PSNRs); 
% %     lineStyle = '-';
% %     if contains(fPath, 'Miami')
% %         lineStyle = '--';
% %     end
% %     plot(x, f, 'Color', char(colors(fileCounter)), 'LineStyle', lineStyle ,'LineWidth', 3, 'DisplayName',  char(displayNames(fileCounter)));
% %     hold on;
% % end
% % grid on;
% % legend show;
% % set(gca, 'FontSize', 16);
% % xlabel('PSNR of the encoded frame (dB)');
% % ylabel('CDF of encoded frame PSNR');
% % 
% % 
