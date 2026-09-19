from fastapi import APIRouter

from .alerts import router as alerts_router
from .attacks import router as attacks_router
from .events import router as events_router
from .experiments import router as experiments_router
from .metrics import router as metrics_router
from .signatures import router as signatures_router
from .verification import router as verification_router

router = APIRouter()

router.include_router(signatures_router)
router.include_router(verification_router)
router.include_router(alerts_router)
router.include_router(attacks_router)
router.include_router(events_router)
router.include_router(experiments_router)
router.include_router(metrics_router)