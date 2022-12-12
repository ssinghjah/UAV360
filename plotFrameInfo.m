grid  on;
close all;
fileNames = {'./Encoded/frameSizes_Miami_5.csv'
'./Encoded/frameSizes_Miami_15.csv', 
'./Encoded/frameSizes_Miami_25.csv',
'./Encoded/frameSizes_Miami_35.csv',
'./Encoded/frameSizes_Miami_45.csv', 
'./Encoded/frameSizes_Ven_5.csv',
'./Encoded/frameSizes_Ven_15.csv', 
'./Encoded/frameSizes_Ven_25.csv', 
'./Encoded/frameSizes_Ven_35.csv', 
'./Encoded/frameSizes_Ven_45.csv'
};

displayNames = {'Miami, QP=5',
'Miami, QP=15',
'Miami, QP=25',
'Miami, QP=35', 
'Miami, QP=45', 
'Venuezvela, QP=5',
'Venuezvela, QP=15',
'Venuezvela, QP=25',
'Venuezvela, QP=35',
'Venuezvela, QP=45'};

colors = {'#0072BD', 
    '#EDB120',
    '#77AC30',
    '#A2142F',
    '#7E2F8E',
    '#0072BD', 
    '#EDB120',
    '#77AC30',
    '#A2142F',
    '#7E2F8E'}

numFiles = numel(fileNames);
for fileCounter = 1:numFiles
    fPath = char(fileNames(fileCounter));
    frameSizes = csvread(fPath);
    frameSizesKB = frameSizes./10^3;
    [f, x] = ecdf(frameSizesKB); 
    lineStyle = '-';
    if contains(fPath, 'Miami')
        lineStyle = '--';
    end
    plot(x, f, 'Color', char(colors(fileCounter)), 'LineStyle', lineStyle ,'LineWidth', 3, 'DisplayName',  char(displayNames(fileCounter)));
    hold on;
end
grid on;
legend show;
xticks([0:50:1200]);
xlim([0, 600]);
set(gca, 'FontSize', 16);
xlabel('Encoded frame size (in kilo-bytes)');
ylabel('CDF of encoded frame size');

figure;

fileNames = {'./Encoded/Miami_5.csv'
'./Encoded/Miami_15.csv', 
'./Encoded/Miami_25.csv',
'./Encoded/Miami_35.csv',
'./Encoded/Miami_45.csv', 
'./Encoded/Ven_5.csv',
'./Encoded/Ven_15.csv', 
'./Encoded/Ven_25.csv', 
'./Encoded/Ven_35.csv', 
'./Encoded/Ven_45.csv'
};

displayNames = {'Miami, QP=5',
'Miami, QP=15',
'Miami, QP=25',
'Miami, QP=35', 
'Miami, QP=45', 
'Venuezvela, QP=5',
'Venuezvela, QP=15',
'Venuezvela, QP=25',
'Venuezvela, QP=35',
'Venuezvela, QP=45'};

colors = {'#0072BD', 
    '#EDB120',
    '#77AC30',
    '#A2142F',
    '#7E2F8E',
    '#0072BD', 
    '#EDB120',
    '#77AC30',
    '#A2142F',
    '#7E2F8E'}

numFiles = numel(fileNames);
for fileCounter = 1:numFiles
    fPath = char(fileNames(fileCounter));
    PSNRs = csvread(fPath);
    [f, x] = ecdf(PSNRs); 
    lineStyle = '-';
    if contains(fPath, 'Miami')
        lineStyle = '--';
    end
    plot(x, f, 'Color', char(colors(fileCounter)), 'LineStyle', lineStyle ,'LineWidth', 3, 'DisplayName',  char(displayNames(fileCounter)));
    hold on;
end
grid on;
legend show;
set(gca, 'FontSize', 16);
xlabel('PSNR of the encoded frame (dB)');
ylabel('CDF of encoded frame PSNR');


