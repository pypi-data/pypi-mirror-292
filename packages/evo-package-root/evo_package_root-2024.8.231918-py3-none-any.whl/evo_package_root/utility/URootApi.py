#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 Internation    https://github.com/cyborg-ai-git | 
#========================================================================================================================================

from evo_framework import *
from evo_package_root.entity import *
from evo_framework.core.evo_core_api.entity.EApiConfig import EApiConfig

#<
from evo_package_firebase.utility.UFirebaseApi import UFirebaseApi
#>
# ---------------------------------------------------------------------------------------------------------------------------------------
# URootApi
# ---------------------------------------------------------------------------------------------------------------------------------------
"""URootApi
"""
class URootApi():
    __instance = None
# ---------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self):   
        if URootApi.__instance != None:
            raise Exception("ERROR:SINGLETON")
        else:
            super().__init__()
            URootApi.__instance = self
            self.currentPath = os.path.dirname(os.path.abspath(__file__))
            self.mapEApiConfig:EvoMap = EvoMap()
            
# ---------------------------------------------------------------------------------------------------------------------------------------
    """getInstance Singleton

    Raises:
        Exception:  api exception

    Returns:
        _type_: URootApi instance
    """
    @staticmethod
    def getInstance():
        if URootApi.__instance is None:
            uObject = URootApi()  
            uObject.doInit()  
        return URootApi.__instance
# ---------------------------------------------------------------------------------------------------------------------------------------
    """doInit

    Raises:
        Exception: api exception

    Returns:

    """   
    def doInit(self):   
        try:
#<
           UFirebaseApi.getInstance().doInit()
#>   
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise
# ---------------------------------------------------------------------------------------------------------------------------------------
    async def doOnSet(self, eAction:EAction) -> EAction:
        """doOnSet utility callback
            input: EApiConfig
            output: EApiText

            Raises:
                Exception: api exception

            Returns:
                EAction:  EObject 
        """   
        try:

            eApiConfig:EApiConfig = eAction.doGetInput(EApiConfig)
           
            #Dispose eAction.input for free memory
            eAction.input = b''

            if eApiConfig is None:
                raise Exception("ERROR_REQUIRED|eApiConfig|")

#<        
            IuLog.doDebug(__name__, f"eApiConfig:{eApiConfig}")

            idSha256 = IuCryptHash.toSha256Bytes(eApiConfig.publicKey)
            
            if idSha256 != eApiConfig.id:
                raise Exception("ERROR_NOT_VALID_ID")
            
    
            eApiconfigID = f"cyborgai://{eApiConfig.id.hex()}"
           
            data=eApiConfig.toBytes()
           
            await UFirebaseApi.getInstance().doSet(collection=EApiConfig.VERSION, id=eApiConfig.id, data=data, isEncrypt=False)
            self.mapEApiConfig.doSet(eApiConfig)
   
            eApiText = EApiText()
            eApiText.doGenerateID()
            eApiText.text=eApiconfigID

            eAction.enumApiAction = EnumApiAction.COMPLETE
            eAction.doSetOutput(eApiText)        
            yield eAction
#>
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise
# ---------------------------------------------------------------------------------------------------------------------------------------
    async def doOnGet(self, eAction:EAction) -> EAction:
        """doOnGet utility callback
            input: EApiQuery
            output: EApiConfig

            Raises:
                Exception: api exception

            Returns:
                EAction:  EObject 
        """   
        try:

            eApiQuery:EApiQuery = eAction.doGetInput(EApiQuery)
           
            #Dispose eAction.input for free memory
            eAction.input = b''

            if eApiQuery is None:
                raise Exception("ERROR_REQUIRED|eApiQuery|")

#<        
            #Add other check
            '''
            if eApiQuery. is None:
                raise Exception("ERROR_REQUIRED|eApiQuery.|")
            '''
   
            if IuText.StringEmpty(eApiQuery.eObjectID) :
                raise Exception("ERROR_REQUIRED|EApiQuery.eObjectID|")
            
            id = eApiQuery.eObjectID # IuConvert.fromHex(eApiQuery.eObjectID)
            if id in self.mapEApiConfig.keys():
                eApiConfig:EApiConfig = self.mapEApiConfig.doGet(id)
            else:
                data = await UFirebaseApi.getInstance().doGet(collection=EApiConfig.VERSION, id=id)
                eApiConfig = IuApi.toEObject(EApiConfig(), data)
                self.mapEApiConfig.doGet(eApiConfig)


            eAction.enumApiAction = EnumApiAction.COMPLETE
            eAction.doSetOutput(eApiConfig)        
            yield eAction
#>
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise
# ---------------------------------------------------------------------------------------------------------------------------------------
    async def doOnGetPackage(self, eAction:EAction) -> EAction:
        """doOnGetPackage utility callback
            input: EApiQuery
            output: EEApiPackage

            Raises:
                Exception: api exception

            Returns:
                EAction:  EObject 
        """   
        try:

            eApiQuery:EApiQuery = eAction.doGetInput(EApiQuery)
           
            #Dispose eAction.input for free memory
            eAction.input = b''

            if eApiQuery is None:
                raise Exception("ERROR_REQUIRED|eApiQuery|")

#<        
            #Add other check
            '''
            if eApiQuery. is None:
                raise Exception("ERROR_REQUIRED|eApiQuery.|")
            '''
   
            eEApiPackage = EEApiPackage()
            eEApiPackage.doGenerateID()
            eEApiPackage.doGenerateTime()

            eAction.enumApiAction = EnumApiAction.COMPLETE
            eAction.doSetOutput(eEApiPackage)        
            yield eAction
#>
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise
# ---------------------------------------------------------------------------------------------------------------------------------------

#<
#OTHER METHODS ...
#>
# ---------------------------------------------------------------------------------------------------------------------------------------
