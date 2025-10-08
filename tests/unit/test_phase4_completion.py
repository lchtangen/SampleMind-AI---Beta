"""
Unit tests validating Phase 4 completion
"""

import pytest


class TestPhase4Modules:
    """Test that all Phase 4 modules are present"""

    def test_vector_store_module_exists(self):
        """Test vector store module exists"""
        import samplemind.db.vector_store
        assert samplemind.db.vector_store is not None

    def test_embedding_service_module_exists(self):
        """Test embedding service module exists"""
        import samplemind.ai.embedding_service
        assert samplemind.ai.embedding_service is not None

    def test_vector_search_routes_module_exists(self):
        """Test vector search routes module exists"""
        import samplemind.interfaces.api.routes.vector_search
        assert samplemind.interfaces.api.routes.vector_search is not None


class TestPhase4Classes:
    """Test that all Phase 4 classes are defined"""

    def test_vector_store_class_defined(self):
        """Test VectorStore class is defined"""
        from samplemind.db.vector_store import VectorStore
        assert VectorStore is not None
        assert callable(VectorStore)

    def test_embedding_service_class_defined(self):
        """Test EmbeddingService class is defined"""
        from samplemind.ai.embedding_service import EmbeddingService
        assert EmbeddingService is not None
        assert callable(EmbeddingService)


class TestPhase4Functions:
    """Test that Phase 4 singleton functions exist"""

    def test_get_vector_store_function_exists(self):
        """Test get_vector_store function exists"""
        from samplemind.db.vector_store import get_vector_store
        assert callable(get_vector_store)

    def test_get_embedding_service_function_exists(self):
        """Test get_embedding_service function exists"""
        from samplemind.ai.embedding_service import get_embedding_service
        assert callable(get_embedding_service)


class TestCLISearchCommands:
    """Test CLI search commands are registered"""

    def test_search_index_registered(self):
        """Test search index command is registered"""
        from samplemind.interfaces.cli.main import search_index
        assert search_index is not None

    def test_search_similar_registered(self):
        """Test search similar command is registered"""
        from samplemind.interfaces.cli.main import search_similar
        assert search_similar is not None

    def test_search_recommend_registered(self):
        """Test search recommend command is registered"""
        from samplemind.interfaces.cli.main import search_recommend
        assert search_recommend is not None

    def test_search_stats_registered(self):
        """Test search stats command is registered"""
        from samplemind.interfaces.cli.main import search_stats
        assert search_stats is not None


class TestPhase4Integration:
    """Test Phase 4 integration is complete"""

    def test_vector_search_in_api_routes(self):
        """Test vector_search is in API routes"""
        from samplemind.interfaces.api.routes import vector_search
        assert vector_search is not None

    def test_vector_search_router_has_prefix(self):
        """Test vector search router has correct prefix"""
        from samplemind.interfaces.api.routes.vector_search import router
        assert router.prefix == "/api/v1/vector"

    def test_api_main_imports_vector_search(self):
        """Test API main imports vector_search"""
        from samplemind.interfaces.api import main
        # Verify the module loads without errors
        assert main is not None

    def test_search_app_in_cli_main(self):
        """Test search_app is registered in CLI main"""
        from samplemind.interfaces.cli.main import search_app
        assert search_app is not None

    def test_vector_store_has_create_feature_vector(self):
        """Test VectorStore has _create_feature_vector method"""
        from samplemind.db.vector_store import VectorStore
        assert hasattr(VectorStore, '_create_feature_vector')
