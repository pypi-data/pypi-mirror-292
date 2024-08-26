#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International  https://github.com/cyborg-ai-git 
#========================================================================================================================================

from evo_framework import *
from evo_package_admin.entity import *
from evo_package_admin.utility import *
from evo_framework.core.evo_core_api.entity.EApiQuery import EApiQuery
from evo_framework.core.evo_core_api.entity.EApiConfig import EApiConfig
from evo_framework.core.evo_core_api.entity.EApiFile import EApiFile

# ---------------------------------------------------------------------------------------------------------------------------------------
# CAdminApi
# ---------------------------------------------------------------------------------------------------------------------------------------
"""CAdminApi
"""
class CAdminApi(CApi):
	__instance = None
# ---------------------------------------------------------------------------------------------------------------------------------------
	def __init__(self):   
		if CAdminApi.__instance != None:
			raise Exception("ERROR:SINGLETON")
		else:
			super().__init__()
			CAdminApi.__instance = self
			self.currentPath = os.path.dirname(os.path.abspath(__file__))
			
# ---------------------------------------------------------------------------------------------------------------------------------------
	"""getInstance Singleton

	Raises:
		Exception:  api exception

	Returns:
		_type_: CAdminApi instance
	"""
	@staticmethod
	def getInstance():
		if CAdminApi.__instance is None:
			cObject = CAdminApi()  
			cObject.doInit()  
		return CAdminApi.__instance
# ---------------------------------------------------------------------------------------------------------------------------------------
	"""doInit

	Raises:
		Exception: api exception

	Returns:

	"""   
	def doInit(self):   
		try:			
			UAdminApi.getInstance().doInit()
		except Exception as exception:
			IuLog.doException(__name__, exception)
			raise	  
# ---------------------------------------------------------------------------------------------------------------------------------------
	"""doAddApi

	Raises:
		Exception: api exception

	Returns:

	"""
	@override   
	def doAddApi(self):
		try:			
			
			api0 = self.newApi("admin-set_eapiconfig", callback=self.onSetEApiConfig, input=EApiQuery, output=EApiConfig )
			api0.description="admin-api0 _DESCRIPTION_"
			api0.required="EApiQuery.eApiAdmin"

			api1 = self.newApi("admin-get_eapiconfig", callback=self.onGetEApiConfig, input=EApiQuery, output=EApiConfig )
			api1.description="admin-get_eapiconfig _DESCRIPTION_"
			api1.required="*"

			api2 = self.newApi("admin-query_automation", callback=self.onQueryAutomation, input=EApiQuery, output=EApiFile )
			api2.description="admin-query_automation _DESCRIPTION_"
			api2.required="*"
  
		except Exception as exception:
			IuLog.doException(__name__, exception)
			raise
# ---------------------------------------------------------------------------------------------------------------------------------------

	"""onSetEApiConfig api callback

	Raises:
		Exception: api exception

	Returns:
		EAction:  EObject 
	"""   
	async def onSetEApiConfig(self,  eAction: EAction) -> EAction:
		try:
			IuLog.doDebug(__name__,f"onSetEApiConfig: {eAction} ")

					
			async for eActionOutput in UAdminApi.getInstance().doOnSetEApiConfig(eAction):
				IuLog.doVerbose(__name__, f"{eActionOutput}")
				yield eActionOutput	


		except Exception as exception:
			IuLog.doException(__name__, exception)
			eAction.doSetError(f"{exception}")
			yield eAction
# ---------------------------------------------------------------------------------------------------------------------------------------

	"""onGetEApiConfig api callback

	Raises:
		Exception: api exception

	Returns:
		EAction:  EObject 
	"""   
	async def onGetEApiConfig(self,  eAction: EAction) -> EAction:
		try:
			IuLog.doDebug(__name__,f"onGetEApiConfig: {eAction} ")

					
			async for eActionOutput in UAdminApi.getInstance().doOnGetEApiConfig(eAction):
				IuLog.doVerbose(__name__, f"{eActionOutput}")
				yield eActionOutput	


		except Exception as exception:
			IuLog.doException(__name__, exception)
			eAction.doSetError(f"{exception}")
			yield eAction
# ---------------------------------------------------------------------------------------------------------------------------------------

	"""onQueryAutomation api callback

	Raises:
		Exception: api exception

	Returns:
		EAction:  EObject 
	"""   
	async def onQueryAutomation(self,  eAction: EAction) -> EAction:
		try:
			IuLog.doDebug(__name__,f"onQueryAutomation: {eAction} ")

					
			async for eActionOutput in UAdminApi.getInstance().doOnQueryAutomation(eAction):
				IuLog.doVerbose(__name__, f"{eActionOutput}")
				yield eActionOutput	


		except Exception as exception:
			IuLog.doException(__name__, exception)
			eAction.doSetError(f"{exception}")
			yield eAction
# ---------------------------------------------------------------------------------------------------------------------------------------
