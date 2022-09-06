# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 15:33:20 2011

@author: juherask
"""

import sys
import copy
import random
import logging



MAX_INT = 2147483647 #operate in 32 bit, sys.maxint
MAX_FLOAT = 1.7976931348623157e+308 #operate in 32 bit, sys.float_info.max
MIN_FLOAT = 2.2250738585072014e-308 #operate in 32 bit, sys.float_info.min
    
    
class ParameterSetSet:    
    def __init__(self, definition):  
        self._definition = definition
        self._sets = list()
    
    def __iter__(self):
        # ParameterSetSet is iterated from the internal list
        return self._sets.__iter__()
        
    def Add( self, parameterSet ):
        # Ensure that the parameter set is compatible with the 
        if self._definition.__neq__(parameterSet):
            raise ValueError("ParameterSet does not define all required parameters" )
        
        self._sets.append(parameterSet)
    
    """ Allows you to get the parameter set definition of this parameter
    set set. You can use the definition to create new parameter sets."""
    def GetDefinition(self):
        return self._definition
        

class ParameterSetDefinition:
    
    def __init__(self, existing = None, discretize = None):
        """ Can be used to make discretized clone. If the existing is given, 
        the discretize sets the number of steps for tunable variables for
        which the discretization makes sense.
        """
        if (existing!=None):
            # Parameter definitions
            self._descriptions = copy.deepcopy( existing._descriptions )
            self._switches = copy.deepcopy( existing._switches )
            
            self._defaults = copy.deepcopy( existing._defaults )
            self._required = copy.deepcopy( existing._required )
            self._tunable = copy.deepcopy( existing._tunable)
            self._conditions = copy.deepcopy( existing._conditions)
            
            self._param_count = existing._param_count
            
            self._ranges = copy.deepcopy(existing._ranges )
            if discretize:
                for idx in range(len(self._tunable)):
                    if not self._tunable[idx]:
                        continue
                    
                    startr = self._ranges[idx][0]
                    endr = self._ranges[idx][-1]
                    countr = len(self._ranges[idx])
                    
                    if countr>2:
                        continue # Categocial, makes no sense do Dze
                    if type(startr)==int:
                        if abs(startr-endr)==1:
                            continue # Boolean?, makes no sense to Dze
                    elif type(startr)==float:
                        pass # Always dze
                    else:
                        continue # String or other type we cannot Dze
                    
                    self._ranges[idx] = ParameterSetDefinition._Discretize(startr,endr,discretize)                    
            
        else:
            if discretize:
                raise ValueError("discretize", "Discretization can only be done on existing definitions.")
            
            # Parameter definitions
            self._descriptions = dict()
            self._switches = dict()
            
            self._ranges = list()
            self._defaults = list()
            self._required = list()
            self._tunable = list()
            self._conditions = list()
            
            self._param_count = 0
    
    def __eq__(self, other):
        """ Checks that the other has all the required parameters
            and no parameters not mentioned in definition
        """
        for sw in self.RequiredParameters():
            if ( sw not in other.keys() ):
                logging.error( "Param set %s has not required parameter %s" % (str(list(other.keys())), sw) )
                return False
        for sw in other.keys():
            if ( sw not in self.keys() ):
                logging.error( "Param %s not in allowed %s" % (sw, str(list(self.keys()))) )
                return False
        return True
        
    def __neq__(self, other):
        return not self.__eq__(other)
  
    # Static function to get a random value from the range
    @staticmethod 
    def _SampleValue(valueRange):
        # Degenerate ranges
        if (len(valueRange)==0):
            return None
        elif (len(valueRange)==1):
            return range[0]
            
        # Categorical variable
        if isinstance(valueRange[0], str) or isinstance(valueRange[0], unicode) or len(valueRange) > 2:
            return valueRange[ random.randint(0, len(valueRange)-1) ]
            
        # Numerical values
        elif isinstance(valueRange[0], int):
            return random.randint(valueRange[0], valueRange[1])
        elif isinstance(valueRange[0], float):
            return random.uniform(valueRange[0], valueRange[1])
        
        raise ValueError("Unknown range definition %s" % str(valueRange)) 
    
    @staticmethod 
    def _Discretize(start, end, steps):
        values = []
        valtype = type(start)
        values.append(start)
        
        step = float(abs(end-start))/(steps-1)
        for i in range(1, steps-1):
            values.append( valtype(start+step*i) )
            
        values.append(end)
        return values
                    
    def Add(self, description, switch, defaultValue, valueRange, isRequired, isTunable, conditions=[]):
        self._descriptions[description] = self._param_count
        self._switches[switch] = self._param_count
        
        self._ranges.append(valueRange)
        self._defaults.append(defaultValue)
        self._required.append(isRequired)
        self._tunable.append(isTunable)
        self._conditions.append(conditions)
        
        self._param_count = self._param_count + 1
        
    def AllParameterDescriptions(self):
        return self._descriptions
            
    def AllParameterSwitches(self):
        return self._switches
    
    def RequiredParameters(self):
        for sw in self._switches:
            if self._required[self._switches[sw]]:
                yield sw
                
    def keys(self):
        return self.AllParameterSwitches()
                
    def TunableParameters(self):
        for sw in self._switches:
            if self._tunable[self._switches[sw]]:
                yield sw
                
    def FixedParameters(self):
        for sw in self._switches:
            if self._required[self._switches[sw]] and \
               not self._tunable[self._switches[sw]]:
                yield sw
    
    def HasParameter(self, swOrDesc):
        if (swOrDesc in self._switches) or (swOrDesc in self._descriptions):
            return True
        else:
            return False
        
    def GetParameterDescription(self, sw):
        if (sw in self._switches):
            id = self._switches[sw]
            # A slow way, but usually not a problem as there is only few params
            return [key for key, value in self._descriptions.iteritems() if value == id][0]
        else:
            raise KeyError("No switch matching that description")
        
    def GetParameterSwitch(self, desc):
        if (desc in self._descriptions):
            id = self._descriptions[desc]
            # A slow way, but usually not a problem as there is only few params
            return [key for key, value in self._switches.iteritems() if value == id][0]
        else:
            raise KeyError("No switch matching description " + desc)
        
    def GetParameterRange(self, desc):
        if (desc in self._switches):
            return self._ranges[ self._switches[desc] ]
        elif (desc in self._descriptions):
            return self._ranges[ self._descriptions[desc] ]
        else:
            raise KeyError("No such switch or description")
    
    def GetParameterType(self, desc):
        # Use type of the default value to convert the string
        return type(self.GetParameterDefault(desc))
        
    def GetParameterDefault(self, desc):
        if (desc in self._switches):
            return self._defaults[ self._switches[desc] ]
        elif (desc in self._descriptions):
            return self._defaults[ self._descriptions[desc] ]
        else:
            raise KeyError("No such switch or description")
            
    def SetParameterDefault(self, desc, newDefault):
        if (desc in self._switches):
            self._defaults[ self._switches[desc] ] = newDefault
        elif (desc in self._descriptions):
            self._defaults[ self._descriptions[desc] ] = newDefault
        else:
            raise KeyError("No such switch or description")
        
    def SetParameterFixed(self, desc, fixed=True):
        if (desc in self._switches):
            self._required[ self._switches[desc] ] = fixed
        elif (desc in self._descriptions):
            self._required[ self._descriptions[desc] ] = fixed
        else:
            raise KeyError("No such switch or description")
            
    # TODO: Add access/support for conditions
    
    def NewDefaultParameterSet(self):
        """ New default parameter set from the definition. It will include
        all the fixed (required, but nontunable) and tunable parameters with
        their default values.
        
        Note: Set will not include non-tunable non-required parameters.
        """
        ps = dict()
        # Add required and tunable
        for sw in self.FixedParameters():
            ps[sw] = self.GetParameterDefault(sw)
        for sw in self.TunableParameters():
            ps[sw] = self.GetParameterDefault(sw)
        return ps
        
    def NewSampledParameterSet(self):
        """ Sample new random parameter set from the definition. It will include
        all the fixed parameters set to default (required, but nontunable) and
        the uniformly random sampled values for tunable parameters.
        
        Note: Set will not include non-tunable non-required parameters.
        """
        ps = dict()
        
        for sw in self.FixedParameters():
            ps[sw] = self.GetParameterDefault(sw)
        for sw in self.TunableParameters():
            ps[sw] = self._SampleValue( self.GetParameterRange(sw) )
        
        return ps
        
def main():

    vrph_param_count = ParameterSetDefinition()
     
    # Special parameters that are expected to be in every Solver
    vrph_param_count.Add("Instance", "-i", "", (), True, False) # Input File
    vrph_param_count.Add("Seed", "-s", 0, (), False, False) # Random seed for a stochastic algo
    vrph_param_count.Add("Timeout", "-t", 5.0, (0.0,MAX_FLOAT), False, False) # Timebudget for the algo
    
    # Parameters that define the solver behaviour, but are not typically tuned
    vrph_param_count.Add("NumberOfTries", "-n", 1, (0,MAX_INT), False, False)
    vrph_param_count.Add("VehicleCapacity", "-q", 0, (0,MAX_INT), False, False) # Not used
    
    # Objective function evaluation parameters
    vrph_param_count.Add("UseProxy", "-p", False, (False, True), False, True )
    vrph_param_count.Add("UseTSP", "-u", False, (False, True), False, True )
    
    
    vrph_acs_param_count = ParameterSetDefinition(vrph_param_count)
    
    vrph_acs_param_count.Add("ColonySize", "-colonysize", 7, (0,1000), False, True);
    vrph_acs_param_count.Add("tau0", "-tau0", 0.5, (0.0,1.0), False, True);
    vrph_acs_param_count.Add("rho", "-rho", 0.1, (0.0,1.0), False, True);
    vrph_acs_param_count.Add("psi", "-psi", 0.3, (0.0,1.0), False, True);
    vrph_acs_param_count.Add("Q", "-Q", 10000000.0, (0.0,MAX_FLOAT), False, True);
    vrph_acs_param_count.Add("alpha", "-alpha", 1.0, (0.0,1.0), False, True);
    
    # Just see that parameters are there
    for p in vrph_param_count.AllParameterSwitches():
        print p
    
    print 
    
    for p in vrph_acs_param_count.AllParameterSwitches():
        print p
    
    print

    # Try to create a pararameter set        
    acs_pss = ParameterSetSet(vrph_acs_param_count)
    acs_pss.Add( vrph_acs_param_count.NewDefaultParameterSet() )
    acs_pss.Add( vrph_acs_param_count.NewSampledParameterSet() )
    
    print ("Created parameter sets:")
    for ps in acs_pss:
        print (str(ps))

if __name__ == '__main__':
    main()
