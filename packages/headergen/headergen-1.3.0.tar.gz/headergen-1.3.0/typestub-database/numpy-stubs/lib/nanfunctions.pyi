from numpy.core.fromnumeric import amax as amax, amin as amin, argmax as argmax, argmin as argmin, cumprod as cumprod, cumsum as cumsum, mean as mean, prod as prod, std as std, sum as sum, var as var
from numpy.lib.function_base import median as median, percentile as percentile, quantile as quantile

nanmin = amin
nanmax = amax
nanargmin = argmin
nanargmax = argmax
nansum = sum
nanprod = prod
nancumsum = cumsum
nancumprod = cumprod
nanmean = mean
nanvar = var
nanstd = std
nanmedian = median
nanpercentile = percentile
nanquantile = quantile
