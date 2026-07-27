package com.suraksha.ai.screens.callupload

import androidx.compose.ui.res.stringResource
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.suraksha.ai.network.MockApiService
import com.suraksha.ai.network.models.AnalyzeResponse
import kotlinx.coroutines.delay
import androidx.compose.ui.text.style.TextAlign
import kotlinx.coroutines.launch

@Composable
fun CallUploadScreen(
    modifier: Modifier = Modifier,
    onResultReady: (AnalyzeResponse) -> Unit = {}
) {
    var fileName by remember { mutableStateOf<String?>(null) }
    var isProcessing by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()

    val filePicker = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri ->
        if (uri != null) {
            fileName = uri.lastPathSegment ?: "recording.mp3"
        }
    }

    val backgroundGradient = Brush.verticalGradient(
        colors = listOf(Color(0xFF0D47A1), Color(0xFF00897B))
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
            text = "Check a Call Recording",
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "Upload a recording of a suspicious call. We'll transcribe and analyze it for scam patterns.",
            fontSize = 14.sp,
            color = Color.White.copy(alpha = 0.9f),
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(32.dp))

        Button(
            onClick = { filePicker.launch("audio/*") },
            shape = RoundedCornerShape(28.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = Color.White,
                contentColor = Color(0xFF0D47A1)
            ),
            modifier = Modifier.height(56.dp)
        ) {
            Text(text = "Choose an Audio File", fontSize = 16.sp, fontWeight = FontWeight.Bold)
        }

        fileName?.let { name ->
            Spacer(modifier = Modifier.height(16.dp))
            Text(text = "Selected: $name", fontSize = 14.sp, color = Color.White)

            Spacer(modifier = Modifier.height(16.dp))

            if (isProcessing) {
                CircularProgressIndicator(color = Color.White)
                Spacer(modifier = Modifier.height(8.dp))
                Text(text = "Transcribing and analyzing...", fontSize = 14.sp, color = Color.White.copy(alpha = 0.9f))
            } else {
                Button(
                    onClick = {
                        scope.launch {
                            isProcessing = true
                            delay(1500)
                            val fakeTranscribedText = "This is a fake transcribed message from the audio file."
                            val result = MockApiService.analyzeMessage(fakeTranscribedText)
                            isProcessing = false
                            onResultReady(result)
                        }
                    },
                    shape = RoundedCornerShape(28.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color.White.copy(alpha = 0.85f),
                        contentColor = Color(0xFF0D47A1)
                    ),
                    modifier = Modifier.height(56.dp)
                ) {
                    Text(text = "Analyze Recording", fontSize = 16.sp, fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}