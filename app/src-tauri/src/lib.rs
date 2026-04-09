use serde::{Deserialize, Serialize};
use tauri::State;
use std::sync::Mutex;

/// Base URL of the FastAPI sidecar (local server)
const API_BASE: &str = "http://127.0.0.1:8000/api/v1";

// ── App state ──────────────────────────────────────────────────────────────

pub struct AppState {
    pub api_token: Mutex<Option<String>>,
}

// ── Shared types ───────────────────────────────────────────────────────────

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct SampleResult {
    pub filename: String,
    pub path: String,
    pub score: Option<f64>,
    pub bpm: Option<f64>,
    pub key: Option<String>,
    pub energy: Option<String>,
    pub genre_labels: Vec<String>,
    pub mood_labels: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct AnalysisResult {
    pub filename: String,
    pub bpm: Option<f64>,
    pub key: Option<String>,
    pub energy: Option<String>,
    pub genre_labels: Vec<String>,
    pub mood_labels: Vec<String>,
    pub analysis_time_ms: Option<f64>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct LibrarySummary {
    pub total_samples: u64,
    pub indexed: bool,
    pub unique_genres: Option<u64>,
    pub unique_keys: Option<u64>,
    pub top_genres: Vec<String>,
    pub top_keys: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GenerateResult {
    pub file_path: String,
    pub prompt: String,
    pub duration_s: f64,
    pub model_used: String,
    pub is_mock: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SyncStatus {
    pub user_id: String,
    pub running: bool,
    pub message: String,
}

// ── Tauri commands ─────────────────────────────────────────────────────────

/// Analyze a local audio file and return metadata
#[tauri::command]
pub async fn analyze_file(
    file_path: String,
    state: State<'_, AppState>,
) -> Result<AnalysisResult, String> {
    let client = reqwest::Client::new();
    let token = state.api_token.lock().unwrap().clone();

    let mut req = client.post(format!("{}/audio/analyze", API_BASE))
        .json(&serde_json::json!({ "file_path": file_path }));

    if let Some(t) = token {
        req = req.bearer_auth(t);
    }

    req.send()
        .await
        .map_err(|e| format!("Request failed: {}", e))?
        .json::<AnalysisResult>()
        .await
        .map_err(|e| format!("Parse error: {}", e))
}

/// Semantic text search over the FAISS index
#[tauri::command]
pub async fn search_semantic(
    query: String,
    limit: Option<u32>,
    state: State<'_, AppState>,
) -> Result<Vec<SampleResult>, String> {
    let client = reqwest::Client::new();
    let token = state.api_token.lock().unwrap().clone();
    let top = limit.unwrap_or(20);

    let url = format!("{}/ai/faiss?q={}&limit={}", API_BASE, urlencoding::encode(&query), top);
    let mut req = client.get(&url);

    if let Some(t) = token {
        req = req.bearer_auth(t);
    }

    let resp = req.send()
        .await
        .map_err(|e| format!("Request failed: {}", e))?;

    // Handle wrapped or direct array response
    let body: serde_json::Value = resp.json().await
        .map_err(|e| format!("Parse error: {}", e))?;

    let results = if let Some(arr) = body.get("results").and_then(|v| v.as_array()) {
        serde_json::from_value(serde_json::Value::Array(arr.clone()))
    } else if body.is_array() {
        serde_json::from_value(body)
    } else {
        Ok(vec![])
    };

    results.map_err(|e| format!("Deserialize error: {}", e))
}

/// Get the library summary (total samples, top genres, etc.)
#[tauri::command]
pub async fn get_library(
    state: State<'_, AppState>,
) -> Result<LibrarySummary, String> {
    let client = reqwest::Client::new();
    let token = state.api_token.lock().unwrap().clone();

    let mut req = client.get(format!("{}/analytics/summary", API_BASE));
    if let Some(t) = token {
        req = req.bearer_auth(t);
    }

    req.send()
        .await
        .map_err(|e| format!("Request failed: {}", e))?
        .json::<LibrarySummary>()
        .await
        .map_err(|e| format!("Parse error: {}", e))
}

/// Push local library state to Supabase cloud sync
#[tauri::command]
pub async fn sync_push(
    user_id: String,
    state: State<'_, AppState>,
) -> Result<SyncStatus, String> {
    let client = reqwest::Client::new();
    let token = state.api_token.lock().unwrap().clone();

    let mut req = client
        .post(format!("{}/sync/push", API_BASE))
        .json(&serde_json::json!({ "user_id": user_id }));

    if let Some(t) = token {
        req = req.bearer_auth(t);
    }

    req.send()
        .await
        .map_err(|e| format!("Request failed: {}", e))?
        .json::<SyncStatus>()
        .await
        .map_err(|e| format!("Parse error: {}", e))
}

/// Generate an audio sample from a text prompt
#[tauri::command]
pub async fn generate_sample(
    prompt: String,
    duration_s: Option<f64>,
    bpm: Option<i32>,
    key: Option<String>,
    state: State<'_, AppState>,
) -> Result<GenerateResult, String> {
    let client = reqwest::Client::new();
    let token = state.api_token.lock().unwrap().clone();

    let mut req = client
        .post(format!("{}/ai/generate", API_BASE))
        .json(&serde_json::json!({
            "prompt": prompt,
            "duration_s": duration_s.unwrap_or(4.0),
            "bpm": bpm,
            "key": key,
        }));

    if let Some(t) = token {
        req = req.bearer_auth(t);
    }

    req.send()
        .await
        .map_err(|e| format!("Request failed: {}", e))?
        .json::<GenerateResult>()
        .await
        .map_err(|e| format!("Parse error: {}", e))
}

/// Store the auth token for API requests (called after Supabase login)
#[tauri::command]
pub async fn set_auth_token(
    token: String,
    state: State<'_, AppState>,
) -> Result<(), String> {
    let mut guard = state.api_token.lock().unwrap();
    *guard = Some(token);
    Ok(())
}

/// Clear the auth token (logout)
#[tauri::command]
pub async fn clear_auth_token(state: State<'_, AppState>) -> Result<(), String> {
    let mut guard = state.api_token.lock().unwrap();
    *guard = None;
    Ok(())
}

// ── App setup ──────────────────────────────────────────────────────────────

pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_http::init())
        .manage(AppState {
            api_token: Mutex::new(None),
        })
        .invoke_handler(tauri::generate_handler![
            analyze_file,
            search_semantic,
            get_library,
            sync_push,
            generate_sample,
            set_auth_token,
            clear_auth_token,
        ])
        .run(tauri::generate_context!())
        .expect("error while running SampleMind desktop app");
}
