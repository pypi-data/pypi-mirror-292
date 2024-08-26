#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International  https://github.com/cyborg-ai-git 
#========================================================================================================================================

from evo_framework.entity.EObject import EObject
from evo_framework.core.evo_core_type.entity.EvoMap import EvoMap

#========================================================================================================================================
"""EAdminQuery

    EAdminInput _DOC_
    
"""
class EAdminQuery(EObject):

    VERSION:str="8c80fbde97b419b0b9f81bedd6ad27d940b0efc39a020f455eab1d7473e9df72"

    def __init__(self):
        super().__init__()
        
        self.queryID:str = None
        self.queryCollection:str = None
        self.query:str = None
  
    def toStream(self, stream):
        super().toStream(stream)
        
        self._doWriteStr(self.queryID, stream)
        self._doWriteStr(self.queryCollection, stream)
        self._doWriteStr(self.query, stream)
        
    def fromStream(self, stream):
        super().fromStream(stream)
        
        self.queryID = self._doReadStr(stream)
        self.queryCollection = self._doReadStr(stream)
        self.query = self._doReadStr(stream)
    
    def __str__(self) -> str:
        strReturn = "\n".join([
                super().__str__(),
                            
                f"\tqueryID:{self.queryID}",
                f"\tqueryCollection:{self.queryCollection}",
                f"\tquery:{self.query}",
                            ]) 
        return strReturn
    