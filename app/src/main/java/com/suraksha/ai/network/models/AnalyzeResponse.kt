package com.suraksha.ai.network.models


data class AnalyzeResponse(
    val category: String,
    val riskLevel: String,
    val confidence: Int,
    val explanation: String
)