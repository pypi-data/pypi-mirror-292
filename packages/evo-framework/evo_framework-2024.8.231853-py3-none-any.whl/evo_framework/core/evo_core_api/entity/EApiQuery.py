#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International  https://github.com/cyborg-ai-git 
#========================================================================================================================================

from evo_framework.entity.EObject import EObject
from evo_framework.core.evo_core_type.entity.EvoMap import EvoMap

from evo_framework.core.evo_core_api.entity.EApiAdmin import EApiAdmin
#========================================================================================================================================
"""EApiQuery

    EApiQuery defines the structure for querying within the EVO framework, including collection, eObjectID ID, and query string.
    
"""
class EApiQuery(EObject):

    VERSION:str="15f9a69b86160f6297fbd8fe33e0d301706b8441afe84e089162c828e35d42e9"

    def __init__(self):
        super().__init__()
        
        self.collection:str = None
        self.eObjectID:bytes = None
        self.query:str = None
        self.data:bytes = None
        self.eApiAdmin:EApiAdmin = None
  
    def toStream(self, stream):
        super().toStream(stream)
        
        self._doWriteStr(self.collection, stream)
        self._doWriteBytes(self.eObjectID, stream)
        self._doWriteStr(self.query, stream)
        self._doWriteBytes(self.data, stream)
        self._doWriteEObject(self.eApiAdmin, stream)
        
    def fromStream(self, stream):
        super().fromStream(stream)
        
        self.collection = self._doReadStr(stream)
        self.eObjectID = self._doReadBytes(stream)
        self.query = self._doReadStr(stream)
        self.data = self._doReadBytes(stream)
        self.eApiAdmin = self._doReadEObject(EApiAdmin, stream)
    
    def __str__(self) -> str:
        strReturn = "\n".join([
                super().__str__(),
                            
                f"\tcollection:{self.collection}",
                f"\teObjectID length:{len(self.eObjectID) if self.eObjectID else 'None'}",
                f"\tquery:{self.query}",
                f"\tdata length:{len(self.data) if self.data else 'None'}",
                f"\teApiAdmin:{self.eApiAdmin}",
                            ]) 
        return strReturn
    