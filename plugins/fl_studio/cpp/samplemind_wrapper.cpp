/**
 * SampleMind AI - FL Studio Plugin Wrapper Implementation
 * Core audio processing and Python integration
 */

#include "samplemind_wrapper.h"
#include <iostream>
#include <cstring>
#include <chrono>
#include <numpy/arrayobject.h>

// ============================================================================
// CONSTRUCTOR & DESTRUCTOR
// ============================================================================

SampleMindFLPlugin::SampleMindFLPlugin()
    : pPythonModule_(nullptr),
      pPythonPlugin_(nullptr),
      pAnalyzeFunc_(nullptr),
      pProcessFunc_(nullptr),
      sample_rate_(44100),
      block_size_(512),
      is_initialized_(false),
      analysis_enabled_(true),
      analysis_thread_running_(false) {

    // Initialize Python-related members
    import_array();  // Initialize numpy C API
}

SampleMindFLPlugin::~SampleMindFLPlugin() {
    shutdown();
}

// ============================================================================
// PLUGIN LIFECYCLE
// ============================================================================

void SampleMindFLPlugin::initialize(int sample_rate, int block_size) {
    if (is_initialized_) {
        return;  // Already initialized
    }

    sample_rate_ = sample_rate;
    block_size_ = block_size;

    // Initialize Python
    if (!initialize_python()) {
        std::cerr << "Failed to initialize Python" << std::endl;
        return;
    }

    // Initialize preset slots (128 slots)
    preset_slots_.resize(128);

    // Start analysis worker thread
    analysis_thread_running_ = true;
    analysis_thread_ = std::thread(&SampleMindFLPlugin::analysis_worker_thread, this);

    is_initialized_ = true;
    std::cout << "SampleMind FL Studio plugin initialized" << std::endl;
}

void SampleMindFLPlugin::process(float* left_channel, float* right_channel, int num_samples) {
    if (!is_initialized_) {
        return;
    }

    // Create audio buffer
    AudioBuffer buffer(num_samples, sample_rate_, true);
    std::memcpy(buffer.left, left_channel, num_samples * sizeof(float));
    std::memcpy(buffer.right, right_channel, num_samples * sizeof(float));

    // Queue buffer for analysis if enabled
    if (analysis_enabled_) {
        {
            std::lock_guard<std::mutex> lock(analysis_mutex_);
            analysis_queue_.push(buffer);
        }
    }

    // Extract waveform for display
    if (num_samples % 64 == 0) {  // Update display every 64th block
        extract_waveform(buffer);
    }
}

void SampleMindFLPlugin::shutdown() {
    // Stop analysis thread
    analysis_thread_running_ = false;
    if (analysis_thread_.joinable()) {
        analysis_thread_.join();
    }

    // Cleanup Python
    cleanup_python();

    is_initialized_ = false;
    std::cout << "SampleMind FL Studio plugin shutdown" << std::endl;
}

void SampleMindFLPlugin::reset() {
    // Clear analysis queue
    {
        std::lock_guard<std::mutex> lock(analysis_mutex_);
        while (!analysis_queue_.empty()) {
            analysis_queue_.pop();
        }
    }

    // Reset parameters to defaults
    for (auto& param : parameters_) {
        param.current_value = param.default_value;
    }

    // Clear analysis result
    current_analysis_ = AnalysisResult();
}

// ============================================================================
// PARAMETER MANAGEMENT
// ============================================================================

void SampleMindFLPlugin::add_parameter(const PluginParameter& param) {
    parameters_.push_back(param);
    param_id_to_index_[param.id] = parameters_.size() - 1;
}

bool SampleMindFLPlugin::set_parameter(int param_id, float value) {
    auto it = param_id_to_index_.find(param_id);
    if (it == param_id_to_index_.end()) {
        return false;  // Parameter not found
    }

    int index = it->second;
    PluginParameter& param = parameters_[index];

    // Clamp value to valid range
    value = std::max(param.min_value, std::min(value, param.max_value));
    param.current_value = value;

    return true;
}

float SampleMindFLPlugin::get_parameter(int param_id) {
    auto it = param_id_to_index_.find(param_id);
    if (it == param_id_to_index_.end()) {
        return 0.0f;  // Parameter not found
    }

    return parameters_[it->second].current_value;
}

PluginParameter* SampleMindFLPlugin::get_parameter_by_name(const std::string& name) {
    for (auto& param : parameters_) {
        if (param.name == name) {
            return &param;
        }
    }
    return nullptr;
}

// ============================================================================
// AUDIO ANALYSIS
// ============================================================================

AnalysisResult SampleMindFLPlugin::analyze_buffer(const AudioBuffer& buffer) {
    if (!pAnalyzeFunc_) {
        return AnalysisResult();
    }

    // Convert audio to numpy array
    PyObject* audio_array = audio_to_numpy(buffer);
    if (!audio_array) {
        return AnalysisResult();
    }

    // Call Python analysis function
    PyObject* args = PyTuple_Pack(1, audio_array);
    PyObject* result = PyObject_CallObject(pAnalyzeFunc_, args);

    if (result && PyDict_Check(result)) {
        parse_analysis_result(result);
    }

    // Cleanup
    Py_DECREF(audio_array);
    Py_DECREF(args);
    if (result) Py_DECREF(result);

    return current_analysis_;
}

