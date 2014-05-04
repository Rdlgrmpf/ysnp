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

    @staticmethod    
    def scoreToScore(self, scores, weights, lenience):
        sMin = 1
        sMax = 1
        
        for i in range(0, len(scores)):
            sMin *= math.pow(scores[i], weights[i])
            sMax *= math.pow(1 - scores[i], weights[i])
            
        sMax = 1 - sMax
        return (1 - lenience) * sMin + lenience * sMax
        
    @staticmethod    
    def refining(self, impact, performance, score):
        if performance == "inf":
            score = score / (1 - impact * (1 - score))
        else:
            score = score * (1 - math.pow(impact * (1 - score), performance)) / (1 - impact * (1 - score))
        return score
    
    @staticmethod
    def rateToScore(self, rates, impacts, score, i):
        ''' Call with len(rates)-1 as i when calling first time '''
        if(i != 0):
            return self.refining(impacts[i], rates[i], self.rateToScore(rates, impacts, score, i-1))
        else:
            return self.refining(impacts[i], rates[i], score)
    
    @staticmethod
    def profileToScore(self, profile, tolerance):
        #Number of quality categories
        num = len(profile)
        pLower = [0]
        pUpper = [0]
        
        
        for i in range(1, num+1):
            pLower.insert(i, pLower[i - 1] + profile[i - 1])
            pUpper.insert(i, pUpper[i - 1] + profile[num - i])
        

        rLower = 0.0
        rUpper = 0.0
        
        for i in range(1, num):
            if pLower[i] > 0:
                rLower = rLower + math.exp( special.gammaln(i + pLower[i]) - special.gammaln(i + 1) - special.gammaln(pLower[i]) )
            if pUpper[i] > 0:
                rUpper = rUpper + math.exp( special.gammaln(i + pUpper[i]) - special.gammaln(i + 1) - special.gammaln(pUpper[i]) )
                
        rLower = 1 - rLower / (num - 1)
        rUpper = rUpper / (num - 1)
        
        return (1 - tolerance) * min(rUpper, rLower) + tolerance * max(rUpper, rLower)

    @staticmethod
    def scoreToGrade(self, score, curvature=1.678, polarity=1, gMin=1, gMax=5):
        curvature= pow((1-pow(score, curvature)), (1/curvature));
        g = polarity*curvature+(1-polarity)*(1-curvature);
        return g * gMin + (1-g)*gMax; 
    
    @staticmethod
    def scoreToRate(self, score, standart, impact):
        if(standart==0 or standart==1 or impact==0 ):
            return 1;
        elif (score<(standart/(1-impact*(1-standart)))):
            return math.log(1 - score * (1 - impact * (1 - standart)) / standart) / math.log(impact * (1 - standart));
        else :
            return -1; 