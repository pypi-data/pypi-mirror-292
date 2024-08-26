#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International  https://github.com/cyborg-ai-git 
#========================================================================================================================================

from evo_framework.entity.EObject import EObject
from evo_framework.core.evo_core_type.entity.EvoMap import EvoMap

#========================================================================================================================================
"""EAdminOutput

    EAdminOutput _DOC_
    
"""
class EAdminOutput(EObject):

    VERSION:str="0f04c9ff148494bb85f75e70c94eb2f1eb7245210aaf7fcd9f3a3aae2e8023e9"

    def __init__(self):
        super().__init__()
        
        self.attribute0:str = None
  
    def toStream(self, stream):
        super().toStream(stream)
        
        self._doWriteStr(self.attribute0, stream)
        
    def fromStream(self, stream):
        super().fromStream(stream)
        
        self.attribute0 = self._doReadStr(stream)
    
    def __str__(self) -> str:
        strReturn = "\n".join([
                super().__str__(),
                            
                f"\tattribute0:{self.attribute0}",
                            ]) 
        return strReturn
    