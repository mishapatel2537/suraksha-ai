package com.suraksha.ai.screens.messagecheck
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.OutlinedTextField
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
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Box
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.ui.res.stringResource
import com.suraksha.ai.R
import androidx.compose.ui.platform.LocalContext
import androidx.appcompat.app.AppCompatDelegate
import com.suraksha.ai.screens.guardian.GuardianViewModel

@Composable
fun MessageInputScreen(
    modifier: Modifier = Modifier,
    initialText: String = "",
    viewModel: MessageInputViewModel = viewModel(),
    guardianViewModel: GuardianViewModel,
    onCheckMessageClick: () -> Unit = {}
) {
    val context = LocalContext.current
    val currentLanguage = when (AppCompatDelegate.getApplicationLocales().get(0)?.language) {
        "hi" -> "hindi"
        "gu" -> "gujarati"
        else -> "english"
    }

    androidx.compose.runtime.LaunchedEffect(Unit) {
        if (viewModel.messageText.isEmpty() && initialText.isNotEmpty()) {
            viewModel.onMessageTextChange(initialText)
        }
    }

    val backgroundGradient = Brush.verticalGradient(
        colors = listOf(
            Color(0xFF0D47A1),
            Color(0xFF00897B)
        )
    )

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(backgroundGradient)
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = stringResource(R.string.check_message_title),
            fontSize = 28.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White
        )

        Spacer(modifier = Modifier.height(24.dp))

        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(Color.White.copy(alpha = 0.15f), RoundedCornerShape(20.dp))
                .border(2.dp, Color.White.copy(alpha = 0.6f), RoundedCornerShape(20.dp))
                .padding(4.dp)
        ) {
            OutlinedTextField(
                value = viewModel.messageText,
                onValueChange = { viewModel.onMessageTextChange(it) },
                label = { Text(stringResource(R.string.message_input_label), fontFamily = FontFamily.Serif) },
                modifier = Modifier.fillMaxWidth(),
                minLines = 5,
                shape = RoundedCornerShape(16.dp),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = Color.Transparent,
                    unfocusedBorderColor = Color.Transparent,
                    focusedLabelColor = Color.White,
                    unfocusedLabelColor = Color.White.copy(alpha = 0.8f),
                    focusedTextColor = Color.White,
                    unfocusedTextColor = Color.White,
                    cursorColor = Color.White
                ),
                textStyle = androidx.compose.ui.text.TextStyle(
                    fontFamily = FontFamily.Serif,
                    fontSize = 16.sp
                )
            )
        }

        Spacer(modifier = Modifier.height(24.dp))
        Button(
            onClick = {
                viewModel.checkMessage(language = currentLanguage) {
                    val response = viewModel.result
                    if (response?.trigger_alert == true && guardianViewModel.alertsEnabled) {
                        guardianViewModel.sendAlert(response.alert_message, context) { _, _, _ -> }
                    }
                    onCheckMessageClick()
                }
            },
            enabled = !viewModel.isLoading,   // ADD THIS
            shape = RoundedCornerShape(28.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = Color.White,
                contentColor = Color(0xFF0D47A1)
            ),
            modifier = Modifier.height(56.dp)
        ) {
            Text(text = stringResource(R.string.check_message_submit), fontSize = 16.sp, fontWeight = FontWeight.Bold)
        }
        if (viewModel.isLoading) {
            Spacer(modifier = Modifier.height(16.dp))
            androidx.compose.material3.CircularProgressIndicator(color = Color.White)
        }
    }
}