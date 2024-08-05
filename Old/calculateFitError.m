function [absErrors, relErrors] = calculateFitError(xs, ys, fitType, fitCoeffs)
    if numel(fitCoeffs) == 2
        fitCoeffs = [fitCoeffs, 0, 0];
    end
    fitYs = [];
    for x = xs
        if (strcmp(fitType, 'exponential'))
            fitY = fitCoeffs(1)*exp(fitCoeffs(2)*x) +fitCoeffs(3)*exp(fitCoeffs(4)*x) ;
            fitYs = [fitYs; fitY];
        elseif (strcmp(fitType, 'power'))
            fitY = fitCoeffs(1)*power(x, fitCoeffs(2)) + fitCoeffs(3);
            fitYs = [fitYs; fitY];
        end
    end
    relErrors = (fitYs - ys)./ys;
    absErrors = abs(fitYs - ys);
end 
