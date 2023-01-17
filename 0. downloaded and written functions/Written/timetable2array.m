function [arr] = timetable2array(TT)
%workaround of timetable conversion to array, since it is a pain
%deletes time column of timetable

T = timetable2table(TT);
arr = table2array(T(:, 2:end));

end

