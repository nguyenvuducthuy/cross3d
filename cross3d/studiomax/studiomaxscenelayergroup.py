##
#	\namespace	blur3d.api.studiomax.studiomaxscene
#
#	\remarks	The StudiomaxScene class will define all the operations for Studiomax scene interaction.  
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

from Py3dsMax 											import mxs
from blur3d.api.abstract.abstractscenelayergroup 	import AbstractSceneLayerGroup

class StudiomaxSceneLayerGroup( AbstractSceneLayerGroup ):
	def groupName( self ):
		"""
			\remarks	implements the AbstractSceneLayerGroup.groupName method to retrieve the unique layer name for this layer
			\return		<str> name
		"""
		return self._nativePointer
	
	def groupOrder( self ):
		"""
			\remarks	returns the index that this layer group is currently in
			\return		<int>
		"""
		name 	= str(self.groupName())
		gn 		= list(self._scene.metaData().value( 'layerGroupNames' ))
		if ( name in gn ):
			return gn.index( name )
		return -1
		
	def isOpen( self ):
		"""
			\remarks	implements the AbstractLayerGroup.setOpen method to return whether or not the layer group is open
			\return		<bool> open
		"""
		data 	= self._scene.metaData()
		names 	= list(data.value('layerGroupNames'))
		states 	= list(data.value('layerGroupStates'))
		
		name 	= str(self.groupName())
		if ( name in names ):
			return states[names.index(name)]
		return False
	
	def layers( self ):
		"""
			\remarks	implements the AbstractLayerGroup.layers method to retrieve the layers that are currently on this group
			\return		<list> [ <blur3d.api.SceneLayer>, .. ]
		"""
		gi		= self.groupOrder()
		output 	= []
		for layer in self._scene.layers():
			if ( layer.layerName() == 'World Layer' ):
				continue
				
			data 	= layer.metaData()
			lgi 	= data.value( 'groupIndex' ) - 1
			if ( lgi == gi ):
				output.append( layer )
				
		output.sort( lambda x,y: cmp( x.metaData().value( 'groupOrder' ), y.metaData().value( 'groupOrder' ) ) )
		return output
	
	def remove( self, removeLayers = False, removeObjects = False ):
		"""
			\remarks	implements the AbstractLayerGroup.remove method to remove the layer from the scene (layers included when desired)
			\param		removeLayers	<bool>	when true, the layers in the layer group should be removed from the scene, otherwise
												only the layer group should be removed
			\param		removeObjects	<bool>	if removeLayers is true, when removeObjects is true, the objects on the layers in the 
												layer group should be removed from the scene
			\return		<bool> success
		"""
		data 	= self._scene.metaData()
		names 	= list(data.value( 'layerGroupNames' ))
		states	= list(data.value( 'layerGroupStates' ))
		
		# requires at least 1 group
		if ( len(names) == 1 ):
			return False
		
		layers = self.layers()
		
		# remove the layers from the scene
		if ( removeLayers ):
			for layer in layers:
				layer.remove( removeObjects = removeObjects )
		
		# update the layers to be in the root group
		else:
			for layer in layers:
				ldata = layer.metaData()
				ldata.setValue( 'groupIndex', 1 )
		
		# remove this group from the scene
		index = names.index( self.groupName() )
		names 	= names[:index] + names[index+1:]
		states 	= states[:index] + states[index+1:]
		
		data.setValue( 'layerGroupNames', names )
		data.setValue( 'layerGroupStates', states )
		
		return True
	
	def setGroupName( self, groupName ):
		"""
			\remarks	implements the AbstractLayerGroup.setGroupName method to set the name for this layer group
			\param		groupName	<str>
			\return		<bool> changed
		"""
		# make sure we are changing
		if ( groupName == self.groupName() ):
			return False
			
		groupName 	= str(groupName)
		data		= self._scene.metaData()
		names 		= list(data.value( 'layerGroupNames' ))
		
		# make sure we have a unique name
		if ( groupName in names ):
			return False
		
		index 				= names.index(self.groupName())
		names[index] 		= groupName
		self._nativePointer = groupName
		data.setValue( 'layerGroupNames', names )
		return True
	
	def setGroupOrder( self, groupOrder ):
		"""
			\remarks	implements the AbstractLayerGroup.setGroupOrder method to set the order number for this layer group
			\param		groupOrder	<int>
			\return		<bool> changed
		"""
		# make sure we are chaning
		if ( groupOrder == self.groupOrder() ):
			return False
		
		groupName 	= str(self.groupName())
		data		= self._scene.metaData()
		orignames	= list(data.value('layerGroupNames'))
		states		= list(data.value('layerGroupStates'))
		
		if ( not groupName in orignames ):
			return False
		
		index 	= orignames.index(groupName)
		state 	= states[index]
		names 	= orignames[:index] + orignames[index+1:]
		states 	= states[:index] + states[index+1:]
		
		names.insert( groupOrder, groupName )
		states.insert( groupOrder, state )
		
		data.setValue( 'layerGroupNames', names )
		data.setValue( 'layerGroupStates', states )
		
		# update the layers
		for layer in self._scene.layers():
			ldata 	= layer.metaData()
			gi		= ldata.value( 'groupIndex' )
			oname	= orignames[gi-1]
			ldata.setValue( 'groupIndex', names.index(oname) + 1 )
		
		return True
		
	def setOpen( self, state ):
		"""
			\remarks	implements the AbstractLayerGroup.setOpen method to set whether or not the layer group is open
			\return		<bool> open
		"""
		data	= self._scene.metaData()
		names 	= list(data.value('layerGroupNames'))
		states 	= list(data.value('layerGroupStates'))
		
		name 	= str(self.groupName())
		if ( name in names ):
			states[names.index(name)] = state
			data.setValue( 'layerGroupStates', states )
			return True
		return False

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneLayerGroup', StudiomaxSceneLayerGroup )