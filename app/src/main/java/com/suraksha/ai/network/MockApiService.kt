package com.suraksha.ai.network

import kotlinx.coroutines.delay

object MockApiService {
    suspend fun analyzeMessage(message: String, language: String = "english"): AnalyzeResponse {
        delay(1000)

        return when {
            message.contains("otp", ignoreCase = true) || message.contains("kyc", ignoreCase = true) -> {
                AnalyzeResponse(
                    category = "kyc_scam",
                    risk_percent = 87,
                    explanation = "This message asks for your OTP or KYC details under urgency — a common scam tactic. Never share your OTP or KYC info with anyone.",
                    language = language,
                    trigger_alert = true,
                    alert_message = "High-risk KYC scam detected in a checked message."
                )
            }
            message.contains("loan", ignoreCase = true) -> {
                AnalyzeResponse(
                    category = "loan_scam",
                    risk_percent = 78,
                    explanation = "This message offers an unusually easy loan approval, a common tactic to collect upfront fees or personal information fraudulently.",
                    language = language,
                    trigger_alert = true,
                    alert_message = "High-risk loan scam detected in a checked message."
                )
            }
            message.contains("lottery", ignoreCase = true) || message.contains("won", ignoreCase = true) -> {
                AnalyzeResponse(
                    category = "lottery_scam",
                    risk_percent = 82,
                    explanation = "This message claims you've won a prize you never entered for — a classic lottery scam designed to extract fees or personal details.",
                    language = language,
                    trigger_alert = true,
                    alert_message = "High-risk lottery scam detected in a checked message."
                )
            }
            message.contains("upi", ignoreCase = true) || message.contains("bank", ignoreCase = true) -> {
                AnalyzeResponse(
                    category = "upi_scam",
                    risk_percent = 85,
                    explanation = "This message tries to trick you into approving a fraudulent UPI payment request. Never approve a payment request you don't recognize.",
                    language = language,
                    trigger_alert = true,
                    alert_message = "High-risk UPI scam detected in a checked message."
                )
            }
            message.contains("urgent", ignoreCase = true) -> {
                AnalyzeResponse(
                    category = "phishing",
                    risk_percent = 75,
                    explanation = "This message uses urgency and asks for sensitive information, a common phishing tactic.",
                    language = language,
                    trigger_alert = true,
                    alert_message = "High-risk phishing attempt detected in a checked message."
                )
            }
            else -> {
                AnalyzeResponse(
                    category = "not_scam",
                    risk_percent = 8,
                    explanation = "This message doesn't show common scam patterns. Still, always verify unexpected requests independently.",
                    language = language,
                    trigger_alert = false,
                    alert_message = ""
                )
            }
        }
    }
}