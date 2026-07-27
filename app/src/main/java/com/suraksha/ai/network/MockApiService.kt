package com.suraksha.ai.network

import com.suraksha.ai.network.models.AnalyzeResponse
import kotlinx.coroutines.delay

object MockApiService {
    suspend fun analyzeMessage(message: String): AnalyzeResponse {
        delay(1000)

        return when {
            message.contains("otp", ignoreCase = true) || message.contains("kyc", ignoreCase = true) -> {
                AnalyzeResponse(
                    category = "kyc_scam",
                    riskPercent = 87,
                    explanation = "This message asks for your OTP or KYC details under urgency — a common scam tactic. Never share your OTP or KYC info with anyone.",
                    triggerAlert = true,
                    alertMessage = "High-risk KYC scam detected in a checked message."
                )
            }
            message.contains("loan", ignoreCase = true) -> {
                AnalyzeResponse(
                    category = "loan_scam",
                    riskPercent = 78,
                    explanation = "This message offers an unusually easy loan approval, a common tactic to collect upfront fees or personal information fraudulently.",
                    triggerAlert = true,
                    alertMessage = "High-risk loan scam detected in a checked message."
                )
            }
            message.contains("lottery", ignoreCase = true) || message.contains("won", ignoreCase = true) -> {
                AnalyzeResponse(
                    category = "lottery_scam",
                    riskPercent = 82,
                    explanation = "This message claims you've won a prize you never entered for — a classic lottery scam designed to extract fees or personal details.",
                    triggerAlert = true,
                    alertMessage = "High-risk lottery scam detected in a checked message."
                )
            }
            message.contains("upi", ignoreCase = true) || message.contains("bank", ignoreCase = true) -> {
                AnalyzeResponse(
                    category = "upi_scam",
                    riskPercent = 85,
                    explanation = "This message tries to trick you into approving a fraudulent UPI payment request. Never approve a payment request you don't recognize.",
                    triggerAlert = true,
                    alertMessage = "High-risk UPI scam detected in a checked message."
                )
            }
            message.contains("urgent", ignoreCase = true) -> {
                AnalyzeResponse(
                    category = "phishing",
                    riskPercent = 75,
                    explanation = "This message uses urgency and asks for sensitive information, a common phishing tactic.",
                    triggerAlert = true,
                    alertMessage = "High-risk phishing attempt detected in a checked message."
                )
            }
            else -> {
                AnalyzeResponse(
                    category = "not_scam",
                    riskPercent = 8,
                    explanation = "This message doesn't show common scam patterns. Still, always verify unexpected requests independently.",
                    triggerAlert = false,
                    alertMessage = ""
                )
            }
        }
    }
}