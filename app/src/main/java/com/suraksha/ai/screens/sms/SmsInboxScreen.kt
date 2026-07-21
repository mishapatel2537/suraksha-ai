package com.suraksha.ai.screens.sms


import android.provider.Telephony
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

data class SmsMessage(val sender: String, val body: String)

@Composable
fun SmsInboxScreen(modifier: Modifier = Modifier) {
    val context = LocalContext.current

    var messages by remember { mutableStateOf<List<SmsMessage>>(emptyList()) }

    androidx.compose.runtime.LaunchedEffect(Unit) {
        val cursor = context.contentResolver.query(
            Telephony.Sms.Inbox.CONTENT_URI,
            arrayOf(Telephony.Sms.ADDRESS, Telephony.Sms.BODY),
            null,
            null,
            Telephony.Sms.DATE + " DESC"
        )

        val loadedMessages = mutableListOf<SmsMessage>()
        cursor?.use {
            val addressIndex = it.getColumnIndex(Telephony.Sms.ADDRESS)
            val bodyIndex = it.getColumnIndex(Telephony.Sms.BODY)
            while (it.moveToNext() && loadedMessages.size < 50) {
                loadedMessages.add(
                    SmsMessage(
                        sender = it.getString(addressIndex) ?: "Unknown",
                        body = it.getString(bodyIndex) ?: ""
                    )
                )
            }
        }
        messages = loadedMessages
    }

    val backgroundGradient = Brush.verticalGradient(
        colors = listOf(Color(0xFF0D47A1), Color(0xFF00897B))
    )

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(backgroundGradient)
            .padding(24.dp)
    ) {
        Text(
            text = "Inbox",
            fontSize = 28.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White
        )

        Spacer(modifier = Modifier.height(16.dp))

        if (messages.isEmpty()) {
            Text(
                text = "No messages found.",
                fontSize = 16.sp,
                color = Color.White.copy(alpha = 0.8f)
            )
        } else {
            LazyColumn {
                items(messages) { message ->
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 8.dp)
                            .background(Color.White.copy(alpha = 0.15f), RoundedCornerShape(16.dp))
                            .padding(16.dp)
                    ) {
                        Text(
                            text = message.sender,
                            fontSize = 15.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = message.body,
                            fontSize = 14.sp,
                            color = Color.White.copy(alpha = 0.9f)
                        )
                    }
                }
            }
        }
    }
}