class ListRedirect(object):
    """
    A utility class for lists of items joined by an operator.  
    :class:`~rdfextras.sparql2sql.bison.Util.ListRedirect`s 
    with length 1 are a special case and are considered equivalent to the 
    item instead of a list containing it.
    
    """
    reducable = True
    def __getattr__(self, attr):
        if hasattr(self._list, attr):
            return getattr(self._list, attr)
        raise AttributeError, '%s has no such attribute %s' % (repr(self), attr)

    def __iter__(self):
        for i in self._list:
            yield i

    def __len__(self):
        return len(self._list)

    def reduce(self):
        """
        The reduce method is used for normalizing 
        :class:`~rdfextras.sparql2sql.bison.Util.ListRedirect` to the single 
        item (and calling reduce on it recursively)
        """
        if self.reducable and len(self._list) == 1:
            singleItem = self._list[0]
            if isinstance(singleItem,ListRedirect):
                return singleItem.reduce()
            else:
                return singleItem
        else:
            return type(self)(
                [isinstance(item,ListRedirect) and item.reduce() or item 
                    for item in self._list])

def ListPrepend(item, list):
    """Utility function for adding items to the front of a list"""
    #print "adding %s to front of %s"%(item,list)
    return [item] + list

# Convenience
# from rdfextras.sparql2sql.bison.Util import ListRedirect
# from rdfextras.sparql2sql.bison.Util import ListPrepend
