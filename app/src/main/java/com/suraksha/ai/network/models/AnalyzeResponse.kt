package com.suraksha.ai.network.models

data class AnalyzeResponse(
    val category: String,
    val riskPercent: Int,
    val explanation: String,
    val language: String = "english",
    val triggerAlert: Boolean = false,
    val alertMessage: String = ""
) {
    val riskLevel: String
        get() = when {
            riskPercent >= 70 -> "High"
            riskPercent >= 40 -> "Medium"
            else -> "Low"
        }
}