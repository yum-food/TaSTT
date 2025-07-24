// Shared configuration schema with types and defaults
const CONFIG_SCHEMA = {
    // String fields
    compute_type: { type: 'select', default: 'float16' },
    language: { type: 'select', default: 'english' },
    model: { type: 'select', default: 'turbo' },
    microphone: { type: 'number', default: 0 },
    user_prompt: { type: 'text', default: 'Use proper punctuation and grammar. Prefer spelled out numbers like one, eleven, twenty, etc. Mm.' },
    keybind: { type: 'text', default: 'ctrl+alt+x' },
    button_hand: { type: 'select', default: 'right' },
    button_type: { type: 'select', default: 'b' },
    
    // Number fields
    gpu_idx: { type: 'number', default: 0 },
    max_speech_duration_s: { type: 'number', default: 10 },
    min_speech_duration_ms: { type: 'number', default: 250 },
    min_silence_duration_ms: { type: 'number', default: 100 },
    reset_after_silence_s: { type: 'number', default: 15 },
    transcription_loop_delay_ms: { type: 'number', default: 100 },
    block_width: { type: 'number', default: 2 },
    num_blocks: { type: 'number', default: 40 },
    rows: { type: 'number', default: 10 },
    cols: { type: 'number', default: 24 },
    beam_size: { type: 'number', default: 5 },
    best_of: { type: 'number', default: 5 },
    volume: { type: 'number', default: 30 },
    
    // Boolean fields (stored as 1/0)
    enable_debug_mode: { type: 'boolean', default: 0 },
    enable_previews: { type: 'boolean', default: 1 },
    save_audio: { type: 'boolean', default: 0 },
    enable_segment_logging: { type: 'boolean', default: 0 },
    use_cpu: { type: 'boolean', default: 0 },
    enable_lowercase_filter: { type: 'boolean', default: 0 },
    enable_uppercase_filter: { type: 'boolean', default: 0 },
    enable_profanity_filter: { type: 'boolean', default: 0 },
    remove_trailing_period: { type: 'boolean', default: 0 },
    reset_on_toggle: { type: 'boolean', default: 0 },
    use_builtin: { type: 'boolean', default: 1 }
};

// Helper to extract just the default values
function getDefaultConfig() {
    const defaults = {};
    for (const [key, schema] of Object.entries(CONFIG_SCHEMA)) {
        defaults[key] = schema.default;
    }
    return defaults;
}

// Export for both CommonJS (main process) and ES modules (renderer)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CONFIG_SCHEMA, getDefaultConfig };
} else {
    window.CONFIG_SCHEMA = CONFIG_SCHEMA;
    window.getDefaultConfig = getDefaultConfig;
} 