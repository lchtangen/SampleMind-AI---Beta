"""Analysis repository"""

from typing import Any

from samplemind.core.database.mongo import Analysis


class AnalysisRepository:
    """Repository for analysis CRUD operations"""

    @staticmethod
    async def create(
        analysis_id: str,
        file_id: str,
        tempo: float,
        key: str,
        mode: str,
        time_signature: list[int],
        duration: float,
        analysis_level: str,
        processing_time: float,
        user_id: str | None = None,
        spectral_features: dict[str, Any] | None = None,
        ai_provider: str | None = None,
        ai_model: str | None = None,
        ai_summary: str | None = None,
        ai_detailed: dict[str, Any] | None = None,
        production_tips: list[str] | None = None,
        creative_ideas: list[str] | None = None,
        fl_studio_recommendations: list[str] | None = None,
    ) -> Analysis:
        """Create new analysis record"""
        analysis = Analysis(
            analysis_id=analysis_id,
            file_id=file_id,
            user_id=user_id,
            tempo=tempo,
            key=key,
            mode=mode,
            time_signature=time_signature,
            duration=duration,
            spectral_features=spectral_features,
            ai_provider=ai_provider,
            ai_model=ai_model,
            ai_summary=ai_summary,
            ai_detailed=ai_detailed,
            production_tips=production_tips or [],
            creative_ideas=creative_ideas or [],
            fl_studio_recommendations=fl_studio_recommendations or [],
            analysis_level=analysis_level,
            processing_time=processing_time,
        )
        await analysis.insert()
        return analysis

    @staticmethod
    async def get_by_id(analysis_id: str) -> Analysis | None:
        """Get analysis by ID"""
        return await Analysis.find_one(Analysis.analysis_id == analysis_id)

    @staticmethod
    async def get_by_file_id(file_id: str) -> Analysis | None:
        """Get analysis by file ID"""
        return await Analysis.find_one(Analysis.file_id == file_id)

    @staticmethod
    async def get_by_user(
        user_id: str, skip: int = 0, limit: int = 50
    ) -> list[Analysis]:
        """Get all analyses for a user"""
        return (
            await Analysis.find(Analysis.user_id == user_id)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    @staticmethod
    async def delete(analysis_id: str) -> bool:
        """Delete analysis"""
        analysis = await Analysis.find_one(Analysis.analysis_id == analysis_id)
        if analysis:
            await analysis.delete()
            return True
        return False
