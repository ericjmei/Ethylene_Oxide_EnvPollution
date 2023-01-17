function [averagedData, stdevData, nanPercent] = averageTTbyTime(raw, daysNeeded, timeBounds)
%%%calculates average, standard dev, and percent nan for the data in timetable raw for the
%%%days needed between the timebounds, inclusive. Assumes data reported on
%%%a line is for the average between that point and the next
%raw is a timetable of doubles
%daysNeeded is an array of datetime days where data are needed to average
%timeBounds is a two-member array of durations from 0000 between which data
    %are averaged each day

%%preformatting
averagedData = raw; %replicate structure of rawMet and replace with nan
averagedData(length(daysNeeded)+1:end, :) = [];
averagedData.Properties.RowTimes = daysNeeded; %format times to format necessary
temp = timetable2array(averagedData)*nan;
averagedData(:, :) = array2timetable(temp, "RowTimes", daysNeeded); %set all data to nan
stdevData = averagedData; %have stdevData replicate this as well
nanPercent = averagedData; %have nanPercent replicate this as well
times = raw.Properties.RowTimes; %grab the met data times

for i = 1:length(daysNeeded)
    %filter for time needed
    timeStart = daysNeeded(i) + timeBounds(1); %start time is day of + beginning duration
    timeEnd = daysNeeded(i) + timeBounds(end); %end time is day of + ending duration
    inds = find(isbetween(times, timeStart, timeEnd)); %grab met times between
    if ~isempty(inds) %make sure there are values
        inds = [inds(1) - 1; inds]; %grab time step before beginning of period as well
        %grab needed data in the time step
        rawNeeded = timetable2array(raw(inds, :));
        timesNeeded = times(inds);

        %calculate difference in times
        temp = [timeStart; timesNeeded(2:end); timeEnd]; %cap beginning and end times
        timeDiff = diff(temp);
        timeDiff = minutes(timeDiff); %convert to minutes

        %calculate nan percent
        nanPerc = timeDiff'*isnan(rawNeeded); %total number of nans
        nanPerc = nanPerc/sum(timeDiff); %percent of total nan
        nanPercent(i, :) = array2timetable(nanPerc, "RowTimes", daysNeeded(i));
        
        for j = 1:size(rawNeeded, 2) %index over each column of rawNeeded
            
            rawNeededCol = rawNeeded(:, j); %grab needed column
            inds = isnan(rawNeededCol);
            rawNeededCol(inds) = []; %remove nan values
            timeDiffNonNaN = timeDiff(~inds);

            if ~isempty(rawNeededCol) %leave nan if all nan
                %calculate weighted average of necessary times
                avg = timeDiffNonNaN'*rawNeededCol; %weighted element sum
                avg = avg/sum(timeDiffNonNaN); %mean of each element
                averagedData(i, j) = array2timetable(avg, "RowTimes", daysNeeded(i));

                %calculate weighted std of necessary times
                rawDiff = rawNeededCol - avg; %observation differences
                rawDiff = rawDiff.^2; %observation differences squared
                sd = timeDiffNonNaN'*rawDiff; %weighted element sqare diff sum
                M = sum(timeDiffNonNaN ~= 0); %number non-zero weights
                sd = sqrt(sd*M/(M-1)/sum(timeDiffNonNaN)); %weighted std
                stdevData(i, j) = array2timetable(sd, "RowTimes", daysNeeded(i));
            end
        end
    else
        temp = ones([1, size(raw, 2)]); %if missing data, all are nan
        nanPercent(i, :) = array2timetable(temp, "RowTimes", daysNeeded(i));
    end
end

end