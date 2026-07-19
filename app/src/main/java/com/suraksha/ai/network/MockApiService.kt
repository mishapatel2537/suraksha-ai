package com.suraksha.ai.network

import com.suraksha.ai.network.models.AnalyzeResponse
import kotlinx.coroutines.delay

object MockApiService {
    suspend fun analyzeMessage(message: String): AnalyzeResponse {
        delay(1000)

        return if (message.contains("bank", ignoreCase = true) ||
            message.contains("otp", ignoreCase = true) ||
            message.contains("urgent", ignoreCase = true)
        ) {
            AnalyzeResponse(
                category = "Phishing",
                riskLevel = "High",
                confidence = 87,
                explanation = "This message uses urgency and asks for sensitive information, a common phishing tactic. Never share your OTP or bank details."
            )
        } else {
            AnalyzeResponse(
                category = "Safe",
                riskLevel = "Low",
                confidence = 92,
                explanation = "This message doesn't show common scam patterns. Still, always verify unexpected requests independently."
            )
        }
    }
}