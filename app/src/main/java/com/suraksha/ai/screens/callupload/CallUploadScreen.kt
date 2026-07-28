package com.suraksha.ai.screens.callupload

import android.net.Uri
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
import androidx.compose.ui.res.stringResource
import com.suraksha.ai.R
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.suraksha.ai.network.AnalyzeResponse
import com.suraksha.ai.network.RetrofitClient
import kotlinx.coroutines.launch
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File

@Composable
fun CallUploadScreen(
    modifier: Modifier = Modifier,
    onResultReady: (AnalyzeResponse) -> Unit = {}
) {
    val context = LocalContext.current
    var fileName by remember { mutableStateOf<String?>(null) }
    var selectedUri by remember { mutableStateOf<Uri?>(null) }
    var isProcessing by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()

    val filePicker = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri ->
        if (uri != null) {
            fileName = uri.lastPathSegment ?: "recording.mp3"
            selectedUri = uri
            errorMessage = null
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
            text = stringResource(R.string.call_upload_title),
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = stringResource(R.string.call_upload_description),
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
            Text(text = stringResource(R.string.choose_audio_file), fontSize = 16.sp, fontWeight = FontWeight.Bold)
        }

        errorMessage?.let { msg ->
            Spacer(modifier = Modifier.height(12.dp))
            Text(text = msg, fontSize = 13.sp, color = Color(0xFFEF9A9A), textAlign = TextAlign.Center)
        }

        fileName?.let { name ->
            Spacer(modifier = Modifier.height(16.dp))
            Text(text = stringResource(R.string.selected_file, name), fontSize = 14.sp, color = Color.White)

            Spacer(modifier = Modifier.height(16.dp))

            if (isProcessing) {
                CircularProgressIndicator(color = Color.White)
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = stringResource(R.string.processing_audio),
                    fontSize = 14.sp,
                    color = Color.White.copy(alpha = 0.9f)
                )
            } else {
                Button(
                    onClick = {
                        val uri = selectedUri ?: return@Button
                        scope.launch {
                            isProcessing = true
                            errorMessage = null
                            try {
                                // Copy the picked content:// URI to a real file Retrofit/OkHttp can read
                                val inputStream = context.contentResolver.openInputStream(uri)
                                    ?: throw IllegalStateException("Could not open selected file")
                                val tempFile = File(context.cacheDir, fileName ?: "recording.mp3")
                                tempFile.outputStream().use { output ->
                                    inputStream.copyTo(output)
                                }
                                inputStream.close()

                                val mimeType = context.contentResolver.getType(uri) ?: "audio/*"
                                val requestBody = tempFile.asRequestBody(mimeType.toMediaTypeOrNull())
                                val audioPart = MultipartBody.Part.createFormData(
                                    "audio", tempFile.name, requestBody
                                )

                                val result = RetrofitClient.apiService.analyzeCall(audioPart)
                                onResultReady(result)
                            } catch (e: Exception) {
                                errorMessage = "Couldn't analyze the recording: ${e.message}"
                            } finally {
                                isProcessing = false
                            }
                        }
                    },
                    shape = RoundedCornerShape(28.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color.White.copy(alpha = 0.85f),
                        contentColor = Color(0xFF0D47A1)
                    ),
                    modifier = Modifier.height(56.dp)
                ) {
                    Text(
                        text = stringResource(R.string.analyze_recording),
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }
    }
}