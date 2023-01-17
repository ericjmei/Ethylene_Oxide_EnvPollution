function [conc] = ppbToConc(ppb, Mw, T, P)
%%%converts ppb to ug/m3
%ppb, vector
%Mw in g/mol
%T in celsius, vector same dim as ppb
%P in atm, vector same dim as ppb

R = 0.08205; %L atm/mol K

%units work out with ppb (10^9), ug (10^6), and L -> m3 (10^3)
conc = ppb*Mw.*P/R./(T + 273.15); %conversion for ideal gas law
end