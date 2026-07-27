package com.suraksha.ai.network
data class AnalyzeRequest(
    val message: String,
    val language: String // "english" | "hindi" | "gujarati"
)