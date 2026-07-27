package com.suraksha.ai.network
data class AnalyzeResponse(
    val category: String,       // kyc_scam | loan_scam | lottery_scam | upi_scam |
    // phishing | impersonation_digital_arrest |
    // impersonation_blackmail | not_scam | unknown
    val risk_percent: Int,      // 0-100
    val explanation: String,
    val language: String,
    val trigger_alert: Boolean,
    val alert_message: String
)