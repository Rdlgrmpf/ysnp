'''
Created on 29.04.2014

@author: janosch
'''
import math
from scipy import special


class Utils(object):
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        
    def scoreToScore(self, scores, weights, lenience):
        sMin = 1
        sMax = 1
        
        for i in range(0, len(scores)-1):
            sMin *= math.pow(scores[i], weights[i])
            sMax *= math.pow(1 - scores[i], weights[i])
            
        sMax = 1 - sMax
        return (1 - lenience) * sMin + lenience * sMax
        
        
    
    def rateToScore(self):
        pass
    
    def profileToScore(self, profile, tolerance):
        #Number of quality categories
        num = len(profile)
        pLower = []
        pUpper = []
        
        for i in range(1,num):
            pLower.insert(i, pLower(i - 1) + profile[i])
            pUpper.insert(i, pUpper(i - 1) + profile[num + 1 - i])
        
        rLower = 0.0
        rUpper = 0.0
        
        for i in range(1, num-1):
            if pLower[i] > 0:
                rLower = rLower + math.e(special.gammaln(i + pLower(i)) - special.gammaln(i + 1) - special.gammaln(pLower(i)))
            if pUpper[i] > 0:
                rUpper = rUpper + math.e(special.gammaln(i + pUpper(i)) - special.gammaln(i + 1) - special.gammaln(pUpper(i)))
                
        rLower = 1 - rLower / (num - 1)
        rUpper = rUpper / (num - 1)
        
        return (1 - tolerance) * min(rUpper, rLower) + tolerance * max(rUpper, rLower)
        
        
        
       
            