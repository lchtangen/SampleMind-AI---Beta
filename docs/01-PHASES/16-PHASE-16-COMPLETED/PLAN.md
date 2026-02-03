# Phase 16: TUI Integration (Search & Chains)

## Objective
Integrate the newly developed **Semantic Search** (Phase 15) and **Chain Recommender** (Phase 14) functionality into the **Textual TUI**.

## Plan
1.  **Analyze TUI Structure**: Understand `src/samplemind/interfaces/tui/`.
2.  **Implement Search Screen**:
    -   Create `SearchScreen` widget.
    -   Input field for query.
    -   Data table for results.
    -   Connect to `VectorSearchEngine`.
3.  **Implement Chain/Kit Builder Screen**:
    -   Add entry point for Chain Recommender.
    -   Visual representation of the "Chain" (Seed -> Candidate -> Candidate).
4.  **Update Main App**: Register new screens in `app.py`.

## Technical Details
- **Framework**: `textual`
- **Dependencies**: `VectorSearchEngine`, `ChainRecommender`
