"""
file:      signtest.py
author: ernesto.adorio

version:dec 7, 2009 0.0.0 draft!
"""

from math import sqrt
import scipy.stats as stat

pnorm = stat.norm.cdf

def signtest_pvalue(X,Y, p = 0.05, sided= 0, verbose=0, html=True):
    """
    Returns the p-value of the sign test.
    Arguments:
         X,Y -input paired samples (same length)
         p - probability of success of single trial.
         sided- -1 -left sided test.
                 0 - double sided test
                 1 - right sided test.
    Return value:
         p-value of test.
    """
    diffs = [(x-y) for x,y in zip(X,Y)]
    signs = [1 if (d > 0) else 0 if (d == 0) else -1 for d in diffs]
    if verbose == 2:
       if html:
          print ""
       for i,(x, y, diff, sign) in enumerate(zip(X,Y, diffs, signs)):
          if sign == 1: s = "+"
          elif sign== -1: s = "-"
          else: s = "0"
          if html:
             print "error"
          else:
             print "%d%5.2f %5.2f %4.2f %s" % (i ,x, y, diff, s)
       if html:
          print "%d	%5.2f	 %5.2f	 %4.2f	 %s "
    x = sum([1 if (sign > 0) else 0 for sign in signs])
    y = sum([1 if (sign < 0) else 0 for sign in signs])
    N = sum([1 if (sign != 0) else 0  for sign in signs])
    mean = N * p
    se = sqrt(N* p* (1 -p))

    #if N*p >= 5:
        #ztest = (x - mean)/ se
        #if sided == 0:
           #print "double sided test:"
           #pz = stat.norm.cdf(ztest)
           #print "pnorm(ztest) = ",
           #if ztest > 0:
              #pvalue = 2 *(1- pz)
           #else:
              #pvalue = 2 *pz

        #elif sided == -1:
           #print "left-sided test:"
           #pvalue = stat.norm.cdf(ztest)
        #elif sided == 1:
           #print "rightsided test:"
           #pvalue = stat.norm.sf(ztest)
        #else:
           #raise RuntimeError("in signtestpvalue(): Unhandled exception.")

        #if verbose >0:
           #if html:
               #print ""
               #print "<"
               #print "<"
               #print "<"
               #print "<"
               #print "<"
               #print ""
               #print "", pvalue,""
               #print "x = 	", x, "y = 	", y, "N = 	", N, "mean =	", mean, "se =	 ", se, "ztest=	", ztest, "pvalue="
           #else:
               #print "x = ", x
               #print "y = ", y
               #print "N = ", N
               #print "mean =", mean
               #print "se = ", se
               #print "ztest=", ztest

    #else:
      #print "Using exact binomial probabilities."
      #if sided == -1:
         #return stat.binom.cdf(x, N, 0.5)
      #elif sided == 1:
         #return  stat.binom.sf(X, N, 0.5)
      #elif sided == 0:
         #alpha = stat.binom.cdf(X, N, 0.5)
         #print type(alpha)
         #if alpha < 0.5:
            #return 2 * alpha
         #else:
            #return 2 * (1 -alpha)
      #else:
         #raise RuntimeError("")

    p_value = stat.ttest_1samp(diffs, 0)
     
    # p < 0.05 => alternative hypothesis:
    # the difference in mean is not equal to 0
    print "paired t-test", p_value    
    # print "ztest computed pvalue = ", pvalue
    wvalue = stat.wilcoxon(diffs, zero_method='wilcox')
    print "wilcoxon value:", wvalue
    # return pvalue


