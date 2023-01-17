function [outTT] = avSameTime(TT1, TT2)
%%function takes two timetables of m rows and outputs average and standard
%%assumes no duplicates and TT already in chronological order
%%deviations of times where both tables have an observation


%turn inputs into arrays
arr1 = timetable2array(TT1);
arr2 = timetable2array(TT2);
time1 = TT1.Properties.RowTimes;
time2 = TT2.Properties.RowTimes;

inds = ismember(time1, time2);
arr1 = arr1(inds, :);
inds = ismember(time2, time1);
arr2 = arr2(inds, :);
time = time2(inds);

%find rows to keep
inds = any(~isnan(arr1), 2); %non-nan in arr1
inds = inds & any(~isnan(arr2), 2); %both mats need non-nan in each row

%elim unneeded rows
arr1(~inds, :) = [];
arr2(~inds, :) = [];
time(~inds) = [];

%average across rows
avg1 = mean(arr1, 2, "omitnan");
avg2 = mean(arr2, 2, "omitnan");
std1 = std(arr1, 0, 2, "omitnan");
std2 = std(arr2, 0, 2, "omitnan");

%create timetable
outTT = timetable(time, avg1, avg2, std1, std2);
end