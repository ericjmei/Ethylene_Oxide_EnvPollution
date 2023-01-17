function [vec] = unravelTTnan(TT)
%turns contents of timetable to one-D vector with NaN

arr = timetable2array(TT);
vec = arr(:); %unravel

end

