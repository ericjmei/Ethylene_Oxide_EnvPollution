function [TTout] = binByMonth(TT)
%%%put in a timetable of discrete data and get a timetable with data
%%%average and standard deviation by month
%%%only data should be in timetable. Multiple rows okay

%%Preformatting
times = TT.Properties.RowTimes;
data = timetable2array(TT);
begTime = dateshift(times(1), "start", "month"); %get first month
endTime = dateshift(times(end), "start", "month") + calmonths(1); %+ month(1); %get last month
spacing = (begTime:calmonths(1):endTime)'; %last month is end
avgs = nan*ones([length(spacing) - 1, 1]);
stds = nan*ones([length(spacing) - 1, 1]);

%calc avgs and stds for all months
for i = 1:(length(spacing) - 1)
    inds = times >= spacing(i) & times < spacing(i + 1);
    monthData = data(inds, :);

    %if all nan, return nans
    if any(~isnan(monthData), "all")
        avgs(i) = mean(monthData, "all", "omitnan");
        stds(i) = std(monthData, 0, "all", "omitnan");
    end
end

%put data in table: first of month for spacing
TTout = timetable(spacing(1:end-1), avgs, stds);
end

