package com.suraksha.ai.screens.result
import androidx.compose.ui.res.stringResource
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.suraksha.ai.R
import com.suraksha.ai.network.models.AnalyzeResponse

@Composable
fun ResultScreen(
    result: AnalyzeResponse,
    modifier: Modifier = Modifier
) {
    val backgroundGradient = Brush.verticalGradient(
        colors = listOf(
            Color(0xFF0D47A1),
            Color(0xFF00897B)
        )
    )

    val riskColor = when {
        result.riskPercent >= 70 -> Color(0xFFE53935)
        result.riskPercent >= 40 -> Color(0xFFFFA726)
        else -> Color(0xFF43A047)
    }

    val riskLabel = when {
        result.riskPercent >= 70 -> stringResource(R.string.risk_high)
        result.riskPercent >= 40 -> stringResource(R.string.risk_medium)
        else -> stringResource(R.string.risk_low)
    }

    val categoryLabel = when (result.category) {
        "kyc_scam" -> stringResource(R.string.category_kyc_scam)
        "loan_scam" -> stringResource(R.string.category_loan_scam)
        "lottery_scam" -> stringResource(R.string.category_lottery_scam)
        "upi_scam" -> stringResource(R.string.category_upi_scam)
        "phishing" -> stringResource(R.string.category_phishing)
        "impersonation_digital_arrest" -> stringResource(R.string.category_impersonation_digital_arrest)
        "impersonation_blackmail" -> stringResource(R.string.category_impersonation_blackmail)
        "not_scam" -> stringResource(R.string.category_not_scam)
        else -> stringResource(R.string.category_unknown)
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(backgroundGradient)
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .background(Color.White.copy(alpha = 0.15f), RoundedCornerShape(20.dp))
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "$riskLabel ${stringResource(R.string.risk_suffix)}",
                fontSize = 24.sp,
                fontWeight = FontWeight.ExtraBold,
                color = riskColor
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = stringResource(R.string.confidence_label, result.riskPercent),
                fontSize = 16.sp,
                color = Color.White.copy(alpha = 0.9f)
            )

            Spacer(modifier = Modifier.height(16.dp))

            Text(
                text = stringResource(R.string.category_label, categoryLabel),
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                color = Color.White
            )

            Spacer(modifier = Modifier.height(16.dp))

            Text(
                text = result.explanation,
                fontSize = 14.sp,
                color = Color.White.copy(alpha = 0.9f)
            )
        }
    }
}