package com.suraksha.ai.screens.sms

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.appcompat.app.AppCompatDelegate
import androidx.lifecycle.viewmodel.compose.viewModel
import android.provider.Telephony
import com.suraksha.ai.R
import com.suraksha.ai.network.AnalyzeRequest
import com.suraksha.ai.network.AnalyzeResponse
import com.suraksha.ai.network.RetrofitClient
import com.suraksha.ai.screens.guardian.GuardianViewModel
import kotlinx.coroutines.launch

data class SmsMessage(
    val sender: String,
    val body: String,
    val date: Long
)
data class ScannedSms(val message: SmsMessage, val result: AnalyzeResponse?, val isLoading: Boolean)

@Composable
fun SmsInboxScreen(
    modifier: Modifier = Modifier,
    guardianViewModel: GuardianViewModel = viewModel()
) {
    val context = LocalContext.current
    val unknownSenderLabel = stringResource(R.string.sms_unknown_sender)
    val scope = rememberCoroutineScope()

    val displayLanguage = when (AppCompatDelegate.getApplicationLocales().get(0)?.language) {
        "hi" -> "hindi"
        "gu" -> "gujarati"
        else -> "english"
    }

    var scannedMessages by remember { mutableStateOf<List<ScannedSms>>(emptyList()) }
    var isScanning by remember { mutableStateOf(false) }

    fun loadAndScan() {
        scope.launch {
            isScanning = true

            val cursor = context.contentResolver.query(
                Telephony.Sms.Inbox.CONTENT_URI,
                arrayOf(
                    Telephony.Sms.ADDRESS,
                    Telephony.Sms.BODY,
                    Telephony.Sms.DATE
                ),
                null,
                null,
                "${Telephony.Sms.DATE} DESC"
            )

            val loadedMessages = mutableListOf<SmsMessage>()

            cursor?.use {
                val addressIndex = it.getColumnIndex(Telephony.Sms.ADDRESS)
                val bodyIndex = it.getColumnIndex(Telephony.Sms.BODY)
                val dateIndex = it.getColumnIndex(Telephony.Sms.DATE)

                while (it.moveToNext()) {
                    loadedMessages.add(
                        SmsMessage(
                            sender = it.getString(addressIndex) ?: unknownSenderLabel,
                            body = it.getString(bodyIndex) ?: "",
                            date = it.getLong(dateIndex)
                        )
                    )
                }
            }

            val latest20 = loadedMessages
                .sortedByDescending { it.date }
                .take(20)

            scannedMessages = latest20.map {
                ScannedSms(it, null, isLoading = true)
            }

            latest20.forEachIndexed { index, message ->
                try {
                    val response = RetrofitClient.apiService.analyzeMessage(
                        AnalyzeRequest(
                            text = message.body,
                            language = displayLanguage,
                            output_language = displayLanguage
                        )
                    )

                    scannedMessages = scannedMessages.toMutableList().also {
                        it[index] = ScannedSms(message, response, isLoading = false)
                    }

                    if (response.trigger_alert && guardianViewModel.alertsEnabled) {
                        guardianViewModel.sendAlert(response.alert_message, context) { _, _, _ -> }
                    }

                } catch (e: Exception) {
                    scannedMessages = scannedMessages.toMutableList().also {
                        it[index] = ScannedSms(message, null, isLoading = false)
                    }
                }
            }

            isScanning = false
        }
    }


    androidx.compose.runtime.LaunchedEffect(Unit) {
        loadAndScan()
    }

    val backgroundGradient = Brush.verticalGradient(
        colors = listOf(
            MaterialTheme.colorScheme.primary,
            MaterialTheme.colorScheme.secondary
        )
    )

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(backgroundGradient)
            .padding(24.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = stringResource(R.string.sms_inbox_title),
                fontSize = 28.sp,
                fontWeight = FontWeight.Bold,
                color = Color.White
            )

            Button(
                onClick = { loadAndScan() },
                enabled = !isScanning,
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color.White.copy(alpha = 0.2f),
                    contentColor = Color.White
                )
            ) {
                Text(if (isScanning) "Scanning..." else "Refresh")
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        if (scannedMessages.isEmpty() && !isScanning) {
            Text(
                text = stringResource(R.string.sms_inbox_empty),
                fontSize = 16.sp,
                color = Color.White.copy(alpha = 0.8f)
            )
        } else {
            LazyColumn {
                items(scannedMessages) { scanned ->
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 8.dp)
                            .background(Color.White.copy(alpha = 0.15f), RoundedCornerShape(16.dp))
                            .padding(16.dp)
                    ) {
                        Text(
                            text = scanned.message.sender,
                            fontSize = 15.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = scanned.message.body,
                            fontSize = 14.sp,
                            color = Color.White.copy(alpha = 0.9f)
                        )
                        Spacer(modifier = Modifier.height(8.dp))

                        when {
                            scanned.isLoading -> {
                                CircularProgressIndicator(
                                    color = Color.White,
                                    modifier = Modifier.height(16.dp)
                                )
                            }
                            scanned.result != null -> {
                                val riskColor = when {
                                    scanned.result.risk_percent >= 70 -> Color(0xFFEF5350)
                                    scanned.result.risk_percent >= 40 -> Color(0xFFFFCA28)
                                    else -> Color(0xFF66BB6A)
                                }
                                Text(
                                    text = "${scanned.result.risk_percent}% risk — ${scanned.result.category}",
                                    fontSize = 13.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = riskColor
                                )
                            }
                            else -> {
                                Text(
                                    text = "Couldn't analyze this message.",
                                    fontSize = 13.sp,
                                    color = Color.White.copy(alpha = 0.6f)
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}