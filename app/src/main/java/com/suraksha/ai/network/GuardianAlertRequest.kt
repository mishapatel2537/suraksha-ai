package com.suraksha.ai.network

data class GuardianAlertRequest(
    val message_id: String,
    val category: String,
    val risk_percent: Int,
    val guardian_contact: String
)