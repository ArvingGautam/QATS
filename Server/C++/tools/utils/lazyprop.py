def lazyprop(fn):
	"""
	Enables lazy (on-demand) evaluation of a property. 
	
	Ref: http://stackoverflow.com/questions/3012421/ 
	"""
	
	attr_name = '_lazy_' + fn.__name__
	@property
	def _lazyprop(self):
		if not hasattr(self, attr_name):
			setattr(self, attr_name, fn(self))
		return getattr(self, attr_name)
	return _lazyprop