// ============================================================================
// PRESET MANAGEMENT
// ============================================================================

bool SampleMindFLPlugin::save_preset(int slot, const std::string& name) {
    if (slot < 0 || slot >= static_cast<int>(preset_slots_.size())) {
        return false;  // Invalid slot
    }

    Preset& preset = preset_slots_[slot];
    preset.name = name;

    // Save current parameter values
    for (const auto& param : parameters_) {
        preset.parameter_values[param.id] = param.current_value;
    }

    std::cout << "Preset '" << name << "' saved to slot " << slot << std::endl;
    return true;
}

bool SampleMindFLPlugin::load_preset(int slot) {
    if (slot < 0 || slot >= static_cast<int>(preset_slots_.size())) {
        return false;  // Invalid slot
    }

    const Preset& preset = preset_slots_[slot];
    if (preset.name.empty()) {
        return false;  // Slot is empty
    }

    // Restore parameter values
    for (const auto& [param_id, value] : preset.parameter_values) {
        set_parameter(param_id, value);
    }

    std::cout << "Preset '" << preset.name << "' loaded from slot " << slot << std::endl;
    return true;
}

// ============================================================================
// STATE PERSISTENCE
// ============================================================================

std::string SampleMindFLPlugin::get_state_as_json() const {
    // This would serialize to JSON using a library like nlohmann/json
    // For now, return a simplified version
    std::string json = "{\n";
    json += "  \"plugin_name\": \"SampleMind AI\",\n";
    json += "  \"plugin_version\": \"1.0.0\",\n";
    json += "  \"parameters\": {\n";

    for (size_t i = 0; i < parameters_.size(); ++i) {
        const auto& param = parameters_[i];
        json += "    \"" + param.name + "\": " + std::to_string(param.current_value);
        if (i < parameters_.size() - 1) {
            json += ",\n";
        } else {
            json += "\n";
        }
    }

    json += "  }\n";
    json += "}\n";

    return json;
}

bool SampleMindFLPlugin::restore_state_from_json(const std::string& json_state) {
    // This would parse JSON state
    // For now, just acknowledge restoration
    std::cout << "State restoration requested (JSON parsing needed)" << std::endl;
    return true;
}

// ============================================================================
// UI & DISPLAY
// ============================================================================

void SampleMindFLPlugin::update_ui() {
    // Called periodically to update UI elements
    // Update analysis display, waveform, etc.
}

std::string SampleMindFLPlugin::get_analysis_display_data() const {
    std::string data = "Analysis Results:\n";
    data += "  BPM: " + std::to_string(current_analysis_.tempo_bpm) + "\n";
    data += "  Key: " + current_analysis_.key + "\n";
    data += "  Genre: " + current_analysis_.primary_genre + "\n";
    data += "  Mood: " + current_analysis_.mood + "\n";
    data += "  Energy: " + std::to_string(current_analysis_.energy_level) + "\n";
    data += "  Confidence: " + std::to_string(current_analysis_.confidence_score) + "\n";

    return data;
}

std::vector<float> SampleMindFLPlugin::get_waveform_data() const {
    std::lock_guard<std::mutex> lock(waveform_mutex_);
    return waveform_data_;
}

// ============================================================================
// PRIVATE METHODS
// ============================================================================

bool SampleMindFLPlugin::initialize_python() {
    // Initialize Python interpreter if not already initialized
    if (!Py_IsInitialized()) {
        Py_Initialize();
    }

    if (!Py_IsInitialized()) {
        std::cerr << "Failed to initialize Python interpreter" << std::endl;
        return false;
    }

    // Import SampleMind module
    PyObject* module_name = PyUnicode_DecodeFSDefault("samplemind.core.engine.audio_engine");
    pPythonModule_ = PyImport_Import(module_name);
    Py_DECREF(module_name);

    if (!pPythonModule_) {
        PyErr_Print();
        std::cerr << "Failed to import SampleMind module" << std::endl;
        return false;
    }

    // Get the AudioEngine class
    PyObject* audio_engine_class = PyObject_GetAttrString(pPythonModule_, "AudioEngine");
    if (!audio_engine_class || !PyCallable_Check(audio_engine_class)) {
        std::cerr << "Cannot find AudioEngine class" << std::endl;
        Py_XDECREF(audio_engine_class);
        return false;
    }

    // Instantiate AudioEngine
    pPythonPlugin_ = PyObject_CallObject(audio_engine_class, nullptr);
    Py_DECREF(audio_engine_class);

    if (!pPythonPlugin_) {
        PyErr_Print();
        std::cerr << "Failed to instantiate AudioEngine" << std::endl;
        return false;
    }

    // Get analysis method
    pAnalyzeFunc_ = PyObject_GetAttrString(pPythonPlugin_, "analyze_full");
    if (!pAnalyzeFunc_ || !PyCallable_Check(pAnalyzeFunc_)) {
        std::cerr << "Cannot find analyze_full method" << std::endl;
        Py_XDECREF(pAnalyzeFunc_);
        return false;
    }

    std::cout << "Python integration initialized successfully" << std::endl;
    return true;
}

