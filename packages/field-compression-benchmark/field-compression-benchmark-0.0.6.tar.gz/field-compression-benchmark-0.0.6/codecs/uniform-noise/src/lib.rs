#![cfg_attr(not(test), no_main)]

#[allow(dead_code)]
type UniformNoiseCodec =
    codecs_wasm_logging::LoggingCodec<numcodecs_uniform_noise::UniformNoiseCodec>;

numcodecs_wasm_guest::export_codec!(UniformNoiseCodec);
