import statistics
import math

# Main maths class
class maths():
        def getMean(meanVal):
            return statistics.mean(meanVal)
        
        def getMedian(medianVal):
            return statistics.median(medianVal)
        
        def getMode(modeVal):
            return statistics.mode(modeVal)

        def squareRoot(squarerootValue):
             return math.sqrt(squarerootValue)
                
        def getMod(valOne, valTwo):
             return math.fmod(valOne, valTwo)