void SampleMindFLPlugin::cleanup_python() {
    Py_XDECREF(pAnalyzeFunc_);
    Py_XDECREF(pProcessFunc_);
    Py_XDECREF(pPythonPlugin_);
    Py_XDECREF(pPythonModule_);

    if (Py_IsInitialized()) {
        Py_Finalize();
    }
}

void SampleMindFLPlugin::analysis_worker_thread() {
    // Background thread for audio analysis
    while (analysis_thread_running_) {
        // Check if there's work in the queue
        AudioBuffer buffer(block_size_, sample_rate_, true);

        {
            std::lock_guard<std::mutex> lock(analysis_mutex_);
            if (analysis_queue_.empty()) {
                // Sleep briefly to avoid busy-waiting
                std::this_thread::sleep_for(std::chrono::milliseconds(10));
                continue;
            }

            buffer = analysis_queue_.front();
            analysis_queue_.pop();
        }

        // Analyze the buffer
        analyze_buffer(buffer);
    }
}

PyObject* SampleMindFLPlugin::audio_to_numpy(const AudioBuffer& buffer) {
    // Create numpy array from audio buffer
    npy_intp dims[2] = {buffer.is_stereo ? 2 : 1, buffer.num_samples};
    PyObject* array = PyArray_SimpleNew(2, dims, NPY_FLOAT32);

    if (!array) {
        return nullptr;
    }

    float* data = (float*)PyArray_DATA((PyArrayObject*)array);

    // Copy left channel
    std::memcpy(data, buffer.left, buffer.num_samples * sizeof(float));

    // Copy right channel if stereo
    if (buffer.is_stereo && buffer.right) {
        std::memcpy(data + buffer.num_samples, buffer.right, buffer.num_samples * sizeof(float));
    }

    return array;
}

bool SampleMindFLPlugin::numpy_to_audio(PyObject* numpy_array, AudioBuffer& buffer) {
    if (!PyArray_Check(numpy_array)) {
        return false;
    }

    float* data = (float*)PyArray_DATA((PyArrayObject*)numpy_array);
    int num_samples = PyArray_SIZE((PyArrayObject*)numpy_array);

    // Copy data back to buffer
    std::memcpy(buffer.left, data, std::min(num_samples, buffer.num_samples) * sizeof(float));

    return true;
}

void SampleMindFLPlugin::parse_analysis_result(PyObject* py_dict) {
    // Extract values from Python dictionary
    PyObject* value;

    // Extract BPM
    value = PyDict_GetItemString(py_dict, "tempo_bpm");
    if (value && PyFloat_Check(value)) {
        current_analysis_.tempo_bpm = (float)PyFloat_AsDouble(value);
    }

    // Extract key
    value = PyDict_GetItemString(py_dict, "key");
    if (value && PyUnicode_Check(value)) {
        current_analysis_.key = PyUnicode_AsUTF8(value);
    }

    // Extract genre
    value = PyDict_GetItemString(py_dict, "primary_genre");
    if (value && PyUnicode_Check(value)) {
        current_analysis_.primary_genre = PyUnicode_AsUTF8(value);
    }

    // Extract mood
    value = PyDict_GetItemString(py_dict, "mood");
    if (value && PyUnicode_Check(value)) {
        current_analysis_.mood = PyUnicode_AsUTF8(value);
    }

    // Extract energy
    value = PyDict_GetItemString(py_dict, "energy_level");
    if (value && PyFloat_Check(value)) {
        current_analysis_.energy_level = (float)PyFloat_AsDouble(value);
    }

    // Extract confidence
    value = PyDict_GetItemString(py_dict, "confidence_score");
    if (value && PyFloat_Check(value)) {
        current_analysis_.confidence_score = (float)PyFloat_AsDouble(value);
    }
}

void SampleMindFLPlugin::extract_waveform(const AudioBuffer& buffer) {
    // Extract waveform data for visualization
    // Downsample to ~1000 samples for display
    int display_samples = 1000;
    int step = std::max(1, buffer.num_samples / display_samples);

    std::vector<float> waveform;
    waveform.reserve(display_samples);

    for (int i = 0; i < buffer.num_samples; i += step) {
        float sample = buffer.left[i];
        if (buffer.is_stereo && buffer.right) {
            // Average stereo channels
            sample = (sample + buffer.right[i]) / 2.0f;
        }
        waveform.push_back(sample);
    }

    // Update waveform data
    {
        std::lock_guard<std::mutex> lock(waveform_mutex_);
        waveform_data_ = waveform;
    }
}
