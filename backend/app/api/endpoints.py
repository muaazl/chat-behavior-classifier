from fastapi import APIRouter, HTTPException, File, UploadFile, Body, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import time
import logging
from ..services.coordinator import AnalysisCoordinator
from ..schemas.api_responses import AnalysisRequest, AnalysisSuccessResponse, ErrorResponse
from ..services.scoring.schemas import ScoringResponse

router = APIRouter(prefix="/analyze", tags=["Analysis"])
coordinator = AnalysisCoordinator()
logger = logging.getLogger(__name__)
@router.post("/text", response_model=AnalysisSuccessResponse)
async def analyze_text(request_obj: Request, request: AnalysisRequest = Body(...)):
    """Analyze a pasted excerpt of WhatsApp chat text."""
    start_t = time.time()
    try:
        scoring_result: ScoringResponse = await coordinator.run_full_analysis(request.text)
        duration = round(time.time() - start_t, 2)
        return AnalysisSuccessResponse(
            data=scoring_result,
            metadata={
                "timestamp": datetime.utcnow().isoformat(),
                "processing_time": duration,
                "request_id": getattr(request_obj.state, "request_id", None)
            }
        )
    except Exception as e:
        logger.exception("Text analysis failed")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                status="error",
                code="ANALYSIS_FAILED",
                message=f"Analysis failed: {str(e)}"
            ).model_dump()
        )

@router.post("/file", response_model=AnalysisSuccessResponse)
async def analyze_file(request_obj: Request, file: UploadFile = File(...)):
    """Analyze a WhatsApp export .txt file."""
    if not file.filename.endswith(".txt"):
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                status="error",
                code="INVALID_FORMAT",
                message="Only .txt files are supported currently."
            ).model_dump()
        )
    start_t = time.time()
    try:
        content = await file.read()
        scoring_result: ScoringResponse = await coordinator.analyze_file_content(content)
        duration = round(time.time() - start_t, 2)
        return AnalysisSuccessResponse(
            data=scoring_result,
            metadata={
                "timestamp": datetime.utcnow().isoformat(),
                "processing_time": duration,
                "request_id": getattr(request_obj.state, "request_id", None)
            }
        )
    except ValueError as ve:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                status="error",
                code="FILE_TOO_LARGE",
                message=str(ve)
            ).model_dump()
        )
    except Exception as e:
        logger.exception("File analysis failed")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                status="error",
                code="ANALYSIS_FAILED",
                message=f"File analysis failed: {str(e)}"
            ).model_dump()
        )
    finally:
        await file.close()
