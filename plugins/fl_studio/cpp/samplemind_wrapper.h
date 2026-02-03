/**
 * SampleMind AI - FL Studio Plugin Wrapper Header
 * C++ interface for real-time audio analysis and sample management
 *
 * Provides:
 * - Audio processing callbacks
 * - Parameter management
 * - Preset system
 * - State persistence
 * - Python integration
 */

#pragma once

#include <Python.h>
#include <vector>
#include <string>
#include <map>
#include <memory>
#include <queue>
#include <mutex>
#include <thread>

/**
 * Audio processing buffer for sample data
 */
struct AudioBuffer {
    float* left;
    float* right;
    int num_samples;
    int sample_rate;
    bool is_stereo;

    AudioBuffer(int samples, int sr, bool stereo = true)
        : num_samples(samples), sample_rate(sr), is_stereo(stereo) {
        left = new float[samples];
        right = stereo ? new float[samples] : nullptr;
    }

    ~AudioBuffer() {
        delete[] left;
        if (right) delete[] right;
    }
};

/**
 * Parameter definition for FL Studio parameter mapping
 */
struct PluginParameter {
    int id;
    std::string name;
    float min_value;
    float max_value;
    float default_value;
    float current_value;
    bool is_automatable;
    std::string display_format;

    PluginParameter(int _id, const std::string& _name, float min_val, float max_val,
                    float def_val, const std::string& fmt = "%.2f")
        : id(_id), name(_name), min_value(min_val), max_value(max_val),
          default_value(def_val), current_value(def_val),
          is_automatable(true), display_format(fmt) {}
};

/**
 * Analysis result from SampleMind backend
 */
struct AnalysisResult {
    float tempo_bpm;
    std::string key;
    std::string primary_genre;
    std::string mood;
    float energy_level;
    float confidence_score;
    float duration_seconds;
    std::map<std::string, float> extended_features;

    AnalysisResult()
        : tempo_bpm(0.0f), key(""), primary_genre(""), mood(""),
          energy_level(0.0f), confidence_score(0.0f), duration_seconds(0.0f) {}
};

/**
 * Main FL Studio plugin wrapper class
 * Inherits from FL Studio plugin base class (platform-specific)
 */
class SampleMindFLPlugin {
public:
    /**
     * Constructor
     */
    SampleMindFLPlugin();

    /**
     * Destructor
     */
    ~SampleMindFLPlugin();

    // ========================================================================
    // PLUGIN LIFECYCLE
    // ========================================================================

    /**
     * Initialize plugin with sample rate and block size
     */
    void initialize(int sample_rate, int block_size);

    /**
     * Process audio block
     */
    void process(float* left_channel, float* right_channel, int num_samples);

    /**
     * Shutdown and cleanup
     */
    void shutdown();

    /**
     * Reset plugin state
     */
    void reset();

    // ========================================================================
    // PARAMETER MANAGEMENT
    // ========================================================================

    /**
     * Add a parameter to the plugin
     */
    void add_parameter(const PluginParameter& param);

    /**
     * Set parameter value
     */
    bool set_parameter(int param_id, float value);

    /**
     * Get parameter value
     */
    float get_parameter(int param_id);

    /**
     * Get parameter by name
     */
    PluginParameter* get_parameter_by_name(const std::string& name);

    /**
     * Get all parameters
     */
    const std::vector<PluginParameter>& get_all_parameters() const {
        return parameters_;
    }

    // ========================================================================
    // AUDIO ANALYSIS
    // ========================================================================

    /**
     * Analyze current audio buffer
     */
    AnalysisResult analyze_buffer(const AudioBuffer& buffer);

    /**
     * Get current analysis result
     */
    const AnalysisResult& get_current_analysis() const {
        return current_analysis_;
    }

    /**
     * Enable/disable real-time analysis
     */
    void set_analysis_enabled(bool enabled) {
        analysis_enabled_ = enabled;
    }

    // ========================================================================
    // PRESET MANAGEMENT
    // ========================================================================

    /**
     * Save current state as preset
     */
    bool save_preset(int slot, const std::string& name);

    /**
     * Load preset
     */
    bool load_preset(int slot);

    /**
     * Get number of preset slots
     */
    int get_preset_count() const { return preset_slots_.size(); }

    // ========================================================================
    // STATE PERSISTENCE
    // ========================================================================

    /**
     * Get plugin state for saving
     */
    std::string get_state_as_json() const;

    /**
     * Restore plugin state from JSON
     */
    bool restore_state_from_json(const std::string& json_state);

    // ========================================================================
    // UI & DISPLAY
    // ========================================================================

    /**
     * Update UI elements
     */
    void update_ui();

    /**
     * Get analysis display data
     */
    std::string get_analysis_display_data() const;

    /**
     * Get waveform data for visualization
     */
    std::vector<float> get_waveform_data() const;

    // ========================================================================
    // INFORMATION
    // ========================================================================

    /**
     * Get plugin name
     */
    const char* get_plugin_name() const {
        return "SampleMind AI";
    }

    /**
     * Get plugin version
     */
    const char* get_plugin_version() const {
        return "1.0.0";
    }

    /**
     * Get unique plugin ID
     */
    int get_unique_id() const {
        return 0x534D5041;  // "SMPA" in hex
    }

private:
    // ========================================================================
    // PRIVATE MEMBERS
    // ========================================================================

    // Python integration
    PyObject* pPythonModule_;
    PyObject* pPythonPlugin_;
    PyObject* pAnalyzeFunc_;
    PyObject* pProcessFunc_;

    // Plugin state
    int sample_rate_;
    int block_size_;
    bool is_initialized_;
    bool analysis_enabled_;

    // Parameters
    std::vector<PluginParameter> parameters_;
    std::map<int, int> param_id_to_index_;

    // Analysis
    AnalysisResult current_analysis_;
    std::queue<AudioBuffer> analysis_queue_;
    std::mutex analysis_mutex_;
    std::thread analysis_thread_;
    bool analysis_thread_running_;

    // Presets
    struct Preset {
        std::string name;
        std::map<int, float> parameter_values;
    };
    std::vector<Preset> preset_slots_;

    // Waveform display data
    std::vector<float> waveform_data_;
    std::mutex waveform_mutex_;

    // ========================================================================
    // PRIVATE METHODS
    // ========================================================================

    /**
     * Initialize Python integration
     */
    bool initialize_python();

    /**
     * Cleanup Python integration
     */
    void cleanup_python();

    /**
     * Worker thread for background analysis
     */
    void analysis_worker_thread();

    /**
     * Process audio buffer to numpy array
     */
    PyObject* audio_to_numpy(const AudioBuffer& buffer);

    /**
     * Extract numpy data back to buffer
     */
    bool numpy_to_audio(PyObject* numpy_array, AudioBuffer& buffer);

    /**
     * Convert analysis result from Python dict
     */
    void parse_analysis_result(PyObject* py_dict);

    /**
     * Extract waveform from buffer
     */
    void extract_waveform(const AudioBuffer& buffer);
};
