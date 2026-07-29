package com.suraksha.ai.network

data class AnalyzeRequest(
    val text: String,
    val language: String, // "english" | "hindi" | "gujarati" — the message's actual language
    val output_language: String? = null // language the explanation should come back in; defaults to `language` if omitted
)