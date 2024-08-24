#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International  https://github.com/cyborg-ai-git 
#========================================================================================================================================

from evo_framework.entity.EObject import EObject
from evo_framework.core.evo_core_type.entity.EvoMap import EvoMap

from evo_framework.core.evo_core_api.entity.EApiAdmin import EApiAdmin
from evo_framework.core.evo_core_api.entity.EApiQuery import EApiQuery
#========================================================================================================================================
"""EFirebaseAdmin

    EFirebaseAdmin DOC
    
"""
class EFirebaseAdmin(EObject):

    VERSION:str="84c7b8aab6f9af10ee31579f4e908e3d81acc6fd1571c93f83363c9b2c7b1273"

    def __init__(self):
        super().__init__()
        
        self.type:str = None
        self.data:bytes = None
        self.eApiAdmin:EApiAdmin = None
        self.eApiQuery:EApiQuery = None
  
    def toStream(self, stream):
        super().toStream(stream)
        
        self._doWriteStr(self.type, stream)
        self._doWriteBytes(self.data, stream)
        self._doWriteEObject(self.eApiAdmin, stream)
        self._doWriteEObject(self.eApiQuery, stream)
        
    def fromStream(self, stream):
        super().fromStream(stream)
        
        self.type = self._doReadStr(stream)
        self.data = self._doReadBytes(stream)
        self.eApiAdmin = self._doReadEObject(EApiAdmin, stream)
        self.eApiQuery = self._doReadEObject(EApiQuery, stream)
    
    def __str__(self) -> str:
        strReturn = "\n".join([
                super().__str__(),
                            
                f"\ttype:{self.type}",
                f"\tdata length:{len(self.data) if self.data else 'None'}",
                f"\teApiAdmin:{self.eApiAdmin}",
                f"\teApiQuery:{self.eApiQuery}",
                            ]) 
        return strReturn
    