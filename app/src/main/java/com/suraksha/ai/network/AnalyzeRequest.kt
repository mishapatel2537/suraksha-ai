package com.suraksha.ai.network
data class AnalyzeRequest(
    val text: String,
    val language: String // "english" | "hindi" | "gujarati"
)