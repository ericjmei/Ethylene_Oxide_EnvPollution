function [vec] = unravelTT(TT)
%turns contents of timetable to one-D vector without NaN

arr = timetable2array(TT);
vec = arr(:); %unravel
vec = vec(~isnan(vec)); %remove nans

end

