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
        print "Score2Score {}".format(self.scoreToScore([0.6, 0.75, 0.55], [0.3, 0.3, 0.4], 0.2))
        print "Rate2Score {}".format(self.rateToScore([2.0, 1.38, 1.0], [0.5, 0.5, 0.5], 0.75, 2))
        print "An {}".format(self.profileToScore([0.1, 0.25, 0.25, 0.25, 0.15], 0.5))
        print "Hn {}".format(self.profileToScore([0.05, 0.05, 0.30, 0.40, 0.20], 0.5))
        print "H2 {}".format(self.profileToScore([0.1, 0.9], 0.6))
        print "A2 {}".format(self.profileToScore([0.15, 0.85], 0.0))

        
    def scoreToScore(self, scores, weights, lenience):
        sMin = 1
        sMax = 1
        
        for i in range(0, len(scores)):
            sMin *= math.pow(scores[i], weights[i])
            sMax *= math.pow(1 - scores[i], weights[i])
            
        sMax = 1 - sMax
        return (1 - lenience) * sMin + lenience * sMax
        
        
    def refining(self, impact, performance, score):
        if performance == "inf":
            score = score / (1 - impact * (1 - score))
        else:
            score = score * (1 - math.pow(impact * (1 - score), performance)) / (1 - impact * (1 - score))
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


        def scoreToGrade(score, model='Pass', curvature, polarity, gMin, gMax):
            curvature= pow((1-pow(score, curvature)), (1/curvature));
            g = polarity*curvature+(1-polarity)*(1-curvature);
            return g * gMin + (1-g)*gMax; 
        
        
        def scoreToRate(score, standart, impact):
            if(standart==0 or standart==1 or impact==0 ):
                return 1;
            elif (score<(standart/(1-impact*(1-standart)))):
                return math.log(1 - score * (1 - impact * (1 - standart)) / standart) / math.log(impact * (1 - standart));
            else :
                return -1;
          
        
Utils(1)      
            