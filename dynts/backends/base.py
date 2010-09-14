from itertools import izip
from dynts.exceptions import *
from dynts.utils import wrappers


Formatters = {}

class TimeSeries(object):
    '''Interface class for timeseries back-ends.
    
    .. attribute:: type
    
        string indicating the backend type (zoo, rmetrics, numpy, etc...)
    '''
    type = None
    
    def __init__(self, name = '', date = None, data = None):
        self.name    = str(name)
        self.make(date,data)
        
    def __repr__(self):
        d = self.description()
        b = '%s:%s' % (self.__class__.__name__,self.__class__.type)
        if d:
            return '%s:%s' % (b,d)
        else:
            return b
    
    def __str__(self):
        return self.description()
    
    def names(self):
        '''List of names for each timeseries'''
        N = self.count()
        names = self.name.split(',')[:N]
        n = 0
        while len(names) < N:
            n += 1
            names.append('unnamed%s' % n)
        return names        
        
    def description(self):
        return self.name
    
    def __len__(self):
        return self.shape[0]
    
    def count(self):
        '''Number of series in the timeseries'''
        return self.shape[1]
    
    def asdict(self):
        '''Return an instance of :class:`dynts.utils.wrappers.asdict`
which exposes dictionary-like functionalities of ``self``.'''
        return wrappers.asdict(self)
    
    def dateconvert(self, dte):
        return dte
    
    def dateinverse(self, key):
        return key
    
    def max(self):
        '''Max value'''
        return self.rollmax()[0]
    
    def min(self):
        '''Max value'''
        return self.rollmin()[0]
    
    def mean(self):
        '''Mean value'''
        return self.rollmean()[0]
    
    def returns(self, k = 1):
        '''Calculate returns as delta(log(self))'''
        return self.log().delta(k)
    
    def dates(self):
        '''Returns an iterable over ``datetime.date`` instances in the timeseries.'''
        c = self.dateinverse
        for key in self.keys():
            yield c(key)
            
    def values(self):
        '''Returns a ``numpy.ndarray`` containing the values of the timeseries.
Implementations should try not to copy data if possible. This function
can be used to access the timeseries as if it was a matrix.'''
        raise NotImplementedError
    
    def items(self):
        '''Returns a python ``generator`` which can be used to iterate over
:func:`dates` and :func:`values` returning a two dimensional
tuple ``(date,value)`` in each iteration. Similar to the python dictionary items
function.'''
        for d,v in izip(self.dates(),self.values()):
            yield d,v
    
    def display(self):
        '''Nicely display self on the shell. Useful during prototyping and development.'''
        for d,v in self.items():
            print('%s: %s' % d,v)
            
    def dump(self, format = None, **kwargs):
        '''Dump the timeseries using a specific :ref:`format <formatters>`.'''
        formatter = Formatters.get(format,None)
        if not format:
            return self.display()
        else:
            return formatter(self,**kwargs)
        
    # PURE VIRTUAL FUNCTIONS
    
    @property
    def shape(self):
        raise NotImplementedError
    
    def __getitem__(self, i):
        raise NotImplementedError
    
    def keys(self):
        raise NotImplementedError
    
    def colnames(self):
        raise NotImplementedError
    
    def delta(self, k = 1):
        raise NotImplementedError
    
    def lag(self, k = 1):
        raise NotImplementedError
    
    def log(self):
        raise NotImplementedError
    
    def stddev(self):
        raise NotImplementedError
    
    def rollmax(self, window = None):
        raise NotImplementedError
    
    def rollmin(self, window = None):
        raise NotImplementedError
    
    def rollmean(self, window = None):
        raise NotImplementedError
    
    def start(self):
        '''Start date of timeseries'''
        raise NotImplementedError
    
    def end(self):
        '''End date of timeseries'''
        raise NotImplementedError
    
    def window(self, start, end):
        raise NotImplementedError
    
    def merge(self, ts, all = True):
        raise NotImplementedError
    
    def clone(self, data = None, name = None):
        name = name or self.name
        data = data if data is not None else self.values()
        ts = self.__class__(name)
        ts.make(self.keys(),data,raw=True)
        return ts
        
    def __add__(self, other):
        return addts(self,other)
    
    # INTERNALS
    ################################################################
    
    def make(self, date, data, **kwargs):
        '''Internal function to create the inner data:
        
* *date* iterable/iterator/generator over dates
* *data* iterable/iterator/generator over values'''
        raise NotImplementedError