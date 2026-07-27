package com.suraksha.ai.screens.settings
import androidx.compose.ui.res.stringResource
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Divider
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.suraksha.ai.components.LanguageToggle

@Composable
fun SettingsScreen(modifier: Modifier = Modifier) {
    var notificationsEnabled by remember { mutableStateOf(true) }
    var darkModeEnabled by remember { mutableStateOf(false) }
    var dataCleared by remember { mutableStateOf(false) }

    val backgroundGradient = Brush.verticalGradient(
        colors = listOf(Color(0xFF0D47A1), Color(0xFF00897B))
    )

    val switchColors = SwitchDefaults.colors(
        checkedThumbColor = Color.White,
        checkedTrackColor = Color(0xFF00897B),
        uncheckedThumbColor = Color.White,
        uncheckedTrackColor = Color.White.copy(alpha = 0.3f)
    )

    val dividerColor = Color.White.copy(alpha = 0.25f)

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(backgroundGradient)
            .padding(24.dp)
    ) {
        Text(
            text = "Settings",
            fontSize = 26.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White
        )

        Spacer(modifier = Modifier.height(20.dp))
        Divider(color = dividerColor)
        Spacer(modifier = Modifier.height(20.dp))

        Text(text = "Language", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color.White)
        Spacer(modifier = Modifier.height(8.dp))
        LanguageToggle()

        Spacer(modifier = Modifier.height(20.dp))
        Divider(color = dividerColor)
        Spacer(modifier = Modifier.height(20.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(text = "Guardian Alerts", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color.White)
                Text(
                    text = "Alert my family if a high-risk scam is detected",
                    fontSize = 12.sp,
                    color = Color.White.copy(alpha = 0.8f)
                )
            }
            Switch(checked = notificationsEnabled, onCheckedChange = { notificationsEnabled = it }, colors = switchColors)
        }

        Spacer(modifier = Modifier.height(20.dp))
        Divider(color = dividerColor)
        Spacer(modifier = Modifier.height(20.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(text = "Dark Mode", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color.White)
            Switch(checked = darkModeEnabled, onCheckedChange = { darkModeEnabled = it }, colors = switchColors)
        }

        Spacer(modifier = Modifier.height(20.dp))
        Divider(color = dividerColor)
        Spacer(modifier = Modifier.height(20.dp))

        Text(text = "Data", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color.White)
        Spacer(modifier = Modifier.height(8.dp))
        Button(
            onClick = { dataCleared = true },
            shape = RoundedCornerShape(20.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = Color.White.copy(alpha = 0.15f),
                contentColor = Color.White
            )
        ) {
            Text("Clear Activity Data")
        }
        if (dataCleared) {
            Spacer(modifier = Modifier.height(6.dp))
            Text(text = "✓ Activity data cleared", fontSize = 12.sp, color = Color(0xFFA5D6A7))
        }

        Spacer(modifier = Modifier.height(20.dp))
        Divider(color = dividerColor)
        Spacer(modifier = Modifier.height(20.dp))

        Text(text = "About Suraksha", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color.White)
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = "Suraksha helps you detect scam calls, fake UPI requests, phishing, and loan scams. Paste or share a suspicious message, scan your SMS inbox, or upload a call recording — Suraksha analyzes it and shows a risk score with a simple explanation in your own chosen language. If a high-risk scam is detected, your Family Guardian can be alerted automatically.",
            fontSize = 14.sp,
            color = Color.White.copy(alpha = 0.9f)
        )

        Spacer(modifier = Modifier.height(16.dp))
        Text(text = "Suraksha v1.0", fontSize = 12.sp, color = Color.White.copy(alpha = 0.6f))
    }
}