// SampleMind AI v7 - MongoDB Performance Configuration
// Run this script to create optimized indexes for production

use samplemind;

// ============================================================================
// Users Collection Indexes
// ============================================================================
db.users.createIndex({ "email": 1 }, { unique: true, name: "idx_users_email" });
db.users.createIndex({ "username": 1 }, { unique: true, name: "idx_users_username" });
db.users.createIndex({ "user_id": 1 }, { unique: true, name: "idx_users_user_id" });
db.users.createIndex({ "created_at": -1 }, { name: "idx_users_created_at" });
db.users.createIndex({ "is_active": 1, "created_at": -1 }, { name: "idx_users_active_created" });

// ============================================================================
// Audio Files Collection Indexes
// ============================================================================
db.audio_files.createIndex({ "_id": 1 }, { name: "idx_audio_files_id" });
db.audio_files.createIndex({ "user_id": 1, "created_at": -1 }, { name: "idx_audio_files_user_created" });
db.audio_files.createIndex({ "file_hash": 1 }, { unique: true, name: "idx_audio_files_hash" });
db.audio_files.createIndex({ "tags": 1 }, { name: "idx_audio_files_tags" });
db.audio_files.createIndex({ "metadata.duration": 1 }, { name: "idx_audio_files_duration" });
db.audio_files.createIndex({ "metadata.sample_rate": 1 }, { name: "idx_audio_files_sample_rate" });
db.audio_files.createIndex({ "user_id": 1, "tags": 1 }, { name: "idx_audio_files_user_tags" });
db.audio_files.createIndex({ "status": 1, "created_at": -1 }, { name: "idx_audio_files_status_created" });

// Text index for full-text search
db.audio_files.createIndex(
  { "filename": "text", "tags": "text", "description": "text" },
  { name: "idx_audio_files_text_search", weights: { filename: 10, tags: 5, description: 1 } }
);

// ============================================================================
// Analyses Collection Indexes
// ============================================================================
db.analyses.createIndex({ "_id": 1 }, { name: "idx_analyses_id" });
db.analyses.createIndex({ "audio_file_id": 1 }, { name: "idx_analyses_audio_file" });
db.analyses.createIndex({ "user_id": 1, "created_at": -1 }, { name: "idx_analyses_user_created" });
db.analyses.createIndex({ "status": 1 }, { name: "idx_analyses_status" });
db.analyses.createIndex({ "user_id": 1, "status": 1 }, { name: "idx_analyses_user_status" });
db.analyses.createIndex({ "audio_file_id": 1, "analysis_type": 1 }, { name: "idx_analyses_file_type" });
db.analyses.createIndex({ "created_at": -1 }, { name: "idx_analyses_created", expireAfterSeconds: 2592000 }); // 30 days TTL

// ============================================================================
// Batch Jobs Collection Indexes
// ============================================================================
db.batch_jobs.createIndex({ "_id": 1 }, { name: "idx_batch_jobs_id" });
db.batch_jobs.createIndex({ "user_id": 1, "created_at": -1 }, { name: "idx_batch_jobs_user_created" });
db.batch_jobs.createIndex({ "status": 1, "created_at": -1 }, { name: "idx_batch_jobs_status_created" });
db.batch_jobs.createIndex({ "user_id": 1, "status": 1 }, { name: "idx_batch_jobs_user_status" });
db.batch_jobs.createIndex({ "completed_at": 1 }, { name: "idx_batch_jobs_completed", expireAfterSeconds: 604800 }); // 7 days TTL

// ============================================================================
// Sessions Collection Indexes (if using session-based auth)
// ============================================================================
db.sessions.createIndex({ "session_id": 1 }, { unique: true, name: "idx_sessions_session_id" });
db.sessions.createIndex({ "user_id": 1 }, { name: "idx_sessions_user_id" });
db.sessions.createIndex({ "expires_at": 1 }, { name: "idx_sessions_expires", expireAfterSeconds: 0 });

// ============================================================================
// Performance Statistics
// ============================================================================
print("✅ MongoDB Indexes Created Successfully!");
print("\n📊 Index Statistics:");
print("---");
db.users.getIndexes().forEach(idx => print(`Users: ${idx.name}`));
print("---");
db.audio_files.getIndexes().forEach(idx => print(`Audio Files: ${idx.name}`));
print("---");
db.analyses.getIndexes().forEach(idx => print(`Analyses: ${idx.name}`));
print("---");
db.batch_jobs.getIndexes().forEach(idx => print(`Batch Jobs: ${idx.name}`));
print("---");
db.sessions.getIndexes().forEach(idx => print(`Sessions: ${idx.name}`));

print("\n🔥 Run this to apply configuration:");
print("mongosh --file config/mongodb-indexes.js");
