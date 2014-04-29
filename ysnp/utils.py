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
        
        
    def refining(self, impact, performance, score):
        if performance == "inf":
            score = score / (1 - impact * (1 - score))
        else:
            score = score * (1 - (impact * (1 - score)) ^ performance) / (1 - impact * (1 - score))
        return score
    
    
    def rateToScore(self, rates, impacts, score, i):
        ''' Call with len(rates)-1 as i when calling first time '''
        if(i != 0):
            return self.refining(impacts[i], rates[i], self.rateToScore(rates, impacts, score, i-1))
        else:
            return self.refining(impacts[i], rates[i], score)
    
    
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
        
        
        
       
            