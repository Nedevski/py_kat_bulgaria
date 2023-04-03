from obligations import has_obligations, KatPersonDetails
from logging import Logger

_LOGGER = Logger(__name__)

result = has_obligations(KatPersonDetails("9402230507", "285740315"), _LOGGER)
print(result)
