#![cfg_attr(not(test), no_main)]

#[allow(dead_code)]
type LinearQuantizeCodec =
    codecs_wasm_logging::LoggingCodec<numcodecs_linear_quantize::LinearQuantizeCodec>;

numcodecs_wasm_guest::export_codec!(LinearQuantizeCodec);
